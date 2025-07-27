# 🚀 NaviFi Hybrid AI Setup Guide

Complete setup instructions for the privacy-first hybrid AI orchestration system.

## 📋 Prerequisites

- **Python 3.8+** 
- **Google ADK access** (Google AI Studio or Vertex AI)
- **MCP server** for financial data (running separately)
- **Git** (for cloning and version control)

## 🔧 Step 1: Environment Setup

### 1.1 Clone and Navigate
```bash
cd /Users/gorakhchavan/Desktop/NaviFi
```

### 1.2 Create Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
# .venv\Scripts\activate
```

### 1.3 Verify Python Version
```bash
python --version  # Should be 3.8+
```

## 📦 Step 2: Install Dependencies

```bash
# Install all required dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep -E "(google-adk|fastapi|mcp)"
```

### Optional Enhanced Features

For full multimodal capabilities, uncomment and install these in `requirements.txt`:

```bash
# For audio processing
pip install pydub speechrecognition

# For PDF processing  
pip install PyMuPDF pdfplumber

# For data analysis
pip install numpy pandas
```

## 🔑 Step 3: Environment Variables

Create a `.env` file in your project root:

```bash
# Create environment file
touch .env
```

Add the following configuration to `.env`:

```bash
# Google AI Configuration (choose one method)

# Method 1: Google AI Studio (Recommended for development)
GOOGLE_API_KEY=your_google_ai_studio_api_key_here

# Method 2: Vertex AI (For production)
# GOOGLE_CLOUD_PROJECT=your-gcp-project-id
# GOOGLE_CLOUD_LOCATION=us-central1

# MCP Server Configuration (Required)
MCP_SERVER_URL=http://localhost:3000

# Optional: Authentication URL for better UX
MCP_LOGIN_URL=http://localhost:3000/login

# Optional: Custom configuration
LOG_LEVEL=INFO
MAX_FILE_SIZE_MB=10
```

### 3.1 Get Google AI Studio API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file

### 3.2 Set Up MCP Server

Make sure your MCP server is running with financial data access:

```bash
# Test MCP server connectivity
curl http://localhost:3000/health
```

## 🚀 Step 4: Run the System

### 4.1 Test Original API (Optional)
```bash
# Start the original API on port 8000
python start_api.py
```

### 4.2 Start Hybrid API
```bash
# Start the new hybrid API on port 8001
python start_hybrid_api.py
```

You should see:
```
🚀 NaviFi Hybrid AI Financial Agent
==================================================
🏗️  Architecture: Hybrid AI Orchestration Strategy
🔒 Privacy: Three-tier privacy system
🎙️  Features: Voice, Document, Real-time processing

🌐 Starting Hybrid API Server...
📡 Server will be available at: http://localhost:8001
📚 API documentation at: http://localhost:8001/docs
```

## 🧪 Step 5: Test the System

### 5.1 Basic Health Check
```bash
curl http://localhost:8001/hybrid/health
```

### 5.2 Privacy Tiers Information
```bash
curl http://localhost:8001/hybrid/privacy/tiers
```

### 5.3 Test Chat with Different Privacy Levels

**Cloud Hybrid Mode (Default):**
```bash
curl -X POST "http://localhost:8001/hybrid/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "What is my net worth?",
    "user_id": "test_user",
    "privacy_tier": "cloud_hybrid"
  }'
```

**Private-First Mode:**
```bash
curl -X POST "http://localhost:8001/hybrid/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Best SIP plans for 2025",
    "user_id": "test_user", 
    "privacy_tier": "private_first"
  }'
```

**Offline Mode:**
```bash
curl -X POST "http://localhost:8001/hybrid/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "How to budget for marriage?",
    "user_id": "test_user",
    "privacy_tier": "offline_mode"
  }'
```

### 5.4 Test PII Protection
```bash
curl -X POST "http://localhost:8001/hybrid/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "My credit card 4532-1234-5678-9012 spending analysis",
    "user_id": "test_user",
    "privacy_level": "standard"
  }'
```

### 5.5 Test Streaming Response
```bash
curl -X POST "http://localhost:8001/hybrid/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Analyze my portfolio performance",
    "user_id": "test_user"
  }'
```

## 🔍 Step 6: Interactive Testing

### 6.1 Open API Documentation
Visit: http://localhost:8001/docs

### 6.2 Test Different Endpoints

1. **Text Chat**: `/hybrid/chat`
2. **Streaming Chat**: `/hybrid/chat/stream`  
3. **Voice Chat**: `/hybrid/voice/chat`
4. **Document Upload**: `/hybrid/document/process`
5. **Privacy Report**: `/hybrid/session/{session_id}/report`

### 6.3 Test Document Upload

1. Go to http://localhost:8001/docs
2. Find `/hybrid/document/process` endpoint
3. Upload a sample PDF or CSV file
4. Set `privacy_tier` to `private_first`
5. Add a query like "Analyze this document"

## 🔧 Step 7: Configuration Options

### 7.1 Privacy Tier Selection

**🟢 Cloud Hybrid (Default)**
- Full features with privacy safeguards
- PII is tokenized before cloud processing
- Best for general users

**🟡 Private-First**
- Local processing preferred
- Limited cloud access for market data only
- Best for privacy-conscious users

**🔴 Offline Mode**
- Complete privacy, no cloud processing
- Cached responses only
- Best for maximum security

### 7.2 PII Protection Levels

**Minimal**: Only high-confidence financial data
**Standard**: Financial and identification data  
**Aggressive**: Everything including names and amounts

## 🔴 Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

**2. Google AI API Errors**
```bash
# Check API key
echo $GOOGLE_API_KEY

# Test API key
curl -H "Authorization: Bearer $GOOGLE_API_KEY" \
  https://generativelanguage.googleapis.com/v1/models
```

**3. MCP Connection Errors**
```bash
# Check MCP server status
curl http://localhost:3000/health

# Check environment variable
echo $MCP_SERVER_URL
```

**4. Port Conflicts**
```bash
# Check if port 8001 is in use
lsof -i :8001

# Kill existing process if needed
kill -9 $(lsof -t -i:8001)
```

**5. File Permission Errors**
```bash
# Make startup script executable
chmod +x start_hybrid_api.py
```

### Debug Mode

For detailed logging, set environment variable:
```bash
export LOG_LEVEL=DEBUG
python start_hybrid_api.py
```

### Component Testing

Test individual components:

```bash
# Test Intent Agent
python -c "
import asyncio
from root_agent.intent_agent import test_intent_agent
asyncio.run(test_intent_agent())
"

# Test PII Tokenizer
python -c "
import asyncio  
from root_agent.pii_tokenizer import test_privacy_tokenizer
asyncio.run(test_privacy_tokenizer())
"

# Test Privacy Tiers
python -c "
import asyncio
from root_agent.privacy_tiers import test_privacy_tiers  
asyncio.run(test_privacy_tiers())
"
```

## 🎯 Step 8: Production Deployment

### 8.1 Security Considerations
- Use HTTPS in production
- Set strong environment variables
- Enable request rate limiting
- Monitor privacy compliance

### 8.2 Scaling Options
- Deploy on Google Cloud Run
- Use load balancers for high availability
- Implement Redis for session management
- Add monitoring and logging

### 8.3 Performance Optimization
- Enable response caching
- Optimize model selection
- Use connection pooling
- Implement request batching

## 📱 Step 9: Mobile Integration

For Google ADK mobile apps:
- Use the `/hybrid/voice/chat` endpoint for voice input
- Implement file upload for document scanning  
- Use streaming endpoints for real-time responses
- Configure privacy tiers based on user preferences

## 🔒 Step 10: Privacy Compliance

### Audit Trail
```bash
# Get session privacy report
curl "http://localhost:8001/hybrid/session/test_session/report"
```

### Data Flow Verification
- All PII is tokenized before cloud processing
- Local components process sensitive data on-device
- Privacy tiers enforce data flow restrictions
- Complete audit trail for compliance

## 🎉 Success Verification

If everything is working correctly, you should be able to:

✅ **Chat with privacy protection**: PII automatically masked  
✅ **Switch privacy tiers**: Different behavior based on selection  
✅ **Process voice input**: Local speech-to-text processing  
✅ **Upload documents**: Secure local parsing for financial docs  
✅ **Get privacy reports**: Complete transparency on data handling  
✅ **Stream responses**: Real-time updates with privacy info  

Your hybrid AI orchestration system is now ready for use! 🚀 