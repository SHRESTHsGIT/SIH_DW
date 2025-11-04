## config.py
import os
import pandas as pd
import qrcode
from datetime import datetime

def setup_directories():
    """Create directory structure and initialize CSV files"""
    
    # Base directory structure
    base_dir = "data"
    os.makedirs(base_dir, exist_ok=True)
    
    # Initialize branches.csv FIRST if it doesn't exist
    branches_path = os.path.join(base_dir, "branches.csv")
    if not os.path.exists(branches_path):
        # Default branches if CSV doesn't exist
        branches_data = [
            ["CSH", "CSE(HCI & Gaming Tech)"],
            ["CSA", "CSE(AIML)"],
            ["CSD", "CSE(Data Science & Analytics)"],
            ["CSE", "CSE"],
            ["ECE", "Electronics & Communication Engineering"],
            ["ECI", "ECE (Internet of Things)"]
        ]
        branches_df = pd.DataFrame(branches_data, columns=["branch_code", "branch_name"])
        branches_df.to_csv(branches_path, index=False)
        print("✅ Created branches.csv with default branches")
    else:
        print("📁 branches.csv already exists - reading from file")
    
    # READ branches from CSV file
    branches_df = pd.read_csv(branches_path)
    branches = branches_df['branch_code'].tolist()
    
    print(f"\n📚 Found {len(branches)} branches in CSV: {', '.join(branches)}")
    
    # Year range
    years = ["2022", "2023", "2024", "2025"]
    
    # Create directories for each branch-year combination
    print("\n🔨 Creating directory structure...")
    for branch in branches:
        for year in years:
            branch_year_dir = os.path.join(base_dir, "branches", branch, year)
            os.makedirs(branch_year_dir, exist_ok=True)
            os.makedirs(os.path.join(branch_year_dir, "faces"), exist_ok=True)
            os.makedirs(os.path.join(branch_year_dir, "qrcodes"), exist_ok=True)
            
            # CREATE PERSONAL ASSISTANT DIRECTORY
            personal_assistant_dir = os.path.join(branch_year_dir, "personal_assistant")
            os.makedirs(personal_assistant_dir, exist_ok=True)
            
            print(f"   ✅ {branch}/{year} (with faces, qrcodes, personal_assistant)")
    
    # Initialize teachers.csv ONLY if it doesn't exist
    teachers_path = os.path.join(base_dir, "teachers.csv")
    if not os.path.exists(teachers_path):
        teachers_data = [
            ["T001", "Prof. Sharma", "password123"],
            ["T002", "Ms. Rao", "password456"],
            ["T003", "Dr. Kumar", "teacher789"],
            ["T004", "Prof. Singh", "prof123"]
        ]
        teachers_df = pd.DataFrame(teachers_data, columns=["teacher_id", "teacher_name", "password"])
        teachers_df.to_csv(teachers_path, index=False)
        print("\n✅ Created teachers.csv")
    else:
        print("\n📁 teachers.csv already exists - keeping existing data")
    
    # Initialize CSV files for each branch-year ONLY if they don't exist
    print("\n📄 Initializing CSV files...")
    for branch in branches:
        for year in years:
            branch_year_dir = os.path.join(base_dir, "branches", branch, year)
            
            # Create empty students.csv ONLY if it doesn't exist
            students_path = os.path.join(branch_year_dir, "students.csv")
            if not os.path.exists(students_path):
                students_columns = ["roll_no", "name", "face_path", "qr_code_path", "registered_on", "password"]
                students_df = pd.DataFrame(columns=students_columns)
                students_df.to_csv(students_path, index=False)
                print(f"   ✅ students.csv for {branch}/{year}")
            
            # Create empty attendance.csv ONLY if it doesn't exist
            attendance_path = os.path.join(branch_year_dir, "attendance.csv")
            if not os.path.exists(attendance_path):
                attendance_columns = ["roll_no", "name"]
                attendance_df = pd.DataFrame(columns=attendance_columns)
                attendance_df.to_csv(attendance_path, index=False)
                print(f"   ✅ attendance.csv for {branch}/{year}")
            
            # Create empty stats.csv ONLY if it doesn't exist
            stats_path = os.path.join(branch_year_dir, "stats.csv")
            if not os.path.exists(stats_path):
                stats_columns = ["roll_no", "name", "present_days", "absent_days", "total_days", "attendance_pct", "last_present", "last_absent"]
                stats_df = pd.DataFrame(columns=stats_columns)
                stats_df.to_csv(stats_path, index=False)
                print(f"   ✅ stats.csv for {branch}/{year}")
            
            # Create empty sessions.csv ONLY if it doesn't exist
            sessions_path = os.path.join(branch_year_dir, "sessions.csv")
            if not os.path.exists(sessions_path):
                sessions_columns = ["session_id", "teacher_id", "branch_code", "year", "start_time", "deadline_time", "status"]
                sessions_df = pd.DataFrame(columns=sessions_columns)
                sessions_df.to_csv(sessions_path, index=False)
                print(f"   ✅ sessions.csv for {branch}/{year}")
    
    # Print summary
    print("\n" + "="*70)
    print("✅ SETUP COMPLETE!")
    print("="*70)
    print(f"\n📂 Created structure for {len(branches)} branches × 4 years = {len(branches)*4} directories")
    print(f"\n📁 Branches from CSV: {', '.join(branches)}")
    print("📅 Years: 2022, 2023, 2024, 2025")
    print("\n📋 Each branch/year has:")
    print("   • students.csv")
    print("   • attendance.csv")
    print("   • stats.csv")
    print("   • sessions.csv")
    print("   • faces/ folder")
    print("   • qrcodes/ folder")
    print("   • personal_assistant/ folder ← For AI features!")
    print("\n🎓 Roll number format: BT[YY][BRANCH][XXX]")
    print("   Examples: BT23CSH013, BT24ECE042, BT25CSE001")
    print("\n💡 To add more branches: Edit data/branches.csv and run this script again!")
    print("="*70)

if __name__ == "__main__":
    setup_directories()