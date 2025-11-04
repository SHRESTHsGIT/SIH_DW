## services/ai_service.py
from groq import Groq
from dotenv import load_dotenv
import json
import os

load_dotenv()

class AIService:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables. Please set it in .env file")
        
        self.client = Groq(api_key=api_key)
        self.model = "openai/gpt-oss-120b"  # KEPT ORIGINAL MODEL
    
    def generate_roadmap(self, topic: str, experience_level: str = "beginner", 
                        hours_per_week: int = 5, user_input: str = "") -> dict:
        """Generate learning roadmap with user's detailed input"""
        
        user_context = f"\n\nStudent's specific needs/goals:\n{user_input}" if user_input else ""
        
        prompt = f"""You are an expert learning path designer. Create a structured, personalized learning roadmap for: {topic}

Student context:
- Current level: {experience_level}
- Available time: {hours_per_week} hours/week{user_context}

IMPORTANT: Create a UNIQUE roadmap based on the student's specific situation. Don't use generic templates.

Generate a phase-by-phase roadmap with:
1. Realistic timelines based on available time
2. 3-5 specific, actionable topics per phase
3. Clear progression from basics to advanced

CRITICAL: Return ONLY valid JSON, no other text:
{{
    "title": "{topic} Roadmap",
    "phases": [
        {{
            "name": "Phase 1: [Descriptive Name]",
            "duration": "[X weeks/months]",
            "topics": [
                {{"name": "Specific Topic 1", "completed": false}},
                {{"name": "Specific Topic 2", "completed": false}}
            ]
        }}
    ]
}}"""

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.9,
                max_completion_tokens=2500,
                top_p=0.95,
                stream=True,
                stop=None
            )
            
            full_response = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
            
            content = full_response.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            return json.loads(content)
        except Exception as e:
            print(f"Error generating roadmap: {e}")
            return self._get_default_roadmap(topic)
    
    def generate_exercise_plan(self, profile: dict, user_input: str = "") -> dict:
        """Generate personalized exercise plan with user's specific needs"""
        
        fitness_goals = profile.get('fitness_goals', [])
        if isinstance(fitness_goals, list):
            fitness_goal = ", ".join(fitness_goals) if fitness_goals else "Stay fit"
        else:
            fitness_goal = str(fitness_goals)
        
        weight = profile.get('weight', 65)
        height = profile.get('height', 170)
        diet_type = profile.get('diet_type', 'Vegetarian')
        experience = profile.get('exercise_frequency', 'Beginner')
        time_available = profile.get('exercise_time', '30-45 min')
        
        user_context = f"\n\nStudent's specific situation/constraints:\n{user_input}" if user_input else ""
        
        prompt = f"""You are a certified fitness trainer. Create a PERSONALIZED weekly workout plan for an Indian college student.

Student Profile:
- Height: {height} cm
- Weight: {weight} kg
- Goals: {fitness_goal}
- Experience: {experience}
- Time: {time_available} per day
- Diet: {diet_type} (adjust protein recommendations accordingly){user_context}

IMPORTANT RULES:
1. Create a UNIQUE plan - don't repeat same exercises
2. Consider the student's diet type for nutrition advice
3. Be specific with exercises (not just generic names)
4. Include proper warm-up/cool-down
5. Account for equipment availability in college gyms
6. Provide {diet_type}-specific protein sources

CRITICAL: Return ONLY valid JSON:
{{
    "weekly_plan": {{
        "Monday": {{"focus": "Body Part/Type", "exercises": ["Specific Exercise 1 Sets×Reps", "..."], "duration": "XX min"}},
        "Tuesday": {{"focus": "...", "exercises": ["..."], "duration": "..."}},
        "Wednesday": {{"focus": "...", "exercises": ["..."], "duration": "..."}},
        "Thursday": {{"focus": "...", "exercises": ["..."], "duration": "..."}},
        "Friday": {{"focus": "...", "exercises": ["..."], "duration": "..."}},
        "Saturday": {{"focus": "...", "exercises": ["..."], "duration": "..."}},
        "Sunday": {{"focus": "Rest/Active Recovery", "exercises": ["Light activity"], "duration": "..."}}
    }},
    "nutrition": {{
        "daily_protein": "{int(weight * 1.6)}g",
        "daily_calories": "[appropriate for goal]",
        "daily_water": "3-4L",
        "meal_tips": ["Tip 1 specific to {diet_type}", "Tip 2", "Tip 3", "Tip 4"]
    }}
}}

NOTE: For vegetarian - focus on dal, paneer, milk, curd, nuts
      For non-vegetarian - also include eggs, chicken"""

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.85,
                max_completion_tokens=2500,
                top_p=0.95,
                stream=True,
                stop=None
            )
            
            full_response = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
            
            content = full_response.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            return json.loads(content)
        except Exception as e:
            print(f"Error generating exercise plan: {e}")
            return self._get_default_exercise_plan(profile)
    
    def generate_daily_nutrition_tip(self, profile: dict, today_workout: str) -> str:
        """Generate daily nutrition advice"""
        
        fitness_goals = profile.get('fitness_goals', [])
        if isinstance(fitness_goals, list):
            fitness_goal = ", ".join(fitness_goals) if fitness_goals else "Stay fit"
        else:
            fitness_goal = str(fitness_goals)
        
        weight = profile.get('weight', 65)
        diet_type = profile.get('diet_type', 'Vegetarian')
        protein_target = int(weight * 1.6)
        
        prompt = f"""You are a nutrition expert. Give brief Indian college mess food advice (100-150 words).

Student: Weight {weight}kg, Goal: {fitness_goal}
Today's workout: {today_workout}
Diet type: {diet_type}
Protein target: {protein_target}g

Focus on:
- Protein sources from mess (dal, paneer, eggs, milk, curd) - match diet type
- What to prioritize and what to avoid
- Hydration (3L water target)
- Pre/post workout nutrition if applicable

Keep it simple, practical, and specific to TODAY's workout."""

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_completion_tokens=500,
                top_p=1,
                stream=True,
                stop=None
            )
            
            full_response = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
            
            return full_response.strip()
        except Exception as e:
            print(f"Error generating nutrition tip: {e}")
            return f"Aim for {protein_target}g protein today. Include dal, paneer from mess. Stay hydrated with 3L water. Good luck with your {today_workout} workout!"
    
    def generate_daily_todos(self, student_data: dict, profile: dict, timetable: list, 
                            roadmaps: list, exercise_plan: dict, reminders: list,
                            user_input: str = "") -> dict:
        """Generate comprehensive daily to-do list with user's additional input - returns JSON"""
        
        from datetime import datetime
        
        today = datetime.now().strftime("%A, %B %d, %Y")
        today_day = datetime.now().strftime("%A")
        
        # Build TODAY's timetable context (only today)
        timetable_text = f"TODAY ({today_day}) Schedule:\n"
        if timetable:
            for slot in timetable:
                if not slot.get('is_lunch'):
                    timetable_text += f"- {slot.get('time', '')} to {slot.get('end_time', '')}: {slot.get('subject', '')}\n"
        else:
            timetable_text += "No classes scheduled\n"
        
        # Build roadmap context - ONLY NEXT 2-3 UNCOMPLETED TASKS
        roadmap_text = ""
        if roadmaps:
            roadmap_text = "Pending Learning Tasks (pick 1-2 for today):\n"
            task_count = 0
            for rm in roadmaps[:2]:
                for phase in rm.get('phases', []):
                    for topic in phase.get('topics', []):
                        if not topic.get('completed', False) and task_count < 3:
                            roadmap_text += f"- {rm.get('title', '')}: {topic.get('name', '')}\n"
                            task_count += 1
                    if task_count >= 3:
                        break
                if task_count >= 3:
                    break
        
        # Build exercise context for TODAY only
        exercise_text = ""
        if exercise_plan:
            today_workout = exercise_plan.get('weekly_plan', {}).get(today_day, {})
            if today_workout and today_workout.get('focus', '') != 'Rest':
                exercise_text = f"Today's Workout:\n"
                exercise_text += f"- {today_workout.get('focus', '')} ({today_workout.get('duration', '')})\n"
                exercises = today_workout.get('exercises', [])[:3]
                if exercises:
                    exercise_text += f"- Exercises: {', '.join(exercises)}\n"
        
        # Build reminders for TODAY
        reminders_text = ""
        if reminders:
            reminders_text = "URGENT Reminders:\n"
            for rem in reminders[:3]:
                priority = rem.get('priority', 'Medium')
                reminders_text += f"- [{priority}] {rem.get('title', '')} at {rem.get('time', '')}\n"
        
        # Profile wellness targets - ADDED DIET TYPE HERE
        sleep_target = profile.get('sleep_hours', 7)
        water_goal = profile.get('water_intake', '3L')
        protein_target = profile.get('daily_protein_target', 80)
        social_limit = profile.get('social_media_limit', 30)
        meditation_freq = profile.get('meditation_frequency', 'Sometimes')
        diet_type = profile.get('diet_type', 'Vegetarian')  # ✅ ADDED THIS
        
        # Check if student spends too much time on social media
        screen_time = profile.get('screen_time_hours', 4)
        social_warning = ""
        if screen_time > 4:
            social_warning = f"\n⚠️ IMPORTANT: You spend {screen_time}hrs on screens. Today, STRICTLY limit social media to {social_limit} minutes!"
        
        user_context = f"\n\nStudent's Additional Notes:\n{user_input}" if user_input else ""
        
        # ✅ UPDATED PROMPT WITH DIET TYPE
        prompt = f"""You are a personal productivity assistant. Generate a REALISTIC, BALANCED daily to-do list for TODAY.

DATE: {today}
STUDENT: {student_data.get('name', 'Student')}{social_warning}

WELLNESS TARGETS:
- Sleep: {sleep_target}h | Water: {water_goal} | Protein: {protein_target}g
- Diet Type: {diet_type} | Social Media Limit: {social_limit} min | Meditation: {meditation_freq}

{timetable_text}

{roadmap_text}

{exercise_text}

{reminders_text}{user_context}

RULES:
1. Be REALISTIC - don't overload (max 10-12 tasks total)
2. Include specific times from timetable
3. Add meditation if frequency is Daily/Sometimes
4. ENFORCE social media limit if screen time > 4hrs
5. Include sleep reminder
6. Add 1-2 learning tasks from roadmap (30-60 min max)
7. Include HIGH PRIORITY reminders
8. Add specific nutrition targets based on {diet_type} diet
9. Balance study/fitness/wellness
10. For food recommendations: STRICTLY use dal/paneer/milk/curd for Vegetarian, add eggs/chicken ONLY for Non-vegetarian

CRITICAL: Return ONLY valid JSON, no other text. Format:
{{
    "todos": [
        {{
            "category": "🌅 Morning Routine",
            "tasks": [
                {{"task": "Wake up by 7:00 AM", "completed": false}},
                {{"task": "15-min meditation", "completed": false}},
                {{"task": "Breakfast + {protein_target//4}g protein (dal/paneer for veg, eggs for non-veg)", "completed": false}}
            ]
        }},
        {{
            "category": "📚 Academic",
            "tasks": [
                {{"task": "Attend class at TIME", "completed": false}}
            ]
        }},
        {{
            "category": "🎯 Learning",
            "tasks": [
                {{"task": "Roadmap task (30 min)", "completed": false}}
            ]
        }},
        {{
            "category": "💪 Fitness",
            "tasks": [
                {{"task": "Workout details", "completed": false}},
                {{"task": "Post-workout protein ({diet_type}-appropriate source)", "completed": false}}
            ]
        }},
        {{
            "category": "🌙 Evening Routine",
            "tasks": [
                {{"task": "Dinner + {protein_target//3}g protein ({diet_type} sources)", "completed": false}},
                {{"task": "Social media max {social_limit} min", "completed": false}},
                {{"task": "Sleep by 11:00 PM", "completed": false}}
            ]
        }}
    ]
}}"""

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_completion_tokens=2000,
                top_p=0.95,
                stream=True,
                stop=None
            )
            
            full_response = ""
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
            
            # Extract JSON from response
            content = full_response.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            result = json.loads(content)
            return result.get('todos', [])
            
        except Exception as e:
            print(f"Error generating daily todos: {e}")
            import traceback
            traceback.print_exc()
            return self._get_default_todos_list(profile)
    
    def _get_default_roadmap(self, topic: str) -> dict:
        """Fallback roadmap"""
        return {
            "title": f"{topic} Roadmap",
            "phases": [
                {
                    "name": "Fundamentals",
                    "duration": "2-3 months",
                    "topics": [
                        {"name": "Basic Concepts", "completed": False},
                        {"name": "Core Theory", "completed": False},
                        {"name": "Practical Basics", "completed": False}
                    ]
                }
            ]
        }
    
    def _get_default_exercise_plan(self, profile: dict) -> dict:
        """Fallback exercise plan"""
        protein_target = f"{int(profile.get('weight', 65) * 1.6)}g"
        diet_type = profile.get('diet_type', 'Vegetarian')
        
        # Adjust meal tips based on diet type
        if diet_type == 'Vegetarian':
            meal_tips = ["Include dal daily", "Paneer for protein", "Milk and curd", "Avoid fried snacks"]
        else:
            meal_tips = ["Include dal daily", "Eggs for protein", "Chicken/fish when available", "Avoid fried snacks"]
        
        return {
            "weekly_plan": {
                "Monday": {"focus": "Upper Body", "exercises": ["Push-ups 3x15", "Dips 3x10"], "duration": "30 min"},
                "Tuesday": {"focus": "Lower Body", "exercises": ["Squats 3x15", "Lunges 3x12"], "duration": "30 min"},
                "Wednesday": {"focus": "Cardio", "exercises": ["Running 20 min"], "duration": "30 min"},
                "Thursday": {"focus": "Upper Body", "exercises": ["Pull-ups 3x8", "Rows 3x12"], "duration": "30 min"},
                "Friday": {"focus": "Core", "exercises": ["Planks 3x60s", "Crunches 3x20"], "duration": "30 min"},
                "Saturday": {"focus": "Full Body", "exercises": ["Burpees 3x10", "Jumping Jacks 3x30"], "duration": "30 min"},
                "Sunday": {"focus": "Rest", "exercises": ["Light stretching"], "duration": "20 min"}
            },
            "nutrition": {
                "daily_protein": protein_target,
                "daily_calories": "2200-2400",
                "daily_water": "3L",
                "meal_tips": meal_tips
            }
        }
    
    def _get_default_todos_list(self, profile: dict) -> list:
        """Fallback to-do list as structured list"""
        protein = profile.get('daily_protein_target', 80)
        water = profile.get('water_intake', '3L')
        sleep = profile.get('sleep_hours', 7)
        diet_type = profile.get('diet_type', 'Vegetarian')
        
        # Adjust protein sources based on diet type
        if diet_type == 'Vegetarian':
            breakfast_protein = "dal/paneer/milk"
            dinner_protein = "dal/paneer/curd"
        else:
            breakfast_protein = "eggs/dal/milk"
            dinner_protein = "chicken/dal/paneer"
        
        return [
            {
                "category": "🌅 Morning Routine",
                "tasks": [
                    {"task": "Wake up by 7:00 AM", "completed": False},
                    {"task": "15-min meditation", "completed": False},
                    {"task": f"Breakfast + {int(protein * 0.25)}g protein ({breakfast_protein})", "completed": False}
                ]
            },
            {
                "category": "📚 Academic",
                "tasks": [
                    {"task": "Attend scheduled classes", "completed": False},
                    {"task": "Review class notes (30 min)", "completed": False}
                ]
            },
            {
                "category": "💪 Fitness",
                "tasks": [
                    {"task": "45-min workout", "completed": False},
                    {"task": f"Post-workout protein ({breakfast_protein})", "completed": False}
                ]
            },
            {
                "category": "🌙 Evening Routine",
                "tasks": [
                    {"task": f"Dinner + {int(protein * 0.35)}g protein ({dinner_protein})", "completed": False},
                    {"task": "Social media max 30 min", "completed": False},
                    {"task": f"Sleep by 11:00 PM (Target: {sleep}h)", "completed": False}
                ]
            },
            {
                "category": "💧 Daily Targets",
                "tasks": [
                    {"task": f"Water: {water}", "completed": False},
                    {"task": f"Protein: {protein}g ({diet_type} sources)", "completed": False}
                ]
            }
        ]