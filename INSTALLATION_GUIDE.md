# 🚀 NaviFi API Installation & Setup Guide

This guide will help you properly install all dependencies and start the NaviFi API with security guardrails.

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Access to Google ADK (if using full functionality)

## 🔧 Installation Steps

### Step 1: Clone or Download the Project

```bash
# If you have the project files, navigate to the project directory
cd /path/to/NaviFi
```

### Step 2: Install Dependencies

```bash
# Install all required packages
pip install -r requirement.txt
```

**Expected Output:**
```
Collecting fastapi>=0.104.1
  Downloading fastapi-0.104.1-py3-none-any.whl (62 kB)
Collecting uvicorn[standard]>=0.24.0
  Downloading uvicorn-0.24.0-py3-none-any.whl (57 kB)
Collecting google-adk>=0.1.0
  Downloading google_adk-0.1.0-py3-none-any.whl (2.1 MB)
...
Successfully installed fastapi-0.104.1 uvicorn-0.24.0 google-adk-0.1.0 ...
```

### Step 3: Verify Installation

```bash
# Test if guardrails can be imported
python -c "from guardrails import ToolSecurityGuardrail; print('✅ Guardrails imported successfully')"
```

**Expected Output:**
```
✅ Google ADK components imported successfully
✅ Guardrails imported successfully
```

## 🚀 Starting the Server

### Option 1: Full API (Recommended if google-adk is available)

```bash
# Start the full API with Google ADK
python start_api.py
```

**Expected Output:**
```
🚀 Starting NaviFi Financial Agent API...
🔒 Security Features Enabled:
   - Tool access control (MCP + Google Search)
   - Input validation and sanitization
   - Rate limiting (per-user and per-tool)
   - PII protection and redaction
   - Security logging and monitoring
   - Pattern blocking (XSS, SQL injection, etc.)
   - Financial advice disclaimers

📡 Server will be available at: http://localhost:8000
📚 API documentation at: http://localhost:8000/docs
🔧 Interactive API explorer at: http://localhost:8000/redoc

🔍 Security Monitoring:
   - Security status: http://localhost:8000/security/status
   - Allowed tools: http://localhost:8000/security/tools

🛡️ Available Tools (Secured):
   Financial Data:
     - fetch_net_worth
     - fetch_credit_report
     - fetch_epf_details
     - fetch_mf_transactions
     - fetch_bank_transactions
     - fetch_stock_transactions
   Market Research:
     - google_search

INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

### Option 2: Simplified API (If google-adk is not available)

```bash
# Start the simplified API (works without google-adk)
python start_simple_api.py
```

**Expected Output:**
```
⚠️ Google ADK not available: No module named 'google.adk.runtime'
📝 Using simplified guardrails implementation
🚀 Starting NaviFi Simplified API with Security Guardrails...
🔒 Security Features Enabled:
   - Tool access control (MCP + Google Search)
   - Input validation and sanitization
   - Rate limiting (per-user and per-tool)
   - PII protection and redaction
   - Security logging and monitoring
   - Pattern blocking (XSS, SQL injection, etc.)
   - Financial advice disclaimers

📡 Server will be available at: http://localhost:8000
📚 API documentation at: http://localhost:8000/docs
🔧 Interactive API explorer at: http://localhost:8000/redoc

🔍 Security Monitoring:
   - Security status: http://localhost:8000/security/status
   - Allowed tools: http://localhost:8000/security/tools

🛡️ Available Tools (Secured):
   Financial Data:
     - fetch_net_worth
     - fetch_credit_report
     - fetch_epf_details
     - fetch_mf_transactions
     - fetch_bank_transactions
     - fetch_stock_transactions
   Market Research:
     - google_search

📝 Note: This is a simplified version for testing security guardrails
   It uses mock responses instead of the actual Google ADK agent

Press CTRL+C to stop the server
------------------------------------------------------------
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## 🧪 Testing the Installation

### Quick Health Check

```bash
# Test if server is running
curl http://localhost:8000/health
```

**Expected Output:**
```json
{
  "status": "healthy",
  "service": "NaviFi Financial Agent API",
  "version": "2.0.0",
  "security_enabled": true,
  "timestamp": "2024-01-15T10:30:00"
}
```

### Security Status Check

```bash
# Check security features
curl http://localhost:8000/security/status
```

**Expected Output:**
```json
{
  "allowed_tools": ["fetch_net_worth", "fetch_credit_report", "fetch_epf_details", "fetch_mf_transactions", "fetch_bank_transactions", "fetch_stock_transactions", "google_search"],
  "rate_limit_store_size": 0,
  "security_features": ["Input sanitization", "Pattern blocking", "Rate limiting", "Tool restriction", "Output sanitization", "PII redaction", "Security logging"],
  "timestamp": "2024-01-15T10:30:00"
}
```

### Test Chat Endpoint

```bash
# Test a valid chat request
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is my net worth?", "user_id": "test_user"}'
```

**Expected Output:**
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

## 🚨 Troubleshooting

### Issue 1: ModuleNotFoundError: No module named 'google.adk'

**Solution:**
```bash
# Use the simplified API instead
python start_simple_api.py
```

**Or install google-adk from the correct source:**
```bash
# If you have access to Google's internal repository
pip install google-adk --index-url https://your-internal-repo.com/pypi/
```

### Issue 2: Port 8000 already in use

**Solution:**
```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process or use a different port
python start_api.py --port 8001
```

### Issue 3: Permission denied when running curl_test_script.sh

**Solution:**
```bash
# Make the script executable
chmod +x curl_test_script.sh

# Run the tests
./curl_test_script.sh
```

### Issue 4: Import errors for other packages

**Solution:**
```bash
# Upgrade pip first
pip install --upgrade pip

# Install dependencies with verbose output
pip install -r requirement.txt -v

# Check Python version
python --version
```

## 📊 Verification Checklist

- [ ] All dependencies installed successfully
- [ ] Guardrails imported without errors
- [ ] Server starts without errors
- [ ] Health endpoint responds correctly
- [ ] Security status endpoint works
- [ ] Chat endpoint accepts requests
- [ ] Security guardrails block malicious input
- [ ] Rate limiting works correctly

## 🔒 Security Features Verification

### Test Malicious Input Blocking

```bash
# This should be blocked (403 error)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "<script>alert(\"xss\")</script>What is my net worth?", "user_id": "test_user"}'
```

**Expected Output:**
```json
{
  "detail": "⚠️ Your request contains sensitive information that cannot be processed for security reasons."
}
```

### Test Rate Limiting

```bash
# Send multiple requests quickly
for i in {1..15}; do
  curl -X POST http://localhost:8000/chat \
    -H "Content-Type: application/json" \
    -d '{"prompt": "What is my net worth?", "user_id": "rate_test_user"}'
  sleep 0.1
done
```

**Expected Output:** Some requests should be blocked with rate limit messages.

## 📝 Next Steps

1. **Run the comprehensive test suite:**
   ```bash
   python test_api_guardrails.py
   ```

2. **Use the curl test script:**
   ```bash
   ./curl_test_script.sh
   ```

3. **Explore the API documentation:**
   - Open http://localhost:8000/docs in your browser
   - Interactive API testing interface

4. **Monitor security events:**
   - Check server logs for security events
   - Use `/security/status` endpoint for monitoring

## 🆘 Getting Help

If you encounter issues:

1. Check the server logs for detailed error messages
2. Verify all dependencies are installed correctly
3. Ensure you're using Python 3.8 or higher
4. Try the simplified API if google-adk is not available
5. Check the troubleshooting section above

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Google ADK Documentation](https://developers.google.com/ai/agents)
- [Security Best Practices](https://owasp.org/www-project-api-security/) 