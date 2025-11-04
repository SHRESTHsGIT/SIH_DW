## services/data_service.py

import pandas as pd
import os
from datetime import datetime
from typing import List, Dict, Optional

class DataService:
    def __init__(self):
        self.base_dir = "data"
    
    def get_branches(self) -> List[Dict]:
        """Get all available branches"""
        branches_path = os.path.join(self.base_dir, "branches.csv")
        if os.path.exists(branches_path):
            df = pd.read_csv(branches_path)
            return df.to_dict('records')
        return []
    
    def verify_teacher(self, teacher_id: str, password: str) -> bool:
        """Verify teacher credentials"""
        teachers_path = os.path.join(self.base_dir, "teachers.csv")
        if os.path.exists(teachers_path):
            df = pd.read_csv(teachers_path)
            teacher = df[(df['teacher_id'] == teacher_id) & (df['password'] == password)]
            return not teacher.empty
        return False
    
    def verify_student(self, roll_no: str, password: str) -> Optional[Dict]:
        """Verify student credentials and return student info"""
        # Extract branch and year from roll number (e.g., BT23CSH013)
        if len(roll_no) < 8:
            return None
        
        try:
            year = "20" + roll_no[2:4]  # BT23 -> 2023
            branch = roll_no[4:7]      # CSH
        except:
            return None
        
        students_path = os.path.join(self.base_dir, "branches", branch, year, "students.csv")
        if os.path.exists(students_path):
            df = pd.read_csv(students_path)
            student = df[(df['roll_no'] == roll_no) & (df['password'] == password)]
            if not student.empty:
                student_dict = student.iloc[0].to_dict()
                student_dict['branch'] = branch
                student_dict['year'] = year
                return student_dict
        return None
    
    def register_student(self, roll_no: str, name: str, password: str, branch_code: str) -> bool:
        """Register a new student"""
        # Extract year from roll number
        try:
            year = "20" + roll_no[2:4]
        except:
            return False
        
        students_path = os.path.join(self.base_dir, "branches", branch_code, year, "students.csv")
        
        # Check if student already exists
        if os.path.exists(students_path):
            df = pd.read_csv(students_path)
            if roll_no in df['roll_no'].values:
                return False
        else:
            df = pd.DataFrame(columns=["roll_no", "name", "face_path", "qr_code_path", "registered_on", "password"])
        
        # Add new student
        face_path = f"data/branches/{branch_code}/{year}/faces/{roll_no}.jpg"
        qr_path = f"data/branches/{branch_code}/{year}/qrcodes/{roll_no}.png"
        
        new_student = {
            "roll_no": roll_no,
            "name": name,
            "face_path": face_path,
            "qr_code_path": qr_path,
            "registered_on": datetime.now().strftime("%Y-%m-%d"),
            "password": password
        }
        
        df = pd.concat([df, pd.DataFrame([new_student])], ignore_index=True)
        df.to_csv(students_path, index=False)
        
        # Initialize in attendance.csv
        self._add_student_to_attendance(roll_no, name, branch_code, year)
        
        # Initialize in stats.csv
        self._add_student_to_stats(roll_no, name, branch_code, year)
        
        return True
    
    def _add_student_to_attendance(self, roll_no: str, name: str, branch_code: str, year: str):
        """Add student to attendance.csv"""
        attendance_path = os.path.join(self.base_dir, "branches", branch_code, year, "attendance.csv")
        
        if os.path.exists(attendance_path):
            df = pd.read_csv(attendance_path)
        else:
            df = pd.DataFrame(columns=["roll_no", "name"])
        
        if roll_no not in df['roll_no'].values:
            new_row = {"roll_no": roll_no, "name": name}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(attendance_path, index=False)
    
    def _add_student_to_stats(self, roll_no: str, name: str, branch_code: str, year: str):
        """Add student to stats.csv"""
        stats_path = os.path.join(self.base_dir, "branches", branch_code, year, "stats.csv")
        
        if os.path.exists(stats_path):
            df = pd.read_csv(stats_path)
        else:
            df = pd.DataFrame(columns=["roll_no", "name", "present_days", "absent_days", "total_days", "attendance_pct", "last_present", "last_absent"])
        
        if roll_no not in df['roll_no'].values:
            new_row = {
                "roll_no": roll_no,
                "name": name,
                "present_days": 0,
                "absent_days": 0,
                "total_days": 0,
                "attendance_pct": 0.0,
                "last_present": "",
                "last_absent": ""
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(stats_path, index=False)
    
    def get_students(self, branch_code: str, year: str) -> List[Dict]:
        """Get all students for a branch-year"""
        students_path = os.path.join(self.base_dir, "branches", branch_code, year, "students.csv")
        if os.path.exists(students_path):
            df = pd.read_csv(students_path)
            return df.to_dict('records')
        return []
    
    def mark_attendance(self, roll_no: str, branch_code: str, year: str, status: str = "Present") -> bool:
        """Mark attendance for a student"""
        attendance_path = os.path.join(self.base_dir, "branches", branch_code, year, "attendance.csv")
        today = datetime.now().strftime("%Y-%m-%d")
        
        if os.path.exists(attendance_path):
            df = pd.read_csv(attendance_path)
        else:
            return False
        
        # Add today's column if it doesn't exist
        if today not in df.columns:
            df[today] = "Absent"
        
        # Mark attendance
        if roll_no in df['roll_no'].values:
            df.loc[df['roll_no'] == roll_no, today] = status
            df.to_csv(attendance_path, index=False)
            
            # Update stats
            self._update_stats(roll_no, branch_code, year, status, today)
            return True
        
        return False
    
    def _update_stats(self, roll_no: str, branch_code: str, year: str, status: str, date: str):
        """Update student statistics"""
        stats_path = os.path.join(self.base_dir, "branches", branch_code, year, "stats.csv")
        
        if os.path.exists(stats_path):
            df = pd.read_csv(stats_path)
            
            if roll_no in df['roll_no'].values:
                idx = df[df['roll_no'] == roll_no].index[0]
                
                if status == "Present":
                    df.at[idx, 'present_days'] = df.at[idx, 'present_days'] + 1
                    df.at[idx, 'last_present'] = date
                else:
                    df.at[idx, 'absent_days'] = df.at[idx, 'absent_days'] + 1
                    df.at[idx, 'last_absent'] = date
                
                df.at[idx, 'total_days'] = df.at[idx, 'present_days'] + df.at[idx, 'absent_days']
                
                if df.at[idx, 'total_days'] > 0:
                    df.at[idx, 'attendance_pct'] = (df.at[idx, 'present_days'] / df.at[idx, 'total_days']) * 100
                
                df.to_csv(stats_path, index=False)
    
    def get_attendance_data(self, branch_code: str, year: str) -> Dict:
        """Get attendance data for a branch-year"""
        attendance_path = os.path.join(self.base_dir, "branches", branch_code, year, "attendance.csv")
        if os.path.exists(attendance_path):
            df = pd.read_csv(attendance_path)
            return df.to_dict('records')
        return []
    
    def get_stats_data(self, branch_code: str, year: str) -> Dict:
        """Get statistics data for a branch-year"""
        stats_path = os.path.join(self.base_dir, "branches", branch_code, year, "stats.csv")
        if os.path.exists(stats_path):
            df = pd.read_csv(stats_path)
            return df.to_dict('records')
        return []