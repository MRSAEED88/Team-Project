from Student import Student
import users_db
import random

def create_students(number=10):
    """
    Generates a specified number of random students and adds them to the database.
    """
    names = ["Abdulilah", "Saeed", "Sulaiman", "Alaa", "Mohtadi", "Baraa",
             "Faisal", "Omar", "Khalid", "Ahmed", "Rayan", "Hassan"]
    programs = ["Power and Machines", "Communication and Electronics", "Computer",
                "Biomedical"] # Corrected typo "Biomedecal"

    created_students = []
    for i in range(number):
        name = random.choice(names)
        program = random.choice(programs)
        level = random.randint(1, 4)
        # Ensure the generated ID is unique
        while True:
            try:
                ID = random.randint(2400000, 2499999)
                passw = str(random.randint(1234567, 2345678))
                email = (f"{name.lower()}{ID}@kau.edu.stu.com") # Use ID for unique email
                
                # Insert into users table first
                user = users_db.add_users((ID, name, email, passw, "student"))
                user.insertData()
                break # Exit loop if insertion is successful (ID/email was unique)
            except :
                continue # Try again with a new ID/email

        # Then, insert into the students table
        student = Student(ID, name, email, program, level, passw)
        student.store_data()
        created_students.append(student)
        print(f"Created student: {name}, ID: {ID}, Email: {email}, Password: {passw}")

    return created_students

if __name__ == "__main__":
    print(f"Creating 10 new students...")
    newly_created = create_students(10)
    print("\nStudent creation complete.")

    # Example of how to search for a student
    if newly_created:
        first_student_id = newly_created[0].user_id
        print(f"\n--- Testing search for student ID: {first_student_id} ---")
        search_result = users_db.search(parameter=first_student_id, table="students", search_by="id").fetch()
        print("Search Result:", search_result)
