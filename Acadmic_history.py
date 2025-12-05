import sqlite3
import random

# Run this file once and it will do the job
courses = [
    ("MENG 102", 3), ("PHYS 202", 4), ("IE 255", 3), ("EE 201", 3),
    ("IE 201", 3),   ("IE 200", 1),   ("MATH 206", 4), ("MATH 207", 4),
    ("PHYS 281", 1), ("CHEM 281", 1), ("ARAB 101", 2), ("ISLS 101", 2),
    ("MATH 110", 3), ("CPIT 110", 3), ("CHEM 110", 4), ("STAT 110", 3),
    ("BIO 110", 3),  ("PHYS 110", 4)
]

grade_choices = ["A+", "A", "B+", "B", "C+", "C", "D+", "D", "F"]

def generate_all_transcripts():
    print("Connecting to database...")
    con = sqlite3.connect('User.db')
    cur = con.cursor()

    # 1. Get all existing Student IDs
    cur.execute("SELECT id, name FROM students")
    students = cur.fetchall()

    if not students:
        print("No students found in the database! Please add students first.")
        con.close()
        return

    print(f"Found {len(students)} students. Generating transcripts...")

    # 2. Loop through each student
    count = 0
    for student_id, name in students:
        # Optional: Clear old transcript for this student to avoid duplicates
        cur.execute("DELETE FROM transcripts WHERE student_id=?", (student_id,))

        # 3. Generate random grades for THIS student
        print(f" -> Generating for {name} (ID: {student_id})...")
        
        for course_code, credit_hours in courses:
            random_grade = random.choice(grade_choices)
            
            # 4. Insert into Database
            # Note: We only need student_id, course_code, and grade. 
            # Credits are usually stored in the 'courses' table, but the transcript just links them.
            cur.execute(
                "INSERT INTO transcripts (student_id, course_code, grade) VALUES (?, ?, ?)",
                (student_id, course_code, random_grade)
            )
            
            # OPTIONAL: Ensure these courses exist in the 'courses' table too
            # (so the dashboard can look up their credits later)
            cur.execute("""
                INSERT OR IGNORE INTO courses (course_code, course_name, credits, max_capacity) 
                VALUES (?, ?, ?, ?)
            """, (course_code, "Generated Course", credit_hours, 50))
            
        count += 1

    con.commit()
    con.close()
    print(f"\nSuccess! Generated transcripts for {count} students.")

if __name__ == "__main__":
    generate_all_transcripts()
