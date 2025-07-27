"""
Streaming Configuration for Multimodal Capabilities

Handles voice input, document processing, real-time streaming, and privacy-first
multimodal interactions for the NaviFi hybrid AI orchestration system.
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator, Union
from dataclasses import dataclass, asdict
from enum import Enum
import base64
from datetime import datetime
import aiofiles
import tempfile
import os

logger = logging.getLogger(__name__)

class MediaType(Enum):
    VOICE = "voice"
    TEXT = "text"
    PDF = "pdf"
    IMAGE = "image"
    CSV = "csv"
    REAL_TIME = "real_time"

class ProcessingMode(Enum):
    LOCAL_ONLY = "local_only"          # Process completely on device
    LOCAL_FIRST = "local_first"        # Try local, fallback to cloud
    CLOUD_HYBRID = "cloud_hybrid"      # Default cloud with local privacy
    CLOUD_OPTIMIZED = "cloud_optimized" # Full cloud processing

@dataclass
class StreamingConfig:
    user_id: str
    session_id: str
    privacy_mode: ProcessingMode
    enable_voice: bool = True
    enable_tts: bool = True
    enable_document_parsing: bool = True
    max_file_size_mb: int = 10
    supported_formats: List[str] = None
    real_time_updates: bool = True
    local_cache_enabled: bool = True
    
    def __post_init__(self):
        if self.supported_formats is None:
            self.supported_formats = ["pdf", "csv", "xlsx", "txt", "jpg", "png"]

@dataclass
class VoiceInput:
    audio_data: bytes
    format: str  # "wav", "mp3", "webm"
    duration_seconds: float
    language: str = "en-IN"
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class DocumentInput:
    file_data: bytes
    filename: str
    file_type: str
    size_bytes: int
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class ProcessingResult:
    original_input: Union[str, VoiceInput, DocumentInput]
    processed_text: str
    confidence: float
    processing_time_ms: int
    privacy_score: float
    metadata: Dict[str, Any]
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

class MultimodalStreamingProcessor:
    """
    Handles multimodal input processing with privacy-first approach
    """
    
    def __init__(self, config: StreamingConfig):
        self.config = config
        self.session_cache: Dict[str, Any] = {}
        self.processing_stats = {
            "voice_processed": 0,
            "documents_processed": 0,
            "privacy_score_avg": 0.0,
            "session_start": datetime.now()
        }
    
    async def process_voice_input(self, voice_input: VoiceInput) -> ProcessingResult:
        """
        Process voice input with privacy-first speech-to-text
        """
        start_time = datetime.now()
        
        try:
            # For local processing, you'd integrate with on-device STT
            if self.config.privacy_mode == ProcessingMode.LOCAL_ONLY:
                text = await self._local_speech_to_text(voice_input)
                privacy_score = 1.0  # Maximum privacy for local processing
                
            elif self.config.privacy_mode == ProcessingMode.LOCAL_FIRST:
                try:
                    text = await self._local_speech_to_text(voice_input)
                    privacy_score = 1.0
                except Exception as e:
                    logger.warning(f"Local STT failed, falling back to cloud: {e}")
                    text = await self._cloud_speech_to_text(voice_input)
                    privacy_score = 0.6
                    
            else:
                # Cloud processing with privacy considerations
                text = await self._cloud_speech_to_text(voice_input)
                privacy_score = 0.7
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Update statistics
            self.processing_stats["voice_processed"] += 1
            
            return ProcessingResult(
                original_input=voice_input,
                processed_text=text,
                confidence=0.9,  # Would come from actual STT service
                processing_time_ms=int(processing_time),
                privacy_score=privacy_score,
                metadata={
                    "language": voice_input.language,
                    "duration": voice_input.duration_seconds,
                    "format": voice_input.format,
                    "processing_mode": self.config.privacy_mode.value
                }
            )
            
        except Exception as e:
            logger.error(f"Voice processing failed: {str(e)}")
            return ProcessingResult(
                original_input=voice_input,
                processed_text="",
                confidence=0.0,
                processing_time_ms=0,
                privacy_score=1.0,  # Safe default
                metadata={"error": str(e)},
                errors=[f"Voice processing failed: {str(e)}"]
            )
    
    async def process_document_input(self, document: DocumentInput) -> ProcessingResult:
        """
        Process document input with local-first approach for sensitive documents
        """
        start_time = datetime.now()
        
        try:
            # Always process financial documents locally for privacy
            if document.file_type.lower() in ['pdf', 'csv', 'xlsx'] and self._is_financial_document(document.filename):
                text = await self._local_document_processing(document)
                privacy_score = 1.0
                processing_mode = "local_financial"
                
            elif self.config.privacy_mode == ProcessingMode.LOCAL_ONLY:
                text = await self._local_document_processing(document)
                privacy_score = 1.0
                processing_mode = "local_only"
                
            elif self.config.privacy_mode == ProcessingMode.LOCAL_FIRST:
                try:
                    text = await self._local_document_processing(document)
                    privacy_score = 1.0
                    processing_mode = "local_first"
                except Exception:
                    text = await self._cloud_document_processing(document)
                    privacy_score = 0.5
                    processing_mode = "cloud_fallback"
                    
            else:
                # Cloud processing for non-sensitive documents
                text = await self._cloud_document_processing(document)
                privacy_score = 0.6
                processing_mode = "cloud"
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            # Update statistics
            self.processing_stats["documents_processed"] += 1
            
            return ProcessingResult(
                original_input=document,
                processed_text=text,
                confidence=0.85,
                processing_time_ms=int(processing_time),
                privacy_score=privacy_score,
                metadata={
                    "filename": document.filename,
                    "file_type": document.file_type,
                    "size_bytes": document.size_bytes,
                    "processing_mode": processing_mode
                }
            )
            
        except Exception as e:
            logger.error(f"Document processing failed: {str(e)}")
            return ProcessingResult(
                original_input=document,
                processed_text="",
                confidence=0.0,
                processing_time_ms=0,
                privacy_score=1.0,
                metadata={"error": str(e)},
                errors=[f"Document processing failed: {str(e)}"]
            )
    
    async def stream_agent_response(self, processed_input: ProcessingResult) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream responses from agents with real-time updates
        """
        try:
            # Initial processing status
            yield {
                "type": "processing_start",
                "input_type": type(processed_input.original_input).__name__,
                "privacy_score": processed_input.privacy_score,
                "processing_time": processed_input.processing_time_ms,
                "timestamp": datetime.now().isoformat()
            }
            
            # Simulate agent processing with real-time updates
            agents_to_process = ["intent_analysis", "data_coordination", "financial_analysis", "response_generation"]
            
            for i, agent in enumerate(agents_to_process):
                yield {
                    "type": "agent_processing",
                    "agent": agent,
                    "progress": (i + 1) / len(agents_to_process),
                    "message": f"Processing with {agent.replace('_', ' ').title()}...",
                    "timestamp": datetime.now().isoformat()
                }
                
                # Simulate processing time
                await asyncio.sleep(0.5)
            
            # Final response
            yield {
                "type": "processing_complete",
                "message": "Analysis complete",
                "total_time": processed_input.processing_time_ms + 2000,  # Add agent processing time
                "privacy_maintained": processed_input.privacy_score > 0.8,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            yield {
                "type": "error",
                "message": f"Streaming failed: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    async def _local_speech_to_text(self, voice_input: VoiceInput) -> str:
        """
        Local speech-to-text processing (placeholder for actual implementation)
        In a real implementation, this would use on-device STT libraries
        """
        # Simulate local STT processing
        await asyncio.sleep(0.2)
        
        # This would be replaced with actual local STT library calls
        # e.g., SpeechRecognition with offline engines, or device APIs
        
        # For demonstration, return a placeholder
        return "[LOCAL_STT_PLACEHOLDER] User spoke for {:.1f} seconds".format(voice_input.duration_seconds)
    
    async def _cloud_speech_to_text(self, voice_input: VoiceInput) -> str:
        """
        Cloud-based speech-to-text using Google Speech API
        """
        # Simulate cloud STT processing
        await asyncio.sleep(0.5)
        
        # This would integrate with Google Speech-to-Text API
        # or other cloud STT services
        
        return "[CLOUD_STT_PLACEHOLDER] Processed {:.1f}s audio in {}".format(
            voice_input.duration_seconds, voice_input.language)
    
    async def _local_document_processing(self, document: DocumentInput) -> str:
        """
        Local document processing for privacy-sensitive files
        """
        # Simulate local document processing
        await asyncio.sleep(1.0)
        
        if document.file_type.lower() == 'pdf':
            return f"[LOCAL_PDF] Processed {document.filename} ({document.size_bytes} bytes) locally for privacy"
        elif document.file_type.lower() in ['csv', 'xlsx']:
            return f"[LOCAL_SPREADSHEET] Processed {document.filename} with financial data locally"
        else:
            return f"[LOCAL_DOCUMENT] Processed {document.filename} on device"
    
    async def _cloud_document_processing(self, document: DocumentInput) -> str:
        """
        Cloud-based document processing for non-sensitive files
        """
        # Simulate cloud document processing
        await asyncio.sleep(0.8)
        
        return f"[CLOUD_DOCUMENT] Processed {document.filename} using cloud OCR/parsing services"
    
    def _is_financial_document(self, filename: str) -> bool:
        """
        Determine if a document likely contains financial information
        """
        financial_keywords = [
            'statement', 'bank', 'credit', 'card', 'transaction', 'portfolio',
            'investment', 'tax', 'income', 'salary', 'payslip', 'receipt',
            'invoice', 'mutual', 'fund', 'stock', 'trading', 'loan'
        ]
        
        filename_lower = filename.lower()
        return any(keyword in filename_lower for keyword in financial_keywords)
    
    async def text_to_speech(self, text: str, voice_config: Optional[Dict] = None) -> bytes:
        """
        Convert text to speech for voice responses
        """
        if not self.config.enable_tts:
            return b""
        
        try:
            # This would integrate with Google Text-to-Speech or local TTS
            # For demonstration, return placeholder
            await asyncio.sleep(0.3)
            
            # Would return actual audio bytes in WAV/MP3 format
            return f"[TTS_AUDIO_PLACEHOLDER] {len(text)} characters converted to speech".encode()
            
        except Exception as e:
            logger.error(f"TTS failed: {str(e)}")
            return b""
    
    def get_session_stats(self) -> Dict[str, Any]:
        """
        Get current session processing statistics
        """
        current_time = datetime.now()
        session_duration = (current_time - self.processing_stats["session_start"]).total_seconds()
        
        return {
            "session_id": self.config.session_id,
            "session_duration_seconds": session_duration,
            "voice_inputs_processed": self.processing_stats["voice_processed"],
            "documents_processed": self.processing_stats["documents_processed"],
            "privacy_mode": self.config.privacy_mode.value,
            "average_privacy_score": self.processing_stats["privacy_score_avg"],
            "features_enabled": {
                "voice_input": self.config.enable_voice,
                "text_to_speech": self.config.enable_tts,
                "document_parsing": self.config.enable_document_parsing,
                "real_time_updates": self.config.real_time_updates
            }
        }
    
    def update_privacy_mode(self, new_mode: ProcessingMode):
        """
        Update privacy mode for current session
        """
        self.config.privacy_mode = new_mode
        logger.info(f"Privacy mode updated to: {new_mode.value}")

# Factory functions for easy configuration
def create_cloud_hybrid_config(user_id: str, session_id: str) -> StreamingConfig:
    """Create configuration for cloud hybrid mode (default)"""
    return StreamingConfig(
        user_id=user_id,
        session_id=session_id,
        privacy_mode=ProcessingMode.CLOUD_HYBRID,
        enable_voice=True,
        enable_tts=True,
        enable_document_parsing=True,
        real_time_updates=True
    )

def create_private_first_config(user_id: str, session_id: str) -> StreamingConfig:
    """Create configuration for privacy-first mode"""
    return StreamingConfig(
        user_id=user_id,
        session_id=session_id,
        privacy_mode=ProcessingMode.LOCAL_FIRST,
        enable_voice=True,
        enable_tts=True,
        enable_document_parsing=True,
        max_file_size_mb=5,  # Smaller for local processing
        real_time_updates=True
    )

def create_offline_mode_config(user_id: str, session_id: str) -> StreamingConfig:
    """Create configuration for offline mode"""
    return StreamingConfig(
        user_id=user_id,
        session_id=session_id,
        privacy_mode=ProcessingMode.LOCAL_ONLY,
        enable_voice=True,
        enable_tts=True,
        enable_document_parsing=True,
        max_file_size_mb=3,  # Even smaller for offline
        real_time_updates=False,  # No cloud updates
        local_cache_enabled=True
    )

# Example usage for testing
async def test_streaming_processor():
    """Test the streaming processor with sample inputs"""
    
    # Test voice input
    config = create_private_first_config("test_user", "test_session")
    processor = MultimodalStreamingProcessor(config)
    
    # Simulate voice input
    voice_input = VoiceInput(
        audio_data=b"fake_audio_data",
        format="wav",
        duration_seconds=3.5,
        language="en-IN"
    )
    
    print("Testing voice processing...")
    voice_result = await processor.process_voice_input(voice_input)
    print(f"Voice Result: {voice_result.processed_text}")
    print(f"Privacy Score: {voice_result.privacy_score}")
    
    # Simulate document input
    doc_input = DocumentInput(
        file_data=b"fake_pdf_data",
        filename="bank_statement.pdf",
        file_type="pdf",
        size_bytes=1024000
    )
    
    print("\nTesting document processing...")
    doc_result = await processor.process_document_input(doc_input)
    print(f"Document Result: {doc_result.processed_text}")
    print(f"Privacy Score: {doc_result.privacy_score}")
    
    # Test streaming
    print("\nTesting streaming response...")
    async for update in processor.stream_agent_response(voice_result):
        print(f"Stream Update: {update}")
    
    # Get session stats
    print(f"\nSession Stats: {processor.get_session_stats()}")

if __name__ == "__main__":
    asyncio.run(test_streaming_processor()) 