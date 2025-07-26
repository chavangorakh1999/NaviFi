#!/usr/bin/env python3
"""
Startup script for NaviFi Simplified API with Security Guardrails
This version works without google.adk dependency
"""

import uvicorn
import os
import sys
from pathlib import Path

def main():
    """Start the simplified API server"""
    
    # Add current directory to Python path for imports
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    print("🚀 Starting NaviFi Simplified API with Security Guardrails...")
    print("🔒 Security Features Enabled:")
    print("   - Tool access control (MCP + Google Search)")
    print("   - Input validation and sanitization")
    print("   - Rate limiting (per-user and per-tool)")
    print("   - PII protection and redaction")
    print("   - Security logging and monitoring")
    print("   - Pattern blocking (XSS, SQL injection, etc.)")
    print("   - Financial advice disclaimers")
    print()
    print("📡 Server will be available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("🔧 Interactive API explorer at: http://localhost:8000/redoc")
    print()
    print("🔍 Security Monitoring:")
    print("   - Security status: http://localhost:8000/security/status")
    print("   - Allowed tools: http://localhost:8000/security/tools")
    print()
    print("🛡️ Available Tools (Secured):")
    print("   Financial Data:")
    print("     - fetch_net_worth")
    print("     - fetch_credit_report")
    print("     - fetch_epf_details")
    print("     - fetch_mf_transactions")
    print("     - fetch_bank_transactions")
    print("     - fetch_stock_transactions")
    print("   Market Research:")
    print("     - google_search")
    print()
    print("📝 Note: This is a simplified version for testing security guardrails")
    print("   It uses mock responses instead of the actual Google ADK agent")
    print()
    print("Press CTRL+C to stop the server")
    print("-" * 60)
    
    try:
        uvicorn.run(
            "api_simple:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 Simplified server stopped by user")
    except Exception as e:
        print(f"❌ Error starting simplified server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 