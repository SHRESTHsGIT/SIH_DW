## services/session_service.py

import pandas as pd
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, List

class SessionService:
    def __init__(self):
        self.base_dir = "data"
    
    def start_session(self, teacher_id: str, branch_code: str, year: str, duration_minutes: int = 60) -> str:
        """Start a new attendance session"""
        # Check if there's already an active session
        active_session = self.get_active_session(branch_code, year)
        if active_session:
            return None  # Session already active
        
        # Generate session ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = f"SES_{timestamp}_{branch_code}_{year}"
        
        start_time = datetime.now()
        deadline_time = start_time + timedelta(minutes=duration_minutes)
        
        # Save session
        sessions_path = os.path.join(self.base_dir, "branches", branch_code, year, "sessions.csv")
        
        if os.path.exists(sessions_path):
            df = pd.read_csv(sessions_path)
        else:
            df = pd.DataFrame(columns=["session_id", "teacher_id", "branch_code", "year", "start_time", "deadline_time", "status"])
        
        new_session = {
            "session_id": session_id,
            "teacher_id": teacher_id,
            "branch_code": branch_code,
            "year": year,
            "start_time": start_time.isoformat(),
            "deadline_time": deadline_time.isoformat(),
            "status": "active"
        }
        
        df = pd.concat([df, pd.DataFrame([new_session])], ignore_index=True)
        df.to_csv(sessions_path, index=False)
        
        return session_id
    
    def get_active_session(self, branch_code: str, year: str) -> Optional[Dict]:
        """Get active session for a branch-year"""
        sessions_path = os.path.join(self.base_dir, "branches", branch_code, year, "sessions.csv")
        
        if not os.path.exists(sessions_path):
            return None
        
        df = pd.read_csv(sessions_path)
        active_sessions = df[df['status'] == 'active']
        
        if active_sessions.empty:
            return None
        
        # Check if session is still valid (not expired)
        for _, session in active_sessions.iterrows():
            deadline = datetime.fromisoformat(session['deadline_time'])
            if datetime.now() < deadline:
                return session.to_dict()
            else:
                # Session expired, close it
                self.close_session(session['session_id'], branch_code, year, auto_close=True)
        
        return None
    
    def close_session(self, session_id: str, branch_code: str, year: str, auto_close: bool = False):
        """Close a session and mark absent students"""
        sessions_path = os.path.join(self.base_dir, "branches", branch_code, year, "sessions.csv")
        
        if os.path.exists(sessions_path):
            df = pd.read_csv(sessions_path)
            df.loc[df['session_id'] == session_id, 'status'] = 'closed'
            df.to_csv(sessions_path, index=False)
            
            if auto_close:
                # Mark all unmarked students as absent
                self._mark_absent_students(branch_code, year)
    
    def _mark_absent_students(self, branch_code: str, year: str):
        """Mark students who didn't attend as absent"""
        from .data_service import DataService
        data_service = DataService()
        
        # Get all students
        students = data_service.get_students(branch_code, year)
        today = datetime.now().strftime("%Y-%m-%d")
        
        attendance_path = os.path.join(self.base_dir, "branches", branch_code, year, "attendance.csv")
        
        if os.path.exists(attendance_path):
            df = pd.read_csv(attendance_path)
            
            # Add today's column if it doesn't exist
            if today not in df.columns:
                df[today] = "Absent"
            
            # Mark all students who don't have attendance today as absent
            for student in students:
                roll_no = student['roll_no']
                if roll_no in df['roll_no'].values:
                    current_status = df.loc[df['roll_no'] == roll_no, today].iloc[0]
                    if pd.isna(current_status) or current_status == "":
                        data_service.mark_attendance(roll_no, branch_code, year, "Absent")
            
            df.to_csv(attendance_path, index=False)
    
    def get_session_attendance(self, session_id: str, branch_code: str, year: str) -> List[Dict]:
        """Get attendance for a specific session"""
        from .data_service import DataService
        data_service = DataService()
        
        today = datetime.now().strftime("%Y-%m-%d")
        attendance_data = data_service.get_attendance_data(branch_code, year)
        
        # Filter for today's attendance
        result = []
        for record in attendance_data:
            if today in record:
                result.append({
                    "roll_no": record["roll_no"],
                    "name": record["name"],
                    "status": record.get(today, "Absent")
                })
        
        return result