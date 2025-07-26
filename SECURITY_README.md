# 🔒 NaviFi Security Guardrails

Comprehensive security guardrails for the NaviFi Financial Agent, based on the reference implementation with enhanced security features.

## 🛡️ Security Features

### 1. **Tool Access Control**
- **Whitelist-based tool access**: Only pre-approved tools can be used
- **Argument validation**: Strict validation of tool arguments
- **Rate limiting**: Per-tool and per-user rate limits
- **Usage logging**: All tool usage is logged for security monitoring

### 2. **Input Validation & Sanitization**
- **Pattern blocking**: Blocks malicious patterns (XSS, SQL injection, etc.)
- **Input sanitization**: Removes potentially dangerous content
- **Length limits**: Prevents overly long queries
- **Character filtering**: Removes dangerous characters

### 3. **Output Sanitization**
- **PII redaction**: Automatically redacts sensitive personal information
- **HTML sanitization**: Removes HTML tags and scripts
- **Financial advice disclaimers**: Adds disclaimers when financial advice is detected
- **Content filtering**: Filters inappropriate or dangerous content

### 4. **Rate Limiting**
- **User-based limits**: 10 requests per minute per user
- **Tool-specific limits**: Different limits for different tools
- **Sliding window**: Uses sliding window for accurate rate limiting

### 5. **Security Monitoring**
- **Event logging**: Logs all security events
- **Audit trails**: Maintains audit trails for compliance
- **Real-time monitoring**: Real-time security event monitoring
- **Alert system**: Alerts for suspicious activities

## 📁 File Structure

```
NaviFi/
├── guardrails.py              # Main security guardrails implementation
├── api.py                     # Main API with integrated security guardrails
├── start_api.py               # Startup script with security information
├── test_security_guardrails.py # Comprehensive security tests
├── SECURITY_README.md         # This file
└── ...
```

## 🚀 Quick Start

### 1. Basic Usage

```python
from guardrails import create_secure_agent, ToolSecurityGuardrail

# Create a secure agent
secure_agent = create_secure_agent("my_secure_agent")

# Use security guardrails
guardrail = ToolSecurityGuardrail()
result = await guardrail.apply_pre_hook("What is my net worth?")
```

### 2. API Usage

```python
# Option 1: Use the main API (now with integrated security)
from api import app
import uvicorn

# Start the API with security guardrails
uvicorn.run(app, host="0.0.0.0", port=8000)

# Option 2: Use the startup script
# python start_api.py
```

### 3. Testing

```bash
# Run security tests
python test_security_guardrails.py

# Or with pytest
pytest test_security_guardrails.py -v
```

## 🔧 Configuration

### Allowed Tools Configuration

```python
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
```

### Blocked Patterns

```python
BLOCKED_PATTERNS = [
    r"password\s*[:=]\s*\w+",  # Password exposure
    r"api[_-]?key\s*[:=]\s*\w+",  # API key exposure
    r"token\s*[:=]\s*\w+",  # Token exposure
    r"secret\s*[:=]\s*\w+",  # Secret exposure
    r"ssn\s*[:=]\s*\d{3}-\d{2}-\d{4}",  # SSN format
    r"aadhaar\s*[:=]\s*\d{12}",  # Aadhaar number
    r"pan\s*[:=]\s*[A-Z]{5}\d{4}[A-Z]",  # PAN number
    # ... more patterns
]
```

### Sensitive Data Patterns

```python
SENSITIVE_PATTERNS = [
    (r"\b\d{12,16}\b", "[REDACTED_NUMBER]"),  # 12-16 digit numbers
    (r"\b[A-Z]{5}\d{4}[A-Z]\b", "[REDACTED_PAN]"),  # PAN format
    (r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", "[REDACTED_CARD]"),  # Credit card
    # ... more patterns
]
```

## 🛡️ Security Guardrails in Detail

### 1. ToolSecurityGuardrail

The main security guardrail class that provides comprehensive protection:

```python
class ToolSecurityGuardrail(Guardrails):
    async def apply_pre_hook(self, query: str, tool_context: Any = None) -> GuardrailResult:
        # Pre-execution security checks
        # - Input sanitization
        # - Pattern blocking
        # - Rate limiting
        # - Security logging
    
    async def apply_post_hook(self, result: str, tool_context: Any = None) -> GuardrailResult:
        # Post-execution security checks
        # - Output sanitization
        # - PII redaction
        # - Financial advice detection
        # - Security logging
```

### 2. before_tool_guardrail

Function-based guardrail for tool usage:

```python
def before_tool_guardrail(tool, args, tool_context):
    # Tool access validation
    # - Check if tool is allowed
    # - Validate arguments
    # - Check rate limits
    # - Log usage
```

### 3. SecurityMiddleware

API-level security middleware:

```python
class SecurityMiddleware:
    async def validate_request(self, user_id: str, query: str) -> dict:
        # Request validation
        # - Basic validation
        # - Suspicious pattern detection
        # - Request logging
```

## 🔍 API Endpoints

### API Endpoints (All with Security Guardrails)

- `POST /chat/stream` - Streaming chat with security guardrails
- `POST /chat` - Chat completion with security guardrails
- `GET /security/status` - Security monitoring status
- `GET /security/tools` - Allowed tools information
- `GET /health` - Health check with security info
- `GET /` - Root endpoint with security info

### Example Usage

```bash
# Streaming chat with security guardrails
curl -X POST "http://localhost:8000/chat/stream" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "What is my net worth?", "user_id": "user123"}'

# Chat completion with security guardrails
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "What is my net worth?", "user_id": "user123"}'

# Check security status
curl "http://localhost:8000/security/status"

# Get allowed tools info
curl "http://localhost:8000/security/tools"

# Health check with security info
curl "http://localhost:8000/health"
```

## 🧪 Testing

### Running Tests

```bash
# Run all security tests
python test_security_guardrails.py

# Run specific test categories
pytest test_security_guardrails.py::TestToolSecurityGuardrail -v
pytest test_security_guardrails.py::TestToolUsageGuardrails -v
pytest test_security_guardrails.py::TestSecurityMiddleware -v
```

### Test Categories

1. **ToolSecurityGuardrail Tests**
   - Valid query processing
   - Malicious query blocking
   - Sensitive data redaction
   - Financial advice detection
   - Input sanitization
   - Rate limiting

2. **Tool Usage Guardrails Tests**
   - Allowed tool access
   - Blocked tool access
   - Invalid argument rejection

3. **Security Middleware Tests**
   - Request validation
   - Suspicious pattern blocking
   - Error handling

4. **Integration Tests**
   - End-to-end security flow
   - Malicious flow blocking

5. **Performance Tests**
   - Guardrail performance
   - Pattern matching performance

## 🔒 Security Best Practices

### 1. Environment Variables

```bash
# Set required environment variables
export MCP_SERVER_URL="https://your-mcp-server.com"
export SECURITY_LOG_LEVEL="INFO"
export RATE_LIMIT_ENABLED="true"
```

### 2. Logging Configuration

```python
import logging

# Configure security logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('security.log'),
        logging.StreamHandler()
    ]
)
```

### 3. Monitoring

```python
# Monitor security events
from guardrails import ToolSecurityGuardrail

guardrail = ToolSecurityGuardrail()

# Check security status
status = await guardrail.get_security_status()
print(f"Security events: {status['total_events']}")
print(f"Blocked requests: {status['blocked_requests']}")
```

## 🚨 Security Alerts

The system automatically detects and logs security events:

- **Unauthorized tool access attempts**
- **Rate limit violations**
- **Suspicious pattern detection**
- **PII exposure attempts**
- **Malicious input patterns**

### Alert Examples

```
WARNING: Blocked unauthorized tool access: unauthorized_tool
WARNING: Rate limit exceeded for user: user123
WARNING: Blocked suspicious request from user123: <script
WARNING: Sensitive data detected in output, applying redaction
```

## 📊 Security Metrics

Monitor security metrics through the API:

```bash
# Get security status
curl "http://localhost:8000/security/status"

# Response example:
{
  "total_requests": 150,
  "blocked_requests": 5,
  "allowed_tools": ["fetch_net_worth", "fetch_credit_report", ...],
  "security_features": ["Input sanitization", "Pattern blocking", ...],
  "timestamp": "2024-01-15T10:30:00"
}
```

## 🔧 Customization

### Adding New Tools

```python
# Add new tool to allowed list
ALLOWED_FETCH_TOOLS["new_tool"] = {
    "description": "Description of new tool",
    "allowed_args": {},
    "rate_limit": 10,
    "requires_auth": True
}
```

### Adding New Blocked Patterns

```python
# Add new blocked pattern
BLOCKED_PATTERNS.append(r"new_pattern\s*[:=]\s*\w+")
```

### Custom Rate Limits

```python
# Modify rate limits
ALLOWED_FETCH_TOOLS["fetch_net_worth"]["rate_limit"] = 20
```

## 🆘 Troubleshooting

### Common Issues

1. **Tool Access Denied**
   - Check if tool is in `ALLOWED_FETCH_TOOLS`
   - Verify tool arguments match allowed schema

2. **Rate Limit Exceeded**
   - Wait for rate limit window to reset
   - Check current usage in security status

3. **Input Blocked**
   - Check for blocked patterns in input
   - Sanitize input before sending

4. **Performance Issues**
   - Monitor guardrail performance
   - Optimize pattern matching if needed

### Debug Mode

```python
# Enable debug logging
import logging
logging.getLogger('guardrails').setLevel(logging.DEBUG)
```

## 📚 References

- [Google ADK Documentation](https://developers.google.com/adk)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [OWASP Security Guidelines](https://owasp.org/www-project-top-ten/)
- [Financial Data Security Standards](https://www.pcisecuritystandards.org/)

## 🤝 Contributing

When contributing to security features:

1. **Follow security best practices**
2. **Add comprehensive tests**
3. **Update documentation**
4. **Review security implications**
5. **Test with malicious inputs**

## 📄 License

This security implementation is part of the NaviFi project and follows the same license terms.

---

**⚠️ Security Notice**: This implementation provides comprehensive security guardrails but should be regularly reviewed and updated to address new security threats. Always follow security best practices and conduct regular security audits. 