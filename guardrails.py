from typing import Optional, Dict, Any, List
import re
import os
import logging
import json
from datetime import datetime
import hashlib
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import Google ADK components
try:
    from google.adk.agents import LlmAgent
    from google.adk.runtime.guardrails import Guardrails, GuardrailResult
    from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams
    from google.adk.tools import google_search
    GOOGLE_ADK_AVAILABLE = True
    logger.info("✅ Google ADK components imported successfully")
except ImportError as e:
    GOOGLE_ADK_AVAILABLE = False
    logger.warning(f"⚠️ Google ADK not available: {e}")
    logger.info("📝 Using simplified guardrails implementation")

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================

# Allowed tools for financial data queries - RESTRICTIVE WHITELIST
ALLOWED_FETCH_TOOLS = {
    # MCP Tools (Financial Data)
    "fetch_net_worth": {
        "description": "Get current assets, liabilities, and net worth",
        "allowed_args": {},
        "rate_limit": 10,  # calls per minute
        "requires_auth": True,
        "category": "financial_data"
    },
    "fetch_credit_report": {
        "description": "Get credit score and debt information", 
        "allowed_args": {},
        "rate_limit": 5,  # calls per minute
        "requires_auth": True,
        "category": "financial_data"
    },
    "fetch_epf_details": {
        "description": "Get retirement fund balance and contributions",
        "allowed_args": {},
        "rate_limit": 10,
        "requires_auth": True,
        "category": "financial_data"
    },
    "fetch_mf_transactions": {
        "description": "Get mutual fund investment history",
        "allowed_args": {},
        "rate_limit": 15,
        "requires_auth": True,
        "category": "financial_data"
    },
    "fetch_bank_transactions": {
        "description": "Get complete bank transaction history",
        "allowed_args": {},
        "rate_limit": 20,
        "requires_auth": True,
        "category": "financial_data"
    },
    "fetch_stock_transactions": {
        "description": "Get stock trading history",
        "allowed_args": {},
        "rate_limit": 15,
        "requires_auth": True,
        "category": "financial_data"
    },
    # Google Search Tools (Market Research)
    "google_search": {
        "description": "Search for real-time market information and financial data",
        "allowed_args": {
            "query": "string"  # Search query
        },
        "rate_limit": 30,  # Higher limit for search
        "requires_auth": True,
        "category": "market_research"
    }
}

# Blocked patterns for input sanitization
BLOCKED_PATTERNS = [
    r"password\s*[:=]\s*\w+",  # Password exposure
    r"api[_-]?key\s*[:=]\s*\w+",  # API key exposure
    r"token\s*[:=]\s*\w+",  # Token exposure
    r"secret\s*[:=]\s*\w+",  # Secret exposure
    r"ssn\s*[:=]\s*\d{3}-\d{2}-\d{4}",  # SSN format
    r"aadhaar\s*[:=]\s*\d{12}",  # Aadhaar number
    r"pan\s*[:=]\s*[A-Z]{5}\d{4}[A-Z]",  # PAN number
    r"credit\s*card\s*[:=]\s*\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}",  # Credit card
    r"bank\s*account\s*[:=]\s*\d{9,18}",  # Bank account number
    r"upi\s*[:=]\s*\w+@\w+",  # UPI ID
    r"ifsc\s*[:=]\s*[A-Z]{4}0[A-Z0-9]{6}",  # IFSC code
    r"micr\s*[:=]\s*\d{9}",  # MICR code
]

# Sensitive data patterns for redaction
SENSITIVE_PATTERNS = [
    (r"\b\d{12,16}\b", "[REDACTED_NUMBER]"),  # 12-16 digit numbers
    (r"\b[A-Z]{5}\d{4}[A-Z]\b", "[REDACTED_PAN]"),  # PAN format
    (r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", "[REDACTED_CARD]"),  # Credit card
    (r"\b\d{10,12}\b", "[REDACTED_ACCOUNT]"),  # Account numbers
    (r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", "[REDACTED_EMAIL]"),  # Email addresses
    (r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", "[REDACTED_IP]"),  # IP addresses
]

# Rate limiting storage
rate_limit_store: Dict[str, List[datetime]] = {}

# =============================================================================
# GUARDRAIL RESULT CLASS
# =============================================================================

if GOOGLE_ADK_AVAILABLE:
    # Use Google ADK GuardrailResult
    GuardrailResult = GuardrailResult
else:
    # Use simplified GuardrailResult
    @dataclass
    class GuardrailResult:
        """Simplified guardrail result class"""
        output: str
        blocked: bool = False

# =============================================================================
# TOOL GUARDRAILS
# =============================================================================

if GOOGLE_ADK_AVAILABLE:
    class ToolSecurityGuardrail(Guardrails):
        """
        Comprehensive security guardrail for tool usage (Google ADK version)
        """
        
        async def apply_pre_hook(self, query: str, tool_context: Any = None) -> GuardrailResult:
            """
            Pre-execution security checks
            """
            try:
                # 1. Input sanitization
                sanitized_query = self._sanitize_input(query)
                
                # 2. Check for blocked patterns
                blocked_reason = self._check_blocked_patterns(sanitized_query)
                if blocked_reason:
                    logger.warning(f"Blocked query due to {blocked_reason}: {query[:100]}...")
                    return GuardrailResult(
                        output="⚠️ Your request contains sensitive information that cannot be processed for security reasons.",
                        blocked=True
                    )
                
                # 3. Rate limiting check
                user_id = getattr(tool_context, 'user_id', 'default') if tool_context else 'default'
                if not self._check_rate_limit(user_id):
                    logger.warning(f"Rate limit exceeded for user: {user_id}")
                    return GuardrailResult(
                        output="⚠️ Rate limit exceeded. Please wait before making another request.",
                        blocked=True
                    )
                
                # 4. Log the request for security monitoring
                self._log_security_event("query_received", {
                    "user_id": user_id,
                    "query_length": len(query),
                    "timestamp": datetime.now().isoformat()
                })
                
                return GuardrailResult(output=sanitized_query)
                
            except Exception as e:
                logger.error(f"Error in pre-hook guardrail: {str(e)}")
                return GuardrailResult(
                    output="⚠️ An error occurred while processing your request.",
                    blocked=True
                )
        
        async def apply_post_hook(self, result: str, tool_context: Any = None) -> GuardrailResult:
            """
            Post-execution security checks and output sanitization
            """
            try:
                # 1. Output sanitization
                sanitized_result = self._sanitize_output(result)
                
                # 2. Check for sensitive data in output
                if self._contains_sensitive_data(sanitized_result):
                    logger.warning("Sensitive data detected in output, applying redaction")
                    sanitized_result = self._redact_sensitive_data(sanitized_result)
                
                # 3. Add security disclaimer if financial advice detected
                if self._contains_financial_advice(sanitized_result):
                    sanitized_result += "\n\n⚠️ **DISCLAIMER**: This information is for educational purposes only and should not be considered as financial advice. Please consult with a qualified financial advisor before making any investment decisions."
                
                # 4. Log the response for security monitoring
                user_id = getattr(tool_context, 'user_id', 'default') if tool_context else 'default'
                self._log_security_event("response_generated", {
                    "user_id": user_id,
                    "response_length": len(sanitized_result),
                    "timestamp": datetime.now().isoformat()
                })
                
                return GuardrailResult(output=sanitized_result)
                
            except Exception as e:
                logger.error(f"Error in post-hook guardrail: {str(e)}")
                return GuardrailResult(
                    output="⚠️ An error occurred while processing the response.",
                    blocked=True
                )
        
        def _sanitize_input(self, query: str) -> str:
            """Sanitize input query"""
            # Remove potential script injections
            query = re.sub(r'<script.*?</script>', '', query, flags=re.IGNORECASE | re.DOTALL)
            query = re.sub(r'javascript:', '', query, flags=re.IGNORECASE)
            query = re.sub(r'on\w+\s*=', '', query, flags=re.IGNORECASE)
            
            # Remove SQL injection patterns
            query = re.sub(r'(\b(union|select|insert|update|delete|drop|create|alter)\b)', '', query, flags=re.IGNORECASE)
            
            # Remove command injection patterns
            query = re.sub(r'[;&|`$()]', '', query)
            
            return query.strip()
        
        def _check_blocked_patterns(self, query: str) -> Optional[str]:
            """Check for blocked patterns in query"""
            for pattern in BLOCKED_PATTERNS:
                if re.search(pattern, query, re.IGNORECASE):
                    return f"blocked_pattern: {pattern}"
            return None
        
        def _check_rate_limit(self, user_id: str) -> bool:
            """Check rate limiting for user"""
            current_time = datetime.now()
            if user_id not in rate_limit_store:
                rate_limit_store[user_id] = []
            
            # Remove requests older than 1 minute
            rate_limit_store[user_id] = [
                req_time for req_time in rate_limit_store[user_id]
                if (current_time - req_time).seconds < 60
            ]
            
            # Check if user has exceeded rate limit (10 requests per minute)
            if len(rate_limit_store[user_id]) >= 10:
                return False
            
            # Add current request
            rate_limit_store[user_id].append(current_time)
            return True
        
        def _sanitize_output(self, result: str) -> str:
            """Sanitize output result"""
            # Remove HTML tags
            result = re.sub(r'<[^>]+>', '', result)
            
            # Remove potential script content
            result = re.sub(r'<script.*?</script>', '', result, flags=re.IGNORECASE | re.DOTALL)
            
            # Escape special characters
            result = result.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            
            return result
        
        def _contains_sensitive_data(self, text: str) -> bool:
            """Check if text contains sensitive data patterns"""
            for pattern, _ in SENSITIVE_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    return True
            return False
        
        def _redact_sensitive_data(self, text: str) -> str:
            """Redact sensitive data from text"""
            for pattern, replacement in SENSITIVE_PATTERNS:
                text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
            return text
        
        def _contains_financial_advice(self, text: str) -> bool:
            """Check if text contains financial advice indicators"""
            advice_indicators = [
                "invest in", "buy", "sell", "recommend", "should invest",
                "financial advice", "investment advice", "trading advice"
            ]
            text_lower = text.lower()
            return any(indicator in text_lower for indicator in advice_indicators)
        
        def _log_security_event(self, event_type: str, data: Dict[str, Any]):
            """Log security events for monitoring"""
            log_entry = {
                "event_type": event_type,
                "timestamp": datetime.now().isoformat(),
                "data": data
            }
            logger.info(f"SECURITY_EVENT: {json.dumps(log_entry)}")

else:
    class ToolSecurityGuardrail:
        """
        Comprehensive security guardrail for tool usage (Simplified version)
        """
        
        async def apply_pre_hook(self, query: str, user_id: str = "default") -> GuardrailResult:
            """
            Pre-execution security checks
            """
            try:
                # 1. Input sanitization
                sanitized_query = self._sanitize_input(query)
                
                # 2. Check for blocked patterns
                blocked_reason = self._check_blocked_patterns(sanitized_query)
                if blocked_reason:
                    logger.warning(f"Blocked query due to {blocked_reason}: {query[:100]}...")
                    return GuardrailResult(
                        output="⚠️ Your request contains sensitive information that cannot be processed for security reasons.",
                        blocked=True
                    )
                
                # 3. Rate limiting check
                if not self._check_rate_limit(user_id):
                    logger.warning(f"Rate limit exceeded for user: {user_id}")
                    return GuardrailResult(
                        output="⚠️ Rate limit exceeded. Please wait before making another request.",
                        blocked=True
                    )
                
                # 4. Log the request for security monitoring
                self._log_security_event("query_received", {
                    "user_id": user_id,
                    "query_length": len(query),
                    "timestamp": datetime.now().isoformat()
                })
                
                return GuardrailResult(output=sanitized_query)
                
            except Exception as e:
                logger.error(f"Error in pre-hook guardrail: {str(e)}")
                return GuardrailResult(
                    output="⚠️ An error occurred while processing your request.",
                    blocked=True
                )
        
        async def apply_post_hook(self, result: str, user_id: str = "default") -> GuardrailResult:
            """
            Post-execution security checks and output sanitization
            """
            try:
                # 1. Output sanitization
                sanitized_result = self._sanitize_output(result)
                
                # 2. Check for sensitive data in output
                if self._contains_sensitive_data(sanitized_result):
                    logger.warning("Sensitive data detected in output, applying redaction")
                    sanitized_result = self._redact_sensitive_data(sanitized_result)
                
                # 3. Add security disclaimer if financial advice detected
                if self._contains_financial_advice(sanitized_result):
                    sanitized_result += "\n\n⚠️ **DISCLAIMER**: This information is for educational purposes only and should not be considered as financial advice. Please consult with a qualified financial advisor before making any investment decisions."
                
                # 4. Log the response for security monitoring
                self._log_security_event("response_generated", {
                    "user_id": user_id,
                    "response_length": len(sanitized_result),
                    "timestamp": datetime.now().isoformat()
                })
                
                return GuardrailResult(output=sanitized_result)
                
            except Exception as e:
                logger.error(f"Error in post-hook guardrail: {str(e)}")
                return GuardrailResult(
                    output="⚠️ An error occurred while processing the response.",
                    blocked=True
                )
        
        def _sanitize_input(self, query: str) -> str:
            """Sanitize input query"""
            # Remove potential script injections
            query = re.sub(r'<script.*?</script>', '', query, flags=re.IGNORECASE | re.DOTALL)
            query = re.sub(r'javascript:', '', query, flags=re.IGNORECASE)
            query = re.sub(r'on\w+\s*=', '', query, flags=re.IGNORECASE)
            
            # Remove SQL injection patterns
            query = re.sub(r'(\b(union|select|insert|update|delete|drop|create|alter)\b)', '', query, flags=re.IGNORECASE)
            
            # Remove command injection patterns
            query = re.sub(r'[;&|`$()]', '', query)
            
            return query.strip()
        
        def _check_blocked_patterns(self, query: str) -> Optional[str]:
            """Check for blocked patterns in query"""
            for pattern in BLOCKED_PATTERNS:
                if re.search(pattern, query, re.IGNORECASE):
                    return f"blocked_pattern: {pattern}"
            return None
        
        def _check_rate_limit(self, user_id: str) -> bool:
            """Check rate limiting for user"""
            current_time = datetime.now()
            if user_id not in rate_limit_store:
                rate_limit_store[user_id] = []
            
            # Remove requests older than 1 minute
            rate_limit_store[user_id] = [
                req_time for req_time in rate_limit_store[user_id]
                if (current_time - req_time).seconds < 60
            ]
            
            # Check if user has exceeded rate limit (10 requests per minute)
            if len(rate_limit_store[user_id]) >= 10:
                return False
            
            # Add current request
            rate_limit_store[user_id].append(current_time)
            return True
        
        def _sanitize_output(self, result: str) -> str:
            """Sanitize output result"""
            # Remove HTML tags
            result = re.sub(r'<[^>]+>', '', result)
            
            # Remove potential script content
            result = re.sub(r'<script.*?</script>', '', result, flags=re.IGNORECASE | re.DOTALL)
            
            # Escape special characters
            result = result.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            
            return result
        
        def _contains_sensitive_data(self, text: str) -> bool:
            """Check if text contains sensitive data patterns"""
            for pattern, _ in SENSITIVE_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    return True
            return False
        
        def _redact_sensitive_data(self, text: str) -> str:
            """Redact sensitive data from text"""
            for pattern, replacement in SENSITIVE_PATTERNS:
                text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
            return text
        
        def _contains_financial_advice(self, text: str) -> bool:
            """Check if text contains financial advice indicators"""
            advice_indicators = [
                "invest in", "buy", "sell", "recommend", "should invest",
                "financial advice", "investment advice", "trading advice"
            ]
            text_lower = text.lower()
            return any(indicator in text_lower for indicator in advice_indicators)
        
        def _log_security_event(self, event_type: str, data: Dict[str, Any]):
            """Log security events for monitoring"""
            log_entry = {
                "event_type": event_type,
                "timestamp": datetime.now().isoformat(),
                "data": data
            }
            logger.info(f"SECURITY_EVENT: {json.dumps(log_entry)}")

# =============================================================================
# TOOL USAGE GUARDRAILS
# =============================================================================

def before_tool_guardrail(tool, args, tool_context):
    """
    Guardrail to restrict tool usage and ensure no unexpected arguments.
    Based on the reference implementation with enhanced security.
    """
    try:
        # 1. Check if tool is in allowed list
        if tool.name not in ALLOWED_FETCH_TOOLS:
            if hasattr(tool_context, 'state'):
                tool_context.state["blocked_tool"] = tool.name
            logger.warning(f"Blocked unauthorized tool access: {tool.name}")
            return {
                "status": "error",
                "error_message": f"Tool '{tool.name}' is not permitted for security reasons."
            }

        # 2. Validate tool arguments
        allowed_args = ALLOWED_FETCH_TOOLS[tool.name]["allowed_args"]
        
        # Special handling for google_search
        if tool.name == "google_search":
            if not args or "query" not in args:
                if hasattr(tool_context, 'state'):
                    tool_context.state["invalid_args_for"] = tool.name
                logger.warning(f"Google search missing query argument: {args}")
                return {
                    "status": "error",
                    "error_message": "Google search must include a 'query' argument."
                }
            # Validate query content
            query = args.get("query", "")
            if len(query) > 200:  # Limit search query length
                return {
                    "status": "error",
                    "error_message": "Search query too long (max 200 characters)."
                }
        elif args and args != allowed_args:
            if hasattr(tool_context, 'state'):
                tool_context.state["invalid_args_for"] = tool.name
            logger.warning(f"Invalid arguments for tool {tool.name}: {args}")
            return {
                "status": "error",
                "error_message": f"Tool '{tool.name}' must be called with specific arguments only."
            }

        # 3. Check rate limiting for specific tool
        user_id = getattr(tool_context, 'user_id', 'default') if tool_context else 'default'
        tool_rate_limit = ALLOWED_FETCH_TOOLS[tool.name]["rate_limit"]
        
        if not _check_tool_rate_limit(user_id, tool.name, tool_rate_limit):
            logger.warning(f"Tool rate limit exceeded for {tool.name} by user {user_id}")
            return {
                "status": "error",
                "error_message": f"Rate limit exceeded for tool '{tool.name}'. Please wait before trying again."
            }

        # 4. Log tool usage for security monitoring
        _log_tool_usage(user_id, tool.name, args)
        
        # Allowed: return None to proceed
        return None
        
    except Exception as e:
        logger.error(f"Error in before_tool_guardrail: {str(e)}")
        return {
            "status": "error",
            "error_message": "An error occurred during tool validation."
        }

def _check_tool_rate_limit(user_id: str, tool_name: str, rate_limit: int) -> bool:
    """Check rate limiting for specific tool"""
    current_time = datetime.now()
    key = f"{user_id}_{tool_name}"
    
    if key not in rate_limit_store:
        rate_limit_store[key] = []
    
    # Remove requests older than 1 minute
    rate_limit_store[key] = [
        req_time for req_time in rate_limit_store[key]
        if (current_time - req_time).seconds < 60
    ]
    
    # Check if user has exceeded rate limit
    if len(rate_limit_store[key]) >= rate_limit:
        return False
    
    # Add current request
    rate_limit_store[key].append(current_time)
    return True

def _log_tool_usage(user_id: str, tool_name: str, args: Dict[str, Any]):
    """Log tool usage for security monitoring"""
    log_entry = {
        "event_type": "tool_usage",
        "user_id": user_id,
        "tool_name": tool_name,
        "args": args,
        "timestamp": datetime.now().isoformat()
    }
    logger.info(f"TOOL_USAGE: {json.dumps(log_entry)}")

# =============================================================================
# MCP TOOLSET CONFIGURATION WITH GUARDRAILS
# =============================================================================

def create_secure_mcp_toolset():
    """
    Create MCP toolset with security guardrails
    """
    if GOOGLE_ADK_AVAILABLE:
        # Filter only MCP tools (exclude google_search)
        mcp_tools = [tool for tool, config in ALLOWED_FETCH_TOOLS.items() 
                     if config.get("category") == "financial_data"]
        
        mcp = MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=os.getenv("MCP_SERVER_URL"),
            ),
            tool_filter=mcp_tools,
        )
        return mcp
    else:
        logger.warning("MCP toolset not available - using mock implementation")
        return MockMCPToolset()

def create_secure_toolset():
    """
    Create complete toolset with both MCP and Google Search tools
    """
    tools = []
    
    # Add MCP toolset
    try:
        mcp_toolset = create_secure_mcp_toolset()
        tools.append(mcp_toolset)
    except Exception as e:
        logger.warning(f"Could not create MCP toolset: {e}")
    
    # Add Google Search tool
    if GOOGLE_ADK_AVAILABLE:
        tools.append(google_search)
    else:
        logger.warning("Google Search tool not available - using mock implementation")
        tools.append(MockGoogleSearchTool())
    
    return tools

# =============================================================================
# MOCK TOOLS FOR TESTING
# =============================================================================

class MockMCPToolset:
    """Mock MCP toolset for testing when google.adk is not available"""
    
    def __init__(self):
        self.name = "mock_mcp_toolset"
        self.tools = ["fetch_net_worth", "fetch_credit_report", "fetch_epf_details", 
                     "fetch_mf_transactions", "fetch_bank_transactions", "fetch_stock_transactions"]
    
    def __call__(self, *args, **kwargs):
        return "Mock MCP response: Financial data retrieved securely"

class MockGoogleSearchTool:
    """Mock Google Search tool for testing when google.adk is not available"""
    
    def __init__(self):
        self.name = "google_search"
    
    def __call__(self, query: str = "", **kwargs):
        return f"Mock Google Search response for: {query}"

# =============================================================================
# SECURE AGENT CONFIGURATION
# =============================================================================

def create_secure_agent(name: str = "secure_finance_agent"):
    """
    Create a secure agent with comprehensive guardrails
    """
    if GOOGLE_ADK_AVAILABLE:
        tools = create_secure_toolset()
        
        agent = LlmAgent(
            name=name,
            model="gemini-2.0-flash",
            description="Secure finance agent with comprehensive tool guardrails",
            instruction="""
            You are a secure financial data agent with strict security protocols.
            
            SECURITY RULES:
            1. Only use allowed MCP tools for data fetching
            2. Only use Google Search for market research and real-time information
            3. Never expose sensitive financial information
            4. Always validate user permissions before data access
            5. Provide only factual data analysis, not financial advice
            6. Log all activities for security monitoring
            
            Available tools are pre-filtered for security. Use them responsibly.
            
            TOOL CATEGORIES:
            - Financial Data Tools: fetch_net_worth, fetch_credit_report, fetch_epf_details, 
              fetch_mf_transactions, fetch_bank_transactions, fetch_stock_transactions
            - Market Research Tools: google_search (for real-time market data)
            """,
            tools=tools,
            before_tool_callback=before_tool_guardrail,
        )
        
        return agent
    else:
        logger.warning("Google ADK LlmAgent not available - returning mock agent")
        return MockSecureAgent()

class MockSecureAgent:
    """Mock secure agent for testing when google.adk is not available"""
    
    def __init__(self):
        self.name = "mock_secure_finance_agent"
        self.description = "Mock secure finance agent with comprehensive tool guardrails"
    
    async def run(self, prompt: str, user_id: str = "default"):
        """Mock agent run method"""
        return f"Mock secure response for: {prompt}"

# =============================================================================
# LEGACY GUARDRAILS (for backward compatibility)
# =============================================================================

if GOOGLE_ADK_AVAILABLE:
    class PiiRedactionGuardrail(Guardrails):
        """
        Legacy PII redaction guardrail for backward compatibility
        """
        async def apply_pre_hook(self, query: str) -> GuardrailResult:
            # Redact mock credit card or Aadhaar numbers (12–16 digits)
            redacted = re.sub(r"\b\d{12,16}\b", "[REDACTED]", query)
            return GuardrailResult(output=redacted)

    class OutputSanitizer(Guardrails):
        """
        Legacy output sanitizer for backward compatibility
        """
        async def apply_post_hook(self, result: str) -> GuardrailResult:
            if "recommend investing" in result.lower():
                result = "⚠️ Financial investment advice is not permitted by this agent."
            return GuardrailResult(output=result)
else:
    class PiiRedactionGuardrail:
        """
        Legacy PII redaction guardrail for backward compatibility
        """
        async def apply_pre_hook(self, query: str) -> GuardrailResult:
            # Redact mock credit card or Aadhaar numbers (12–16 digits)
            redacted = re.sub(r"\b\d{12,16}\b", "[REDACTED]", query)
            return GuardrailResult(output=redacted)

    class OutputSanitizer:
        """
        Legacy output sanitizer for backward compatibility
        """
        async def apply_post_hook(self, result: str) -> GuardrailResult:
            if "recommend investing" in result.lower():
                result = "⚠️ Financial investment advice is not permitted by this agent."
            return GuardrailResult(output=result)
