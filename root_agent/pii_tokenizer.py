"""
PII Masking/Tokenizer (Local) - Privacy-first data anonymization

This component runs locally to identify, mask, and tokenize sensitive information
before sending data to cloud agents. It maintains a secure mapping for reversible
anonymization while protecting user privacy.
"""

import re
import hashlib
import secrets
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import base64
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PIIType(Enum):
    CREDIT_CARD = "credit_card"
    BANK_ACCOUNT = "bank_account"
    PAN_NUMBER = "pan_number"
    AADHAAR = "aadhaar"
    IFSC_CODE = "ifsc_code"
    UAN_NUMBER = "uan_number"
    PHONE_NUMBER = "phone_number"
    EMAIL = "email"
    NAME = "name"
    ADDRESS = "address"
    AMOUNT = "amount"

@dataclass
class PIIDetection:
    pii_type: PIIType
    original_value: str
    masked_value: str
    token: str
    position: Tuple[int, int]  # start, end positions in text
    confidence: float

@dataclass
class TokenizationResult:
    original_text: str
    masked_text: str
    pii_detections: List[PIIDetection]
    privacy_score: float  # 0-1, higher means more sensitive
    session_token: str

class PrivacyTokenizer:
    """
    Local PII tokenization and masking system for privacy-first cloud processing
    """
    
    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or self._generate_session_id()
        self.token_mapping: Dict[str, str] = {}  # token -> original_value
        self.reverse_mapping: Dict[str, str] = {}  # original_value -> token
        self.pii_patterns = self._build_pii_patterns()
        self.name_indicators = self._build_name_indicators()
        
    def _generate_session_id(self) -> str:
        """Generate unique session identifier"""
        return base64.urlsafe_b64encode(secrets.token_bytes(16)).decode().rstrip('=')
    
    def _build_pii_patterns(self) -> Dict[PIIType, List[Tuple[str, float]]]:
        """Build regex patterns for PII detection with confidence scores"""
        return {
            PIIType.CREDIT_CARD: [
                (r'\b(?:4\d{3}|5[1-5]\d{2}|6011|65\d{2})[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', 0.95),
                (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', 0.75)
            ],
            PIIType.BANK_ACCOUNT: [
                (r'\b\d{9,18}\b', 0.60),  # Generic account number
                (r'\baccount\s*(?:number|no\.?)\s*:?\s*(\d{9,18})\b', 0.85)
            ],
            PIIType.PAN_NUMBER: [
                (r'\b[A-Z]{5}\d{4}[A-Z]\b', 0.95),
                (r'\bPAN\s*:?\s*([A-Z]{5}\d{4}[A-Z])\b', 0.98)
            ],
            PIIType.AADHAAR: [
                (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', 0.70),
                (r'\baadhaar\s*:?\s*(\d{4}[-\s]?\d{4}[-\s]?\d{4})\b', 0.95)
            ],
            PIIType.IFSC_CODE: [
                (r'\b[A-Z]{4}0[A-Z0-9]{6}\b', 0.90),
                (r'\bIFSC\s*:?\s*([A-Z]{4}0[A-Z0-9]{6})\b', 0.95)
            ],
            PIIType.UAN_NUMBER: [
                (r'\b\d{12}\b', 0.50),  # Could be UAN or Aadhaar
                (r'\bUAN\s*:?\s*(\d{12})\b', 0.95)
            ],
            PIIType.PHONE_NUMBER: [
                (r'\b(?:\+91[-\s]?)?[6-9]\d{9}\b', 0.85),
                (r'\bmobile\s*:?\s*((?:\+91[-\s]?)?[6-9]\d{9})\b', 0.90)
            ],
            PIIType.EMAIL: [
                (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 0.95)
            ],
            PIIType.AMOUNT: [
                (r'₹\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?', 0.70),
                (r'\b\d+(?:\.\d{2})?\s*(?:lakh|crore|thousand|k)\b', 0.65)
            ]
        }
    
    def _build_name_indicators(self) -> List[str]:
        """Common patterns that indicate names"""
        return [
            r'\bmy name is\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'\bI am\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'\b([A-Z][a-z]+)\s+(?:here|speaking)',
            r'\bMr\.?\s+([A-Z][a-z]+)',
            r'\bMs\.?\s+([A-Z][a-z]+)',
            r'\bDr\.?\s+([A-Z][a-z]+)'
        ]
    
    async def tokenize_text(self, text: str, privacy_level: str = "standard") -> TokenizationResult:
        """
        Main tokenization function - detects and masks PII in text
        
        Args:
            text: Input text to process
            privacy_level: "minimal", "standard", "aggressive"
        """
        try:
            # 1. Detect all PII in text
            detections = await self._detect_pii(text, privacy_level)
            
            # 2. Generate tokens and create masked text
            masked_text = text
            processed_detections = []
            
            # Sort detections by position (reverse order) to maintain positions during replacement
            detections.sort(key=lambda x: x.position[0], reverse=True)
            
            for detection in detections:
                # Generate secure token
                token = self._generate_token(detection.original_value, detection.pii_type)
                
                # Store mapping
                self.token_mapping[token] = detection.original_value
                self.reverse_mapping[detection.original_value] = token
                
                # Replace in text
                start, end = detection.position
                masked_text = masked_text[:start] + detection.masked_value + masked_text[end:]
                
                # Update detection with token
                detection.token = token
                processed_detections.append(detection)
            
            # 3. Calculate privacy score
            privacy_score = self._calculate_privacy_score(processed_detections)
            
            return TokenizationResult(
                original_text=text,
                masked_text=masked_text,
                pii_detections=processed_detections,
                privacy_score=privacy_score,
                session_token=self.session_id
            )
            
        except Exception as e:
            logger.error(f"Tokenization failed: {str(e)}")
            # Return safe fallback
            return TokenizationResult(
                original_text=text,
                masked_text="[TEXT_PROCESSING_ERROR]",
                pii_detections=[],
                privacy_score=1.0,  # Max privacy score for safety
                session_token=self.session_id
            )
    
    async def _detect_pii(self, text: str, privacy_level: str) -> List[PIIDetection]:
        """Detect PII in text based on privacy level"""
        detections = []
        
        # Standard PII detection
        for pii_type, patterns in self.pii_patterns.items():
            for pattern, confidence in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    original_value = match.group(0)
                    
                    # Skip if already detected (avoid duplicates)
                    if any(d.original_value == original_value for d in detections):
                        continue
                    
                    # Apply privacy level filtering
                    if not self._should_mask_by_privacy_level(pii_type, privacy_level, confidence):
                        continue
                    
                    masked_value = self._create_mask(original_value, pii_type)
                    
                    detection = PIIDetection(
                        pii_type=pii_type,
                        original_value=original_value,
                        masked_value=masked_value,
                        token="",  # Will be filled later
                        position=(match.start(), match.end()),
                        confidence=confidence
                    )
                    detections.append(detection)
        
        # Name detection (aggressive privacy level)
        if privacy_level == "aggressive":
            name_detections = await self._detect_names(text)
            detections.extend(name_detections)
        
        return detections
    
    async def _detect_names(self, text: str) -> List[PIIDetection]:
        """Detect potential names in text"""
        detections = []
        
        for pattern in self.name_indicators:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                if match.groups():
                    name = match.group(1)
                    masked_value = f"[NAME_{len(name)}]"
                    
                    detection = PIIDetection(
                        pii_type=PIIType.NAME,
                        original_value=name,
                        masked_value=masked_value,
                        token="",
                        position=(match.start(1), match.end(1)),
                        confidence=0.70
                    )
                    detections.append(detection)
        
        return detections
    
    def _should_mask_by_privacy_level(self, pii_type: PIIType, privacy_level: str, confidence: float) -> bool:
        """Determine if PII should be masked based on privacy level"""
        if privacy_level == "minimal":
            # Only mask high-confidence financial data
            return pii_type in [PIIType.CREDIT_CARD, PIIType.PAN_NUMBER] and confidence > 0.9
        
        elif privacy_level == "standard":
            # Mask financial and identification data
            financial_types = [PIIType.CREDIT_CARD, PIIType.BANK_ACCOUNT, PIIType.PAN_NUMBER, 
                             PIIType.AADHAAR, PIIType.IFSC_CODE, PIIType.UAN_NUMBER]
            return pii_type in financial_types and confidence > 0.6
        
        elif privacy_level == "aggressive":
            # Mask everything including names and amounts
            return confidence > 0.5
        
        return False
    
    def _create_mask(self, original_value: str, pii_type: PIIType) -> str:
        """Create appropriate mask for different PII types"""
        masks = {
            PIIType.CREDIT_CARD: f"[CARD_****{original_value[-4:]}]",
            PIIType.BANK_ACCOUNT: f"[ACCOUNT_****{original_value[-4:]}]",
            PIIType.PAN_NUMBER: f"[PAN_{original_value[:2]}****{original_value[-1:]}]",
            PIIType.AADHAAR: "[AADHAAR_****]",
            PIIType.IFSC_CODE: f"[IFSC_{original_value[:4]}****]",
            PIIType.UAN_NUMBER: "[UAN_****]",
            PIIType.PHONE_NUMBER: f"[PHONE_****{original_value[-4:]}]",
            PIIType.EMAIL: f"[EMAIL_{original_value.split('@')[0][:2]}****]",
            PIIType.NAME: f"[NAME_{len(original_value)}]",
            PIIType.ADDRESS: "[ADDRESS_****]",
            PIIType.AMOUNT: "[AMOUNT_****]"
        }
        
        return masks.get(pii_type, "[MASKED_DATA]")
    
    def _generate_token(self, value: str, pii_type: PIIType) -> str:
        """Generate secure token for value"""
        # Create deterministic but secure token
        token_input = f"{self.session_id}:{pii_type.value}:{value}:{secrets.token_hex(8)}"
        token_hash = hashlib.sha256(token_input.encode()).hexdigest()[:16]
        return f"TKN_{pii_type.value.upper()}_{token_hash}"
    
    def _calculate_privacy_score(self, detections: List[PIIDetection]) -> float:
        """Calculate privacy score based on detected PII"""
        if not detections:
            return 0.0
        
        # Weight different PII types
        weights = {
            PIIType.CREDIT_CARD: 0.9,
            PIIType.BANK_ACCOUNT: 0.8,
            PIIType.PAN_NUMBER: 0.8,
            PIIType.AADHAAR: 0.9,
            PIIType.IFSC_CODE: 0.6,
            PIIType.UAN_NUMBER: 0.7,
            PIIType.PHONE_NUMBER: 0.5,
            PIIType.EMAIL: 0.4,
            PIIType.NAME: 0.6,
            PIIType.ADDRESS: 0.7,
            PIIType.AMOUNT: 0.3
        }
        
        total_score = 0.0
        for detection in detections:
            weight = weights.get(detection.pii_type, 0.5)
            total_score += weight * detection.confidence
        
        # Normalize to 0-1 range
        max_possible_score = len(detections) * 0.9
        return min(total_score / max_possible_score if max_possible_score > 0 else 0, 1.0)
    
    async def detokenize_response(self, tokenized_text: str) -> str:
        """
        Reverse tokenization to restore original values in response
        
        Args:
            tokenized_text: Text containing tokens to be replaced
            
        Returns:
            Text with original values restored
        """
        try:
            detokenized_text = tokenized_text
            
            # Find all tokens in text and replace with original values
            token_pattern = r'TKN_[A-Z_]+_[a-f0-9]{16}'
            
            for match in re.finditer(token_pattern, tokenized_text):
                token = match.group(0)
                if token in self.token_mapping:
                    original_value = self.token_mapping[token]
                    detokenized_text = detokenized_text.replace(token, original_value)
            
            return detokenized_text
            
        except Exception as e:
            logger.error(f"Detokenization failed: {str(e)}")
            return tokenized_text  # Return as-is if detokenization fails
    
    def get_privacy_summary(self) -> Dict[str, Any]:
        """Get summary of current session's privacy processing"""
        pii_types_detected = set()
        total_tokens = len(self.token_mapping)
        
        for token in self.token_mapping.keys():
            # Extract PII type from token
            parts = token.split('_')
            if len(parts) >= 2:
                pii_types_detected.add(parts[1])
        
        return {
            "session_id": self.session_id,
            "total_tokens_generated": total_tokens,
            "pii_types_detected": list(pii_types_detected),
            "privacy_protection_active": total_tokens > 0,
            "timestamp": datetime.now().isoformat()
        }
    
    def clear_session(self):
        """Clear all tokens and mappings for this session"""
        self.token_mapping.clear()
        self.reverse_mapping.clear()
        logger.info(f"Privacy session {self.session_id} cleared")

# Factory function for easy instantiation
def create_privacy_tokenizer(session_id: Optional[str] = None) -> PrivacyTokenizer:
    """Create and return a configured PrivacyTokenizer instance"""
    return PrivacyTokenizer(session_id)

# Example usage for testing
async def test_privacy_tokenizer():
    """Test the privacy tokenizer with sample data"""
    tokenizer = create_privacy_tokenizer()
    
    test_texts = [
        "My credit card number is 4532-1234-5678-9012 and my PAN is ABCDE1234F",
        "My account number is 123456789012 and IFSC is HDFC0001234",
        "I'm John Doe, my phone is +91-9876543210 and email is john@example.com",
        "I spent ₹25,000 last month and have ₹5 lakh in savings"
    ]
    
    for text in test_texts:
        print(f"\nOriginal: {text}")
        
        result = await tokenizer.tokenize_text(text, "standard")
        print(f"Masked: {result.masked_text}")
        print(f"Privacy Score: {result.privacy_score:.2f}")
        print(f"PII Detected: {len(result.pii_detections)} items")
        
        # Test detokenization
        detokenized = await tokenizer.detokenize_response(result.masked_text)
        print(f"Detokenized: {detokenized}")
        print(f"Match Original: {detokenized == text}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_privacy_tokenizer()) 