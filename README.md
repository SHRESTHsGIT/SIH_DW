# 🎓 Smart Campus Attendance & Wellness System

A comprehensive AI-powered attendance management and student wellness platform combining **face recognition**, **QR codes**, and **personalized AI coaching** for educational institutions.

---

## 🌟 Project Overview

This system revolutionizes campus management by integrating:
- ✅ **Contactless Attendance** - Face recognition + QR code backup
- 🤖 **AI Personal Assistant** - Learning roadmaps, fitness plans, wellness tracking
- 📊 **Real-time Analytics** - Live attendance monitoring and statistics
- 📅 **Smart Scheduling** - Automated timetable integration
- 💪 **Digital Wellness** - Sleep, screen time, exercise, nutrition tracking

Built for **Indian college students**, with mess food recommendations, realistic schedules, and localized features.

---

## 🎯 Core Features

### 📸 **Attendance System**
- **Face Recognition**: VGG-Face deep learning model with 99%+ accuracy
- **QR Code Backup**: Instant attendance marking via QR scan
- **Auto-marking**: Absent students marked automatically at session end
- **Multi-branch Support**: CSH, CSA, CSD, CSE, ECE, ECI
- **Multi-year**: Handles 2022-2025 batches simultaneously
- **Teacher Dashboard**: Real-time session monitoring
- **Student Portal**: Simple attendance marking interface

### 🤖 **AI Personal Assistant** (Powered by Groq)
- **Learning Roadmaps**: AI generates personalized study plans for any topic
  - Machine Learning, Web Development, DSA, System Design, etc.
  - Phase-by-phase progression with realistic timelines
  - Progress tracking with checkboxes
  - Max 2 active roadmaps per student

- **Exercise Plans**: Customized workout routines
  - Based on: weight, height, fitness goals, experience level
  - 6-day weekly schedules with specific exercises
  - Indian diet context (vegetarian/non-vegetarian)
  - Nutrition targets: protein, calories, water

- **Daily To-Do Lists**: AI-generated task management
  - Based on: class schedule, roadmaps, fitness plan, reminders
  - Wellness integration: meditation, sleep, screen time limits
  - Realistic task allocation (10-12 tasks max)
  - Diet-specific meal recommendations

- **Wellness Tracking**: 0-100 score based on:
  - Sleep hours (target: 7-8h)
  - Exercise frequency
  - Screen time (limit: <2h social media)
  - Meditation practice
  - Nutrition habits

- **Smart Reminders**: Date-based with priorities
  - Assignment deadlines, exams, meetings, personal tasks
  - High/Medium/Low priority levels
  - Today's reminders highlighted

- **Timetable Integration**: Excel-based class schedules
  - Today's schedule with current/upcoming/past status
  - Full week overview
  - Automatic todo generation from timetable

---

## 🏗️ System Architecture

### **Technology Stack**

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | FastAPI + Uvicorn | REST API server |
| **Frontend** | Streamlit (×3) | Teacher, Student, Personal Assistant UIs |
| **Face Recognition** | DeepFace + VGG-Face | Face verification & recognition |
| **AI Engine** | Groq (GPT-4 class) | Roadmaps, exercise plans, todos |
| **QR Codes** | qrcode + pyzbar | Generation & scanning |
| **Data Storage** | CSV + JSON | Simple, editable data files |
| **Image Processing** | OpenCV | Face detection & cropping |
| **Timetable** | openpyxl | Excel file reading |

### **Deployment Architecture**

```
┌─────────────────────────────────────────────────────────┐
│ User Access Layer                                       │
├─────────────────────────────────────────────────────────┤
│ Teacher       Student        Personal Assistant        │
│ Dashboard     Portal         (AI Coach)                 │
│ :8502         :8503          :8504                      │
└────────┬──────────────┬─────────────────┬───────────────┘
         │              │                 │
         └──────────────┴─────────────────┘
                        │
         ┌──────────────▼──────────────┐
         │ FastAPI Backend             │
         │ REST API (:8000)            │
         └──────────────┬──────────────┘
                        │
         ┌──────────────┴──────────────┐
         │                             │
    ┌────▼─────┐         ┌────────▼────────┐
    │ CSV       │         │ Groq AI API    │
    │ Storage   │         │ (Cloud-based)  │
    └──────────┘         └─────────────────┘
```

---

## 📁 Project Structure

```
SIH_11_NEW/
├── .env                           # API keys (GROQ_API_KEY)
├── .gitignore                     # Git ignore file
├── requirements.txt               # Python dependencies
├── config.py                      # System initialization
├── run.py                         # Launch all services
│
├── teacher_app.py                 # Teacher Dashboard (Streamlit)
├── student_app.py                 # Student Portal (Streamlit)
├── personal_assistant_app.py      # AI Assistant (Streamlit)
│
├── api/
│   ├── __init__.py
│   ├── main.py                    # FastAPI routes & endpoints
│   └── models.py                  # Pydantic data models
│
├── services/
│   ├── __init__.py
│   ├── data_service.py            # CSV CRUD operations
│   ├── face_service.py            # DeepFace integration
│   ├── qr_service.py              # QR generation/scanning
│   ├── session_service.py         # Session lifecycle management
│   ├── ai_service.py              # Groq AI integration
│   ├── timetable_service.py       # Excel timetable parser
│   └── wellness_service.py        # Wellness scoring & tracking
│
└── data/
    ├── branches.csv               # Branch definitions (editable)
    ├── teachers.csv               # Teacher accounts
    └── branches/
        └── {BRANCH}/              # CSH, CSA, CSD, CSE, ECE, ECI
            └── {YEAR}/            # 2022, 2023, 2024, 2025
                ├── students.csv
                ├── attendance.csv
                ├── stats.csv
                ├── sessions.csv
                ├── timetable.xlsx
                ├── faces/         # Face images (roll_no.jpg)
                ├── qrcodes/       # QR codes (roll_no.png)
                └── personal_assistant/
                    └── {ROLL_NO}/
                        ├── profile.json
                        ├── roadmaps.json
                        ├── exercise_plan.json
                        ├── reminders.json
                        └── daily_todos.json
```

---

## 🚀 Installation & Setup

### **Prerequisites**
- Python 3.8 or higher
- Webcam/Camera (for face capture)
- Groq API Key (free at https://console.groq.com)

### **Step 1: Clone Repository**
```bash
git clone <repository-url>
cd SIH_11_NEW
```

### **Step 2: Install Dependencies**
```bash
pip install -r requirements.txt
```

Key packages:
- `fastapi`, `uvicorn` - Backend API
- `streamlit` - Web interfaces
- `deepface`, `tensorflow` - Face recognition
- `groq` - AI features
- `opencv-python` - Image processing
- `openpyxl` - Excel reading
- `python-dotenv` - Environment variables

### **Step 3: Configure Environment**
Create `.env` file in project root:
```
# Get your free API key from: https://console.groq.com/keys
GROQ_API_KEY=your_groq_api_key_here
```

### **Step 4: Initialize System**
```bash
python config.py
```

This creates:
- Directory structure for all branches (reads from data/branches.csv)
- Empty CSV files with proper headers
- Face, QR code, and personal assistant folders
- Demo teacher accounts

### **Step 5: Configure Branches (Optional)**
Edit `data/branches.csv` to add/remove branches:
```csv
branch_code,branch_name
CSH,CSE(HCI & Gaming Tech)
CSA,CSE(AIML)
YOUR_NEW,Your New Branch
```

Then run `python config.py` again to create folders for new branches.

### **Step 6: Add Timetables (Optional for Personal Assistant)**
Create Excel files for each branch/year:
```
data/branches/CSH/2023/timetable.xlsx
data/branches/CSA/2024/timetable.xlsx
```

**Excel Format:**
- Column A: Day name (Monday, Tuesday, etc.)
- Columns B-K: Time slots (8 AM to 5 PM)
- Content: Subject codes or "LUNCH"

Example:
```
Day     8    9    10   11   12    13   14   15   16   17
Monday  CG   DBMS TOC  OC   LUNCH Lab  Lab  Lab
Tuesday CN   ToC  Tut  OC   LUNCH
```

### **Step 7: Start All Services**
```bash
python run.py
```

This launches:
- 🔧 FastAPI Backend → http://localhost:8000
- 👨‍🏫 Teacher Dashboard → http://localhost:8502
- 🎓 Student Portal → http://localhost:8503
- 🤖 Personal Assistant → http://localhost:8504

---

## 📚 User Guides

### **👨‍🏫 For Teachers**

#### Login
- URL: http://localhost:8502
- Credentials: T001 / password123

#### Start Attendance Session
1. Select branch (CSH, CSA, etc.)
2. Select year (2022-2025)
3. Set duration (default: 60 minutes)
4. Click "Start Session"

#### Monitor Session
- View real-time attendance list
- See present/absent students
- Session auto-closes at deadline
- Manually close anytime

#### View Statistics
- Attendance percentages
- Present/absent counts
- Individual student records
- Download CSV reports

### **🎓 For Students**

#### First Time Registration
1. Open http://localhost:8503
2. Click "Register New Student"
3. Fill details:
   - Roll No: BT23CSH024 (format: BT[YY][BRANCH][XXX])
   - Name: Your full name
   - Branch: Select from dropdown
   - Password: Create password
4. Capture face photo using camera
5. System generates QR code automatically

#### Daily Attendance
1. Select your branch and year
2. System checks for active session
3. If session active, mark attendance:
   - **Option A**: Capture face → AI recognizes → Marked
   - **Option B**: Scan QR code → Marked
4. Get confirmation message

#### Personal Assistant
1. Click "Personal Assistant" button
2. Login with roll number + password
3. First time: Complete wellness questionnaire (19 questions)
4. Use features:
   - Create AI learning roadmaps
   - Generate exercise plans
   - View today's schedule
   - Generate daily to-do list
   - Set reminders
   - Track wellness score

---

## 🎓 Roll Number Format

**Structure:** `BT[YY][BRANCH][XXX]`

| Component | Description | Values |
|-----------|-----------|---------|
| BT | Course (Bachelor of Technology) | Fixed |
| YY | Admission Year | 22, 23, 24, 25 |
| BRANCH | Branch Code | CSH, CSA, CSD, CSE, ECE, ECI |
| XXX | Student Number | 001-999 |

**Examples:**
- BT23CSH013 → 2023, CSE(HCI), Student #013
- BT24ECE042 → 2024, ECE, Student #042
- BT25CSE001 → 2025, CSE, Student #001

---

## 🏢 Available Branches

| Code | Full Name |
|------|-----------|
| CSH | CSE (HCI & Gaming Technology) |
| CSA | CSE (Artificial Intelligence & Machine Learning) |
| CSD | CSE (Data Science & Analytics) |
| CSE | Computer Science & Engineering |
| ECE | Electronics & Communication Engineering |
| ECI | ECE (Internet of Things) |

**Adding More Branches:** Edit `data/branches.csv` and run `python config.py`

---

## 🔐 Demo Credentials

### Teachers

| Teacher ID | Password | Name |
|-----------|----------|------|
| T001 | password123 | Prof. Sharma |
| T002 | password456 | Ms. Rao |
| T003 | teacher789 | Dr. Kumar |
| T004 | prof123 | Prof. Singh |

### Students
Register via Student Portal. No pre-created accounts.

---

## 🔧 API Documentation

**Swagger UI:** http://localhost:8000/docs

### Key Endpoints

#### Authentication
- `POST /api/teacher/login` - Teacher login
- `POST /api/student/login` - Student login

#### Student Management
- `POST /api/students/register` - Register with face photo
- `GET /api/students/{branch}/{year}` - List students

#### Session Management
- `POST /api/sessions/start` - Start attendance session
- `GET /api/sessions/{branch}/{year}/active` - Check active session
- `POST /api/sessions/{session_id}/close` - Close session

#### Attendance
- `POST /api/attendance/mark-face` - Mark via face recognition
- `POST /api/attendance/mark-qr` - Mark via QR scan

#### Data & Reports
- `GET /api/branches` - List all branches
- `GET /api/attendance/{branch}/{year}` - Attendance records
- `GET /api/stats/{branch}/{year}` - Statistics
- `GET /api/qr/{branch}/{year}/{roll_no}` - Download QR code

---

## 🤖 AI Features Explained

### Learning Roadmaps
**Powered by:** Groq (gpt-4-like model)

**How it works:**
1. Student enters topic (e.g., "Machine Learning")
2. AI analyzes: experience level, available time, specific goals
3. Generates phase-by-phase roadmap with 3-5 topics per phase
4. Student tracks progress with checkboxes
5. Tasks auto-added to daily to-do list

**Example Topics:** ML, Web Dev, DSA, System Design, Mobile Dev, DevOps

### Exercise Plans

**How it works:**
1. Student provides: weight, height, fitness goals, experience
2. AI creates 6-day weekly workout schedule
3. Includes: exercises with sets/reps, duration, focus areas
4. Generates nutrition plan: protein target (1.6g/kg), calories, water
5. Indian diet context: dal/paneer for veg, eggs/chicken for non-veg

### Daily To-Do Lists

**Generated from:**
- Today's class schedule (from timetable.xlsx)
- Active roadmap tasks (1-2 per day)
- Exercise plan for today
- High-priority reminders
- Wellness tasks (meditation, sleep, screen time)

**AI ensures:**
- Realistic workload (10-12 tasks max)
- Diet-specific meal recommendations
- Balanced study/fitness/wellness
- Time-bound tasks with deadlines

### Wellness Scoring (0-100)
- **Sleep** (25 pts): 7-8 hours = full points
- **Exercise** (25 pts): Daily = full points
- **Screen Time** (25 pts): <2 hours = full points
- **Meditation** (15 pts): Daily = full points
- **Nutrition** (10 pts): Tracking protein = full points

---

## 🚨 Troubleshooting

### Groq API Issues
**Error:** `ValueError: GROQ_API_KEY not found`

**Solution:** Create `.env` file with `GROQ_API_KEY=your_key` and restart

### Camera Not Working
- Check browser permissions (allow camera access)
- Ensure no other app is using camera
- Try Chrome/Edge (best compatibility)

### Face Recognition Fails
- Ensure good lighting
- Face clearly visible, no sunglasses/masks
- Look directly at camera
- At least 1 student must be registered first

### Timetable Not Showing
- Check if `timetable.xlsx` exists in correct folder
- Verify Excel format (Day column + time slots)
- Check column headers match specification

### Personal Assistant Won't Start
- Verify Groq API key is valid
- Check if port 8504 is free: `lsof -i :8504`
- Run manually: `streamlit run personal_assistant_app.py --server.port 8504`

### Import Errors
```bash
# Reinstall all dependencies
pip install -r requirements.txt --upgrade

# Test imports
python -c "import deepface"
python -c "import groq"
python -c "from dotenv import load_dotenv"
```

---

## 📊 Data Management

### CSV Files
- **Editable:** Open any CSV in Excel/LibreOffice
- **Backup:** Copy `data/` folder regularly
- **No Database:** Everything in text format
- **Version Control:** CSV files are git-friendly

### Adding New Branches
1. Edit `data/branches.csv`
2. Add row: `NEW,New Branch Name`
3. Run `python config.py`
4. Restart system

### Adding New Teachers
1. Edit `data/teachers.csv`
2. Add row: `T005,Prof. New,password`
3. No restart needed

### Resetting System (⚠️ Deletes all data)
```bash
rm -rf data/
python config.py
```

---

## 🔒 Security & Privacy

### Data Protection
- Face images stored locally only (not in cloud)
- No external face recognition APIs
- Password-based authentication
- Session-based access control
- CSV files easily auditable

### API Keys
- Groq API key in `.env` (gitignored)
- No hardcoded credentials
- Environment variable based

### Privacy Features
- Face data never leaves your server
- QR codes contain only roll numbers
- Personal Assistant data per-student isolated
- No tracking or analytics sent externally

---

## 📈 System Highlights

### What Makes This Special
- 🤖 **AI-Powered:** Groq integration for personalized learning & wellness
- 📸 **Privacy-First:** Local face recognition, no cloud services
- 💪 **Holistic:** Attendance + Academics + Fitness + Wellness
- 🎓 **Student-Centric:** Personal Assistant helps beyond attendance
- 🇮🇳 **Indian Context:** Mess food advice, realistic schedules
- 📊 **Simple Data:** CSV-based, easy to edit/backup/audit
- 🚀 **Production-Ready:** Complete error handling, logging
- 🔧 **Extensible:** Easy to add branches, features

---

## 🎯 Use Cases

### Educational Institutions
- Colleges & Universities
- Training Centers
- Coaching Institutes
- Skill Development Centers

### Features for Different Users

**Management:**
- Real-time attendance monitoring
- Statistical reports
- Branch-wise analytics
- Session history

**Teachers:**
- Quick session start/stop
- Live attendance view
- Student statistics
- CSV exports

**Students:**
- Contactless attendance
- Personalized learning paths
- Fitness coaching
- Wellness tracking
- Time management

---

## 🔄 System Workflow Example

### Monday Morning - CSH Branch

**8:30 AM - Teacher:**
- Login to dashboard
- Start session: CSH/2023, 60 minutes
- Session becomes active

**9:05 AM - Student: Raj (BT23CSH024):**
- Opens Student Portal
- Selects CSH/2023
- Sees active session (55 min remaining)
- Captures face → Recognized → ✅ Present

**9:10 AM - Student: Priya (BT23CSH007):**
- Same process
- Scans QR code → ✅ Present

**9:35 AM - Student: Arjun (BT23CSH050):**
- Tries to mark attendance
- Session expired (60 min passed)
- ❌ Too late

**9:35 AM - System (Automatic):**
- Marks Arjun as Absent
- Updates all statistics
- Closes session
- Generates attendance report

**12:00 PM - Student: Raj (Personal Assistant):**
- Logs into Personal Assistant
- Dashboard shows:
  - Attendance: 95% ✅
  - Completed classes: CG, DBMS
  - Upcoming: TOC at 11 AM, Lunch at 1 PM
  - Checks ML roadmap: 45% complete
  - Sees workout reminder: Chest day at 5 PM
  - AI nutrition tip: "Aim for 80g protein. Include dal and paneer from mess."

---

## 📞 Support

### Common Commands

```bash
# Start all services
python run.py

# Start services individually
python -m uvicorn api.main:app --port 8000
streamlit run teacher_app.py --server.port 8502
streamlit run student_app.py --server.port 8503
streamlit run personal_assistant_app.py --server.port 8504

# Check Python version
python --version  # Should be 3.8+

# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Reset system (WARNING: Deletes all data)
rm -rf data/
python config.py
```

### Getting Help
- Check API docs: http://localhost:8000/docs
- Review console logs for errors
- Verify all services running
- Check `.env` configuration
- Ensure dependencies installed

---

## 📝 Version History

### v2.0.0 (Current)
- ✨ AI Personal Assistant with Groq integration
- ✨ Learning roadmaps, exercise plans, wellness tracking
- ✨ Timetable integration from Excel
- ✨ Smart reminders and daily to-do generation
- ✨ Diet-specific recommendations (veg/non-veg)
- 🐛 Fixed session ID parsing
- 🐛 Fixed face recognition best-match algorithm
- 📚 Comprehensive documentation

### v1.0.0 (Initial)
- ✅ Face recognition attendance
- ✅ QR code backup
- ✅ Teacher & Student portals
- ✅ Real-time statistics

---

## 🤝 Contributing

To add features or fix bugs:
1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

---

## 📄 License

[Specify your license here]

---

## 🙏 Acknowledgments

**Technologies Used:**
- DeepFace - Face recognition
- Groq - AI features
- FastAPI - Backend framework
- Streamlit - Frontend interfaces
- TensorFlow - Deep learning
- OpenCV - Image processing

---

## 📧 Contact

- **Project Team:** [Your Team Name]
- **Email:** [Contact Email]
- **Institution:** [Your Institution]

---

## 🎯 Built for Smart India Hackathon 2024 - Digital Wellness & Campus Management

🔗 **Technologies:** Python · FastAPI · Streamlit · DeepFace · TensorFlow · Groq · OpenCV

**Last Updated:** November 2024
