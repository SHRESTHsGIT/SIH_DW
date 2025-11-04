## api/models.py

## api/models.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TeacherLogin(BaseModel):
    teacher_id: str
    password: str

class StudentLogin(BaseModel):
    roll_no: str
    password: str

class StudentRegister(BaseModel):
    roll_no: str
    name: str
    password: str
    branch_code: str

class SessionStart(BaseModel):
    teacher_id: str
    branch_code: str
    year: str
    duration_minutes: int = 60

class AttendanceMark(BaseModel):
    roll_no: str
    session_id: str

class FaceAttendance(BaseModel):
    session_id: str
    # image will be sent as form data

class QRAttendance(BaseModel):
    qr_data: str
    session_id: str