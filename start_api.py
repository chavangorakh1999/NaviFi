#!/usr/bin/env python3
"""
Startup script for NaviFi Financial Agent API
"""

import uvicorn
import os
import sys
from pathlib import Path

def main():
    """Start the API server"""
    
    # Check required environment variables
    missing_vars = []
    
    if not os.getenv("MCP_SERVER_URL"):
        missing_vars.append("MCP_SERVER_URL - URL for your MCP server (e.g., http://localhost:3000)")
    
    # Check for Google AI/Vertex AI credentials
    has_google_ai = os.getenv("GOOGLE_API_KEY")
    has_vertex_ai = os.getenv("GOOGLE_CLOUD_PROJECT") and os.getenv("GOOGLE_CLOUD_LOCATION")
    
    if not has_google_ai and not has_vertex_ai:
        missing_vars.append("Google AI credentials - either:")
        missing_vars.append("  - GOOGLE_API_KEY for Google AI Studio, OR")
        missing_vars.append("  - GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION for Vertex AI")
    
    if missing_vars:
        print("⚠️  Warning: Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print()
        print("Example setup:")
        print("   # For Google AI Studio:")
        print("   export GOOGLE_API_KEY='your_api_key_here'")
        print("   export MCP_SERVER_URL='http://localhost:3000'")
        print()
        print("   # For Vertex AI:")
        print("   export GOOGLE_CLOUD_PROJECT='your-project-id'")
        print("   export GOOGLE_CLOUD_LOCATION='us-central1'")
        print("   export MCP_SERVER_URL='http://localhost:3000'")
        print()
        print("The API will still start but may not work properly without these variables.")
        print()
    
    # Add current directory to Python path for imports
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    print("🚀 Starting NaviFi Financial Agent API...")
    print("📡 Server will be available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("🔧 Interactive API explorer at: http://localhost:8000/redoc")
    print()
    print("Press CTRL+C to stop the server")
    print("-" * 50)
    
    try:
        uvicorn.run(
            "api:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 