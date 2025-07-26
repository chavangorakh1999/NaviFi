from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json
import logging
from typing import AsyncGenerator, Optional
import uvicorn
from root_agent.agent import root_agent
import os
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="NaviFi Financial Agent API",
    description="Intelligent streaming API for comprehensive financial planning and analysis",
    version="2.0.0"
)

class ChatRequest(BaseModel):
    prompt: str
    user_id: str = "default_user"
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    status: str = "success"
    agents_used: Optional[list] = None
    authentication_required: bool = False
    login_url: Optional[str] = None

async def stream_agent_response(prompt: str, user_id: str, session_id: Optional[str] = None) -> AsyncGenerator[str, None]:
    """
    Stream responses from the intelligent financial agent with robust error handling
    """
    agents_invoked = []
    authentication_required = False
    login_url = os.getenv("MCP_LOGIN_URL", "https://your-mcp-server.com/login")
    
    try:
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
        from google.genai import types
        
        logger.info(f"Processing prompt for user {user_id}: {prompt[:100]}...")
        
        # Send initial response with authentication check
        yield f"data: {json.dumps({'type': 'start', 'message': 'Analyzing your financial query...', 'timestamp': datetime.now().isoformat()})}\n\n"
        
        # Create session and runner with error handling
        try:
            session_service = InMemorySessionService()
            app_name = "navifi_api"
            
            if session_id:
                try:
                    session = await session_service.get_session(app_name=app_name, user_id=user_id, session_id=session_id)
                except:
                    logger.info(f"Session {session_id} not found, creating new session")
                    session = await session_service.create_session(app_name=app_name, user_id=user_id)
            else:
                session = await session_service.create_session(app_name=app_name, user_id=user_id)
            
            runner = Runner(agent=root_agent, app_name=app_name, session_service=session_service)
            
        except Exception as e:
            logger.error(f"Session/Runner creation failed: {str(e)}")
            yield f"data: {json.dumps({'type': 'error', 'message': 'Failed to initialize session. Please try again.'})}\n\n"
            return
        
        # Check authentication status by looking at context state
        yield f"data: {json.dumps({'type': 'status', 'message': 'Checking authentication and data availability...'})}\n\n"
        
        # Create user message content
        content = types.Content(role='user', parts=[types.Part(text=prompt)])
        
        # Run the agent with comprehensive error handling
        full_response = ""
        agent_count = 0
        successful_agents = []
        failed_agents = []
        
        try:
            async for event in runner.run_async(user_id=user_id, session_id=session.id, new_message=content):
                if event.content and event.content.parts:
                    # Extract text from event parts
                    event_text = ''.join(part.text or '' for part in event.content.parts if part.text)
                    if event_text:
                        # Check for authentication errors in the response
                        if "login" in event_text.lower() or "authentication" in event_text.lower():
                            authentication_required = True
                        
                        # Check for agent invocation mentions
                        if "agent" in event_text.lower():
                            agent_count += 1
                        
                        # Stream in smaller chunks for better UX
                        chunk_size = 30
                        for i in range(0, len(event_text), chunk_size):
                            chunk = event_text[i:i + chunk_size]
                            full_response += chunk
                            
                            yield f"data: {json.dumps({'type': 'chunk', 'content': chunk, 'agents_active': agent_count})}\n\n"
                            await asyncio.sleep(0.02)  # Slightly slower for better readability
                
                # Check if this is the final response
                if hasattr(event, 'is_final_response') and event.is_final_response():
                    break
                    
        except Exception as agent_error:
            logger.error(f"Agent execution error: {str(agent_error)}")
            
            # Provide graceful degradation
            error_message = "I encountered an issue while processing your request. "
            
            if "authentication" in str(agent_error).lower() or "login" in str(agent_error).lower():
                authentication_required = True
                error_message += f"It seems you need to login to access your financial data. Please visit: {login_url}"
            elif "timeout" in str(agent_error).lower():
                error_message += "The request timed out. Please try with a simpler query or check your connection."
            elif "tool" in str(agent_error).lower():
                error_message += "Some data sources are temporarily unavailable, but I can still help with general financial advice."
            else:
                error_message += "I can still provide general financial guidance based on your query."
            
            yield f"data: {json.dumps({'type': 'partial_error', 'message': error_message, 'can_continue': True})}\n\n"
            
            # Try to provide fallback response
            fallback_response = await generate_fallback_response(prompt)
            if fallback_response:
                yield f"data: {json.dumps({'type': 'chunk', 'content': fallback_response})}\n\n"
                full_response += fallback_response
        
        # Send completion signal with metadata
        completion_data = {
            'type': 'end', 
            'message': 'Response complete',
            'agents_used': agent_count,
            'authentication_required': authentication_required,
            'response_length': len(full_response),
            'timestamp': datetime.now().isoformat()
        }
        
        if authentication_required:
            completion_data['login_url'] = login_url
            completion_data['auth_message'] = "Login required for personalized analysis"
        
        yield f"data: {json.dumps(completion_data)}\n\n"
        
    except Exception as e:
        logger.error(f"Critical error processing request: {str(e)}")
        yield f"data: {json.dumps({
            'type': 'critical_error', 
            'message': f'Service temporarily unavailable. Please try again in a moment.',
            'technical_details': str(e)[:100],  # Limited details for security
            'timestamp': datetime.now().isoformat()
        })}\n\n"

async def generate_fallback_response(prompt: str) -> str:
    """
    Generate a basic financial response when agents fail
    """
    try:
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['invest', 'sip', 'stocks', 'mutual fund']):
            return """
            Based on your investment query, here are some general recommendations:
            
            📈 **SIP Investment Basics:**
            - Start with diversified equity mutual funds
            - Consider your risk tolerance and investment horizon
            - Review portfolio quarterly but avoid frequent changes
            
            💡 **General Guidelines:**
            - Emergency fund: 6-12 months expenses
            - Equity allocation: 100 - your age (rough guideline)
            - Regular review and rebalancing
            
            For personalized recommendations based on your financial data, please login to access your complete profile.
            """
            
        elif any(word in prompt_lower for word in ['budget', 'expense', 'spending']):
            return """
            💰 **Budgeting Best Practices:**
            - Track all expenses for at least a month
            - Follow 50/30/20 rule: needs/wants/savings
            - Automate savings and investments
            
            📊 **Expense Management:**
            - Categorize expenses: fixed, variable, discretionary
            - Look for subscription optimization opportunities
            - Use apps or spreadsheets for tracking
            
            For detailed spending analysis based on your actual transactions, please login to access your financial data.
            """
            
        elif any(word in prompt_lower for word in ['retirement', 'epf', 'pension']):
            return """
            🏖️ **Retirement Planning Basics:**
            - Start as early as possible (compound interest)
            - Maximize EPF contributions if available
            - Consider NPS/PPF for additional tax benefits
            
            📈 **Retirement Corpus Planning:**
            - Target: 25-30x annual expenses
            - Diversify across asset classes
            - Review and adjust regularly
            
            For personalized retirement projections based on your current savings, please login to access your financial profile.
            """
        else:
            return """
            I'd be happy to help with your financial query! For the most accurate and personalized advice, I would need access to your financial data.
            
            🔐 **To get started:**
            1. Login to securely connect your financial accounts
            2. I'll analyze your complete financial picture
            3. Receive personalized recommendations
            
            In the meantime, feel free to ask general financial questions!
            """
            
    except Exception as e:
        logger.error(f"Fallback response generation failed: {str(e)}")
        return "I'm experiencing technical difficulties but I'm still here to help with general financial questions!"

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream chat responses from the intelligent financial agent with robust error handling
    """
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    
    return StreamingResponse(
        stream_agent_response(request.prompt, request.user_id, request.session_id),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
            "X-API-Version": "2.0.0"
        }
    )

@app.post("/chat", response_model=ChatResponse)
async def chat_complete(request: ChatRequest):
    """
    Get complete response from the intelligent financial agent with enhanced error handling
    """
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    
    try:
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
        from google.genai import types
        
        logger.info(f"Processing complete response for user {request.user_id}")
        
        # Create session and runner with error handling
        session_service = InMemorySessionService()
        app_name = "navifi_api"
        
        if request.session_id:
            try:
                session = await session_service.get_session(app_name=app_name, user_id=request.user_id, session_id=request.session_id)
            except:
                session = await session_service.create_session(app_name=app_name, user_id=request.user_id)
        else:
            session = await session_service.create_session(app_name=app_name, user_id=request.user_id)
        
        runner = Runner(agent=root_agent, app_name=app_name, session_service=session_service)
        
        # Create user message content
        content = types.Content(role='user', parts=[types.Part(text=request.prompt)])
        
        # Run the agent and collect complete response
        full_response = ""
        authentication_required = False
        agents_used = []
        
        try:
            async for event in runner.run_async(user_id=request.user_id, session_id=session.id, new_message=content):
                if event.content and event.content.parts:
                    # Extract text from event parts
                    event_text = ''.join(part.text or '' for part in event.content.parts if part.text)
                    if event_text:
                        full_response += event_text
                        
                        # Check for authentication requirements
                        if "login" in event_text.lower() or "authentication" in event_text.lower():
                            authentication_required = True
                
                # Check if this is the final response
                if hasattr(event, 'is_final_response') and event.is_final_response():
                    break
                    
        except Exception as agent_error:
            logger.error(f"Agent execution error: {str(agent_error)}")
            
            # Provide fallback response
            if "authentication" in str(agent_error).lower():
                authentication_required = True
                fallback = await generate_fallback_response(request.prompt)
                full_response = fallback + f"\n\nPlease login at: {os.getenv('MCP_LOGIN_URL', 'https://your-mcp-server.com/login')}"
            else:
                fallback = await generate_fallback_response(request.prompt)
                full_response = fallback + "\n\nNote: Some features may be limited due to temporary technical issues."
        
        return ChatResponse(
            response=full_response or "I apologize, but I couldn't generate a response. Please try again.",
            status="success" if full_response else "partial_success",
            agents_used=agents_used,
            authentication_required=authentication_required,
            login_url=os.getenv('MCP_LOGIN_URL') if authentication_required else None
        )
        
    except Exception as e:
        logger.error(f"Critical error processing request: {str(e)}")
        
        # Always return a helpful response rather than failing completely
        fallback_response = await generate_fallback_response(request.prompt)
        
        return ChatResponse(
            response=fallback_response + "\n\nNote: Full functionality temporarily limited. Please try again shortly.",
            status="fallback",
            authentication_required=True,
            login_url=os.getenv('MCP_LOGIN_URL')
        )

@app.get("/health")
async def health_check():
    """
    Enhanced health check endpoint
    """
    return {
        "status": "healthy", 
        "service": "NaviFi Intelligent Financial Agent API",
        "version": "2.0.0",
        "features": {
            "dynamic_agent_selection": True,
            "intelligent_error_handling": True,
            "authentication_aware": True,
            "streaming_responses": True
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
async def root():
    """
    Root endpoint with comprehensive API information
    """
    return {
        "message": "NaviFi Intelligent Financial Agent API",
        "version": "2.0.0",
        "description": "Dynamic financial planning with intelligent agent selection",
        "endpoints": {
            "streaming_chat": "/chat/stream",
            "complete_chat": "/chat", 
            "health": "/health"
        },
        "features": [
            "🧠 Dynamic agent selection based on query analysis",
            "🔐 Authentication-aware responses",
            "🚨 Robust error handling and graceful degradation", 
            "⚡ Optimized parallel/sequential agent execution",
            "📊 Context state management for data efficiency"
        ],
        "authentication": {
            "required_for": "Personalized financial data analysis",
            "login_endpoint": os.getenv('MCP_LOGIN_URL', '/login')
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 