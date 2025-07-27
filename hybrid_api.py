"""
Hybrid NaviFi API - Complete Implementation of Hybrid AI Orchestration Strategy

This API integrates local privacy-first components with cloud AI agents:
🎙️ Intent Agent (Local) - Fast voice/text parsing
🔒 PII Masking/Tokenizer (Local) - Privacy-first data anonymization  
📊 Privacy Tiers - Configurable privacy modes
🌐 Cloud Agents - Full financial analysis capabilities
📱 Multimodal Support - Voice, documents, real-time streaming
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json
import logging
from typing import AsyncGenerator, Optional, List, Dict, Any, Union
import uvicorn
from datetime import datetime
import base64

# Import existing cloud agents
from root_agent.agent import root_agent

# Import new local components
from root_agent.intent_agent import (
    LocalIntentAgent, create_intent_agent, QueryIntent, PrivacyLevel
)
from root_agent.pii_tokenizer import (
    PrivacyTokenizer, create_privacy_tokenizer, PIIType, TokenizationResult
)
from root_agent.privacy_tiers import (
    PrivacyTierManager, create_privacy_manager, PrivacyTier, DataSensitivity
)
from root_agent.streaming_config import (
    MultimodalStreamingProcessor, create_cloud_hybrid_config, 
    create_private_first_config, create_offline_mode_config,
    VoiceInput, DocumentInput, ProcessingResult
)

import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="NaviFi Hybrid AI Financial Agent",
    description="Privacy-first hybrid AI orchestration for comprehensive financial planning",
    version="3.0.0"
)

# Global components - Initialize once
intent_agent = create_intent_agent()
privacy_manager = create_privacy_manager()

# Session management
active_sessions: Dict[str, Dict[str, Any]] = {}

# Request/Response Models
class HybridChatRequest(BaseModel):
    prompt: str
    user_id: str = "default_user"
    session_id: Optional[str] = None
    privacy_tier: Optional[str] = "cloud_hybrid"  # cloud_hybrid, private_first, offline_mode
    enable_voice_response: bool = False
    privacy_level: Optional[str] = "standard"  # minimal, standard, aggressive

class VoiceChatRequest(BaseModel):
    audio_data: str  # Base64 encoded audio
    audio_format: str = "wav"
    duration_seconds: float
    user_id: str = "default_user"
    session_id: Optional[str] = None
    privacy_tier: Optional[str] = "cloud_hybrid"
    language: str = "en-IN"

class HybridChatResponse(BaseModel):
    response: str
    status: str = "success"
    processing_summary: Dict[str, Any]
    privacy_report: Dict[str, Any]
    intent_analysis: Optional[Dict[str, Any]] = None
    authentication_required: bool = False
    login_url: Optional[str] = None

class DocumentProcessRequest(BaseModel):
    user_id: str = "default_user"
    session_id: Optional[str] = None
    privacy_tier: Optional[str] = "private_first"  # Documents default to private processing
    query: Optional[str] = "Analyze this document"

def get_or_create_session(user_id: str, session_id: Optional[str], privacy_tier: str) -> Dict[str, Any]:
    """Get existing session or create new one with privacy configuration"""
    
    if session_id and session_id in active_sessions:
        return active_sessions[session_id]
    
    # Create new session
    new_session_id = session_id or f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Map privacy tier string to enum
    tier_mapping = {
        "cloud_hybrid": PrivacyTier.CLOUD_HYBRID,
        "private_first": PrivacyTier.PRIVATE_FIRST,
        "offline_mode": PrivacyTier.OFFLINE_MODE
    }
    
    privacy_tier_enum = tier_mapping.get(privacy_tier, PrivacyTier.CLOUD_HYBRID)
    
    # Create session components
    tokenizer = create_privacy_tokenizer(new_session_id)
    
    # Create appropriate streaming config
    if privacy_tier_enum == PrivacyTier.PRIVATE_FIRST:
        stream_config = create_private_first_config(user_id, new_session_id)
    elif privacy_tier_enum == PrivacyTier.OFFLINE_MODE:
        stream_config = create_offline_mode_config(user_id, new_session_id)
    else:
        stream_config = create_cloud_hybrid_config(user_id, new_session_id)
    
    streaming_processor = MultimodalStreamingProcessor(stream_config)
    
    session = {
        "session_id": new_session_id,
        "user_id": user_id,
        "privacy_tier": privacy_tier_enum,
        "tokenizer": tokenizer,
        "streaming_processor": streaming_processor,
        "created_at": datetime.now(),
        "last_activity": datetime.now()
    }
    
    active_sessions[new_session_id] = session
    
    # Set user's privacy tier in manager
    privacy_manager.set_user_privacy_tier(user_id, privacy_tier_enum, "User preference")
    
    logger.info(f"Created new session {new_session_id} for user {user_id} with {privacy_tier} privacy")
    
    return session

async def hybrid_process_request(session: Dict[str, Any], user_input: str, privacy_level: str = "standard") -> Dict[str, Any]:
    """
    Main hybrid processing pipeline that coordinates local and cloud components
    """
    
    try:
        processing_start = datetime.now()
        
        # 1. LOCAL PROCESSING - Intent Analysis
        logger.info("Step 1: Local intent analysis")
        intent_analysis = await intent_agent.analyze_intent(user_input, session["privacy_tier"])
        
        # 2. LOCAL PROCESSING - PII Detection and Tokenization
        logger.info("Step 2: PII detection and tokenization")
        tokenization_result = await session["tokenizer"].tokenize_text(user_input, privacy_level)
        
        # 3. PRIVACY DECISION - Determine data flow
        logger.info("Step 3: Privacy tier evaluation")
        data_flow_decision = await privacy_manager.evaluate_data_flow(
            user_id=session["user_id"],
            query=user_input,
            data_sensitivity=DataSensitivity.PERSONAL if intent_analysis.requires_personal_data else DataSensitivity.PUBLIC,
            pii_detected=tokenization_result.pii_detections,
            intended_agents=intent_analysis.suggested_agents
        )
        
        # 4. CLOUD PROCESSING - If allowed by privacy tier
        response_text = ""
        agents_used = []
        authentication_required = False
        
        if data_flow_decision.can_process_in_cloud and session["privacy_tier"] != PrivacyTier.OFFLINE_MODE:
            logger.info("Step 4: Cloud agent processing")
            
            # Use tokenized text for cloud processing
            cloud_input = tokenization_result.masked_text if data_flow_decision.requires_tokenization else user_input
            
            try:
                # Run cloud agents with filtered agent list
                from google.adk.runners import Runner
                from google.adk.sessions import InMemorySessionService
                from google.genai import types
                
                session_service = InMemorySessionService()
                app_name = "navifi_hybrid_api"
                
                adk_session = await session_service.create_session(app_name=app_name, user_id=session["user_id"])
                runner = Runner(agent=root_agent, app_name=app_name, session_service=session_service)
                
                # Create user message content
                content = types.Content(role='user', parts=[types.Part(text=cloud_input)])
                
                # Collect cloud response
                cloud_response = ""
                async for event in runner.run_async(user_id=session["user_id"], session_id=adk_session.id, new_message=content):
                    if event.content and event.content.parts:
                        event_text = ''.join(part.text or '' for part in event.content.parts if part.text)
                        if event_text:
                            cloud_response += event_text
                
                # Detokenize response if needed
                if data_flow_decision.requires_tokenization:
                    response_text = await session["tokenizer"].detokenize_response(cloud_response)
                else:
                    response_text = cloud_response
                
                agents_used = data_flow_decision.suggested_agents
                
                # Check for authentication requirements
                if "login" in response_text.lower() or "authentication" in response_text.lower():
                    authentication_required = True
                
            except Exception as cloud_error:
                logger.error(f"Cloud processing failed: {str(cloud_error)}")
                response_text = await generate_local_fallback_response(intent_analysis, user_input)
                authentication_required = "authentication" in str(cloud_error).lower()
        
        else:
            logger.info("Step 4: Local-only processing (privacy restricted)")
            response_text = await generate_local_fallback_response(intent_analysis, user_input)
        
        # 5. LOCAL PROCESSING - Generate final response with privacy context
        if session["privacy_tier"] == PrivacyTier.OFFLINE_MODE:
            response_text += "\n\n🔴 **Offline Mode**: This response is based on cached data only. For real-time information, consider switching to Private-First or Cloud Hybrid mode."
        elif session["privacy_tier"] == PrivacyTier.PRIVATE_FIRST:
            response_text += "\n\n🟡 **Private-First Mode**: Your personal data was processed locally for maximum privacy."
        
        processing_time = (datetime.now() - processing_start).total_seconds()
        
        # Update session activity
        session["last_activity"] = datetime.now()
        
        return {
            "response": response_text,
            "processing_summary": {
                "intent": intent_analysis.primary_intent.value,
                "confidence": intent_analysis.confidence_score,
                "processing_time_seconds": processing_time,
                "privacy_tier": session["privacy_tier"].value,
                "agents_used": agents_used,
                "cloud_processing": data_flow_decision.can_process_in_cloud,
                "tokenization_applied": data_flow_decision.requires_tokenization
            },
            "privacy_report": {
                "pii_detections": len(tokenization_result.pii_detections),
                "privacy_score": tokenization_result.privacy_score,
                "data_stayed_local": not data_flow_decision.can_process_in_cloud,
                "tokenization_required": data_flow_decision.requires_tokenization,
                "reasoning": data_flow_decision.reasoning
            },
            "intent_analysis": {
                "primary_intent": intent_analysis.primary_intent.value,
                "confidence": intent_analysis.confidence_score,
                "requires_personal_data": intent_analysis.requires_personal_data,
                "suggested_agents": intent_analysis.suggested_agents,
                "estimated_time": intent_analysis.estimated_response_time
            },
            "authentication_required": authentication_required
        }
        
    except Exception as e:
        logger.error(f"Hybrid processing failed: {str(e)}")
        return {
            "response": "I apologize, but I encountered an error processing your request. Your privacy settings have been maintained.",
            "processing_summary": {"error": str(e), "privacy_tier": session["privacy_tier"].value},
            "privacy_report": {"error": "Processing failed, no data transmitted"},
            "intent_analysis": None,
            "authentication_required": False
        }

async def generate_local_fallback_response(intent_analysis, user_input: str) -> str:
    """Generate local fallback response based on intent analysis"""
    
    intent = intent_analysis.primary_intent
    
    if intent == QueryIntent.NET_WORTH:
        return """
🏠 **Net Worth Analysis** (Local Mode)

For a complete net worth analysis, I would need access to your financial accounts. In privacy-first mode, here's what I can help you with:

📊 **Manual Net Worth Calculation:**
- **Assets**: Cash + Investments + Property + Other valuables
- **Liabilities**: Loans + Credit card debt + Other debts
- **Net Worth** = Total Assets - Total Liabilities

💡 **Best Practices:**
- Update valuations quarterly
- Include all accounts and assets
- Don't forget employer-provided benefits (EPF, insurance)

To get personalized analysis, you can switch to Cloud Hybrid mode or login to securely connect your accounts.
"""
    
    elif intent == QueryIntent.STOCK_RESEARCH:
        return """
📈 **Investment Research** (Local Mode)

I'd normally provide real-time stock recommendations, but in privacy/offline mode, here are general principles:

🎯 **Investment Guidelines:**
- **Diversification**: Don't put all money in one stock
- **Research**: Understand the company before investing
- **Risk Management**: Only invest what you can afford to lose
- **Long-term Focus**: Markets fluctuate, stay disciplined

💡 **For Current Recommendations:**
Switch to Cloud Hybrid mode for real-time market data and specific stock/SIP suggestions.
"""
    
    elif intent in [QueryIntent.SALARY_HIKE, QueryIntent.JOB_LOSS, QueryIntent.MARRIAGE]:
        return f"""
🎯 **Life Event Planning** (Local Mode)

I can provide general guidance for your situation:

📋 **General Steps:**
1. **Assess Current Situation**: Review income, expenses, savings
2. **Set Priorities**: List immediate vs. long-term goals  
3. **Create Action Plan**: Break down into specific steps
4. **Emergency Planning**: Ensure adequate safety net

💡 **For Personalized Planning:**
Switch to Cloud Hybrid or Private-First mode for detailed analysis based on your actual financial data and current market conditions.
"""
    
    else:
        return """
💭 **General Financial Guidance** (Local Mode)

I'm operating in privacy-first mode, so I can provide general advice without accessing external data.

🔐 **Privacy Benefits:**
- Your data stays completely on your device
- No cloud processing of personal information
- Maximum privacy protection

🌐 **For Enhanced Features:**
- **Private-First Mode**: Limited cloud access for market data only
- **Cloud Hybrid Mode**: Full features with privacy safeguards

How can I help you with general financial planning questions?
"""

async def stream_hybrid_response(session: Dict[str, Any], user_input: str, privacy_level: str = "standard") -> AsyncGenerator[str, None]:
    """Stream hybrid processing with real-time updates"""
    
    try:
        # Initial status
        yield f"data: {json.dumps({'type': 'start', 'message': 'Starting privacy-first analysis...', 'timestamp': datetime.now().isoformat()})}\n\n"
        
        # Step 1: Intent analysis
        yield f"data: {json.dumps({'type': 'step', 'step': 1, 'message': 'Analyzing intent locally...', 'privacy_protected': True})}\n\n"
        intent_analysis = await intent_agent.analyze_intent(user_input)
        
        yield f"data: {json.dumps({'type': 'intent', 'intent': intent_analysis.primary_intent.value, 'confidence': intent_analysis.confidence_score})}\n\n"
        
        # Step 2: PII Detection
        yield f"data: {json.dumps({'type': 'step', 'step': 2, 'message': 'Scanning for sensitive information...', 'privacy_protected': True})}\n\n"
        tokenization_result = await session["tokenizer"].tokenize_text(user_input, privacy_level)
        
        if tokenization_result.pii_detections:
            yield f"data: {json.dumps({'type': 'privacy', 'message': f'Protected {len(tokenization_result.pii_detections)} sensitive items', 'privacy_score': tokenization_result.privacy_score})}\n\n"
        
        # Step 3: Privacy decision
        yield f"data: {json.dumps({'type': 'step', 'step': 3, 'message': 'Evaluating privacy requirements...', 'privacy_tier': session['privacy_tier'].value})}\n\n"
        
        # Step 4: Processing
        processing_result = await hybrid_process_request(session, user_input, privacy_level)
        
        # Stream response in chunks
        response_text = processing_result["response"]
        chunk_size = 50
        
        for i in range(0, len(response_text), chunk_size):
            chunk = response_text[i:i + chunk_size]
            yield f"data: {json.dumps({'type': 'chunk', 'content': chunk})}\n\n"
            await asyncio.sleep(0.03)
        
        # Final summary
        yield f"data: {json.dumps({'type': 'complete', 'processing_summary': processing_result['processing_summary'], 'privacy_report': processing_result['privacy_report'], 'timestamp': datetime.now().isoformat()})}\n\n"
        
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': f'Processing failed: {str(e)}', 'timestamp': datetime.now().isoformat()})}\n\n"

# API Endpoints

@app.post("/hybrid/chat/stream")
async def hybrid_chat_stream(request: HybridChatRequest):
    """Stream hybrid chat responses with privacy-first processing"""
    
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    
    # Get or create session
    session = get_or_create_session(request.user_id, request.session_id, request.privacy_tier)
    
    return StreamingResponse(
        stream_hybrid_response(session, request.prompt, request.privacy_level),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "X-Privacy-Tier": session["privacy_tier"].value,
            "X-API-Version": "3.0.0-hybrid"
        }
    )

@app.post("/hybrid/chat", response_model=HybridChatResponse)
async def hybrid_chat_complete(request: HybridChatRequest):
    """Complete hybrid chat response with privacy-first processing"""
    
    if not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    
    # Get or create session
    session = get_or_create_session(request.user_id, request.session_id, request.privacy_tier)
    
    # Process request
    result = await hybrid_process_request(session, request.prompt, request.privacy_level)
    
    return HybridChatResponse(
        response=result["response"],
        processing_summary=result["processing_summary"],
        privacy_report=result["privacy_report"],
        intent_analysis=result["intent_analysis"],
        authentication_required=result["authentication_required"],
        login_url=os.getenv('MCP_LOGIN_URL') if result["authentication_required"] else None
    )

@app.post("/hybrid/voice/chat")
async def hybrid_voice_chat(request: VoiceChatRequest):
    """Process voice input with local speech-to-text and hybrid processing"""
    
    try:
        # Get or create session
        session = get_or_create_session(request.user_id, request.session_id, request.privacy_tier)
        
        # Decode audio data
        audio_bytes = base64.b64decode(request.audio_data)
        
        # Create voice input
        voice_input = VoiceInput(
            audio_data=audio_bytes,
            format=request.audio_format,
            duration_seconds=request.duration_seconds,
            language=request.language
        )
        
        # Process voice input
        voice_result = await session["streaming_processor"].process_voice_input(voice_input)
        
        if not voice_result.processed_text:
            raise HTTPException(status_code=400, detail="Could not process voice input")
        
        # Process the transcribed text
        result = await hybrid_process_request(session, voice_result.processed_text)
        
        # Generate TTS response if requested
        tts_audio = None
        if session["streaming_processor"].config.enable_tts:
            tts_audio = await session["streaming_processor"].text_to_speech(result["response"])
        
        return {
            "transcribed_text": voice_result.processed_text,
            "response": result["response"],
            "audio_response": base64.b64encode(tts_audio).decode() if tts_audio else None,
            "voice_processing": {
                "confidence": voice_result.confidence,
                "processing_time_ms": voice_result.processing_time_ms,
                "privacy_score": voice_result.privacy_score
            },
            "processing_summary": result["processing_summary"],
            "privacy_report": result["privacy_report"]
        }
        
    except Exception as e:
        logger.error(f"Voice processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Voice processing failed: {str(e)}")

@app.post("/hybrid/document/process")
async def hybrid_document_process(
    file: UploadFile = File(...),
    user_id: str = Form("default_user"),
    session_id: Optional[str] = Form(None),
    privacy_tier: str = Form("private_first"),
    query: str = Form("Analyze this document")
):
    """Process document upload with local-first privacy"""
    
    try:
        # Validate file
        if file.size > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=413, detail="File too large")
        
        # Get or create session
        session = get_or_create_session(user_id, session_id, privacy_tier)
        
        # Read file data
        file_data = await file.read()
        
        # Create document input
        document_input = DocumentInput(
            file_data=file_data,
            filename=file.filename,
            file_type=file.filename.split('.')[-1] if '.' in file.filename else 'unknown',
            size_bytes=len(file_data)
        )
        
        # Process document
        doc_result = await session["streaming_processor"].process_document_input(document_input)
        
        # Process the extracted text with user query
        combined_input = f"Document content: {doc_result.processed_text}\n\nUser query: {query}"
        result = await hybrid_process_request(session, combined_input)
        
        return {
            "filename": file.filename,
            "extracted_text": doc_result.processed_text,
            "analysis": result["response"],
            "document_processing": {
                "confidence": doc_result.confidence,
                "processing_time_ms": doc_result.processing_time_ms,
                "privacy_score": doc_result.privacy_score,
                "processed_locally": doc_result.privacy_score > 0.8
            },
            "processing_summary": result["processing_summary"],
            "privacy_report": result["privacy_report"]
        }
        
    except Exception as e:
        logger.error(f"Document processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")

@app.get("/hybrid/privacy/tiers")
async def get_privacy_tiers():
    """Get information about available privacy tiers"""
    
    tiers_info = {}
    for tier in PrivacyTier:
        tiers_info[tier.value] = privacy_manager.get_privacy_tier_info(tier)
    
    return {
        "available_tiers": tiers_info,
        "default_tier": "cloud_hybrid",
        "recommendations": {
            "individual_users": "cloud_hybrid",
            "privacy_conscious": "private_first", 
            "enterprise_users": "private_first",
            "offline_scenarios": "offline_mode"
        }
    }

@app.get("/hybrid/session/{session_id}/report")
async def get_session_privacy_report(session_id: str):
    """Get privacy report for a specific session"""
    
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = active_sessions[session_id]
    user_id = session["user_id"]
    
    # Get comprehensive privacy report
    privacy_report = privacy_manager.get_session_privacy_report(user_id)
    tokenizer_summary = session["tokenizer"].get_privacy_summary()
    streaming_stats = session["streaming_processor"].get_session_stats()
    
    return {
        "session_id": session_id,
        "privacy_tier": session["privacy_tier"].value,
        "session_duration": (datetime.now() - session["created_at"]).total_seconds(),
        "privacy_report": privacy_report,
        "tokenization_summary": tokenizer_summary,
        "processing_stats": streaming_stats
    }

@app.get("/hybrid/health")
async def hybrid_health_check():
    """Enhanced health check for hybrid system"""
    
    return {
        "status": "healthy",
        "service": "NaviFi Hybrid AI Financial Agent",
        "version": "3.0.0",
        "architecture": "hybrid_orchestration",
        "components": {
            "intent_agent": "operational",
            "pii_tokenizer": "operational", 
            "privacy_manager": "operational",
            "cloud_agents": "operational",
            "streaming_processor": "operational"
        },
        "privacy_features": {
            "local_intent_analysis": True,
            "pii_tokenization": True,
            "privacy_tiers": ["cloud_hybrid", "private_first", "offline_mode"],
            "multimodal_support": True,
            "document_local_processing": True
        },
        "active_sessions": len(active_sessions),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
async def hybrid_root():
    """Root endpoint with comprehensive hybrid API information"""
    
    return {
        "message": "NaviFi Hybrid AI Financial Agent - Privacy-First Architecture",
        "version": "3.0.0",
        "architecture": "Hybrid AI Orchestration Strategy",
        "description": "Local privacy processing + Cloud AI capabilities",
        "endpoints": {
            "hybrid_chat": "/hybrid/chat",
            "hybrid_streaming": "/hybrid/chat/stream",
            "voice_chat": "/hybrid/voice/chat",
            "document_processing": "/hybrid/document/process",
            "privacy_tiers": "/hybrid/privacy/tiers",
            "session_report": "/hybrid/session/{session_id}/report",
            "health": "/hybrid/health"
        },
        "privacy_tiers": {
            "🟢 cloud_hybrid": "Full features with privacy safeguards (default)",
            "🟡 private_first": "Local processing preferred, limited cloud",
            "🔴 offline_mode": "Complete privacy, cached responses only"
        },
        "features": [
            "🎙️ Local intent analysis for fast response",
            "🔒 PII tokenization before cloud processing",
            "📊 Three-tier privacy configuration",
            "🌐 Smart cloud/local orchestration",
            "📱 Voice and document multimodal support",
            "⚡ Real-time streaming with privacy protection"
        ],
        "getting_started": {
            "basic_chat": "POST /hybrid/chat with privacy_tier preference",
            "voice_input": "POST /hybrid/voice/chat with base64 audio",
            "document_upload": "POST /hybrid/document/process with file",
            "privacy_config": "GET /hybrid/privacy/tiers for options"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "hybrid_api:app",
        host="0.0.0.0",
        port=8001,  # Different port from original API
        reload=True,
        log_level="info"
    ) 