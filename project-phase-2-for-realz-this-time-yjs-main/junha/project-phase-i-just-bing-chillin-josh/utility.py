from flask import session
import mysql.connector
from main import mydb


def get_courses():
    c = mydb.cursor()
    c.execute("SELECT course_id, title, credits FROM courses")
    courses = c.fetchall()
    mydb.commit()
    return courses

def get_student_info(user_id):
    c = mydb.cursor()
    c.execute("SELECT fname, lname FROM users WHERE user_id = ? AND user_type = 'MS'", (user_id,))
    student_info = c.fetchone()
    mydb.commit()
    return student_info

def get_user_role(user_id):
    cursor = mydb.cursor()
    user_role = conn.execute('SELECT user_type FROM users WHERE user_id = ?', (user_id,)).fetchone()
    mydb.commit()
    return user_role['user_type'] if user_role else None

def get_student_courses(user_id):
    c = mydb.cursor()
    query = """
    SELECT sc.course_id, c.title, sc.semester, sc.grade
    FROM student_courses sc
    JOIN Courses c ON sc.course_id = c.course_id
    WHERE sc.user_id = ?
    """
    c.execute(query, (user_id,))
    courses = c.fetchall()
    mydb.commit()
    return courses

#Checks if user is logged in and has a type
def has_session():
    if "user_type" in session and "user_id" in session:
        return "true"
    return redirect('/login')

def form1_clear(user_id):
    cursor = mydb.cursor()
    cursor.execute("DELETE FROM form1 WHERE user_id = ?", (user_id,))
    cursor.close()
    mydb.commit()

#Checks if the currently logged in user meets the base MS requirements (doesnt include review)
def ms_graduates():
    ms_gpa = gpa()
    ms_credits = total_ms_credits()
    ms_b_grades = total_b_grades()
    ms_all_courses = ms_required_courses()

    if ms_all_courses == False:
        return 0
    if ms_gpa < 3.0:
        return 1
    if ms_credits == False:
        return 2
    if ms_b_grades > 2:
        return 3

    return -1 # success

#Checks if the currently logged in user meets the base PHD requirements (doesnt include review)
def phd_graduates():
    phd_gpa = gpa()
    phd_credits = total_phd_credits()
    phd_b_grades = total_b_grades()

    if phd_gpa < 3.5:
        return 4
    if phd_credits == False:
        return 5
    if phd_b_grades > 1:
        return 6

    return -1 # success

def gpa():
    cursor = mydb.cursor()

    # Select course_id, credits, grade on join of student courses and courses where course ids match, and user id for that course in sc is session userid
    cursor.execute("SELECT C.credits, SC.grade FROM student_courses AS SC JOIN Courses AS C ON SC.course_id = C.course_id WHERE SC.user_id = ? AND SC.counts = 1", (session['user_id'],))
    results = cursor.fetchall()
    total_hours = 0

    if results:
        points = 0
        grade_dic = {'A': 4.0, 'A-': 3.7, 'B+': 3.3, 'B': 3.0, 'B-': 2.7, 'C+': 2.3, 'C': 2.0, 'F': 0.0 }

        for result in results:
            points += result['credits'] * grade_dic.get(result['grade'])
            total_hours += result['credits']
    
    gpa = 0
    if total_hours != 0:
        gpa = points / total_hours

    mydb.commit()
    cursor.close()

    return gpa

def total_ms_credits():
    total = 0

    cursor = mydb.cursor()

    cursor.execute("SELECT SUM(credits) AS sum FROM student_courses AS SC JOIN Courses AS C ON SC.course_id = C.course_id WHERE SC.user_id = ? AND SC.course_id LIKE 'CSCI%' AND SC.counts = 1", (session['user_id'],))
    results_cs = cursor.fetchone()
    total_cs = results_cs['sum'] if results_cs['sum'] is not None else 0

    cursor.execute("""
        SELECT SUM(sub.credits) AS sum 
        FROM (
            SELECT C.credits 
            FROM student_courses AS SC 
            JOIN Courses AS C ON SC.course_id = C.course_id 
            WHERE SC.user_id = ? AND SC.course_id NOT LIKE 'CSCI%' AND SC.counts = 1 
            ORDER BY C.credits DESC 
            LIMIT 2
        ) AS sub
    """, (session['user_id'],))

    results_noncs = cursor.fetchone()
    total_non_cs = results_noncs['sum'] if results_noncs['sum'] is not None else 0

    total = total_cs + total_non_cs

    cursor.close()
    mydb.commit()
    return total >= 30

def total_phd_credits():
    total = 0

    cursor = mydb.cursor()

    cursor.execute("SELECT SUM(C.credits) AS sum FROM student_courses AS SC JOIN Courses AS C ON SC.course_id = C.course_id WHERE SC.user_id = ? AND SC.course_id LIKE 'CSCI%' AND SC.counts = 1", (session['user_id'],))
    results_cs = cursor.fetchone()
    total_cs = results_cs['sum'] if results_cs['sum'] is not None else 0

    cursor.execute("SELECT SUM(C.credits) AS sum FROM student_courses AS SC JOIN Courses AS C ON SC.course_id = C.course_id WHERE SC.user_id = ? AND SC.course_id NOT LIKE 'CSCI%' AND SC.counts = 1)", (session['user_id']))
    results_noncs = cursor.fetchone()
    total_non_cs = results_noncs['sum'] if results_noncs['sum'] is not None else 0

    mydb.commit()

    if total_cs >= 30 and total_cs + total_non_cs >= 36:
        return True
    return False

def total_b_grades():
    total = 0
    cursor = mydb.cursor()
    cursor.execute("SELECT COUNT(course_id) AS total FROM student_courses WHERE user_id = ? AND grade IN ('F', 'C', 'C+', 'B-') AND counts = 1", (session['user_id'],))
    result = cursor.fetchone() # how many courses with worse than a B: integer
    if result: 
        total = result['total']
    cursor.close()
    mydb.commit()
    return total

def ms_required_courses():
    has_required = False
    cursor = mydb.cursor()
    cursor.execute("SELECT course_id FROM student_courses WHERE user_id = ? AND counts = 1 AND course_id IN ('CSCI6212', 'CSCI6221', 'CSCI6461')", (session['user_id'],))
    matching_courses = cursor.fetchall() # how many of these required 3 the student has
    if len(matching_courses) == 3:
        has_required = True
    cursor.close()
    mydb.commit()
    return has_required
