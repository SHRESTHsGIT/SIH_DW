## run.py

import subprocess
import sys
import os
import time
import threading
from config import setup_directories

def run_api():
    """Run FastAPI server"""
    print("🚀 Starting FastAPI server on port 8000...")
    subprocess.Popen([sys.executable, "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"])

def run_teacher_app():
    """Run Streamlit teacher dashboard"""
    print("👨‍🏫 Starting Teacher Dashboard on port 8502...")
    subprocess.Popen([sys.executable, "-m", "streamlit", "run", "teacher_app.py", "--server.port", "8502"])

def run_student_app():
    """Run Streamlit student portal"""
    print("🎓 Starting Student Portal on port 8503...")
    subprocess.Popen([sys.executable, "-m", "streamlit", "run", "student_app.py", "--server.port", "8503"])

def run_personal_assistant():
    """Run Streamlit personal assistant"""
    print("🤖 Starting Personal Assistant on port 8504...")
    subprocess.Popen([sys.executable, "-m", "streamlit", "run", "personal_assistant_app.py", "--server.port", "8504"])

def main():
    print("🎯 Face Recognition Attendance System")
    print("=====================================")
    
    # Setup directories and initialize data
    print("📁 Setting up directories and initializing data...")
    setup_directories()
    
    print("\n🚀 Starting all services...")
    print("Please wait for all services to start...")
    
    # Create threads for each service
    api_thread = threading.Thread(target=run_api, daemon=True)
    teacher_thread = threading.Thread(target=run_teacher_app, daemon=True)
    student_thread = threading.Thread(target=run_student_app, daemon=True)
    pa_thread = threading.Thread(target=run_personal_assistant, daemon=True)
    
    # Start all services
    api_thread.start()
    time.sleep(3)  # Give API time to start
    
    teacher_thread.start()
    time.sleep(2)  # Give teacher app time to start
    
    student_thread.start()
    time.sleep(2)  # Give student app time to start
    
    pa_thread.start()
    time.sleep(2)  # Give PA time to start
    
    print("\n✅ All services started successfully!")
    print("\n🌐 Access URLs:")
    print("📊 API Documentation: http://localhost:8000/docs")
    print("👨‍🏫 Teacher Dashboard: http://localhost:8502")
    print("🎓 Student Portal: http://localhost:8503")
    print("🤖 Personal Assistant: http://localhost:8504")
    
    print("\n📋 Demo Credentials:")
    print("👨‍🏫 Teachers:")
    print("   - Teacher ID: T001, Password: password123")
    print("   - Teacher ID: T002, Password: password456")
    print("\n🎓 Students: (Register first with your camera)")
    print("   - Roll Number Format: BT[YY][BRANCH][XXX]")
    print("   - Example: BT23CSH013, BT24CSA001, BT25CSD045")
    
    print("\n💡 Personal Assistant Features:")
    print("   - AI Learning Roadmaps")
    print("   - Daily To-Do Lists")
    print("   - Exercise Plans")
    print("   - Wellness Tracking")
    print("   - Smart Reminders")
    
    print("\n🔄 System is running... Press Ctrl+C to stop all services")
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down all services...")
        print("✅ Goodbye!")

if __name__ == "__main__":
    main()