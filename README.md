# 🚀 NaviFi Financial Agent API

A secure FastAPI-based financial agent with comprehensive security guardrails.

## 📦 Quick Installation

### Option 1: Automatic Setup (Recommended)
```bash
python setup.py
```

### Option 2: Manual Installation
```bash
# Install essential packages only
pip install fastapi uvicorn pydantic requests

# Or install from requirements file
pip install -r requirements.txt
```

## 🚀 Quick Start

### Start the API Server
```bash
python start_simple_api.py
```

### Test the API
```bash
# Basic test
python quick_test.py

# Full test suite (requires aiohttp)
pip install aiohttp
python test_api.py
```

## 🔒 Security Features

- ✅ Input validation and sanitization
- ✅ Pattern blocking (XSS, SQL injection, sensitive data)
- ✅ Rate limiting (per-user and per-tool)
- ✅ Tool access control (whitelist)
- ✅ Output sanitization and PII redaction
- ✅ Security logging and monitoring
- ✅ Financial advice disclaimers

## 📡 API Endpoints

- `GET /health` - Health check
- `GET /` - API information
- `POST /chat` - Complete chat response
- `POST /chat/stream` - Streaming chat response
- `GET /security/status` - Security monitoring
- `GET /security/tools` - Allowed tools list

## 🧪 Testing

### Basic Test
```bash
curl http://localhost:8000/health
```

### Chat Test
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What is my net worth?", "user_id": "test_user"}'
```

### Security Test
```bash
# This should be blocked
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "<script>alert(\"xss\")</script>What is my net worth?", "user_id": "test_user"}'
```

## 📚 Documentation

- Interactive API docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## 🔧 Troubleshooting

### Missing Packages
If you get import errors:
```bash
# Install missing packages
pip install fastapi uvicorn pydantic requests

# For testing
pip install aiohttp pytest pytest-asyncio
```

### Port Already in Use
```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process or use a different port
python start_simple_api.py --port 8001
```

### Google ADK Not Available
The simplified version works without Google ADK. If you have access to Google ADK:
```bash
# Install Google ADK (if available)
pip install google-adk

# Use the full API
python start_api.py
```

## 📁 Project Structure

```
NaviFi/
├── api_simple.py          # Simplified API (no Google ADK required)
├── start_simple_api.py    # Startup script for simplified API
├── guardrails.py          # Security guardrails implementation
├── requirements.txt       # Essential packages
├── setup.py              # Automatic setup script
├── test_api.py           # Test suite
├── quick_test.py         # Quick interactive test
├── curl_test_script.sh   # Comprehensive curl tests
└── README.md             # This file
```

## 🆘 Support

If you encounter issues:
1. Check the server logs for error messages
2. Ensure all dependencies are installed
3. Verify the server is running on port 8000
4. Try the simplified API first

## 📝 Notes

- The simplified version uses mock responses for testing
- All security guardrails are fully functional
- Real Google ADK integration requires internal access
- Security features work independently of the AI model 