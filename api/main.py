## api/main.py

## api/main.py

from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime
import os

from api.models import *
from services.data_service import DataService
from services.session_service import SessionService
from services.face_service import FaceService
from services.qr_service import QRService

app = FastAPI(title="Face Recognition Attendance System", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
data_service = DataService()
session_service = SessionService()
face_service = FaceService()
qr_service = QRService()

@app.get("/")
def read_root():
    return {"message": "Face Recognition Attendance System API", "status": "running"}

# Authentication endpoints
@app.post("/api/teacher/login")
def teacher_login(login_data: TeacherLogin):
    if data_service.verify_teacher(login_data.teacher_id, login_data.password):
        return {"success": True, "teacher_id": login_data.teacher_id}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/api/student/login")
def student_login(login_data: StudentLogin):
    student = data_service.verify_student(login_data.roll_no, login_data.password)
    if student:
        return {"success": True, "student": student}
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Branch and Student endpoints
@app.get("/api/branches")
def get_branches():
    return data_service.get_branches()

@app.post("/api/students/register")
async def register_student(
    roll_no: str = Form(...),
    name: str = Form(...),
    password: str = Form(...),
    branch_code: str = Form(...),
    face_image: UploadFile = File(...)
):
    # Validate roll number format (BT23CSH013)
    if len(roll_no) < 8 or not roll_no.startswith('BT'):
        raise HTTPException(status_code=400, detail="Invalid roll number format. Use BT[YY][BRANCH][XXX]")
    
    try:
        # Extract year from roll number
        year = "20" + roll_no[2:4]
        
        # Read face image
        face_image_bytes = await face_image.read()
        
        # Register student
        success = data_service.register_student(roll_no, name, password, branch_code)
        if not success:
            raise HTTPException(status_code=400, detail="Student already exists or registration failed")
        
        # Save face image
        face_saved = face_service.save_face_image(face_image_bytes, roll_no, branch_code, year)
        if not face_saved:
            raise HTTPException(status_code=400, detail="Failed to save face image")
        
        # Generate QR code
        qr_generated = qr_service.generate_qr_code(roll_no, branch_code, year)
        if not qr_generated:
            raise HTTPException(status_code=400, detail="Failed to generate QR code")
        
        return {"success": True, "message": "Student registered successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.get("/api/students/{branch_code}/{year}")
def get_students(branch_code: str, year: str):
    return data_service.get_students(branch_code, year)

# Session Management endpoints
@app.post("/api/sessions/start")
def start_session(session_data: SessionStart):
    session_id = session_service.start_session(
        session_data.teacher_id,
        session_data.branch_code,
        session_data.year,
        session_data.duration_minutes
    )
    
    if session_id:
        return {"success": True, "session_id": session_id}
    else:
        raise HTTPException(status_code=400, detail="Session already active for this branch-year")

@app.get("/api/sessions/{branch_code}/{year}/active")
def get_active_session(branch_code: str, year: str):
    session = session_service.get_active_session(branch_code, year)
    if session:
        return session
    else:
        raise HTTPException(status_code=404, detail="No active session found")

@app.post("/api/sessions/{session_id}/close")
def close_session(session_id: str, branch_code: str, year: str):
    session_service.close_session(session_id, branch_code, year)
    return {"success": True, "message": "Session closed successfully"}

@app.get("/api/sessions/{session_id}/attendance")
def get_session_attendance(session_id: str, branch_code: str, year: str):
    return session_service.get_session_attendance(session_id, branch_code, year)

# Attendance endpoints
@app.post("/api/attendance/mark-face")
async def mark_attendance_face(
    session_id: str = Form(...),
    face_image: UploadFile = File(...)
):
    try:
        print(f"📸 Face attendance request for session: {session_id}")
        
        # Get session info
        # Extract branch and year from session_id (format: SES_YYYYMMDD_HHMMSS_BRANCH_YEAR)
        parts = session_id.split('_')
        if len(parts) < 5:
            print(f"❌ Invalid session ID format: {session_id}")
            raise HTTPException(status_code=400, detail="Invalid session ID format")
        
        branch_code = parts[3]
        year = parts[4]
        print(f"📂 Extracted branch: {branch_code}, year: {year}")
        
        # Verify session is active
        active_session = session_service.get_active_session(branch_code, year)
        if not active_session or active_session['session_id'] != session_id:
            print(f"❌ Session not active: {session_id}")
            raise HTTPException(status_code=400, detail="Session not active or expired")
        
        print("✅ Session verified as active")
        
        # Read face image
        face_image_bytes = await face_image.read()
        print(f"📷 Face image read: {len(face_image_bytes)} bytes")
        
        if len(face_image_bytes) == 0:
            print("❌ Empty face image")
            raise HTTPException(status_code=400, detail="Empty face image received")
        
        # Recognize face
        print("🔍 Starting face recognition...")
        recognized_roll_no = face_service.recognize_face(face_image_bytes, branch_code, year)
        
        if recognized_roll_no:
            print(f"✅ Face recognized as: {recognized_roll_no}")
            
            # Mark attendance
            success = data_service.mark_attendance(recognized_roll_no, branch_code, year, "Present")
            if success:
                print(f"✅ Attendance marked for: {recognized_roll_no}")
                return {
                    "success": True, 
                    "roll_no": recognized_roll_no, 
                    "message": "Attendance marked successfully via face recognition"
                }
            else:
                print(f"❌ Failed to mark attendance for: {recognized_roll_no}")
                raise HTTPException(status_code=400, detail="Failed to mark attendance in database")
        else:
            print("❌ Face not recognized or no match found")
            raise HTTPException(status_code=400, detail="Face not recognized. Please ensure good lighting and clear face visibility.")
            
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Unexpected error in face recognition: {error_msg}")
        raise HTTPException(status_code=500, detail=f"Face recognition failed: {error_msg}")

@app.post("/api/attendance/mark-qr")
async def mark_attendance_qr(
    session_id: str = Form(...),
    qr_image: UploadFile = File(...)
):
    try:
        print(f"📱 QR attendance request for session: {session_id}")
        
        # Get session info
        parts = session_id.split('_')
        if len(parts) < 5:
            print(f"❌ Invalid session ID format: {session_id}")
            raise HTTPException(status_code=400, detail="Invalid session ID format")
        
        branch_code = parts[3]
        year = parts[4]
        print(f"📂 Extracted branch: {branch_code}, year: {year}")
        
        # Verify session is active
        active_session = session_service.get_active_session(branch_code, year)
        if not active_session or active_session['session_id'] != session_id:
            print(f"❌ Session not active: {session_id}")
            raise HTTPException(status_code=400, detail="Session not active or expired")
        
        print("✅ Session verified as active")
        
        # Read QR image
        qr_image_bytes = await qr_image.read()
        print(f"📱 QR image read: {len(qr_image_bytes)} bytes")
        
        if len(qr_image_bytes) == 0:
            print("❌ Empty QR image")
            raise HTTPException(status_code=400, detail="Empty QR image received")
        
        # Decode QR code
        print("🔍 Starting QR code decoding...")
        roll_no = qr_service.decode_qr_code(qr_image_bytes)
        
        if roll_no:
            print(f"📱 QR code decoded as: {roll_no}")
            
            # Verify student exists in this branch-year
            students = data_service.get_students(branch_code, year)
            student_exists = any(s['roll_no'] == roll_no for s in students)
            
            if student_exists:
                print(f"✅ Student {roll_no} found in database")
                
                # Mark attendance
                success = data_service.mark_attendance(roll_no, branch_code, year, "Present")
                if success:
                    print(f"✅ Attendance marked for: {roll_no}")
                    return {
                        "success": True, 
                        "roll_no": roll_no, 
                        "message": "Attendance marked successfully via QR code"
                    }
                else:
                    print(f"❌ Failed to mark attendance for: {roll_no}")
                    raise HTTPException(status_code=400, detail="Failed to mark attendance in database")
            else:
                print(f"❌ Student {roll_no} not found in {branch_code}/{year}")
                raise HTTPException(status_code=400, detail=f"Student {roll_no} not found in this branch-year")
        else:
            print("❌ QR code not decoded")
            raise HTTPException(status_code=400, detail="QR code not recognized. Please ensure clear and well-lit QR code.")
            
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Unexpected error in QR recognition: {error_msg}")
        raise HTTPException(status_code=500, detail=f"QR recognition failed: {error_msg}")

@app.get("/api/attendance/{branch_code}/{year}")
def get_attendance_data(branch_code: str, year: str):
    return data_service.get_attendance_data(branch_code, year)

@app.get("/api/stats/{branch_code}/{year}")
def get_stats_data(branch_code: str, year: str):
    return data_service.get_stats_data(branch_code, year)

# File serving endpoints
@app.get("/api/qr/{branch_code}/{year}/{roll_no}")
def get_qr_code(branch_code: str, year: str, roll_no: str):
    qr_path = qr_service.get_qr_code_path(roll_no, branch_code, year)
    if os.path.exists(qr_path):
        return FileResponse(qr_path)
    else:
        raise HTTPException(status_code=404, detail="QR code not found")
## api/main.py - ADD THIS NEW ENDPOINT
# Add after the existing student_login endpoint (around line 1673)

@app.post("/api/student/face-login")
async def student_face_login(
    branch_code: str = Form(...),
    year: str = Form(...),
    face_image: UploadFile = File(...)
):
    """Login student using face recognition"""
    try:
        print(f"📸 Face login request for {branch_code}/{year}")
        
        # Read face image
        face_image_bytes = await face_image.read()
        print(f"📷 Face image read: {len(face_image_bytes)} bytes")
        
        if len(face_image_bytes) == 0:
            print("❌ Empty face image")
            raise HTTPException(status_code=400, detail="Empty face image received")
        
        # Recognize face
        print("🔍 Starting face recognition for login...")
        recognized_roll_no = face_service.recognize_face(face_image_bytes, branch_code, year)
        
        if recognized_roll_no:
            print(f"✅ Face recognized as: {recognized_roll_no}")
            
            # Get student data
            students = data_service.get_students(branch_code, year)
            student = next((s for s in students if s['roll_no'] == recognized_roll_no), None)
            
            if student:
                # Add branch and year to student data
                student['branch'] = branch_code
                student['year'] = year
                
                print(f"✅ Login successful for: {student['name']}")
                return {
                    "success": True,
                    "student": student,
                    "message": f"Welcome back, {student['name']}!"
                }
            else:
                print(f"❌ Student data not found for: {recognized_roll_no}")
                raise HTTPException(status_code=404, detail="Student data not found")
        else:
            print("❌ Face not recognized")
            raise HTTPException(status_code=401, detail="Face not recognized. Please try again with better lighting or use manual login.")
            
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Unexpected error in face login: {error_msg}")
        raise HTTPException(status_code=500, detail=f"Face login failed: {error_msg}")
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)