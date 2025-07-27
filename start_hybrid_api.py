#!/usr/bin/env python3
"""
Startup script for NaviFi Hybrid AI Financial Agent
Implements complete hybrid AI orchestration strategy with privacy-first approach
"""

import uvicorn
import os
import sys
from pathlib import Path

def main():
    """Start the Hybrid API server"""
    
    print("🚀 NaviFi Hybrid AI Financial Agent")
    print("=" * 50)
    print("🏗️  Architecture: Hybrid AI Orchestration Strategy")
    print("🔒 Privacy: Three-tier privacy system")
    print("🎙️  Features: Voice, Document, Real-time processing")
    print()
    
    # Check required environment variables
    missing_vars = []
    warnings = []
    
    # Core requirements
    if not os.getenv("MCP_SERVER_URL"):
        missing_vars.append("MCP_SERVER_URL - URL for your MCP server (e.g., http://localhost:3000)")
    
    # Google AI/Vertex AI credentials
    has_google_ai = os.getenv("GOOGLE_API_KEY")
    has_vertex_ai = os.getenv("GOOGLE_CLOUD_PROJECT") and os.getenv("GOOGLE_CLOUD_LOCATION")
    
    if not has_google_ai and not has_vertex_ai:
        missing_vars.append("Google AI credentials - either:")
        missing_vars.append("  - GOOGLE_API_KEY for Google AI Studio, OR")
        missing_vars.append("  - GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION for Vertex AI")
    
    # Optional but recommended
    if not os.getenv("MCP_LOGIN_URL"):
        warnings.append("MCP_LOGIN_URL - URL for user authentication (enhances user experience)")
    
    if missing_vars:
        print("⚠️  Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print()
        print("🔧 Setup Examples:")
        print("   # For Google AI Studio:")
        print("   export GOOGLE_API_KEY='your_api_key_here'")
        print("   export MCP_SERVER_URL='http://localhost:3000'")
        print("   export MCP_LOGIN_URL='http://localhost:3000/login'")
        print()
        print("   # For Vertex AI:")
        print("   export GOOGLE_CLOUD_PROJECT='your-project-id'")
        print("   export GOOGLE_CLOUD_LOCATION='us-central1'")
        print("   export MCP_SERVER_URL='http://localhost:3000'")
        print()
        print("The API will start but may not work properly without these variables.")
        print()
    
    if warnings:
        print("💡 Optional configurations:")
        for warning in warnings:
            print(f"   - {warning}")
        print()
    
    # Add current directory to Python path for imports
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    print("🌐 Starting Hybrid API Server...")
    print("📡 Server will be available at: http://localhost:8001")
    print("📚 API documentation at: http://localhost:8001/docs")
    print("🔧 Interactive API explorer at: http://localhost:8001/redoc")
    print()
    print("🏗️  Hybrid Architecture Components:")
    print("   🎙️  Intent Agent (Local) - Fast query analysis")
    print("   🔒 PII Tokenizer (Local) - Privacy-first data masking")
    print("   📊 Privacy Tiers - Cloud Hybrid | Private-First | Offline")
    print("   🌐 Cloud Agents - Full financial analysis capabilities")
    print("   📱 Multimodal Support - Voice, documents, streaming")
    print()
    print("🔒 Privacy Modes Available:")
    print("   🟢 Cloud Hybrid (default) - Full features with privacy safeguards")
    print("   🟡 Private-First - Local processing preferred, limited cloud")
    print("   🔴 Offline Mode - Complete privacy, cached responses only")
    print()
    print("📋 Example API Calls:")
    print("   POST /hybrid/chat - Text chat with privacy tier selection")
    print("   POST /hybrid/voice/chat - Voice input processing")
    print("   POST /hybrid/document/process - Secure document analysis")
    print("   GET /hybrid/privacy/tiers - View privacy options")
    print()
    print("Press CTRL+C to stop the server")
    print("-" * 70)
    
    try:
        uvicorn.run(
            "hybrid_api:app",
            host="0.0.0.0",
            port=8001,
            reload=True,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 Hybrid API server stopped by user")
        print("🔒 All local privacy components safely shut down")
    except Exception as e:
        print(f"❌ Error starting hybrid API server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 