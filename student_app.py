## student_app.py

import streamlit as st
import requests
from PIL import Image
import io
from datetime import datetime
import cv2
import numpy as np
import time

# Configure Streamlit
st.set_page_config(
    page_title="Student Portal - Attendance System",
    page_icon="🎓",
    layout="wide"
)

API_BASE_URL = "http://localhost:8000"

def main():
    st.title("🎓 Student Portal - Face Recognition Attendance System")
    
    # Session state initialization
    if 'selected_branch' not in st.session_state:
        st.session_state.selected_branch = None
    if 'selected_year' not in st.session_state:
        st.session_state.selected_year = None
    if 'show_registration' not in st.session_state:
        st.session_state.show_registration = False
    
    # Navigation
    if st.session_state.show_registration:
        show_registration()
    elif not st.session_state.selected_branch:
        show_branch_selection()
    else:
        show_attendance_interface()

def show_branch_selection():
    st.markdown("### 🏫 Select Your Branch and Year")
    st.info("Choose your branch and year to check for active attendance sessions")
    
    # Personal Assistant button
    col1, col2, col3 = st.columns([2, 1, 1])
    with col2:
        if st.button("📝 Register New Student", type="secondary"):
            st.session_state.show_registration = True
            st.rerun()
    with col3:
        if st.button("🤖 Personal Assistant", type="primary"):
            st.markdown("[Open Personal Assistant](http://localhost:8504)")
            st.info("Opening Personal Assistant in new window...")
    
    # Get branches
    try:
        response = requests.get(f"{API_BASE_URL}/api/branches")
        if response.status_code == 200:
            branches = response.json()
        else:
            branches = []
    except:
        branches = []
        st.error("Could not fetch branches")
    
    if not branches:
        st.warning("No branches available")
        return
    
    with st.form("branch_selection_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            branch_options = [f"{b['branch_code']} - {b['branch_name']}" for b in branches]
            selected_branch = st.selectbox("Select Branch", [""] + branch_options)
            branch_code = selected_branch.split(" - ")[0] if selected_branch else ""
        
        with col2:
            year = st.selectbox("Select Year", ["", "2022", "2023", "2024", "2025"])
        
        submit_button = st.form_submit_button("🔍 Check for Active Session", use_container_width=True)
        
        if submit_button and branch_code and year:
            # Store selection in session state
            st.session_state.selected_branch = branch_code
            st.session_state.selected_year = year
            st.rerun()
        elif submit_button:
            st.warning("⚠️ Please select both branch and year")

def show_attendance_interface():
    # Header with branch selection
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        st.markdown(f"### 🎓 Attendance Portal")
        st.markdown(f"📚 **Branch:** {st.session_state.selected_branch} | 📅 **Year:** {st.session_state.selected_year}")
    
    with col2:
        # Show current time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.markdown(f"⏰ **Current Time:** {current_time}")
    
    with col3:
        if st.button("🔄 Change Branch", type="secondary"):
            st.session_state.selected_branch = None
            st.session_state.selected_year = None
            st.rerun()
    
    st.divider()
    
    # Check for active session
    try:
        response = requests.get(f"{API_BASE_URL}/api/sessions/{st.session_state.selected_branch}/{st.session_state.selected_year}/active")
        
        if response.status_code == 200:
            session = response.json()
            show_active_session_interface(session)
        
        elif response.status_code == 404:
            show_no_session_message()
        
        else:
            st.error("❌ Error checking for active sessions")
            
    except requests.exceptions.RequestException:
        st.error("❌ Could not connect to server")

def show_active_session_interface(session):
    """Show interface when there's an active session"""
    
    # Session info and countdown timer
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.success(f"🟢 **Active Session Found!**")
        st.info(f"📝 **Session ID:** {session['session_id']}")
    
    with col2:
        # Calculate remaining time
        try:
            deadline = datetime.fromisoformat(session['deadline_time'])
            now = datetime.now()
            remaining = deadline - now
            
            if remaining.total_seconds() > 0:
                hours, remainder = divmod(int(remaining.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                st.metric("⏰ Time Remaining", f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            else:
                st.error("⏰ Session has expired!")
                return
                
        except Exception as e:
            st.warning("⏰ Could not calculate remaining time")
    
    st.divider()
    
    # Attendance marking interface
    st.markdown("### ✅ Mark Your Attendance")
    st.info("Choose one of the methods below to mark your attendance")
    
    # Two methods side by side
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📸 Method 1: Face Recognition")
        st.info("Capture your face to mark attendance automatically")
        
        face_image = st.camera_input("📷 Capture your face", key="face_attendance")
        
        if face_image:
            if st.button("🔍 Mark Attendance via Face", type="primary", use_container_width=True):
                mark_attendance_face(session['session_id'], face_image)
    
    with col2:
        st.markdown("#### 📱 Method 2: QR Code Scan")
        st.info("Scan your QR code to mark attendance")
        
        qr_image = st.camera_input("📱 Scan your QR code", key="qr_attendance")
        
        if qr_image:
            if st.button("📱 Mark Attendance via QR", type="primary", use_container_width=True):
                mark_attendance_qr(session['session_id'], qr_image)
    
    # Auto-refresh every 10 seconds to update timer
    import time
    time.sleep(10)
    st.rerun()

def show_no_session_message():
    """Show message when no active session"""
    st.warning("⚠️ No Active Session")
    st.info("There is currently no active attendance session for your selected branch and year.")
    st.markdown("""
    ### 📋 What to do:
    - **Wait for your teacher** to start an attendance session
    - **Refresh this page** periodically to check for new sessions
    - **Contact your teacher** if you think there should be an active session
    """)
    
    # Auto refresh button
    if st.button("🔄 Refresh", type="secondary", use_container_width=False):
        st.rerun()
    
    # Auto refresh every 30 seconds
    st.markdown("*Page will auto-refresh every 30 seconds*")
    time.sleep(30)
    st.rerun()

def mark_attendance_face(session_id, face_image):
    """Handle face recognition attendance marking"""
    try:
        files = {"face_image": ("face.jpg", face_image.getvalue(), "image/jpeg")}
        data = {"session_id": session_id}
        
        with st.spinner("🔍 Recognizing face... Please wait..."):
            response = requests.post(f"{API_BASE_URL}/api/attendance/mark-face", 
                                   files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            st.success(f"✅ **Attendance Marked Successfully!**")
            st.success(f"🎓 **Roll Number:** {result['roll_no']}")
            st.balloons()
            
            # Show success for 3 seconds then refresh
            time.sleep(3)
            st.rerun()
        else:
            error_msg = response.json().get("detail", "Face recognition failed")
            st.error(f"❌ {error_msg}")
            st.error("💡 Try again with better lighting or clearer face position")
            
    except requests.exceptions.RequestException:
        st.error("❌ Could not connect to server")

def show_registration():
    """Show student registration form"""
    st.markdown("### 📝 Student Registration")
    
    # Back button
    if st.button("← Back to Main", type="secondary"):
        st.session_state.show_registration = False
        st.rerun()
    
    st.info("Register yourself in the system to use face recognition for attendance")
    
    # Get branches
    try:
        response = requests.get(f"{API_BASE_URL}/api/branches")
        if response.status_code == 200:
            branches = response.json()
        else:
            branches = []
    except:
        branches = []
        st.error("Could not fetch branches")
    
    if not branches:
        st.warning("No branches available for registration")
        return
    
    with st.form("registration_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            roll_no = st.text_input("Roll Number", placeholder="e.g., BT23CSH013", help="Format: BT[YY][BRANCH][XXX]")
            name = st.text_input("Full Name", placeholder="e.g., John Doe")
        
        with col2:
            branch_options = [f"{b['branch_code']} - {b['branch_name']}" for b in branches]
            selected_branch = st.selectbox("Branch", branch_options)
            branch_code = selected_branch.split(" - ")[0] if selected_branch else ""
            password = st.text_input("Password", type="password", help="Create a password for your account")
        
        st.markdown("#### 📸 Face Photo Capture")
        st.info("📷 Click below to capture your face photo using your camera")
        
        # Camera input for face capture
        face_image = st.camera_input("Capture your face photo")
        
        submit_button = st.form_submit_button("📝 Register", use_container_width=True, type="primary")
        
        if submit_button:
            if all([roll_no, name, password, branch_code, face_image]):
                # Validate roll number format
                if not validate_roll_number(roll_no, branch_code):
                    st.error("❌ Invalid roll number format or doesn't match selected branch")
                    return
                
                try:
                    # Prepare form data
                    files = {"face_image": ("face.jpg", face_image.getvalue(), "image/jpeg")}
                    data = {
                        "roll_no": roll_no.upper(),
                        "name": name,
                        "password": password,
                        "branch_code": branch_code
                    }
                    
                    with st.spinner("📝 Registering student... Please wait..."):
                        response = requests.post(f"{API_BASE_URL}/api/students/register", 
                                               files=files, data=data)
                    
                    if response.status_code == 200:
                        st.success("✅ Registration successful!")
                        st.success("🎉 You can now use the system to mark attendance!")
                        st.balloons()
                        
                        # Auto redirect back to main after 3 seconds
                        time.sleep(3)
                        st.session_state.show_registration = False
                        st.rerun()
                    else:
                        error_msg = response.json().get("detail", "Registration failed")
                        st.error(f"❌ {error_msg}")
                        
                except requests.exceptions.RequestException:
                    st.error("❌ Could not connect to server")
            else:
                st.warning("⚠️ Please fill all fields and capture your face photo")

def validate_roll_number(roll_no, branch_code):
    """Validate roll number format: BT[YY][BRANCH][XXX]"""
    if len(roll_no) < 8 or not roll_no.startswith('BT'):
        return False
    
    try:
        # Extract components
        year_part = roll_no[2:4]  # Should be 22, 23, 24, or 25
        branch_part = roll_no[4:7]  # Should match selected branch
        number_part = roll_no[7:]  # Should be 3 digits
        
        # Validate year (22-25)
        if year_part not in ['22', '23', '24', '25']:
            return False
        
        # Validate branch matches selection
        if branch_part != branch_code:
            return False
        
        # Validate number part (3 digits)
        if len(number_part) != 3 or not number_part.isdigit():
            return False
        
        return True
        
    except:
        return False

def mark_attendance_face(session_id, face_image):
    """Handle face recognition attendance marking"""
    try:
        files = {"face_image": ("face.jpg", face_image.getvalue(), "image/jpeg")}
        data = {"session_id": session_id}
        
        with st.spinner("🔍 Recognizing face... Please wait..."):
            response = requests.post(f"{API_BASE_URL}/api/attendance/mark-face", 
                                   files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            st.success(f"✅ **Attendance Marked Successfully!**")
            st.success(f"🎓 **Roll Number:** {result['roll_no']}")
            st.balloons()
            
            # Show success message and auto-refresh after 3 seconds
            with st.empty():
                st.info("🔄 Refreshing page in 3 seconds...")
                import time
                time.sleep(3)
            st.rerun()
        else:
            error_msg = response.json().get("detail", "Face recognition failed")
            st.error(f"❌ {error_msg}")
            st.error("💡 **Try again with:**")
            st.error("   • Better lighting")
            st.error("   • Clear face visibility")
            st.error("   • Look directly at camera")
            
    except requests.exceptions.RequestException:
        st.error("❌ Could not connect to server")
        st.error("💡 Please check if the API server is running")

def mark_attendance_qr(session_id, qr_image):
    """Handle QR code attendance marking"""
    try:
        files = {"qr_image": ("qr.jpg", qr_image.getvalue(), "image/jpeg")}
        data = {"session_id": session_id}
        
        with st.spinner("📱 Scanning QR code... Please wait..."):
            response = requests.post(f"{API_BASE_URL}/api/attendance/mark-qr", 
                                   files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            st.success(f"✅ **Attendance Marked Successfully!**")
            st.success(f"🎓 **Roll Number:** {result['roll_no']}")
            st.balloons()
            
            # Show success message and auto-refresh after 3 seconds
            with st.empty():
                st.info("🔄 Refreshing page in 3 seconds...")
                import time
                time.sleep(3)
            st.rerun()
        else:
            error_msg = response.json().get("detail", "QR code scanning failed")
            st.error(f"❌ {error_msg}")
            st.error("💡 **Try again with:**")
            st.error("   • Clear QR code image")
            st.error("   • Good lighting")
            st.error("   • Hold camera steady")
            
    except requests.exceptions.RequestException:
        st.error("❌ Could not connect to server")
        st.error("💡 Please check if the API server is running")

if __name__ == "__main__":
    main()