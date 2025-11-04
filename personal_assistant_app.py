## personal_assistant_app.py
import streamlit as st
import requests
from datetime import datetime
import json
from services.wellness_service import WellnessService
from services.ai_service import AIService
from services.timetable_service import TimetableService

# Configure page
st.set_page_config(
    page_title="Personal Assistant",
    page_icon="🤖",
    layout="wide"
)

API_BASE_URL = "http://localhost:8000"

# Initialize services
wellness_service = WellnessService()
ai_service = AIService()
timetable_service = TimetableService()

def main():
    st.title("🤖 Student Personal Assistant")
    
    # Session state
    if 'pa_logged_in' not in st.session_state:
        st.session_state.pa_logged_in = False
    if 'pa_student_data' not in st.session_state:
        st.session_state.pa_student_data = None
    
    # Auth
    if not st.session_state.pa_logged_in:
        show_auth()
    else:
        # Check if profile exists
        student = st.session_state.pa_student_data
        
        try:
            profile = wellness_service.load_student_profile(
                student['roll_no'],
                student['branch'],
                student['year']
            )
        except Exception as e:
            print(f"🔍 DEBUG: Profile load error: {e}")
            profile = None
        
        if not profile:
            show_onboarding()
        else:
            show_dashboard()

def show_auth():
    st.markdown("### 🔐 Login to Personal Assistant")
    
    tab1, tab2 = st.tabs(["Manual Login", "Face Recognition"])
    
    with tab1:
        with st.form("pa_login_form"):
            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col2:
                roll_no = st.text_input("Roll Number", placeholder="BT23CSH024")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit and roll_no and password:
                try:
                    response = requests.post(f"{API_BASE_URL}/api/student/login",
                                           json={"roll_no": roll_no.upper(), "password": password})
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.pa_logged_in = True
                        st.session_state.pa_student_data = data["student"]
                        st.success("✅ Login successful!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials!")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Could not connect to API server. Make sure it's running on port 8000")
                except Exception as e:
                    st.error(f"❌ Login error: {str(e)}")
    
    with tab2:
        st.info("Face recognition login coming soon!")

def show_onboarding():
    st.markdown("## 🎉 Welcome! Let's Set Up Your Personal Assistant")
    
    student = st.session_state.pa_student_data
    
    st.info("Answer these questions to personalize your experience")
    
    with st.form("onboarding_form"):
        st.markdown("### 📱 Digital Wellness")
        
        col1, col2 = st.columns(2)
        
        with col1:
            social_media_hours = st.selectbox(
                "Daily social media usage",
                ["< 30 minutes", "30min-1hr", "1-2hrs", "2-4hrs", "4+ hrs"]
            )
            
            sleep_hours = st.selectbox(
                "Average sleep per night",
                ["< 5 hours", "5-6 hours", "6-7 hours", "7-8 hours", "8+ hours"]
            )
            
            screen_time = st.selectbox(
                "Total screen time daily",
                ["< 2 hrs", "2-4 hrs", "4-6 hrs", "6-8 hrs", "8+ hrs"]
            )
        
        with col2:
            meditation = st.selectbox(
                "Meditation practice",
                ["Daily", "Sometimes", "Rarely", "Never"]
            )
            
            stress_level = st.selectbox(
                "Stress level during college",
                ["Very low", "Low", "Moderate", "High", "Very high"]
            )
        
        st.markdown("### 💪 Physical Activity")
        
        col1, col2 = st.columns(2)
        
        with col1:
            exercise_freq = st.selectbox(
                "Exercise frequency",
                ["Daily", "3-4 times/week", "1-2 times/week", "Rarely", "Never"]
            )
            
            exercise_time = st.selectbox(
                "Time available for exercise",
                ["15-30 min", "30-45 min", "45-60 min", "60-90 min", "90+ min"]
            )
            
            fitness_goals = st.multiselect(
                "Fitness goals",
                ["Build muscle", "Lose weight", "Stay fit", "Increase stamina", "Flexibility", "General health"]
            )
        
        with col2:
            weight = st.number_input("Weight (kg)", min_value=30, max_value=150, value=65)
            height = st.number_input("Height (cm)", min_value=120, max_value=220, value=170)
        
        st.markdown("### 🍽️ Nutrition")
        
        col1, col2 = st.columns(2)
        
        with col1:
            diet_type = st.selectbox(
                "Diet preference",
                ["Vegetarian", "Non-vegetarian"]
            )
            
            meals_per_day = st.selectbox(
                "Meals per day",
                ["1-2", "3", "4-5", "More than 5"]
            )
        
        with col2:
            water_intake = st.selectbox(
                "Water intake daily",
                ["< 1L", "1-2L", "2-3L", "3-4L", "4+ L"]
            )
            
            mess_food = st.selectbox(
                "College mess usage",
                ["All meals", "Some meals", "Rarely", "Never"]
            )
        
        submitted = st.form_submit_button("Complete Setup", use_container_width=True, type="primary")
        
        if submitted:
            # Calculate BMI
            height_m = height / 100
            bmi = weight / (height_m ** 2)
            
            # Calculate protein target
            protein_target = int(weight * 1.6)
            
            # Process data
            profile_data = {
                "name": student.get('name', ''),
                "social_media_hours": social_media_hours,
                "sleep_hours": int(sleep_hours.split('-')[0].replace('< ', '').replace('+ ', '').split(' ')[0]),
                "screen_time_hours": int(screen_time.split('-')[0].replace('< ', '').replace('+ ', '').split(' ')[0]),
                "meditation_frequency": meditation,
                "stress_level": stress_level,
                "exercise_frequency": exercise_freq,
                "exercise_time": exercise_time,
                "fitness_goals": fitness_goals,
                "weight": weight,
                "height": height,
                "bmi": round(bmi, 1),
                "diet_type": diet_type,
                "meals_per_day": meals_per_day,
                "water_intake": water_intake,
                "mess_food": mess_food,
                "daily_protein_target": protein_target,
                "social_media_limit": 30,
                "sleep_time": "11:00 PM",
                "tracks_protein": False,
                "created_on": datetime.now().isoformat()
            }
            
            # Save profile
            wellness_service.save_student_profile(
                student['roll_no'],
                student['branch'],
                student['year'],
                profile_data
            )
            
            st.success("✅ Profile created successfully!")
            st.rerun()

def show_dashboard():
    student = st.session_state.pa_student_data
    profile = wellness_service.load_student_profile(
        student['roll_no'],
        student['branch'],
        student['year']
    )
    
    # Header
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        st.markdown(f"### 👋 Welcome, {student['name']}!")
    with col2:
        wellness_score = wellness_service.calculate_wellness_score(profile)
        st.metric("💫 Wellness Score", f"{wellness_score}/100")
    with col3:
        if st.button("Logout", type="secondary"):
            st.session_state.pa_logged_in = False
            st.session_state.pa_student_data = None
            st.rerun()
    
    st.divider()
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏠 Dashboard", 
        "🎯 Learning Roadmaps", 
        "💪 Fitness", 
        "📅 Schedule", 
        "⚙️ Settings"
    ])
    
    with tab1:
        show_dashboard_tab(student, profile)
    
    with tab2:
        show_roadmaps_tab(student, profile)
    
    with tab3:
        show_fitness_tab(student, profile)
    
    with tab4:
        show_schedule_tab(student, profile)
    
    with tab5:
        show_settings_tab(student, profile)

def show_dashboard_tab(student, profile):
    st.markdown("### 📋 Today's To-Do List")
    
    # Generate button with user input
    with st.expander("🔄 Generate Today's To-Do List", expanded=False):
        user_input = st.text_area(
            "Any specific tasks or notes for today? (optional)",
            placeholder="e.g., Need to prepare for presentation, have doctor appointment at 4pm, want to focus on Python today...",
            height=100
        )
        
        if st.button("🚀 Generate Today's To-Do List", type="primary", use_container_width=True):
            with st.spinner("🤖 AI is creating your personalized to-do list..."):
                try:
                    todos = wellness_service.generate_and_save_daily_todos(
                        student['roll_no'],
                        student['branch'],
                        student['year'],
                        user_input=user_input
                    )
                    st.success("✅ To-do list generated and saved!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error generating todos: {str(e)}")
    
    st.divider()
    
    try:
        # Get todos (loads from file if exists)
        todos = wellness_service.get_daily_todos(
            student['roll_no'],
            student['branch'],
            student['year']
        )
        
        for todo_category in todos:
            with st.expander(todo_category['category'], expanded=True):
                for idx, task in enumerate(todo_category['tasks']):
                    st.checkbox(task['task'], value=task['completed'], key=f"task_{hash(todo_category['category'] + task['task'] + str(idx))}")
    except Exception as e:
        st.warning(f"⚠️ Could not load todos: {str(e)}")
        st.info("💡 Make sure your timetable.xlsx file exists in data/branches/{branch}/{year}/")
    
    st.divider()
    
    # Quick stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💤 Sleep Target", f"{profile.get('sleep_hours', 7)} hours")
    with col2:
        st.metric("🥤 Water Goal", profile.get('water_intake', '3L'))
    with col3:
        st.metric("💪 Protein Target", f"{profile.get('daily_protein_target', 80)}g")

def show_roadmaps_tab(student, profile):
    st.markdown("### 🎯 Learning Roadmaps")
    
    # Load existing roadmaps
    roadmaps = wellness_service.load_roadmaps(
        student['roll_no'],
        student['branch'],
        student['year']
    )
    
    # Create new roadmap with user input
    with st.expander("➕ Create New Roadmap", expanded=len(roadmaps) == 0):
        with st.form("create_roadmap_form"):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                topic = st.text_input("What do you want to learn?", placeholder="e.g., Machine Learning, Web Development")
            with col2:
                experience = st.selectbox("Experience Level", ["Beginner", "Intermediate", "Advanced"])
            with col3:
                hours = st.number_input("Hours/week", min_value=1, max_value=40, value=5)
            
            # User input box for detailed requirements
            user_input = st.text_area(
                "Describe your learning goals and any specific requirements (optional)",
                placeholder="e.g., I want to learn ML for computer vision projects, have Python basics, need practical hands-on projects...",
                height=100
            )
            
            if st.form_submit_button("🚀 Generate Roadmap", type="primary"):
                if topic:
                    with st.spinner("🤖 AI is creating your personalized roadmap..."):
                        try:
                            roadmap = ai_service.generate_roadmap(topic, experience.lower(), hours, user_input=user_input)
                            roadmaps.append(roadmap)
                            wellness_service.save_roadmaps(
                                student['roll_no'],
                                student['branch'],
                                student['year'],
                                roadmaps
                            )
                            st.success("✅ Roadmap created!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
    
    # Display roadmaps
    if roadmaps:
        for idx, roadmap in enumerate(roadmaps):
            with st.expander(f"📚 {roadmap['title']}", expanded=True):
                for phase in roadmap['phases']:
                    st.markdown(f"#### {phase['name']} ({phase['duration']})")
                    for topic_idx, topic in enumerate(phase['topics']):
                        completed = st.checkbox(
                            topic['name'],
                            value=topic.get('completed', False),
                            key=f"roadmap_{idx}_phase_{phase['name']}_topic_{topic_idx}"
                        )
                        # Update completion status
                        if completed != topic.get('completed', False):
                            topic['completed'] = completed
                            wellness_service.save_roadmaps(
                                student['roll_no'],
                                student['branch'],
                                student['year'],
                                roadmaps
                            )
                
                if st.button(f"🗑️ Delete Roadmap", key=f"delete_{idx}"):
                    roadmaps.pop(idx)
                    wellness_service.save_roadmaps(
                        student['roll_no'],
                        student['branch'],
                        student['year'],
                        roadmaps
                    )
                    st.rerun()
    else:
        st.info("No roadmaps yet. Create your first learning roadmap above!")

def show_fitness_tab(student, profile):
    st.markdown("### 💪 Fitness & Wellness")
    
    # Load exercise plan
    exercise_plan = wellness_service.load_exercise_plan(
        student['roll_no'],
        student['branch'],
        student['year']
    )
    
    # Generate new plan with user input
    if not exercise_plan:
        st.info("Generate your personalized exercise plan")
        
        with st.form("generate_plan_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                fitness_goal = st.selectbox(
                    "Primary Goal",
                    ["Build muscle", "Lose weight", "Stay fit", "Increase stamina"]
                )
                experience = st.selectbox(
                    "Exercise Experience",
                    ["Beginner", "Intermediate", "Advanced"]
                )
            
            with col2:
                time_available = st.selectbox(
                    "Daily workout time",
                    ["15-30", "30-45", "45-60", "60-90"]
                )
            
            # User input box for specific needs
            user_input = st.text_area(
                "Any injuries, limitations, or specific requirements? (optional)",
                placeholder="e.g., Have knee pain, prefer bodyweight exercises, no access to gym, want to focus on upper body...",
                height=100
            )
                
            if st.form_submit_button("🎯 Generate Plan", type="primary"):
                with st.spinner("🤖 Creating your personalized workout plan..."):
                    try:
                        plan_profile = {
                            'height': profile['height'],
                            'weight': profile['weight'],
                            'fitness_goals': [fitness_goal],
                            'exercise_frequency': experience.lower(),
                            'exercise_time': time_available,
                            'diet_type': profile['diet_type']
                        }
                        exercise_plan = ai_service.generate_exercise_plan(plan_profile, user_input=user_input)
                        wellness_service.save_exercise_plan(
                            student['roll_no'],
                            student['branch'],
                            student['year'],
                            exercise_plan
                        )
                        st.success("✅ Exercise plan created!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    else:
        # Display weekly plan
        st.markdown("#### 📅 Weekly Workout Plan")
        
        today = datetime.now().strftime("%A")
        
        for day, workout in exercise_plan.get('weekly_plan', {}).items():
            is_today = (day == today)
            
            with st.expander(f"{'🔥 ' if is_today else ''}{day}", expanded=is_today):
                st.markdown(f"**Focus:** {workout['focus']}")
                st.markdown(f"**Duration:** {workout['duration']}")
                st.markdown("**Exercises:**")
                for exercise in workout['exercises']:
                    st.markdown(f"- {exercise}")
        
        # Nutrition tips
        st.divider()
        st.markdown("#### 🍽️ Nutrition Plan")
        
        nutrition = exercise_plan.get('nutrition', {})
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🥚 Daily Protein", nutrition.get('daily_protein', '80g'))
        with col2:
            st.metric("🔥 Daily Calories", nutrition.get('daily_calories', '2400'))
        with col3:
            st.metric("💧 Daily Water", nutrition.get('daily_water', '3L'))
        
        st.markdown("**Meal Tips:**")
        for tip in nutrition.get('meal_tips', []):
            st.markdown(f"- {tip}")
        
        # Today's nutrition advice
        if today in exercise_plan.get('weekly_plan', {}):
            st.divider()
            st.markdown("#### 🎯 Today's Nutrition Advice")
            
            today_workout = exercise_plan['weekly_plan'][today]['focus']
            try:
                advice = ai_service.generate_daily_nutrition_tip(profile, today_workout)
                st.info(advice)
            except Exception as e:
                st.warning(f"Could not generate nutrition tip: {str(e)}")
        
        # Delete plan
        if st.button("🗑️ Delete Exercise Plan"):
            wellness_service.save_exercise_plan(
                student['roll_no'],
                student['branch'],
                student['year'],
                None
            )
            st.rerun()

def show_schedule_tab(student, profile):
    st.markdown("### 📅 Class Schedule & Reminders")
    
    # Today's schedule
    try:
        today_schedule = timetable_service.get_today_schedule(
            student['branch'],
            student['year']
        )
        
        if today_schedule:
            st.markdown("#### 📚 Today's Classes")
            
            for slot in today_schedule:
                status_color = {
                    'current': '🟢',
                    'upcoming': '🔵',
                    'past': '⚪'
                }.get(slot['status'], '⚪')
                
                col1, col2, col3 = st.columns([1, 3, 1])
                with col1:
                    st.markdown(f"**{slot['time']}**")
                with col2:
                    st.markdown(f"{status_color} {slot['subject']}")
                with col3:
                    st.markdown(f"*{slot['status']}*")
        else:
            st.info("No classes scheduled for today")
    except Exception as e:
        st.warning(f"Could not load timetable: {str(e)}")
    
    st.divider()
    
    # Week schedule
    st.markdown("#### 📆 Week Overview")
    try:
        week_schedule = timetable_service.get_week_schedule(
            student['branch'],
            student['year']
        )
        
        if week_schedule:
            for day, schedule in week_schedule.items():
                with st.expander(day):
                    if schedule:
                        for slot in schedule:
                            st.markdown(f"**{slot['time']}** - {slot['subject']}")
                    else:
                        st.info("No classes")
    except Exception as e:
        st.warning(f"Could not load week schedule: {str(e)}")
    
    st.divider()
    
    # Reminders
    st.markdown("#### 🔔 Reminders")
    
    reminders = wellness_service.load_reminders(
        student['roll_no'],
        student['branch'],
        student['year']
    )
    
    with st.form("add_reminder_form"):
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            reminder_title = st.text_input("Reminder", placeholder="Study for exam")
        with col2:
            reminder_date = st.date_input("Date")
        with col3:
            reminder_time = st.time_input("Time")
        
        priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        
        if st.form_submit_button("➕ Add Reminder"):
            if reminder_title:
                new_reminder = {
                    "title": reminder_title,
                    "date": str(reminder_date),
                    "time": str(reminder_time),
                    "priority": priority,
                    "completed": False
                }
                reminders.append(new_reminder)
                wellness_service.save_reminders(
                    student['roll_no'],
                    student['branch'],
                    student['year'],
                    reminders
                )
                st.success("✅ Reminder added!")
                st.rerun()
    
    # Display reminders
    if reminders:
        for idx, reminder in enumerate(reminders):
            priority_emoji = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(reminder['priority'], "⚪")
            
            col1, col2 = st.columns([4, 1])
            with col1:
                completed = st.checkbox(
                    f"{priority_emoji} {reminder['title']} - {reminder['date']} at {reminder['time']}",
                    value=reminder.get('completed', False),
                    key=f"reminder_{idx}"
                )
                if completed != reminder.get('completed', False):
                    reminder['completed'] = completed
                    wellness_service.save_reminders(
                        student['roll_no'],
                        student['branch'],
                        student['year'],
                        reminders
                    )
            with col2:
                if st.button("🗑️", key=f"delete_reminder_{idx}"):
                    reminders.pop(idx)
                    wellness_service.save_reminders(
                        student['roll_no'],
                        student['branch'],
                        student['year'],
                        reminders
                    )
                    st.rerun()
    else:
        st.info("No reminders yet")

def show_settings_tab(student, profile):
    st.markdown("### ⚙️ Settings")
    
    with st.form("update_profile_form"):
        st.markdown("#### Update Your Profile")
        
        # Physical Metrics
        st.markdown("**📏 Physical Metrics**")
        col1, col2 = st.columns(2)
        
        with col1:
            weight = st.number_input("Weight (kg)", min_value=30, max_value=150, value=profile.get('weight', 65))
            height = st.number_input("Height (cm)", min_value=120, max_value=220, value=profile.get('height', 170))
        
        with col2:
            diet_type = st.selectbox(
                "Diet Type",
                ["Vegetarian", "Non-vegetarian"],
                index=0 if profile.get('diet_type', 'Vegetarian') == 'Vegetarian' else 1
            )
            meals_per_day = st.selectbox(
                "Meals per day",
                ["1-2", "3", "4-5", "More than 5"],
                index=["1-2", "3", "4-5", "More than 5"].index(profile.get('meals_per_day', '3')) if profile.get('meals_per_day') in ["1-2", "3", "4-5", "More than 5"] else 1
            )
        
        st.divider()
        
        # Digital Wellness
        st.markdown("**📱 Digital Wellness**")
        col1, col2 = st.columns(2)
        
        with col1:
            social_media_hours = st.selectbox(
                "Daily social media usage",
                ["< 30 minutes", "30min-1hr", "1-2hrs", "2-4hrs", "4+ hrs"],
                index=["< 30 minutes", "30min-1hr", "1-2hrs", "2-4hrs", "4+ hrs"].index(profile.get('social_media_hours', '1-2hrs')) if profile.get('social_media_hours') in ["< 30 minutes", "30min-1hr", "1-2hrs", "2-4hrs", "4+ hrs"] else 2
            )
            
            screen_time = st.selectbox(
                "Total screen time daily",
                ["< 2 hrs", "2-4 hrs", "4-6 hrs", "6-8 hrs", "8+ hrs"],
                index=["< 2 hrs", "2-4 hrs", "4-6 hrs", "6-8 hrs", "8+ hrs"].index(profile.get('screen_time', '4-6 hrs')) if profile.get('screen_time') in ["< 2 hrs", "2-4 hrs", "4-6 hrs", "6-8 hrs", "8+ hrs"] else 2
            )
            
            social_media_limit = st.number_input("Social media limit (min/day)", min_value=0, max_value=180, value=profile.get('social_media_limit', 30))
        
        with col2:
            sleep_hours_select = st.selectbox(
                "Average sleep per night",
                ["< 5 hours", "5-6 hours", "6-7 hours", "7-8 hours", "8+ hours"],
                index=3  # Default 7-8 hours
            )
            
            meditation = st.selectbox(
                "Meditation practice",
                ["Daily", "Sometimes", "Rarely", "Never"],
                index=["Daily", "Sometimes", "Rarely", "Never"].index(profile.get('meditation_frequency', 'Sometimes')) if profile.get('meditation_frequency') in ["Daily", "Sometimes", "Rarely", "Never"] else 1
            )
            
            stress_level = st.selectbox(
                "Stress level during college",
                ["Very low", "Low", "Moderate", "High", "Very high"],
                index=["Very low", "Low", "Moderate", "High", "Very high"].index(profile.get('stress_level', 'Moderate')) if profile.get('stress_level') in ["Very low", "Low", "Moderate", "High", "Very high"] else 2
            )
        
        st.divider()
        
        # Physical Activity
        st.markdown("**💪 Physical Activity**")
        col1, col2 = st.columns(2)
        
        with col1:
            exercise_freq = st.selectbox(
                "Exercise frequency",
                ["Daily", "3-4 times/week", "1-2 times/week", "Rarely", "Never"],
                index=["Daily", "3-4 times/week", "1-2 times/week", "Rarely", "Never"].index(profile.get('exercise_frequency', '1-2 times/week')) if profile.get('exercise_frequency') in ["Daily", "3-4 times/week", "1-2 times/week", "Rarely", "Never"] else 2
            )
            
            exercise_time = st.selectbox(
                "Time available for exercise",
                ["15-30 min", "30-45 min", "45-60 min", "60-90 min", "90+ min"],
                index=["15-30 min", "30-45 min", "45-60 min", "60-90 min", "90+ min"].index(profile.get('exercise_time', '30-45 min')) if profile.get('exercise_time') in ["15-30 min", "30-45 min", "45-60 min", "60-90 min", "90+ min"] else 1
            )
        
        with col2:
            fitness_goals_options = ["Build muscle", "Lose weight", "Stay fit", "Increase stamina", "Flexibility", "General health"]
            current_goals = profile.get('fitness_goals', [])
            if not isinstance(current_goals, list):
                current_goals = []
            
            fitness_goals = st.multiselect(
                "Fitness goals",
                fitness_goals_options,
                default=current_goals
            )
        
        st.divider()
        
        # Nutrition
        st.markdown("**🍽️ Nutrition & Hydration**")
        col1, col2 = st.columns(2)
        
        with col1:
            water_goal = st.selectbox(
                "Daily water goal",
                ["< 1L", "1-2L", "2-3L", "3-4L", "4+ L"],
                index=["< 1L", "1-2L", "2-3L", "3-4L", "4+ L"].index(profile.get('water_intake', '2-3L')) if profile.get('water_intake') in ["< 1L", "1-2L", "2-3L", "3-4L", "4+ L"] else 2
            )
        
        with col2:
            mess_food = st.selectbox(
                "College mess usage",
                ["All meals", "Some meals", "Rarely", "Never"],
                index=["All meals", "Some meals", "Rarely", "Never"].index(profile.get('mess_food', 'Some meals')) if profile.get('mess_food') in ["All meals", "Some meals", "Rarely", "Never"] else 1
            )
        
        if st.form_submit_button("💾 Save Changes", type="primary"):
            # Calculate BMI
            height_m = height / 100
            bmi = weight / (height_m ** 2)
            protein_target = int(weight * 1.6)
            
            # Parse sleep hours
            sleep_target = int(sleep_hours_select.split('-')[0].replace('< ', '').replace('+ ', '').split(' ')[0])
            
            # Parse screen time
            screen_time_hours = int(screen_time.split('-')[0].replace('< ', '').replace('+ ', '').split(' ')[0])
            
            # Update profile with ALL fields
            profile['weight'] = weight
            profile['height'] = height
            profile['bmi'] = round(bmi, 1)
            profile['diet_type'] = diet_type
            profile['meals_per_day'] = meals_per_day
            profile['social_media_hours'] = social_media_hours
            profile['screen_time'] = screen_time
            profile['screen_time_hours'] = screen_time_hours
            profile['social_media_limit'] = social_media_limit
            profile['sleep_hours'] = sleep_target
            profile['meditation_frequency'] = meditation
            profile['stress_level'] = stress_level
            profile['exercise_frequency'] = exercise_freq
            profile['exercise_time'] = exercise_time
            profile['fitness_goals'] = fitness_goals
            profile['water_intake'] = water_goal
            profile['mess_food'] = mess_food
            profile['daily_protein_target'] = protein_target
            
            wellness_service.save_student_profile(
                student['roll_no'],
                student['branch'],
                student['year'],
                profile
            )
            
            st.success("✅ Profile updated!")
            st.info("💡 Regenerate your Exercise Plan and Daily To-Do List to reflect these changes!")
            st.rerun()
    
    st.divider()
    
    # Display current stats
    st.markdown("#### 📊 Your Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("BMI", profile.get('bmi', 0))
    with col2:
        wellness_score = wellness_service.calculate_wellness_score(profile)
        st.metric("Wellness Score", f"{wellness_score}/100")
    with col3:
        st.metric("Protein Target", f"{profile.get('daily_protein_target', 80)}g")
    with col4:
        st.metric("Diet Type", profile.get('diet_type', 'Vegetarian'))

if __name__ == "__main__":
    main()