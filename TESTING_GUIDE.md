# 🧪 NaviFi API Security Guardrails Testing Guide

This guide will help you start the server and test the API with comprehensive security guardrails.

## 🚀 Quick Start

### Option 1: Simplified API (Recommended for Testing)

The simplified version works without `google.adk` dependency and includes all security guardrails:

```bash
# Install dependencies
pip install -r requirement.txt

# Start the simplified API
python start_simple_api.py
```

### Option 2: Full API (Requires google.adk)

If you have access to `google.adk`:

```bash
# Install dependencies
pip install -r requirement.txt

# Start the full API
python start_api.py
```

## 🧪 Testing Methods

### 1. Python Test Scripts

#### Comprehensive Test Suite
```bash
# Run all tests
python test_api_guardrails.py
```

#### Interactive Quick Test
```bash
# Interactive testing
python quick_test.py
```

### 2. Curl Test Script

```bash
# Make script executable
chmod +x curl_test_script.sh

# Run all curl tests
./curl_test_script.sh

# Check if server is running
./curl_test_script.sh --check

# Get help
./curl_test_script.sh --help
```

### 3. Manual Curl Commands

#### Basic Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Root endpoint
curl http://localhost:8000/

# Security status
curl http://localhost:8000/security/status

# Security tools
curl http://localhost:8000/security/tools
```

#### Chat Endpoints
```bash
# Valid chat request
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is my net worth?", "user_id": "test_user"}'

# Streaming chat
curl -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is my net worth?", "user_id": "test_user"}'
```

#### Security Tests
```bash
# Test malicious input (should be blocked)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "<script>alert(\"xss\")</script>What is my net worth?", "user_id": "test_user"}'

# Test empty prompt (should be blocked)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "", "user_id": "test_user"}'

# Test long prompt (should be blocked)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "'$(printf 'a%.0s' {1..1001})'", "user_id": "test_user"}'
```

## 🔒 Security Features to Test

### 1. Input Validation
- ✅ **Empty prompts**: Should return 400 error
- ✅ **Long prompts**: Should return 400 error (>1000 characters)
- ✅ **Malicious patterns**: Should return 403 error

### 2. Pattern Blocking
Test these patterns (should all be blocked):
- `<script>alert('xss')</script>`
- `password=123456`
- `api_key=sk-1234567890abcdef`
- `token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9`
- `secret=my_secret_key`
- `ssn=123-45-6789`
- `aadhaar=123456789012`
- `pan=ABCDE1234F`
- `credit card=1234-5678-9012-3456`
- `bank account=1234567890`
- `union select * from users`
- `rm -rf /`

### 3. Rate Limiting
- ✅ **User-based limits**: 10 requests per minute per user
- ✅ **Tool-specific limits**: Different limits for different tools
- ✅ **Sliding window**: Accurate rate limiting

### 4. Output Sanitization
- ✅ **PII redaction**: Sensitive data should be redacted
- ✅ **HTML sanitization**: HTML tags should be removed
- ✅ **Financial advice disclaimers**: Added when detected

### 5. Tool Access Control
- ✅ **Whitelist access**: Only 7 approved tools allowed
- ✅ **Argument validation**: Strict validation for each tool
- ✅ **Usage logging**: All tool usage tracked

## 📊 Expected Test Results

### Successful Responses (200)
```json
{
  "response": "Based on your financial data, your current net worth is approximately $150,000...",
  "status": "success",
  "security_info": {
    "user_id": "test_user",
    "timestamp": "2024-01-15T10:30:00",
    "guardrails_applied": true,
    "input_sanitized": true,
    "output_sanitized": true
  }
}
```

### Blocked Responses (403)
```json
{
  "detail": "⚠️ Your request contains sensitive information that cannot be processed for security reasons."
}
```

### Bad Request Responses (400)
```json
{
  "detail": "Prompt cannot be empty"
}
```

## 🛡️ Available Tools (Secured)

### MCP Tools (Financial Data)
- `fetch_net_worth` - Rate limit: 10/min
- `fetch_credit_report` - Rate limit: 5/min
- `fetch_epf_details` - Rate limit: 10/min
- `fetch_mf_transactions` - Rate limit: 15/min
- `fetch_bank_transactions` - Rate limit: 20/min
- `fetch_stock_transactions` - Rate limit: 15/min

### Google Search Tools (Market Research)
- `google_search` - Rate limit: 30/min

## 🔍 Monitoring Endpoints

### Security Status
```bash
curl http://localhost:8000/security/status
```
Returns:
- Allowed tools count
- Rate limit store size
- Security features list

### Security Tools
```bash
curl http://localhost:8000/security/tools
```
Returns:
- Detailed tool configurations
- Security policies
- Rate limits per tool

## 🚨 Troubleshooting

### Common Issues

1. **ModuleNotFoundError: No module named 'google.adk.runtime'**
   - Use the simplified API: `python start_simple_api.py`
   - Or install google-adk from Google's internal repository

2. **Server not accessible**
   - Check if server is running: `./curl_test_script.sh --check`
   - Verify port 8000 is not in use
   - Check firewall settings

3. **Tests failing**
   - Ensure server is running before running tests
   - Check logs for detailed error messages
   - Verify all dependencies are installed

### Debug Mode

Enable debug logging:
```python
import logging
logging.getLogger('guardrails').setLevel(logging.DEBUG)
```

## 📈 Performance Testing

### Load Testing
```bash
# Test rate limiting with multiple requests
for i in {1..20}; do
  curl -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"prompt": "What is my net worth?", "user_id": "load_test_user"}'
  sleep 0.1
done
```

### Security Performance
- Input sanitization: <1ms per request
- Pattern matching: <1ms per request
- Rate limiting: <1ms per request
- Output sanitization: <1ms per request

## ✅ Success Criteria

All tests should pass:
- ✅ Health endpoint accessible
- ✅ Security endpoints working
- ✅ Valid chat requests successful
- ✅ Malicious inputs blocked
- ✅ Rate limiting enforced
- ✅ PII redaction working
- ✅ Tool access controlled

## 📝 Notes

- The simplified version uses mock responses for testing
- All security guardrails are fully functional
- Real Google ADK integration requires internal access
- Security features work independently of the AI model

## 🆘 Support

If you encounter issues:
1. Check the server logs
2. Verify all dependencies are installed
3. Ensure the server is running on port 8000
4. Test with the simplified API first 