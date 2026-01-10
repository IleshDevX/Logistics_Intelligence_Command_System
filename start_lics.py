"""
LICS Production System Startup Script
Launches both FastAPI backend and Streamlit frontend
"""

import subprocess
import sys
import os
import time
import threading
import webbrowser
from pathlib import Path

def print_banner():
    """Print startup banner"""
    print("=" * 60)
    print("🚛 LICS - Logistics Intelligence & Command System")
    print("   Production System Startup")
    print("=" * 60)

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'fastapi', 'uvicorn', 'streamlit', 'motor', 'pymongo', 
        'python-jose', 'passlib', 'twilio', 'requests'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        
        pip_install = [sys.executable, '-m', 'pip', 'install'] + missing_packages
        subprocess.run(pip_install, check=True)
        print("✅ Packages installed successfully")
    else:
        print("✅ All dependencies are installed")

def check_environment():
    """Check if .env file exists with required variables"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ .env file not found")
        return False
    
    required_vars = [
        'MONGODB_URL',
        'JWT_SECRET_KEY',
        'TWILIO_ACCOUNT_SID',
        'TWILIO_AUTH_TOKEN', 
        'TWILIO_FROM_PHONE'
    ]
    
    with open(env_file, 'r') as f:
        env_content = f.read()
    
    missing_vars = []
    for var in required_vars:
        if var not in env_content or f'{var}=' not in env_content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ Environment configuration is complete")
        return True

def start_backend():
    """Start FastAPI backend server"""
    print("\n🚀 Starting FastAPI Backend Server...")
    try:
        # Change to project directory
        os.chdir(Path(__file__).parent)
        
        # Start FastAPI with uvicorn
        backend_cmd = [
            sys.executable, '-m', 'uvicorn',
            'main:app',
            '--host', '0.0.0.0',
            '--port', '8000',
            '--reload',
            '--log-level', 'info'
        ]
        
        backend_process = subprocess.Popen(
            backend_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Wait a bit for server to start
        time.sleep(3)
        
        if backend_process.poll() is None:
            print("✅ FastAPI Backend started successfully on http://localhost:8000")
            return backend_process
        else:
            stdout, stderr = backend_process.communicate()
            print(f"❌ Backend startup failed:")
            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting backend: {str(e)}")
        return None

def start_frontend():
    """Start Streamlit frontend"""
    print("\n🌐 Starting Streamlit Frontend...")
    try:
        # Change to webapp directory
        webapp_dir = Path(__file__).parent / 'webapp'
        os.chdir(webapp_dir)
        
        # Start Streamlit
        frontend_cmd = [
            sys.executable, '-m', 'streamlit', 'run',
            'app.py',
            '--server.port', '8501',
            '--server.address', '0.0.0.0',
            '--browser.gatherUsageStats', 'false'
        ]
        
        frontend_process = subprocess.Popen(
            frontend_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        # Wait a bit for server to start
        time.sleep(5)
        
        if frontend_process.poll() is None:
            print("✅ Streamlit Frontend started successfully on http://localhost:8501")
            return frontend_process
        else:
            stdout, stderr = frontend_process.communicate()
            print(f"❌ Frontend startup failed:")
            print(f"stdout: {stdout}")
            print(f"stderr: {stderr}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting frontend: {str(e)}")
        return None

def open_browser():
    """Open browser to the application"""
    def delayed_open():
        time.sleep(8)  # Wait for both servers to be ready
        try:
            print("\n🌐 Opening browser...")
            webbrowser.open('http://localhost:8501')
        except Exception as e:
            print(f"Could not open browser automatically: {e}")
            print("Please open http://localhost:8501 manually")
    
    threading.Thread(target=delayed_open, daemon=True).start()

def monitor_processes(backend_process, frontend_process):
    """Monitor running processes"""
    print("\n📊 System Status:")
    print("   - FastAPI Backend: http://localhost:8000")
    print("   - Streamlit Frontend: http://localhost:8501")
    print("   - API Documentation: http://localhost:8000/docs")
    print("\n⌨️  Press Ctrl+C to stop all services")
    
    try:
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process and backend_process.poll() is not None:
                print("❌ Backend process terminated unexpectedly")
                break
                
            if frontend_process and frontend_process.poll() is not None:
                print("❌ Frontend process terminated unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        
        if backend_process:
            backend_process.terminate()
            backend_process.wait()
            print("✅ Backend stopped")
            
        if frontend_process:
            frontend_process.terminate()
            frontend_process.wait()
            print("✅ Frontend stopped")
        
        print("👋 LICS system shutdown complete")

def main():
    """Main startup function"""
    print_banner()
    
    # Pre-flight checks
    print("🔍 Running pre-flight checks...")
    check_dependencies()
    
    env_ok = check_environment()
    if not env_ok:
        print("\n❌ Environment setup incomplete. Please check .env file.")
        print("Required variables: MONGODB_URL, JWT_SECRET_KEY, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_PHONE")
        return
    
    # Start services
    backend_process = start_backend()
    if not backend_process:
        print("❌ Failed to start backend. Exiting.")
        return
    
    frontend_process = start_frontend()
    if not frontend_process:
        print("❌ Failed to start frontend. Stopping backend.")
        backend_process.terminate()
        return
    
    # Open browser
    open_browser()
    
    # Monitor processes
    monitor_processes(backend_process, frontend_process)

if __name__ == "__main__":
    main()