"""
Simplified NaviFi API with Security Guardrails
This version works without google.adk dependency
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json
import logging
from typing import AsyncGenerator
import uvicorn
from datetime import datetime

# Import security guardrails
from guardrails import (
    ToolSecurityGuardrail, 
    before_tool_guardrail, 
    ALLOWED_FETCH_TOOLS,
    rate_limit_store
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize security components
security_guardrail = ToolSecurityGuardrail()

app = FastAPI(
    title="NaviFi Financial Agent API (Simplified)",
    description="Secure streaming API for comprehensive financial planning and analysis",
    version="2.0.0"
)

class ChatRequest(BaseModel):
    prompt: str
    user_id: str = "default_user"

class ChatResponse(BaseModel):
    response: str
    status: str = "success"
    security_info: dict = None

# Mock agent response for testing
async def mock_agent_response(prompt: str, user_id: str) -> str:
    """
    Mock agent response for testing without google.adk
    """
    # Simulate processing time
    await asyncio.sleep(1)
    
    # Generate mock response based on prompt
    if "net worth" in prompt.lower():
        return "Based on your financial data, your current net worth is approximately $150,000. This includes your assets and liabilities."
    elif "credit" in prompt.lower():
        return "Your credit score is 750, which is considered excellent. You have a good credit history with no late payments."
    elif "epf" in prompt.lower():
        return "Your EPF balance is ₹2,50,000 with monthly contributions of ₹12,000. Your retirement corpus is growing steadily."
    elif "mutual fund" in prompt.lower() or "mf" in prompt.lower():
        return "You have invested ₹5,00,000 in mutual funds across 3 different schemes. Your current portfolio value is ₹5,25,000."
    elif "bank" in prompt.lower():
        return "Your bank account shows a balance of ₹75,000. Recent transactions include salary credit, utility payments, and grocery purchases."
    elif "stock" in prompt.lower():
        return "Your stock portfolio is valued at ₹3,00,000 with investments in 8 different companies. Your returns are 12% year-to-date."
    elif "sip" in prompt.lower():
        return "Current best SIP plans include HDFC Mid-Cap Opportunities Fund, Axis Bluechip Fund, and ICICI Prudential Technology Fund."
    elif "market" in prompt.lower():
        return "Current market trends show strong performance in technology and healthcare sectors. Nifty 50 is trading at 22,500 levels."
    else:
        return "I can help you with financial queries including net worth, credit reports, EPF details, mutual funds, bank transactions, and stock analysis. What specific information would you like to know?"

async def stream_agent_response(prompt: str, user_id: str) -> AsyncGenerator[str, None]:
    """
    Stream responses from the financial agent with security guardrails
    """
    try:
        # 1. Apply pre-execution security guardrails
        pre_result = await security_guardrail.apply_pre_hook(prompt, user_id)
        
        if pre_result.blocked:
            yield f"data: {json.dumps({'type': 'error', 'message': pre_result.output})}\n\n"
            return
        
        logger.info(f"Processing secure prompt for user {user_id}: {prompt[:50]}...")
        
        # Send initial response
        yield f"data: {json.dumps({'type': 'start', 'message': 'Processing your financial query securely...'})}\n\n"
        
        # Get mock response
        response_text = await mock_agent_response(pre_result.output, user_id)
        
        # Apply post-execution security guardrails
        post_result = await security_guardrail.apply_post_hook(response_text, user_id)
        sanitized_text = post_result.output
        
        # Stream in chunks for better UX
        chunk_size = 50
        for i in range(0, len(sanitized_text), chunk_size):
            chunk = sanitized_text[i:i + chunk_size]
            yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
            await asyncio.sleep(0.01)
        
        # Send completion signal
        yield f"data: {json.dumps({'type': 'end', 'message': 'Response complete'})}\n\n"
        
    except Exception as e:
        logger.error(f"Error processing secure request: {str(e)}")
        yield f"data: {json.dumps({'type': 'error', 'message': f'Security Error: {str(e)}'})}\n\n"

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream chat responses from the financial agent with security guardrails
    """
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    
    return StreamingResponse(
        stream_agent_response(request.prompt, request.user_id),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        }
    )

@app.post("/chat", response_model=ChatResponse)
async def chat_complete(request: ChatRequest):
    """
    Get complete response from the financial agent with security guardrails (non-streaming)
    """
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    
    try:
        # 1. Apply pre-execution security guardrails
        pre_result = await security_guardrail.apply_pre_hook(request.prompt, request.user_id)
        
        if pre_result.blocked:
            raise HTTPException(status_code=403, detail=pre_result.output)
        
        logger.info(f"Processing secure complete response for user {request.user_id}")
        
        # Get mock response
        response_text = await mock_agent_response(pre_result.output, request.user_id)
        
        # 2. Apply post-execution security guardrails
        post_result = await security_guardrail.apply_post_hook(response_text, request.user_id)
        
        return ChatResponse(
            response=post_result.output,
            status="success",
            security_info={
                "user_id": request.user_id,
                "timestamp": datetime.now().isoformat(),
                "guardrails_applied": True,
                "input_sanitized": True,
                "output_sanitized": True
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing secure request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy", 
        "service": "NaviFi Financial Agent API (Simplified)",
        "version": "2.0.0",
        "security_enabled": True,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/security/status")
async def get_security_status():
    """
    Get security monitoring status
    """
    return {
        "allowed_tools": list(ALLOWED_FETCH_TOOLS.keys()),
        "rate_limit_store_size": len(rate_limit_store),
        "security_features": [
            "Input sanitization",
            "Pattern blocking", 
            "Rate limiting",
            "Tool restriction",
            "Output sanitization",
            "PII redaction",
            "Security logging"
        ],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/security/tools")
async def get_allowed_tools():
    """
    Get information about allowed tools and their restrictions
    """
    return {
        "allowed_tools": ALLOWED_FETCH_TOOLS,
        "security_policy": {
            "tool_whitelist": "Only pre-approved tools are allowed",
            "rate_limiting": "Per-tool and per-user rate limits enforced",
            "argument_validation": "Strict argument validation for all tools",
            "logging": "All tool usage is logged for security monitoring"
        }
    }

@app.get("/")
async def root():
    """
    Root endpoint with API information
    """
    return {
        "message": "NaviFi Financial Agent API (Simplified)",
        "version": "2.0.0",
        "description": "Secure financial data analysis with comprehensive guardrails (Simplified version)",
        "security_features": [
            "Tool access control",
            "Input validation",
            "Rate limiting", 
            "PII protection",
            "Security logging"
        ],
        "endpoints": {
            "streaming_chat": "/chat/stream",
            "complete_chat": "/chat",
            "health": "/health",
            "security_status": "/security/status",
            "security_tools": "/security/tools"
        },
        "note": "This is a simplified version for testing security guardrails"
    }

if __name__ == "__main__":
    print("🚀 Starting NaviFi Simplified API with Security Guardrails...")
    print("🔒 Security Features Enabled:")
    print("   - Tool access control")
    print("   - Input validation and sanitization")
    print("   - Rate limiting")
    print("   - PII protection")
    print("   - Security logging")
    print("   - Pattern blocking")
    print("📡 Server will be available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    ) 