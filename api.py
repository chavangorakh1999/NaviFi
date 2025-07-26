from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json
import logging
from typing import AsyncGenerator
import uvicorn
from root_agent.agent import root_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="NaviFi Financial Agent API",
    description="Streaming API for comprehensive financial planning and analysis",
    version="1.0.0"
)

class ChatRequest(BaseModel):
    prompt: str
    user_id: str = "default_user"

class ChatResponse(BaseModel):
    response: str
    status: str = "success"

async def stream_agent_response(prompt: str, user_id: str) -> AsyncGenerator[str, None]:
    """
    Stream responses from the financial agent
    """
    try:
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
        from google.genai import types
        
        logger.info(f"Processing prompt for user {user_id}: {prompt[:50]}...")
        
        # Send initial response
        yield f"data: {json.dumps({'type': 'start', 'message': 'Processing your financial query...'})}\n\n"
        
        # Create session and runner
        session_service = InMemorySessionService()
        app_name = "navifi_api"
        session = await session_service.create_session(app_name=app_name, user_id=user_id)
        runner = Runner(agent=root_agent, app_name=app_name, session_service=session_service)
        
        # Create user message content
        content = types.Content(role='user', parts=[types.Part(text=prompt)])
        
        # Run the agent and stream responses
        full_response = ""
        async for event in runner.run_async(user_id=user_id, session_id=session.id, new_message=content):
            if event.content and event.content.parts:
                # Extract text from event parts
                event_text = ''.join(part.text or '' for part in event.content.parts if part.text)
                if event_text:
                    # Stream in chunks for better UX
                    chunk_size = 50
                    for i in range(0, len(event_text), chunk_size):
                        chunk = event_text[i:i + chunk_size]
                        full_response += chunk
                        yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
                        await asyncio.sleep(0.01)
            
            # Check if this is the final response
            if hasattr(event, 'is_final_response') and event.is_final_response():
                break
        
        # Send completion signal
        yield f"data: {json.dumps({'type': 'end', 'message': 'Response complete'})}\n\n"
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        yield f"data: {json.dumps({'type': 'error', 'message': f'Error: {str(e)}'})}\n\n"

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream chat responses from the financial agent
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
    Get complete response from the financial agent (non-streaming)
    """
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    
    try:
        from google.adk.runners import Runner
        from google.adk.sessions import InMemorySessionService
        from google.genai import types
        
        logger.info(f"Processing complete response for user {request.user_id}")
        
        # Create session and runner
        session_service = InMemorySessionService()
        app_name = "navifi_api"
        session = await session_service.create_session(app_name=app_name, user_id=request.user_id)
        runner = Runner(agent=root_agent, app_name=app_name, session_service=session_service)
        
        # Create user message content
        content = types.Content(role='user', parts=[types.Part(text=request.prompt)])
        
        # Run the agent and collect complete response
        full_response = ""
        async for event in runner.run_async(user_id=request.user_id, session_id=session.id, new_message=content):
            if event.content and event.content.parts:
                # Extract text from event parts
                event_text = ''.join(part.text or '' for part in event.content.parts if part.text)
                if event_text:
                    full_response += event_text
            
            # Check if this is the final response
            if hasattr(event, 'is_final_response') and event.is_final_response():
                break
        
        return ChatResponse(
            response=full_response or "No response generated",
            status="success"
        )
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "NaviFi Financial Agent API"}

@app.get("/")
async def root():
    """
    Root endpoint with API information
    """
    return {
        "message": "NaviFi Financial Agent API",
        "version": "1.0.0",
        "endpoints": {
            "streaming_chat": "/chat/stream",
            "complete_chat": "/chat",
            "health": "/health"
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