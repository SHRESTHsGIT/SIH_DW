## teacher_app.py

import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import time

# Configure Streamlit
st.set_page_config(
    page_title="Teacher Dashboard - Attendance System",
    page_icon="👨‍🏫",
    layout="wide"
)

API_BASE_URL = "http://localhost:8000"

def main():
    st.title("👨‍🏫 Teacher Dashboard - Face Recognition Attendance System")
    
    # Session state initialization
    if 'teacher_logged_in' not in st.session_state:
        st.session_state.teacher_logged_in = False
    if 'teacher_id' not in st.session_state:
        st.session_state.teacher_id = None
    if 'current_session' not in st.session_state:
        st.session_state.current_session = None
    
    # Login form
    if not st.session_state.teacher_logged_in:
        show_login()
    else:
        show_dashboard()

def show_login():
    st.markdown("### 🔐 Teacher Login")
    
    with st.form("login_form"):
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            teacher_id = st.text_input("Teacher ID", placeholder="e.g., T001")
            password = st.text_input("Password", type="password")
            submit_button = st.form_submit_button("Login", use_container_width=True)
        
        if submit_button:
            if teacher_id and password:
                try:
                    response = requests.post(f"{API_BASE_URL}/api/teacher/login", 
                                           json={"teacher_id": teacher_id, "password": password})
                    
                    if response.status_code == 200:
                        st.session_state.teacher_logged_in = True
                        st.session_state.teacher_id = teacher_id
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials!")
                        
                except requests.exceptions.RequestException:
                    st.error("❌ Could not connect to server. Please ensure the API is running.")
            else:
                st.warning("⚠️ Please enter both Teacher ID and Password")

def show_dashboard():
    # Header with logout
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"### Welcome, {st.session_state.teacher_id}")
    with col2:
        if st.button("Logout", type="secondary"):
            st.session_state.teacher_logged_in = False
            st.session_state.teacher_id = None
            st.session_state.current_session = None
            st.rerun()
    
    st.divider()
    
    # Main dashboard tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📅 Session Management", "👥 Current Session", "📊 Statistics", "📋 Attendance Records"])
    
    with tab1:
        show_session_management()
    
    with tab2:
        show_current_session()
    
    with tab3:
        show_statistics()
    
    with tab4:
        show_attendance_records()

def show_session_management():
    st.markdown("### 📅 Start New Attendance Session")
    
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
    
    with st.form("start_session_form"):
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            branch_options = [f"{b['branch_code']} - {b['branch_name']}" for b in branches]
            selected_branch = st.selectbox("Select Branch", branch_options)
            branch_code = selected_branch.split(" - ")[0] if selected_branch else ""
        
        with col2:
            year = st.selectbox("Select Year", ["2022", "2023", "2024", "2025"], index=2)
        
        with col3:
            duration = st.number_input("Duration (minutes)", min_value=10, max_value=180, value=60)
        
        start_button = st.form_submit_button("🚀 Start Session", use_container_width=True)
        
        if start_button and branch_code:
            try:
                response = requests.post(f"{API_BASE_URL}/api/sessions/start", 
                                       json={
                                           "teacher_id": st.session_state.teacher_id,
                                           "branch_code": branch_code,
                                           "year": year,
                                           "duration_minutes": duration
                                       })
                
                if response.status_code == 200:
                    session_data = response.json()
                    st.session_state.current_session = {
                        "session_id": session_data["session_id"],
                        "branch_code": branch_code,
                        "year": year
                    }
                    st.success(f"✅ Session started successfully! Session ID: {session_data['session_id']}")
                else:
                    error_msg = response.json().get("detail", "Failed to start session")
                    st.error(f"❌ {error_msg}")
                    
            except requests.exceptions.RequestException:
                st.error("❌ Could not connect to server")

def show_current_session():
    st.markdown("### 👥 Current Active Session")
    
    if st.session_state.current_session:
        session = st.session_state.current_session
        
        # Session info
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Session ID", session["session_id"])
        with col2:
            st.metric("Branch", session["branch_code"])
        with col3:
            st.metric("Year", session["year"])
        with col4:
            if st.button("🔄 Refresh", type="secondary"):
                st.rerun()
        
        # Close session button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("❌ Close Session", type="primary", use_container_width=True):
                try:
                    response = requests.post(f"{API_BASE_URL}/api/sessions/{session['session_id']}/close",
                                           params={"branch_code": session["branch_code"], "year": session["year"]})
                    
                    if response.status_code == 200:
                        st.success("✅ Session closed successfully!")
                        st.session_state.current_session = None
                        st.rerun()
                    else:
                        st.error("❌ Failed to close session")
                        
                except requests.exceptions.RequestException:
                    st.error("❌ Could not connect to server")
        
        st.divider()
        
        # Get current attendance
        try:
            response = requests.get(f"{API_BASE_URL}/api/sessions/{session['session_id']}/attendance",
                                  params={"branch_code": session["branch_code"], "year": session["year"]})
            
            if response.status_code == 200:
                attendance_data = response.json()
                
                if attendance_data:
                    df = pd.DataFrame(attendance_data)
                    
                    # Summary metrics
                    total_students = len(df)
                    present_students = len(df[df['status'] == 'Present'])
                    absent_students = total_students - present_students
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Students", total_students)
                    with col2:
                        st.metric("Present", present_students, delta=f"{(present_students/total_students*100):.1f}%")
                    with col3:
                        st.metric("Absent", absent_students)
                    
                    # Attendance table
                    st.markdown("#### 📋 Real-time Attendance")
                    
                    # Style the dataframe
                    def style_attendance(val):
                        if val == 'Present':
                            return 'background-color: #d4edda; color: #155724'
                        elif val == 'Absent':
                            return 'background-color: #f8d7da; color: #721c24'
                        return ''
                    
                    styled_df = df.style.applymap(style_attendance, subset=['status'])
                    st.dataframe(styled_df, use_container_width=True, hide_index=True)
                    
                else:
                    st.info("No students registered for this branch-year")
                    
            else:
                st.error("Failed to fetch attendance data")
                
        except requests.exceptions.RequestException:
            st.error("Could not connect to server")
    
    else:
        st.info("No active session. Please start a session from the Session Management tab.")

def show_statistics():
    st.markdown("### 📊 Attendance Statistics")
    
    # Branch and year selection
    try:
        response = requests.get(f"{API_BASE_URL}/api/branches")
        if response.status_code == 200:
            branches = response.json()
        else:
            branches = []
    except:
        branches = []
    
    if not branches:
        st.warning("No branches available")
        return
    
    col1, col2 = st.columns(2)
    with col1:
        branch_options = [f"{b['branch_code']} - {b['branch_name']}" for b in branches]
        selected_branch = st.selectbox("Select Branch", branch_options, key="stats_branch")
        branch_code = selected_branch.split(" - ")[0] if selected_branch else ""
    
    with col2:
        year = st.selectbox("Select Year", ["2022", "2023", "2024", "2025"], index=2, key="stats_year")
    
    if branch_code:
        try:
            response = requests.get(f"{API_BASE_URL}/api/stats/{branch_code}/{year}")
            
            if response.status_code == 200:
                stats_data = response.json()
                
                if stats_data:
                    df = pd.DataFrame(stats_data)
                    
                    # Overall statistics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Students", len(df))
                    with col2:
                        avg_attendance = df['attendance_pct'].mean() if not df.empty else 0
                        st.metric("Average Attendance", f"{avg_attendance:.1f}%")
                    with col3:
                        total_present = df['present_days'].sum() if not df.empty else 0
                        st.metric("Total Present Days", total_present)
                    with col4:
                        total_absent = df['absent_days'].sum() if not df.empty else 0
                        st.metric("Total Absent Days", total_absent)
                    
                    st.divider()
                    
                    # Detailed statistics table
                    st.markdown("#### 📋 Detailed Statistics")
                    
                    # Sort by attendance percentage (descending)
                    df_sorted = df.sort_values('attendance_pct', ascending=False)
                    
                    # Format the dataframe
                    df_display = df_sorted[['roll_no', 'name', 'present_days', 'absent_days', 'total_days', 'attendance_pct', 'last_present', 'last_absent']].copy()
                    df_display['attendance_pct'] = df_display['attendance_pct'].apply(lambda x: f"{x:.1f}%")
                    
                    st.dataframe(df_display, use_container_width=True, hide_index=True)
                    
                    # Attendance distribution chart
                    st.markdown("#### 📈 Attendance Distribution")
                    attendance_ranges = ["90-100%", "80-89%", "70-79%", "60-69%", "Below 60%"]
                    counts = [
                        len(df[df['attendance_pct'] >= 90]),
                        len(df[(df['attendance_pct'] >= 80) & (df['attendance_pct'] < 90)]),
                        len(df[(df['attendance_pct'] >= 70) & (df['attendance_pct'] < 80)]),
                        len(df[(df['attendance_pct'] >= 60) & (df['attendance_pct'] < 70)]),
                        len(df[df['attendance_pct'] < 60])
                    ]
                    
                    chart_df = pd.DataFrame({
                        'Attendance Range': attendance_ranges,
                        'Number of Students': counts
                    })
                    
                    st.bar_chart(chart_df.set_index('Attendance Range'))
                    
                else:
                    st.info("No statistics available for this branch-year")
                    
            else:
                st.error("Failed to fetch statistics")
                
        except requests.exceptions.RequestException:
            st.error("Could not connect to server")

def show_attendance_records():
    st.markdown("### 📋 Attendance Records")
    
    # Branch and year selection
    try:
        response = requests.get(f"{API_BASE_URL}/api/branches")
        if response.status_code == 200:
            branches = response.json()
        else:
            branches = []
    except:
        branches = []
    
    if not branches:
        st.warning("No branches available")
        return
    
    col1, col2 = st.columns(2)
    with col1:
        branch_options = [f"{b['branch_code']} - {b['branch_name']}" for b in branches]
        selected_branch = st.selectbox("Select Branch", branch_options, key="records_branch")
        branch_code = selected_branch.split(" - ")[0] if selected_branch else ""
    
    with col2:
        year = st.selectbox("Select Year", ["2022", "2023", "2024", "2025"], index=2, key="records_year")
    
    if branch_code:
        try:
            response = requests.get(f"{API_BASE_URL}/api/attendance/{branch_code}/{year}")
            
            if response.status_code == 200:
                attendance_data = response.json()
                
                if attendance_data:
                    df = pd.DataFrame(attendance_data)
                    
                    st.markdown("#### 📅 Daily Attendance Records")
                    st.info("Green = Present, Red = Absent, Gray = No Data")
                    
                    # Display attendance table
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    
                    # Download attendance data
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Attendance Data (CSV)",
                        data=csv,
                        file_name=f"attendance_{branch_code}_{year}_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                    
                else:
                    st.info("No attendance records available for this branch-year")
                    
            else:
                st.error("Failed to fetch attendance records")
                
        except requests.exceptions.RequestException:
            st.error("Could not connect to server")

if __name__ == "__main__":
    main()