## services/wellness_service.py
import json
import os
from datetime import datetime
from typing import Dict, List
from services.ai_service import AIService
from services.timetable_service import TimetableService

class WellnessService:
    def __init__(self):
        # Use absolute path
        self.base_dir = os.path.abspath("data")
        self.ai_service = AIService()
        self.timetable_service = TimetableService()
    
    def get_student_profile_path(self, roll_no: str, branch: str, year: str) -> str:
        """Get path to student's personal assistant data"""
        pa_dir = os.path.join(self.base_dir, "branches", branch, year, "personal_assistant", roll_no)
        os.makedirs(pa_dir, exist_ok=True)
        return pa_dir
    
    def save_student_profile(self, roll_no: str, branch: str, year: str, profile_data: dict):
        """Save student wellness profile"""
        pa_dir = self.get_student_profile_path(roll_no, branch, year)
        profile_path = os.path.join(pa_dir, "profile.json")
        
        with open(profile_path, 'w') as f:
            json.dump(profile_data, f, indent=2)
    
    def load_student_profile(self, roll_no: str, branch: str, year: str) -> dict:
        """Load student wellness profile"""
        pa_dir = self.get_student_profile_path(roll_no, branch, year)
        profile_path = os.path.join(pa_dir, "profile.json")
        
        if os.path.exists(profile_path):
            with open(profile_path, 'r') as f:
                return json.load(f)
        return None
    
    def save_roadmaps(self, roll_no: str, branch: str, year: str, roadmaps: list):
        """Save student roadmaps"""
        pa_dir = self.get_student_profile_path(roll_no, branch, year)
        roadmaps_path = os.path.join(pa_dir, "roadmaps.json")
        
        with open(roadmaps_path, 'w') as f:
            json.dump(roadmaps, f, indent=2)
    
    def load_roadmaps(self, roll_no: str, branch: str, year: str) -> list:
        """Load student roadmaps"""
        pa_dir = self.get_student_profile_path(roll_no, branch, year)
        roadmaps_path = os.path.join(pa_dir, "roadmaps.json")
        
        if os.path.exists(roadmaps_path):
            with open(roadmaps_path, 'r') as f:
                return json.load(f)
        return []
    
    def save_exercise_plan(self, roll_no: str, branch: str, year: str, plan: dict):
        """Save exercise plan"""
        pa_dir = self.get_student_profile_path(roll_no, branch, year)
        plan_path = os.path.join(pa_dir, "exercise_plan.json")
        
        if plan is None:
            if os.path.exists(plan_path):
                os.remove(plan_path)
            return
        
        with open(plan_path, 'w') as f:
            json.dump(plan, f, indent=2)
    
    def load_exercise_plan(self, roll_no: str, branch: str, year: str) -> dict:
        """Load exercise plan"""
        pa_dir = self.get_student_profile_path(roll_no, branch, year)
        plan_path = os.path.join(pa_dir, "exercise_plan.json")
        
        if os.path.exists(plan_path):
            with open(plan_path, 'r') as f:
                return json.load(f)
        return None
    
    def save_reminders(self, roll_no: str, branch: str, year: str, reminders: list):
        """Save reminders"""
        pa_dir = self.get_student_profile_path(roll_no, branch, year)
        reminders_path = os.path.join(pa_dir, "reminders.json")
        
        with open(reminders_path, 'w') as f:
            json.dump(reminders, f, indent=2)
    
    def load_reminders(self, roll_no: str, branch: str, year: str) -> list:
        """Load reminders"""
        pa_dir = self.get_student_profile_path(roll_no, branch, year)
        reminders_path = os.path.join(pa_dir, "reminders.json")
        
        if os.path.exists(reminders_path):
            with open(reminders_path, 'r') as f:
                return json.load(f)
        return []
    
    def get_today_reminders(self, roll_no: str, branch: str, year: str) -> list:
        """Get today's reminders"""
        all_reminders = self.load_reminders(roll_no, branch, year)
        today = datetime.now().strftime("%Y-%m-%d")
        
        return [r for r in all_reminders if r.get('date') == today and not r.get('completed', False)]
    
    def save_daily_todos(self, roll_no: str, branch: str, year: str, todos: dict):
        """Save today's generated todos to JSON file"""
        pa_dir = self.get_student_profile_path(roll_no, branch, year)
        todos_path = os.path.join(pa_dir, "daily_todos.json")
        
        # Add generation metadata
        todos_with_meta = {
            "generated_on": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "todos": todos
        }
        
        with open(todos_path, 'w') as f:
            json.dump(todos_with_meta, f, indent=2)
        
        print(f"✅ Daily todos saved to: {todos_path}")
    
    def load_daily_todos(self, roll_no: str, branch: str, year: str) -> dict:
        """Load today's todos if they exist and are from today"""
        pa_dir = self.get_student_profile_path(roll_no, branch, year)
        todos_path = os.path.join(pa_dir, "daily_todos.json")
        
        if os.path.exists(todos_path):
            with open(todos_path, 'r') as f:
                saved_todos = json.load(f)
            
            # Check if todos are from today
            today = datetime.now().strftime("%Y-%m-%d")
            if saved_todos.get('date') == today:
                return saved_todos.get('todos', [])
        
        return None
    
    def generate_and_save_daily_todos(self, roll_no: str, branch: str, year: str, user_input: str = "") -> List[Dict]:
        """Generate daily to-do list and save to JSON"""
        
        try:
            # Gather all data
            profile = self.load_student_profile(roll_no, branch, year)
            if not profile:
                return self._get_basic_todos()
            
            roadmaps = self.load_roadmaps(roll_no, branch, year)
            exercise_plan = self.load_exercise_plan(roll_no, branch, year)
            today_reminders = self.get_today_reminders(roll_no, branch, year)
            today_schedule = self.timetable_service.get_today_schedule(branch, year)
            
            student_data = {
                'roll_no': roll_no,
                'name': profile.get('name', roll_no),
                'branch': branch,
                'year': year
            }
            
            # Generate AI-powered todos (now returns JSON list directly)
            todos = self.ai_service.generate_daily_todos(
                student_data=student_data,
                profile=profile,
                timetable=today_schedule,
                roadmaps=roadmaps,
                exercise_plan=exercise_plan,
                reminders=today_reminders,
                user_input=user_input
            )
            
            # Save to JSON file
            self.save_daily_todos(roll_no, branch, year, todos)
            
            return todos
            
        except Exception as e:
            print(f"❌ Error generating AI todos: {e}")
            import traceback
            traceback.print_exc()
            return self._get_basic_todos(profile if 'profile' in locals() else None)
    
    def get_daily_todos(self, roll_no: str, branch: str, year: str) -> List[Dict]:
        """Get today's todos - load from file if exists, otherwise show message"""
        # Try to load existing todos for today
        todos = self.load_daily_todos(roll_no, branch, year)
        
        if todos:
            return todos
        else:
            # Return placeholder message
            return [{
                "category": "📋 Generate Today's To-Do List",
                "tasks": [{
                    "task": "Click 'Generate Today's To-Do List' button above to create personalized tasks",
                    "completed": False
                }]
            }]
    
    def _get_basic_todos(self, profile: dict = None) -> List[Dict]:
        """Fallback basic to-do list"""
        if not profile:
            profile = {
                'sleep_hours': 7,
                'daily_protein_target': 80,
                'water_intake': '3L',
                'social_media_limit': 30
            }
        
        return [
            {
                "category": "🌅 Morning Routine",
                "tasks": [
                    {"task": "Wake up by 7:00 AM", "completed": False},
                    {"task": "15-min meditation", "completed": False},
                    {"task": f"Breakfast + {profile.get('daily_protein_target', 80) // 4}g protein", "completed": False}
                ]
            },
            {
                "category": "📚 Academic Tasks",
                "tasks": [
                    {"task": "Attend scheduled classes", "completed": False},
                    {"task": "Review today's notes (30 min)", "completed": False}
                ]
            },
            {
                "category": "💪 Fitness",
                "tasks": [
                    {"task": "45-min workout", "completed": False},
                    {"task": "Post-workout protein", "completed": False}
                ]
            },
            {
                "category": "🌙 Evening Routine",
                "tasks": [
                    {"task": f"Social media max {profile.get('social_media_limit', 30)} min", "completed": False},
                    {"task": "Sleep by 11:00 PM", "completed": False}
                ]
            }
        ]
    
    def calculate_wellness_score(self, profile: dict) -> int:
        """Calculate wellness score 0-100"""
        score = 0
        
        # Sleep (25 points)
        sleep_hours = profile.get('sleep_hours', 6)
        if sleep_hours >= 7:
            score += 25
        elif sleep_hours >= 6:
            score += 15
        else:
            score += 5
        
        # Exercise (25 points)
        exercise_freq = profile.get('exercise_frequency', 'Rarely')
        if exercise_freq == 'Daily':
            score += 25
        elif exercise_freq == '3-4 times/week':
            score += 20
        elif exercise_freq == '1-2 times/week':
            score += 10
        
        # Screen time (25 points)
        screen_time = profile.get('screen_time_hours', 6)
        if screen_time <= 2:
            score += 25
        elif screen_time <= 4:
            score += 15
        elif screen_time <= 6:
            score += 10
        else:
            score += 5
        
        # Meditation (15 points)
        meditation = profile.get('meditation_frequency', 'Never')
        if meditation == 'Daily':
            score += 15
        elif meditation == 'Sometimes':
            score += 10
        elif meditation == 'Rarely':
            score += 5
        
        # Nutrition (10 points)
        if profile.get('tracks_protein'):
            score += 10
        else:
            score += 5
        
        return min(score, 100)