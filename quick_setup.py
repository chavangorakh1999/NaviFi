#!/usr/bin/env python3
"""
Quick Setup Script for NaviFi Hybrid AI Financial Agent
Automates environment setup, dependency installation, and basic configuration
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_banner():
    """Print welcome banner"""
    print("🚀 NaviFi Hybrid AI Quick Setup")
    print("=" * 50)
    print("🏗️  Setting up hybrid AI orchestration strategy")
    print("🔒 Privacy-first financial AI agent")
    print()

def check_python_version():
    """Check if Python version is 3.8+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required. Current version:", f"{version.major}.{version.minor}")
        sys.exit(1)
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")

def create_virtual_environment():
    """Create and activate virtual environment"""
    print("\n📦 Setting up virtual environment...")
    
    if os.path.exists(".venv"):
        print("✅ Virtual environment already exists")
        return
    
    try:
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
        print("✅ Virtual environment created")
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment")
        sys.exit(1)

def get_pip_command():
    """Get the correct pip command for the virtual environment"""
    if sys.platform == "win32":
        return ".venv\\Scripts\\pip"
    else:
        return ".venv/bin/pip"

def install_dependencies():
    """Install required dependencies"""
    print("\n📥 Installing dependencies...")
    
    pip_cmd = get_pip_command()
    
    try:
        # Install core dependencies
        subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
        print("✅ Core dependencies installed")
        
        # Check for optional dependencies
        print("\n💡 Optional dependencies available:")
        print("   - Audio processing: pydub, speechrecognition")
        print("   - PDF processing: PyMuPDF, pdfplumber") 
        print("   - Data analysis: numpy, pandas")
        print("   Install these manually if needed for enhanced features")
        
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        print("💡 Try manually: pip install -r requirements.txt")
        sys.exit(1)

def create_env_file():
    """Create .env file with template configuration"""
    print("\n🔑 Setting up environment configuration...")
    
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return
    
    env_template = """# Google AI Configuration (choose one method)

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
"""
    
    try:
        env_file.write_text(env_template)
        print("✅ .env template created")
        print("⚠️  Please edit .env file with your actual API keys")
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")

def check_required_files():
    """Check if all required files exist"""
    print("\n📋 Checking project files...")
    
    required_files = [
        "hybrid_api.py",
        "start_hybrid_api.py", 
        "root_agent/intent_agent.py",
        "root_agent/pii_tokenizer.py",
        "root_agent/privacy_tiers.py",
        "root_agent/streaming_config.py",
        "root_agent/agent.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print("\n❌ Missing required files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        print("Please ensure all hybrid AI components are present")
        sys.exit(1)

def test_import():
    """Test importing key modules"""
    print("\n🧪 Testing module imports...")
    
    try:
        # Test core imports
        import fastapi
        import uvicorn
        import pydantic
        print("✅ Core web framework modules")
        
        # Test local imports (modify sys.path first)
        sys.path.insert(0, str(Path.cwd()))
        
        from root_agent.intent_agent import create_intent_agent
        print("✅ Intent Agent module")
        
        from root_agent.pii_tokenizer import create_privacy_tokenizer
        print("✅ PII Tokenizer module")
        
        from root_agent.privacy_tiers import create_privacy_manager
        print("✅ Privacy Tiers module")
        
        from root_agent.streaming_config import MultimodalStreamingProcessor
        print("✅ Streaming Config module")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Try: source .venv/bin/activate && pip install -r requirements.txt")
        return False
    
    return True

def create_test_script():
    """Create a simple test script"""
    print("\n📝 Creating test script...")
    
    test_script = """#!/usr/bin/env python3
\"\"\"
Quick test script for NaviFi Hybrid AI components
\"\"\"

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_components():
    \"\"\"Test all hybrid AI components\"\"\"
    
    print("🧪 Testing Hybrid AI Components")
    print("=" * 40)
    
    try:
        # Test Intent Agent
        print("\\n1. Testing Intent Agent...")
        from root_agent.intent_agent import create_intent_agent
        intent_agent = create_intent_agent()
        
        sample_query = "What's my net worth?"
        analysis = await intent_agent.analyze_intent(sample_query)
        print(f"   Intent: {analysis.primary_intent.value}")
        print(f"   Confidence: {analysis.confidence_score:.2f}")
        print("✅ Intent Agent working")
        
        # Test PII Tokenizer
        print("\\n2. Testing PII Tokenizer...")
        from root_agent.pii_tokenizer import create_privacy_tokenizer
        tokenizer = create_privacy_tokenizer()
        
        sample_text = "My credit card is 4532-1234-5678-9012"
        result = await tokenizer.tokenize_text(sample_text)
        print(f"   Original: {sample_text}")
        print(f"   Masked: {result.masked_text}")
        print(f"   Privacy Score: {result.privacy_score:.2f}")
        print("✅ PII Tokenizer working")
        
        # Test Privacy Tiers
        print("\\n3. Testing Privacy Tiers...")
        from root_agent.privacy_tiers import create_privacy_manager, PrivacyTier, DataSensitivity
        privacy_manager = create_privacy_manager()
        
        decision = await privacy_manager.evaluate_data_flow(
            user_id="test_user",
            query=sample_query,
            data_sensitivity=DataSensitivity.PERSONAL
        )
        print(f"   Cloud Processing: {decision.can_process_in_cloud}")
        print(f"   Tokenization Required: {decision.requires_tokenization}")
        print("✅ Privacy Tiers working")
        
        print("\\n🎉 All components tested successfully!")
        
    except Exception as e:
        print(f"\\n❌ Component test failed: {e}")
        print("💡 Check the setup guide for troubleshooting")

if __name__ == "__main__":
    asyncio.run(test_components())
"""
    
    try:
        Path("test_components.py").write_text(test_script)
        os.chmod("test_components.py", 0o755)
        print("✅ Test script created: test_components.py")
    except Exception as e:
        print(f"❌ Failed to create test script: {e}")

def print_next_steps():
    """Print next steps for the user"""
    print("\n🎉 Setup Complete!")
    print("=" * 50)
    print()
    print("📋 Next Steps:")
    print()
    print("1. 🔑 Configure API Keys:")
    print("   - Edit .env file with your Google AI Studio API key")
    print("   - Ensure your MCP server is running on http://localhost:3000")
    print()
    print("2. 🧪 Test the Setup:")
    print("   python test_components.py")
    print()
    print("3. 🚀 Start the Hybrid API:")
    print("   python start_hybrid_api.py")
    print()
    print("4. 🌐 Open API Documentation:")
    print("   http://localhost:8001/docs")
    print()
    print("5. 📚 Read Full Setup Guide:")
    print("   See SETUP_GUIDE.md for detailed instructions")
    print()
    print("🔒 Privacy Features Ready:")
    print("   🟢 Cloud Hybrid (default)")
    print("   🟡 Private-First mode") 
    print("   🔴 Offline mode")
    print()
    print("💡 Need help? Check SETUP_GUIDE.md for troubleshooting")

def main():
    """Main setup function"""
    print_banner()
    
    # Check prerequisites
    check_python_version()
    
    # Setup environment
    create_virtual_environment()
    
    # Install dependencies
    install_dependencies()
    
    # Create configuration
    create_env_file()
    
    # Verify setup
    check_required_files()
    
    # Test imports (optional, might fail if virtual env not activated)
    print("\n🔍 Verifying setup...")
    if test_import():
        print("✅ All imports successful")
    else:
        print("⚠️  Some imports failed - this is normal if virtual env is not activated")
        print("💡 Activate virtual env: source .venv/bin/activate")
    
    # Create test utilities
    create_test_script()
    
    # Show next steps
    print_next_steps()

if __name__ == "__main__":
    main() 