import random

courses = [
    ("MENG 102", 3),
    ("PHYS 202", 4),
    ("IE 255", 3),
    ("EE 201", 3),
    ("IE 201", 3),
    ("IE 200", 1),
    ("MATH 206", 4),
    ("MATH 207", 4),
    ("PHYS 281", 1),
    ("CHEM 281", 1),
    ("ARAB 101", 2),
    ("ISLS 101", 2),
    ("MATH 110", 3),
    ("CPIT 110", 3),
    ("CHEM 110", 4),
    ("STAT 110", 3),
    ("BIO 110", 3),
    ("PHYS 110", 4)
]


grade_choices = ["A+", "A", "B+", "B", "C+", "C", "D+", "D", "F"]

grade_to_points = {
    "A+": 4.0,
    "A": 3.75,
    "B+": 3.5,
    "B": 3.0,
    "C+": 2.5,
    "C": 2.0,
    "D+": 1.5,
    "D": 1.0,
    "F": 0.0
}


transcripts = {}


def generate_transcript_for_student(student_id):
    transcript_list = []

    for course, hours in courses:
        random_grade = random.choice(grade_choices)
        transcript_list.append((course, random_grade, hours))

    transcripts[student_id] = transcript_list



def get_transcript(student_id):
    if student_id not in transcripts:
        generate_transcript_for_student(student_id)

    return transcripts[student_id]



def calculate_gpa(student_id):
    data = get_transcript(student_id)

    total_points = 0
    total_hours = 0

    for course, grade, hours in data:
        point = grade_to_points.get(grade, 0)
        total_points += point * hours
        total_hours += hours

    if total_hours == 0:
        return 0.0

    return round(total_points / total_hours, 2)



# SHOW TRANSCRIPT FOR ALL STUDENTS (OPTIONAL)

def show_all_transcripts(student_ids):
    for sid in student_ids:
        print("\n" + "="*50)
        print(f"Transcript for Student ID: {sid}")
        print("="*50)

        tr = get_transcript(sid)

        for course, grade, hours in tr:
            print(f"{course:15} | Grade: {grade:2} | Hours: {hours}")

        gpa = calculate_gpa(sid)
        print(f"\n➡ GPA: {gpa}\n")

#for the student
# import transcript_system

# student_id ={} 

# data = transcript_system.get_transcript(student_id)
# gpa = transcript_system.calculate_gpa(student_id)

# # Load into your QTableWidget
# for course, grade, hours in data:

#for the admin
# import transcript_system

# student_list = [1,2,3,4,5]
# transcript_system.show_all_transcripts(student_list)

