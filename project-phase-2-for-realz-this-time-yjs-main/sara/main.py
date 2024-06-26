from flask import Flask, render_template, session, request, redirect, url_for, flash, get_flashed_messages
import sqlite3 

app = Flask('app')
app.secret_key = 'srsecret'

@app.route('/')
def home():
  return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
  connection = sqlite3.connect("regs_database.db")
  connection.row_factory = sqlite3.Row
  cur = connection.cursor()
  if request.method == "GET":
    return render_template("login.html")
  if request.method == 'POST':
    uname = (request.form["username"])
    passwrd = (request.form["password"])
    
    #student
    cur.execute("SELECT username, password FROM students WHERE username = ? and password = ?", (uname, passwrd))
    studentData = cur.fetchone()
    connection.commit()
    if studentData:
      session['username'] = studentData['username']
      session['role'] = 'student'
      return render_template("home.html")
    
    #instructor
    cur.execute("SELECT username, password FROM instructors WHERE username = ? and password = ?", (uname, passwrd))
    instructorData = cur.fetchone()
    connection.commit()
    if instructorData:
      session['username'] = instructorData['username']
      session['role'] = 'instructor'
      return render_template("home.html")

    #gs
    cur.execute("SELECT username, password FROM grad_secretaries WHERE username = ? and password = ?", (uname, passwrd))
    gsData = cur.fetchone()
    connection.commit()
    if gsData:
      session['username'] = gsData['username']
      session['role'] = 'gs'
      return render_template("home.html")
    return render_template("incorrectLogin.html")
  connection.close()

@app.route('/catalog')
def get_courses():
  connection = sqlite3.connect("regs_database.db")
  connection.row_factory = sqlite3.Row
  cur = connection.cursor()
  cur.execute("SELECT * FROM catalog")
  courses = cur.fetchall()
  connection.close()
  return render_template('catalog.html', courses=courses)

@app.route('/schedule')
def get_schedule():
  connection = sqlite3.connect("regs_database.db")
  connection.row_factory = sqlite3.Row
  cur = connection.cursor()
  cur.execute("SELECT * FROM courses_schedule")
  schedule = cur.fetchall()
  connection.close()
  return render_template('schedule.html', schedule=schedule)

@app.route('/gradeAssign', methods=['GET', 'POST'])
def assignGrades():
  valid_grades = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'F']
  connection = sqlite3.connect("regs_database.db")
  connection.row_factory = sqlite3.Row
  cur = connection.cursor()
  cur.execute("SELECT * FROM student_courses")
  student_courses = cur.fetchall()
  if request.method == 'POST':
    if session['role'] == 'instructor' or session['role'] == 'gs':
      student_id = request.form['student_UID']
      course_title = request.form['course_title']
      grade = request.form['grade']
      if session['role'] == 'instructor':
        cur.execute("SELECT * FROM student_courses WHERE student_UID = ? AND IP_course_title = ? AND IP_instructor_username = ?", (student_id, course_title, session['username']))
        student_course = cur.fetchone()
        if student_course:
          if grade in valid_grades:
            if student_course['grade'] == 'IP':
              cur.execute("UPDATE student_courses SET grade = ? WHERE student_UID = ? AND IP_course_title = ? AND IP_instructor_username = ?", (grade, student_id, course_title, session['username']))
              connection.commit()
              return redirect(url_for('assignGrades'))
            else:
              flash("As an instructor, you can submit grades only once. Please contact the GS.", 'error')
          else:
            flash("Invalid grade submitted.", 'error')
        else:
          flash("You are not authorized to grade this student.", 'error')
      elif session['role'] == 'gs':
        cur.execute("SELECT * FROM student_courses WHERE student_UID = ? AND IP_course_title = ?", (student_id, course_title))
        student_course = cur.fetchone()
        if student_course:
          if grade in valid_grades:
            cur.execute("UPDATE student_courses SET grade = ? WHERE student_UID = ? AND IP_course_title = ?", (grade, student_id, course_title))
            connection.commit()
            return redirect(url_for('assignGrades'))
          else:
            flash("Invalid grade submitted.", 'error')
        else:
          flash("Student is not enrolled in the course", 'error')
  cur.execute("SELECT * FROM students WHERE courses IS NOT NULL")
  students = cur.fetchall()
  connection.close()
  return render_template('gradeAssign.html', student_courses=student_courses, students=students)
    

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
  connection = sqlite3.connect("regs_database.db")
  connection.row_factory = sqlite3.Row
  cur = connection.cursor()
  if request.method == 'POST':
    uid = (request.form["uid"])
    uname = (request.form["username"])
    passwrd = (request.form["password"])
    fname = request.form["fname"]
    lname = request.form["lname"]
    address = request.form["address"]
    dob = request.form["dob"]
    email = request.form["email"]
    cur.execute("SELECT * FROM students WHERE username = ?", (uname,))
    existing_user = cur.fetchone()
    if existing_user:
      return "This username already exists. Please pick a different username."
    cur.execute("INSERT INTO students (UID, username, password, fname, lname, address, DOB, email) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (uid, uname, passwrd, fname, lname, address, dob, email))
    connection.commit()
    connection.close()
    return redirect(url_for('login'))
  return render_template('signup.html')

@app.route('/studentProfile', methods=['GET', 'POST'])
def student_profile():
   if 'username' not in session:
      return redirect(url_for('login'))
   
   connection = sqlite3.connect("regs_database.db")
   connection.row_factory = sqlite3.Row
   cur = connection.cursor()

   if request.method == 'POST':
      address = request.form.get('address')
      email = request.form.get('email')
      password = request.form.get('password')

      #updating student information when edited
      cur.execute("UPDATE students SET address=?, email=?, password=? WHERE username=?", (address, email, password, session['username']))
      connection.commit()

   cur.execute("SELECT * FROM students WHERE username = ?", (session['username'],))
   student_data = cur.fetchone()
   connection.close()

   return render_template('studentProfile.html', student_data=student_data)

@app.route('/registration', methods=['GET', 'POST'])
def registration():
 #  checking that person logged in is a student and not instructor
   if 'username' not in session or session['role'] != 'student':
     return redirect(url_for('login'))
 
   if request.method == 'POST':
     chosen_courseID = request.form['course_id']
     student_id = session['username']

  # check if student is already registered into chosen course
     connection = sqlite3.connect("regs_database.db")
     connection.row_factory = sqlite3.Row
     cur = connection.cursor()
     
     cur.execute("SELECT * FROM registrations WHERE student_id = ? AND course_id = ?", (student_id, chosen_courseID))
     registration_exists = cur.fetchone()

     # fetch meeting time of selected course
     cur.execute("SELECT meeting_time FROM courses_schedule WHERE course_ID = ?", (chosen_courseID,))
     chosen_course_data = cur.fetchone()
     chosen_course_time = chosen_course_data['meeting_time']

     # fetch meeting times of courses already registered into by student
     #####
     cur.execute("SELECT courses_schedule.meeting_time FROM student_courses JOIN courses_schedule ON student_courses.IP_course_ID = courses_schedule.course_ID WHERE student_courses.student_UID = ?", (student_id,))
     registered_courses_data = cur.fetchall()
     registered_course_times = [course['meeting_time'] for course in registered_courses_data]

     # check if student had taken all prerequisites for the chosen course
     cur.execute("SELECT course_prereq, course_prereq2 FROM courses WHERE CourseID = ?", (chosen_courseID,))
     prereq_data = cur.fetchone()
     prereq1 = prereq_data['course_prereq']
     prereq2 = prereq_data['course_prereq2']

     if prereq1:
       # check if prereq1 has been taken by student
       cur.execute("SELECT * FROM student_course WHERE student_id = ? AND IP_course_ID = ?", (student_id, prereq1))
       prereq1_exists = cur.fetchone()
       if not prereq1_exists:
         flash(f"You have not taken the required prerequisite course {prereq1}.", "error")
         return redirect(url_for('registration'))
     if prereq2:
       cur.execute("SELECT * FROM student_course WHERE student_id = ? AND IP_course_ID = ?", (student_id, prereq2))
       prereq2_exists = cur.fetchone()
       if not prereq2_exists:
         flash(f"You have not taken the required prerequisite course {prereq2}.", "error")
         return redirect(url_for('registration'))

     if registration_exists:
        flash("You are already registered into this course", "danger")
     elif chosen_course_time in registered_course_times:
        flash("Cannot register for this course because of schedule conflict", "error")
     else:
       #  register student and insert registration into the database
        cur.execute("INSERT INTO registrations (student_id, course_id) VALUES (?, ?)", (student_id, chosen_courseID))
        cur.execute("INSERT INTO student_courses (student_UID, IP_course_ID, IP_course_dname, IP_course_number, IP_course_title, grade, IP_instructor_username) SELECT ?, course_ID, course_dname, course_number, course_title, 'IP', instructor_username FROM courses_schedule WHERE course_ID = ?", (student_id, chosen_courseID))
        connection.commit()
        flash("You have successfully registered into the course", "success")

     connection.close()
  
  # fetch available courses for registration
   connection = sqlite3.connect("regs_database.db")
   connection.row_factory = sqlite3.Row
   cur = connection.cursor()

   cur.execute("SELECT * FROM courses_schedule WHERE semester = 'Spring 2024'")
   available_courses = cur.fetchall()
   connection.close()

   return render_template('registration.html', courses=available_courses)


@app.route('/dropCourse', methods=['GET', 'POST'])
def dropCourse():
  if 'username' not in session or session['role'] != 'student':
    return redirect(url_for('login'))
   
  student_id = session['username']

  connection = sqlite3.connect("regs_database.db")
  connection.row_factory = sqlite3.Row
  cur = connection.cursor()
  if request.method == 'POST':
    course_id = request.form.get('course_id')
    cur.execute("DELETE FROM registrations WHERE student_id = ? AND course_id = ?", (student_id, course_id))
    connection.commit()
    flash("Course removed successfully", "success")

  cur.execute("SELECT courses_schedule.* FROM registrations JOIN courses_schedule ON registrations.course_id = courses_schedule.course_ID WHERE registrations.student_id = ?", (student_id,))
  registered_courses = cur.fetchall()

  connection.close()
  return render_template('dropCourse.html', courses_schedule=registered_courses)


@app.route('/transcript', methods=['GET', 'POST'])
def transcript():
  if 'username' not in session:
    return redirect(url_for('login'))
  connection = sqlite3.connect("regs_database.db")
  connection.row_factory = sqlite3.Row
  cur = connection.cursor()
  transcript_info = None
  if session['role'] == 'student':
    if request.method == 'POST':
      student_id = request.form['student_UID']
      cur.execute("SELECT * FROM student_courses WHERE student_UID = ?", (student_id,))
      transcript_info = cur.fetchall()
  connection.close()
  return render_template('transcript.html', transcript_info=transcript_info)

@app.route('/previousTranscript', methods=['GET', 'POST'])
def previousTranscript():
  if 'username' not in session:
    return redirect(url_for('login'))
  connection = sqlite3.connect("regs_database.db")
  connection.row_factory = sqlite3.Row
  cur = connection.cursor()
  previous_courses = None
  if session['role'] == 'instructor' or session['role'] == 'gs':
    if request.method == 'POST':
      student_id = request.form['student_UID']
      cur.execute("SELECT * FROM previous_courses WHERE student_UID = ?", (student_id,))
      previous_courses = cur.fetchall()
  elif session['role'] == 'student':
    student_id = session['username']
    cur.execute("SELECT * FROM previous_courses WHERE student_UID = ?", (student_id,))
    previous_courses = cur.fetchall()
  connection.close()
  return render_template('transcript.html', previous_courses=previous_courses) 

@app.route('/facultyView_transcript', methods=['GET', 'POST'])
def facultyView_transcript():
  if 'username' not in session:
    return redirect(url_for('login'))
  connection = sqlite3.connect("regs_database.db")
  connection.row_factory = sqlite3.Row
  cur = connection.cursor()
  transcript_info = None
  if session['role'] == 'instructor' or session['role'] == 'gs':
    if request.method == 'POST':
      student_id = request.form['student_UID']
      cur.execute("SELECT * FROM student_courses WHERE student_UID = ?", (student_id,))
      transcript_info = cur.fetchall()
  connection.close()
  return render_template('facultyView_transcript.html', transcript_info=transcript_info)


@app.route('/reset')
def reset_database():
  connection = sqlite3.connect("regs_database.db")
  cur = connection.cursor()
  try:
    cur.execute("DELETE FROM students")
    cur.execute("DELETE FROM instructors")
    cur.execute("DELETE FROM grad_secretaries")
    cur.execute("DELETE FROM courses")
    cur.execute("DELETE FROM catalog")
    cur.execute("DELETE FROM courses_schedule")
    cur.execute("DELETE FROM student_courses")
    cur.execute("DELETE FROM previous_courses")
    cur.execute("DELETE FROM registrations")

    cur.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (88767547, 'sara.almaouf', 'saracourses', 'Sara', 'Almaouf', 'Vienna, VA', 9112004, 'sara.almaouf@gwu.edu', '3, 7, 11, 15, 19', 'Masters Program'))
    cur.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (78276378, 'jake.kat', 'jakecourses','Jake', 'Kat', 'Tysons, VA', 7072003, 'jake.kate@gwu.edu', '1, 5, 9, 13, 17', 'PhD'))
    cur.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (62736219, 'rohina.saeydie', 'rohinapassword', 'Rohina', 'Saeydie', 'Alexandria, VA', 5072004, 'rohina.saeydie@gwu.edu', '4, 8, 12, 16, 20', 'Masters Program'))
    cur.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (89173620, 'emma.holand', 'emmapass', 'Emma', 'Holand', 'Herndon, VA', 4162005, 'emma.holand@gwu.edu', '2, 6, 10, 14, 18', 'PhD'))
    cur.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (88888888, 'holiday', 'pass', 'Billie', 'Holiday', 'Washington, D.C.', 10102003, 'holiday@gwu.edu', '2, 3', 'Masters Program'))
    cur.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (99999999, 'krall', 'pass', 'Diana', 'Krall', 'Woodbridge, VA', 1012001, 'krall@gwu.edu', None, 'Masters Program'))
    
    cur.execute("INSERT INTO instructors VALUES (?, ?, ?, ?, ?, ?)",
      ('Ouska', 'pass1', 'Emily', 'Ouska', '1, 4', 'email1@email.com'))
    cur.execute("INSERT INTO instructors VALUES (?, ?, ?, ?, ?, ?)",
      ('Edwards', 'pass2', 'Ed', 'Edwards', '5, 6, 7, 8', 'email2@email.com'))
    cur.execute("INSERT INTO instructors VALUES (?, ?, ?, ?, ?, ?)",
      ('Ross', 'pass3', 'Bob', 'Ross', '9, 10, 11, 12', 'email3@email.com'))
    cur.execute("INSERT INTO instructors VALUES (?, ?, ?, ?, ?, ?)",
      ('Doubtfire', 'pass4', 'Euphegenia', 'Doubtfire', '13, 14, 15, 16', 'email4@email.com'))
    cur.execute("INSERT INTO instructors VALUES (?, ?, ?, ?, ?, ?)",
      ('Parmer', 'pass5', 'Gabe', 'Parmer', '17, 18, 19, 20', 'email5@email.com'))
    cur.execute("INSERT INTO instructors VALUES (?, ?, ?, ?, ?, ?)",
      ('Narahari', 'pass', 'Lily', 'Narahari', '2', 'email6@email.com'))
    cur.execute("INSERT INTO instructors VALUES (?, ?, ?, ?, ?, ?)",
      ('Choi', 'pass', 'Grace', 'Choi', '3', 'email7@email.com'))

    cur.execute("INSERT INTO grad_secretaries VALUES (?, ?, ?, ?, ?)",
      ('gs', 'gs', 'Razia', 'Yousufi', 'gs@email.com'))

    cur.execute("INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?, ?)",
      (1, 'CSCI', 6221, 'SW Paradigms', 3, None, None))
    cur.execute("INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?, ?)",
      (2, 'CSCI', 6461, 'Computer Architecture', 3, None, None))
    cur.execute("INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?, ?)",
      (3, 'CSCI', 6212, 'Algorithms', 3, None, None))
    cur.execute("INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?, ?)",
      (4, 'CSCI', 6232, 'Networks 1', 3, None, None))
    cur.execute("INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?, ?)",
      (5, 'CSCI', 6233, 'Networks 2', 3, 'CSCI 6232', None))
    cur.execute("INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?, ?)",
      (6, 'CSCI', 6241, 'Database 1', 3, None, None))
    cur.execute("INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?, ?)",
      (7, 'CSCI', 6242, 'Database 2', 3, 'CSCI 6241', None))
    cur.execute("INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?, ?)",
      (8, 'CSCI', 6246, 'Compilers', 3, 'CSCI 6461', 'CSCI 6212'))
    cur.execute("INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?, ?)",
      (9, 'CSCI', 6251, 'Cloud Computing', 3, 'CSCI 6461', None))
    cur.execute("INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?, ?)",
      (10, 'CSCI', 6254, 'SW Engineering', 3, 'CSCI 6221', None))
    cur.execute("INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?, ?)",
      (11, 'CSCI', 6260, 'Multimedia', 3, None, None))
    cur.execute("INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?, ?)",
      (12, 'CSCI', 6262, 'Graphics 1', 3, None, None))
    cur.execute("INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?, ?)",
      (13, 'CSCI', 6283, 'Security 1', 3, 'CSCI 6212', None))
    cur.execute("INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?, ?)",
      (14, 'CSCI', 6284, 'Cryptography', 3, 'CSCI 6212', None))
    cur.execute("INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?, ?)",
      (15, 'CSCI', 6286, 'Network Security', 3, 'CSCI 6283', 'CSCI 6232'))
    cur.execute("INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?, ?)",
      (16, 'CSCI', 6384, 'Cryptography 2', 3, 'CSCI 6284', None))
    cur.execute("INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?, ?)",
      (17, 'ECE', 6241, 'Communication Theory', 3, None, None))
    cur.execute("INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?, ?)",
      (18, 'ECE', 6242, 'Information Theory', 2, None, None))
    cur.execute("INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?, ?)",
      (19, 'MATH', 6210, 'Logic', 2, None, None))
    cur.execute("INSERT INTO courses VALUES (?, ?, ?, ?, ?, ?, ?)",
      (20, 'CSCI', 6339, 'Embedded Systems', 3, 'CSCI 6461', 'CSCI 6212'))

    cur.execute("INSERT INTO student_courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (88767547, 'Sara', 'Almaouf', 3, 'CSCI', 6212, 'Algorithms', 'IP', 'Choi'))
    cur.execute("INSERT INTO student_courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (88767547, 'Sara', 'Almaouf', 7, 'CSCI', 6242, 'Database 2', 'IP', 'Edwards'))
    cur.execute("INSERT INTO student_courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (88767547, 'Sara', 'Almaouf', 11, 'CSCI', 6260, 'Multimedia', 'IP', 'Ross'))
    cur.execute("INSERT INTO student_courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (88767547, 'Sara', 'Almaouf', 15, 'CSCI', 6286, 'Network Security', 'IP', 'Doubtfire'))
    cur.execute("INSERT INTO student_courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (88767547, 'Sara', 'Almaouf', 19, 'MATH', 6210, 'Logic', 'IP', 'Parmer'))
    cur.execute("INSERT INTO student_courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (62736219, 'Rohina', 'Saeydie', 4, 'CSCI', 6232, 'Networks 1', 'IP', 'Ouska'))
    cur.execute("INSERT INTO student_courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (62736219, 'Rohina', 'Saeydie', 8, 'CSCI', 6246, 'Compilers', 'IP', 'Edwards'))
    cur.execute("INSERT INTO student_courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (62736219, 'Rohina', 'Saeydie', 12, 'CSCI', 6262, 'Graphics 1', 'IP', 'Ross'))
    cur.execute("INSERT INTO student_courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (62736219, 'Rohina', 'Saeydie', 16, 'CSCI', 6384, 'Cryptography 2', 'IP', 'Doubtfire'))
    cur.execute("INSERT INTO student_courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (62736219, 'Rohina', 'Saeydie', 20, 'CSCI', 6339, 'Embedded Systems', 'IP', 'Parmer'))
    cur.execute("INSERT INTO student_courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (78276378, 'Jake', 'Kat', 1, 'CSCI', 6221, 'SW Paradigms', 'IP', 'Ouska'))
    cur.execute("INSERT INTO student_courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (78276378, 'Jake', 'Kat', 5, 'CSCI', 6233, 'Networks 2', 'IP', 'Edwards'))
    cur.execute("INSERT INTO student_courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (78276378, 'Jake', 'Kat', 9, 'CSCI', 6251, 'Cloud Computing', 'IP', 'Ross'))
    cur.execute("INSERT INTO student_courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (78276378, 'Jake', 'Kat', 13, 'CSCI', 6283, 'Security 1', 'IP', 'Doubtfire'))
    cur.execute("INSERT INTO student_courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (78276378, 'Jake', 'Kat', 17, 'ECE', 6241, 'Communication Theory', 'IP', 'Parmer'))
    cur.execute("INSERT INTO student_courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (89173620, 'Emma', 'Holand', 2, 'CSCI', 6461, 'Computer Architecture', 'IP', 'Narahari'))
    cur.execute("INSERT INTO student_courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (89173620, 'Emma', 'Holand', 6, 'CSCI', 6241, 'Database 1', 'IP', 'Edwards'))
    cur.execute("INSERT INTO student_courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (89173620, 'Emma', 'Holand', 10, 'CSCI', 6254, 'SW Engineering', 'IP', 'Ross'))
    cur.execute("INSERT INTO student_courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (89173620, 'Emma', 'Holand', 14, 'CSCI', 6284, 'Cryptography', 'IP', 'Doubtfire'))
    cur.execute("INSERT INTO student_courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (89173620, 'Emma', 'Holand', 18, 'ECE', 6242, 'Information Theory', 'IP', 'Parmer'))
    cur.execute("INSERT INTO student_courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (88888888, 'Billie', 'Holiday', 2, 'CSCI', 6461, 'Computer Architecture', 'IP', 'Narahari'))
    cur.execute("INSERT INTO student_courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (88888888, 'Billie', 'Holiday', 3, 'CSCI', 6212, 'Algorithms', 'IP', 'Choi'))

    cur.execute("INSERT INTO previous_courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (88767547, 'Sara', 'Almaouf', 6, 'CSCI', 6241, 'Database 1', 'A', 'Edwards'))
    cur.execute("INSERT INTO previous_courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (88767547, 'Sara', 'Almaouf', 13, 'CSCI', 6283, 'Security 1', 'A', 'Doubtfire'))
    cur.execute("INSERT INTO previous_courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (88767547, 'Sara', 'Almaouf', 4, 'CSCI', 6232, 'Networks 1', 'A', 'Ouska'))
    cur.execute("INSERT INTO previous_courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (88767547, 'Sara', 'Almaouf', 3, 'CSCI', 6212, 'Algorithms', 'A', 'Choi'))
    cur.execute("INSERT INTO previous_courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (62736219, 'Rohina', 'Saeydie', 2, 'CSCI', 6461, 'Computer Architecture', 'A', 'Narahari'))
    cur.execute("INSERT INTO previous_courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (62736219, 'Rohina', 'Saeydie', 3, 'CSCI', 6212, 'Algorithms', 'A', 'Choi'))
    cur.execute("INSERT INTO previous_courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (62736219, 'Rohina', 'Saeydie', 14, 'CSCI', 6284, 'Cryptography', 'A', 'Doubtfire'))
    cur.execute("INSERT INTO previous_courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (78276378, 'Jake', 'Kat', 4, 'CSCI', 6232, 'Networks 1', 'A', 'Ouska'))
    cur.execute("INSERT INTO previous_courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (78276378, 'Jake', 'Kat', 2, 'CSCI', 6461, 'Computer Architecture', 'B+', 'Narahari'))
    cur.execute("INSERT INTO previous_courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (78276378, 'Jake', 'Kat', 3, 'CSCI', 6212, 'Algorithms', 'C+', 'Choi'))
    cur.execute("INSERT INTO previous_courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (89173620, 'Emma', 'Holand', 1, 'CSCI', 6221, 'SW Paradigms', 'A-', 'Ouska'))
    cur.execute("INSERT INTO previous_courses VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      (89173620, 'Emma', 'Holand', 3, 'CSCI', 6212, 'Algorithms', 'B', 'Choi'))

    cur.execute("INSERT INTO departments VALUES (?, ?)",
      (12345, 'CSCI'))
    cur.execute("INSERT INTO departments VALUES (?, ?)",
      (67853, 'MATH'))
    cur.execute("INSERT INTO departments VALUES (?, ?)",  
      (11111, 'ECE'))

    cur.execute("INSERT INTO courses_schedule VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      ('Spring 2024', 1, 'CSCI', 6221, 'SW Paradigms', 3, 1, 'M 1500—1730', 'Ouska'))
    cur.execute("INSERT INTO courses_schedule VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      ('Spring 2024', 2, 'CSCI', 6461, 'Computer Architecture', 3, 1, 'T 1500—1730', 'Narahari'))
    cur.execute("INSERT INTO courses_schedule VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      ('Spring 2024', 3, 'CSCI', 6212, 'Algorithms', 3, 1, 'W 1500—1730', 'Choi'))
    cur.execute("INSERT INTO courses_schedule VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      ('Spring 2024', 4, 'CSCI', 6232, 'Networks 1', 3, 1, 'M 1800—2030', 'Ouska'))
    cur.execute("INSERT INTO courses_schedule VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      ('Spring 2024', 5, 'CSCI', 6233, 'Networks 2', 3, 1, 'T 1800—2030', 'Edwards'))
    cur.execute("INSERT INTO courses_schedule VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      ('Spring 2024', 6, 'CSCI', 6241, 'Database 1', 3, 1, 'W 1800—2030', 'Edwards'))
    cur.execute("INSERT INTO courses_schedule VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      ('Spring 2024', 7, 'CSCI', 6242, 'Database 2', 3, 1, 'R 1800—2030', 'Edwards'))
    cur.execute("INSERT INTO courses_schedule VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      ('Spring 2024', 8, 'CSCI', 6246, 'Compilers', 3, 1, 'T 1500—1730', 'Edwards'))
    cur.execute("INSERT INTO courses_schedule VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      ('Spring 2024', 9, 'CSCI', 6251, 'Cloud Computing', 3, 1, 'M 1800—2030', 'Ross'))
    cur.execute("INSERT INTO courses_schedule VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      ('Spring 2024', 10, 'CSCI', 6254, 'SW Engineering', 3, 1, 'M 1530—1800', 'Ross'))
    cur.execute("INSERT INTO courses_schedule VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      ('Spring 2024', 11, 'CSCI', 6260, 'Multimedia', 3, 1, 'R 1800—2030', 'Ross'))
    cur.execute("INSERT INTO courses_schedule VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      ('Spring 2024', 12, 'CSCI', 6262, 'Graphics 1', 3, 1, 'W 1800—2030', 'Ross'))
    cur.execute("INSERT INTO courses_schedule VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      ('Spring 2024', 13, 'CSCI', 6283, 'Security 1', 3, 1, 'T 1800—2030', 'Doubtfire'))
    cur.execute("INSERT INTO courses_schedule VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      ('Spring 2024', 14, 'CSCI', 6284, 'Cryptography', 3, 1, 'M 1800—2030', 'Doubtfire'))
    cur.execute("INSERT INTO courses_schedule VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      ('Spring 2024', 15, 'CSCI', 6286, 'Network Security', 3, 1, 'W 1800—2030', 'Doubtfire'))
    cur.execute("INSERT INTO courses_schedule VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      ('Spring 2024', 16, 'CSCI', 6384, 'Cryptography 2', 3, 1, 'W 1500—1730', 'Doubtfire'))
    cur.execute("INSERT INTO courses_schedule VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      ('Spring 2024', 17, 'ECE', 6241, 'Communication Theory', 3, 1, 'M 1800—2030', 'Parmer'))
    cur.execute("INSERT INTO courses_schedule VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      ('Spring 2024', 18, 'ECE', 6242, 'Information Theory', 2, 1, 'T 1800—2030', 'Parmer'))
    cur.execute("INSERT INTO courses_schedule VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      ('Spring 2024', 19, 'MATH', 6210, 'Logic', 2, 1, 'W 1800-2030', 'Parmer'))
    cur.execute("INSERT INTO courses_schedule VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
      ('Spring 2024', 20, 'CSCI', 6339, 'Embedded Systems', 3, 1, 'R 1600--1830', 'Parmer'))

    cur.execute("INSERT INTO catalog VALUES (?, ?, ?, ?, ?, ?)",
      ('CSCI', 6221, 'SW Paradigms', 3, None, None))
    cur.execute("INSERT INTO catalog VALUES (?, ?, ?, ?, ?, ?)",
      ('CSCI', 6461, 'Computer Architecture', 3, None, None))
    cur.execute("INSERT INTO catalog VALUES (?, ?, ?, ?, ?, ?)",
      ('CSCI', 6212, 'Algorithms', 3, None, None))
    cur.execute("INSERT INTO catalog VALUES (?, ?, ?, ?, ?, ?)",
      ('CSCI', 6220, 'Machine Learning', 3, None, None))
    cur.execute("INSERT INTO catalog VALUES (?, ?, ?, ?, ?, ?)",
      ('CSCI', 6232, 'Networks 1', 3, None, None))
    cur.execute("INSERT INTO catalog VALUES (?, ?, ?, ?, ?, ?)",
      ('CSCI', 6233, 'Networks 2', 3, 'CSCI 6232', None))
    cur.execute("INSERT INTO catalog VALUES (?, ?, ?, ?, ?, ?)",
      ('CSCI', 6241, 'Database 1', 3, None, None))
    cur.execute("INSERT INTO catalog VALUES (?, ?, ?, ?, ?, ?)",
      ('CSCI', 6242, 'Database 2', 3, 'CSCI 6241', None))
    cur.execute("INSERT INTO catalog VALUES (?, ?, ?, ?, ?, ?)",
      ('CSCI', 6246, 'Compilers', 3, 'CSCI 6461', 'CSCI 6212'))
    cur.execute("INSERT INTO catalog VALUES (?, ?, ?, ?, ?, ?)",
      ('CSCI', 6260, 'Multimedia', 3, None, None))
    cur.execute("INSERT INTO catalog VALUES (?, ?, ?, ?, ?, ?)",
      ('CSCI', 6251, 'Cloud Computing', 3, 'CSCI 6461', None))
    cur.execute("INSERT INTO catalog VALUES (?, ?, ?, ?, ?, ?)",
      ('CSCI', 6254, 'SW Engineering', 3, 'CSCI 6221', None))
    cur.execute("INSERT INTO catalog VALUES (?, ?, ?, ?, ?, ?)",
      ('CSCI', 6262, 'Graphics 1', 3, None, None))
    cur.execute("INSERT INTO catalog VALUES (?, ?, ?, ?, ?, ?)",
      ('CSCI', 6283, 'Security 1', 3, 'CSCI 6212', None))
    cur.execute("INSERT INTO catalog VALUES (?, ?, ?, ?, ?, ?)",
      ('CSCI', 6284, 'Cryptography', 3, 'CSCI 6212', None))
    cur.execute("INSERT INTO catalog VALUES (?, ?, ?, ?, ?, ?)",
      ('CSCI', 6286, 'Network Security', 3, 'CSCI 6283', 'CSCI 6232'))
    cur.execute("INSERT INTO catalog VALUES (?, ?, ?, ?, ?, ?)",
      ('CSCI', 6325, 'Algorithms 2', 3, 'CSCI 6212', None))
    cur.execute("INSERT INTO catalog VALUES (?, ?, ?, ?, ?, ?)",
      ('CSCI', 6339, 'Embedded Systems', 3, 'CSCI 6461', 'CSCI 6212'))
    cur.execute("INSERT INTO catalog VALUES (?, ?, ?, ?, ?, ?)",
      ('CSCI', 6384, 'Cryptography 2', 3, 'CSCI 6284', None))
    cur.execute("INSERT INTO catalog VALUES (?, ?, ?, ?, ?, ?)",
      ('ECE', 6241, 'Communication Theory', 3, None, None))
    cur.execute("INSERT INTO catalog VALUES (?, ?, ?, ?, ?, ?)",
      ('ECE', 6242, 'Information Theory', 2, None, None))
    cur.execute("INSERT INTO catalog VALUES (?, ?, ?, ?, ?, ?)",
      ('MATH', 6210, 'Logic', 2, None, None))
    connection.commit()
    connection.close()
    flash("Database has been reset successfully", "success")
  except Exception as e:
    connection.rollback()
    connection.close()
    flash(f"An error occurred while resetting the database: {str(e)}", "error")
  return render_template('home.html', messages=get_flashed_messages())

app.run(host='0.0.0.0', port=8080, debug=True)