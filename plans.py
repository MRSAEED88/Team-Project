import sqlite3
import users_db

def populate_all_plans():
    """Assigns ALL existing courses to ALL programs (Level 1) for testing."""
    
    # 1. Get all course codes
    all_courses = users_db.get_all_courses() # returns list of tuples
    if not all_courses:
        print("No courses found! Run courseFactory.py first.")
        return

    programs = ["Computer", "Comm", "Power", "Biomedical"]
    
    print("--- Populating Program Plans ---")
    
    with sqlite3.connect('User.db') as con:
        cur = con.cursor()
        
        for course in all_courses:
            code = course[0] # Get the course code (e.g., "EE250")
            
            for prog in programs:
                # Assign every course to Level 1 of every program
                # INSERT OR IGNORE skips it if it already exists
                cur.execute(
                    "INSERT OR IGNORE INTO program_plans (program, level, course_code) VALUES (?, ?, ?)",
                    (prog, 1, code)
                )
                print(f"Assigned {code} to {prog}")
        
        con.commit()
    print("Done! All students should now see all courses.")

if __name__ == "__main__":
    populate_all_plans()