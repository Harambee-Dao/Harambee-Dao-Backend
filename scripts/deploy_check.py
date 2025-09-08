#!/usr/bin/env python3
"""
Harambee DAO Backend - Deployment Readiness Check
This script verifies that all deployment requirements are met.
"""

import os
import sys
import subprocess
import requests
from pathlib import Path

def check_file_exists(file_path: str) -> bool:
    """Check if a required file exists."""
    return Path(file_path).exists()

def check_dependencies() -> bool:
    """Check if all required dependencies are available."""
    required_files = [
        "pyproject.toml",
        "requirements.txt",
        "render.yaml",
        "Dockerfile",
        ".dockerignore",
        "app/main.py",
        ".env.example"
    ]
    
    print("🔍 Checking required files...")
    all_present = True
    
    for file_path in required_files:
        if check_file_exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - MISSING")
            all_present = False
    
    return all_present

def check_python_syntax() -> bool:
    """Check Python syntax for main application files."""
    python_files = [
        "app/main.py",
        "app/core/config.py",
        "app/api/routes.py",
        "app/api/user_routes.py"
    ]
    
    print("\n🐍 Checking Python syntax...")
    all_valid = True
    
    for file_path in python_files:
        if check_file_exists(file_path):
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "py_compile", file_path],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print(f"  ✅ {file_path}")
                else:
                    print(f"  ❌ {file_path} - Syntax Error: {result.stderr}")
                    all_valid = False
            except Exception as e:
                print(f"  ❌ {file_path} - Error: {e}")
                all_valid = False
        else:
            print(f"  ⚠️  {file_path} - File not found")
    
    return all_valid

def check_environment_template() -> bool:
    """Check if .env.example has all required variables."""
    required_vars = [
        "APP_ENV",
        "LOG_LEVEL",
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_PHONE_NUMBER",
        "SECRET_KEY",
        "GROQ_API_KEY",
        "GROQ_API_URL"
    ]
    
    print("\n🔧 Checking environment template...")
    
    if not check_file_exists(".env.example"):
        print("  ❌ .env.example not found")
        return False
    
    with open(".env.example", "r") as f:
        env_content = f.read()
    
    all_present = True
    for var in required_vars:
        if var in env_content:
            print(f"  ✅ {var}")
        else:
            print(f"  ❌ {var} - Missing from .env.example")
            all_present = False
    
    return all_present

def check_render_config() -> bool:
    """Check render.yaml configuration."""
    print("\n🚀 Checking Render configuration...")
    
    if not check_file_exists("render.yaml"):
        print("  ❌ render.yaml not found")
        return False
    
    try:
        import yaml
        with open("render.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        # Check basic structure
        if "services" in config and len(config["services"]) > 0:
            service = config["services"][0]
            required_keys = ["type", "name", "env", "buildCommand", "startCommand"]
            
            for key in required_keys:
                if key in service:
                    print(f"  ✅ {key}: {service[key]}")
                else:
                    print(f"  ❌ {key} - Missing from render.yaml")
                    return False
            
            return True
        else:
            print("  ❌ Invalid render.yaml structure")
            return False
            
    except ImportError:
        print("  ⚠️  PyYAML not installed, skipping detailed validation")
        print("  ✅ render.yaml exists")
        return True
    except Exception as e:
        print(f"  ❌ Error reading render.yaml: {e}")
        return False

def test_local_startup() -> bool:
    """Test if the application can start locally."""
    print("\n🧪 Testing local application startup...")
    
    try:
        # Try to import the main app
        sys.path.insert(0, ".")
        from app.main import app
        print("  ✅ Application imports successfully")
        
        # Check if FastAPI app is created
        if hasattr(app, "routes"):
            print(f"  ✅ FastAPI app created with {len(app.routes)} routes")
            return True
        else:
            print("  ❌ FastAPI app not properly configured")
            return False
            
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        print("  💡 Make sure dependencies are installed: pip install -e .")
        return False
    except Exception as e:
        print(f"  ❌ Startup error: {e}")
        return False

def generate_deployment_summary():
    """Generate a deployment summary with next steps."""
    print("\n" + "="*60)
    print("🎯 DEPLOYMENT SUMMARY")
    print("="*60)
    
    print("\n📋 Pre-deployment Checklist:")
    print("  1. ✅ Create Render account at https://render.com")
    print("  2. ✅ Create Twilio account at https://twilio.com")
    print("  3. ✅ Get Twilio Account SID, Auth Token, and Phone Number")
    print("  4. ✅ Optional: Get Groq API key for AI features")
    
    print("\n🚀 Deployment Steps:")
    print("  1. Go to Render Dashboard → New + → Web Service")
    print("  2. Connect GitHub repository: Harambee-Dao-Backend")
    print("  3. Configure build settings:")
    print("     - Build Command: pip install -e .")
    print("     - Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT")
    print("  4. Add environment variables from .env.example")
    print("  5. Deploy and test endpoints")
    
    print("\n🔧 Post-deployment:")
    print("  1. Configure Twilio webhook URL")
    print("  2. Test SMS functionality")
    print("  3. Set up monitoring and alerts")
    print("  4. Configure custom domain (optional)")
    
    print("\n📚 Documentation:")
    print("  - Full Guide: RENDER_DEPLOYMENT_GUIDE.md")
    print("  - API Docs: README.md")
    print("  - User Management: USER_MANAGEMENT_README.md")

def main():
    """Main deployment check function."""
    print("🏛️ Harambee DAO Backend - Deployment Readiness Check")
    print("="*60)
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Python Syntax", check_python_syntax),
        ("Environment Template", check_environment_template),
        ("Render Configuration", check_render_config),
        ("Local Startup", test_local_startup)
    ]
    
    all_passed = True
    results = []
    
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
            if not result:
                all_passed = False
        except Exception as e:
            print(f"  ❌ {check_name} - Error: {e}")
            results.append((check_name, False))
            all_passed = False
    
    # Summary
    print("\n" + "="*60)
    print("📊 CHECK RESULTS")
    print("="*60)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {check_name}")
    
    if all_passed:
        print("\n🎉 ALL CHECKS PASSED!")
        print("✅ Your backend is ready for deployment to Render!")
        generate_deployment_summary()
    else:
        print("\n⚠️  SOME CHECKS FAILED")
        print("❌ Please fix the issues above before deploying.")
        print("💡 See RENDER_DEPLOYMENT_GUIDE.md for detailed instructions.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
