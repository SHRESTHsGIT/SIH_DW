## services/timetable_service.py
import pandas as pd
import os
from datetime import datetime
from typing import Dict, List

class TimetableService:
    def __init__(self):
        # Use absolute path to ensure correct location
        self.base_dir = os.path.abspath("data")
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.time_slots = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]
    
    def get_today_schedule(self, branch_code: str, year: str) -> List[Dict]:
        """Get today's class schedule"""
        try:
            timetable_path = os.path.join(self.base_dir, "branches", branch_code, year, "timetable.xlsx")
            
            print(f"🔍 Looking for timetable at: {timetable_path}")
            
            if not os.path.exists(timetable_path):
                print(f"❌ Timetable not found: {timetable_path}")
                return []
            
            print(f"✅ Timetable found!")
            
            # Read Excel file
            df = pd.read_excel(timetable_path, engine='openpyxl')
            
            # Get current day
            today = datetime.now().strftime("%A")  # Monday, Tuesday, etc.
            
            print(f"📅 Today is: {today}")
            print(f"📊 Columns in Excel: {df.columns.tolist()}")
            
            # Find today's column - column names are numbers 8-17 (time slots)
            # First column is day name
            schedule = []
            current_time = datetime.now().time()
            
            # Find the row for today
            today_row = df[df.iloc[:, 0] == today]
            
            if today_row.empty:
                print(f"❌ No schedule found for {today}")
                return []
            
            print(f"✅ Found schedule for {today}")
            
            # Parse the schedule row
            # Columns: 0=Day, 1-10 are time slots (8am to 5pm)
            time_mapping = {
                1: "08:00",  # 8 AM
                2: "09:00",  # 9 AM
                3: "10:00",  # 10 AM
                4: "11:00",  # 11 AM
                5: "12:00",  # 12 PM
                6: "13:00",  # 1 PM (Lunch)
                7: "14:00",  # 2 PM
                8: "15:00",  # 3 PM
                9: "16:00",  # 4 PM
                10: "17:00"  # 5 PM
            }
            
            for col_idx, start_time in time_mapping.items():
                try:
                    subject = today_row.iloc[0, col_idx]
                    
                    # Skip if NaN or empty
                    if pd.isna(subject) or str(subject).strip() == '' or str(subject).strip().lower() == 'nan':
                        continue
                    
                    subject = str(subject).strip()
                    
                    # Clean subject name
                    if "Refer below" in subject:
                        subject = subject.replace("Refer below", "").strip()
                    
                    # Skip if still empty
                    if not subject:
                        continue
                    
                    # Check if it's lunch
                    is_lunch = "lunch" in subject.lower()
                    
                    # Determine status (current, upcoming, past)
                    hour = int(start_time.split(':')[0])
                    current_hour = current_time.hour
                    
                    if hour == current_hour:
                        status = "current"
                    elif hour > current_hour:
                        status = "upcoming"
                    else:
                        status = "past"
                    
                    # Handle lab sessions (usually 3-4 hours)
                    if "Lab" in subject or "A1" in subject:
                        end_time = f"{hour+3:02d}:00"
                    else:
                        end_time = f"{hour+1:02d}:00"
                    
                    schedule.append({
                        "time": start_time,
                        "end_time": end_time,
                        "subject": subject,
                        "status": status,
                        "is_lunch": is_lunch
                    })
                    
                    print(f"   ✅ {start_time}: {subject}")
                    
                except Exception as e:
                    print(f"   ⚠️ Error reading column {col_idx}: {e}")
                    continue
            
            print(f"📋 Total classes found: {len(schedule)}")
            return schedule
            
        except Exception as e:
            print(f"❌ Error reading timetable: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_week_schedule(self, branch_code: str, year: str) -> Dict:
        """Get full week schedule"""
        try:
            timetable_path = os.path.join(self.base_dir, "branches", branch_code, year, "timetable.xlsx")
            
            if not os.path.exists(timetable_path):
                print(f"❌ Timetable not found: {timetable_path}")
                return {}
            
            df = pd.read_excel(timetable_path, engine='openpyxl')
            
            week_schedule = {}
            
            time_mapping = {
                1: "08:00",
                2: "09:00",
                3: "10:00",
                4: "11:00",
                5: "12:00",
                6: "13:00",
                7: "14:00",
                8: "15:00",
                9: "16:00",
                10: "17:00"
            }
            
            for day in self.days:
                day_row = df[df.iloc[:, 0] == day]
                
                if day_row.empty:
                    week_schedule[day] = []
                    continue
                
                day_schedule = []
                
                for col_idx, start_time in time_mapping.items():
                    try:
                        subject = day_row.iloc[0, col_idx]
                        
                        if pd.isna(subject) or str(subject).strip() == '' or str(subject).strip().lower() == 'nan':
                            continue
                        
                        subject = str(subject).strip()
                        
                        if "Refer below" in subject:
                            subject = subject.replace("Refer below", "").strip()
                        
                        if not subject:
                            continue
                        
                        day_schedule.append({
                            "time": start_time,
                            "subject": subject
                        })
                    except:
                        continue
                
                week_schedule[day] = day_schedule
            
            return week_schedule
            
        except Exception as e:
            print(f"❌ Error reading week schedule: {e}")
            return {}