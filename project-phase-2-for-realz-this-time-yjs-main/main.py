import mysql.connector
import datetime
import random
from flask import Flask, request, session, render_template, redirect, url_for, flash, get_flashed_messages
from werkzeug.security import generate_password_hash
import string
app = Flask('app')
app.secret_key = 'yjssecret'  
mydb = mysql.connector.connect(
  host = "apps24yan.cnsrva0xhvzg.us-east-1.rds.amazonaws.com",
  user = "admin",
  password = "apps24yan",
  database = "university"
)
@app.route('/', methods=['GET', 'POST'])
def home():
  if request.method == 'POST':
        return "POST request handled"
  return render_template('home.html')

#-------------------HELPER FUNCTIONS----------------------------#
def get_courses():
    c = mydb.cursor(dictionary=True)
    c.execute("SELECT course_id, title, credits FROM courses")
    courses = c.fetchall()
    mydb.commit()
    return courses

def get_student_info(user_id):
    user_id = str(user_id)
    c = mydb.cursor(dictionary=True)
    c.execute("SELECT fname, lname FROM users WHERE user_id = %s AND user_type = 'MS'", (user_id,))
    student_info = c.fetchone()
    mydb.commit()
    return student_info

def get_user_role(user_id):
    cursor = mydb.cursor(dictionary=True)
    cursor.execute('SELECT user_type FROM users WHERE user_id = %s', (user_id,))
    user_role = cursor.fetchone()
    mydb.commit()
    return user_role['user_type'] if user_role else None

def get_student_courses(user_id):
    user_id = str(user_id)
    cursor = mydb.cursor(dictionary=True)
    cursor.execute('SELECT sc.course_id, c.title, sc.semester, sc.grade FROM student_courses sc JOIN courses c ON sc.course_id = c.course_id WHERE sc.user_id = %s', (user_id,))
    courses = cursor.fetchall()
    cursor.close()
    return courses


def send_notification(sender_id, receiver_id, subject, body):
    cursor = mydb.cursor(dictionary=True)
    cursor.execute('INSERT INTO messages (sender_id, receiver_id, subject, body) VALUES (%s, %s, %s, %s)',
                   (sender_id, receiver_id, subject, body))
    mydb.commit()

def find_graduate_secretary_id():
    cursor = mydb.cursor(dictionary=True)
    
    cursor.execute('SELECT user_id FROM users WHERE user_type = "GS" LIMIT 1')
    graduate_secretary = cursor.fetchone()
    
    if graduate_secretary:
        return graduate_secretary['user_id']
    else:
        print("No graduate secretary found.")
        return None

def get_faculty_advisor_id(student_id):
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT faculty_id FROM advisor_assignments WHERE student_id = %s", (student_id,))
    result = cursor.fetchone()
    if result:
        return result['faculty_id']
    else:
        return None

def send_notification_to_faculty_advisor(student_id, faculty_advisor_id):
    cursor = mydb.cursor(dictionary=True)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    subject = 'Form 1 Request Submission'
    body = f'Student {student_id} has submitted Form 1 and requires your approval.'
    cursor.execute("INSERT INTO messages (sender_id, receiver_id, subject, body, timestamp) VALUES (%s, %s, %s, %s, %s)",
                   (student_id, faculty_advisor_id, subject, body, timestamp))
    mydb.commit()
    
#Checks if user is logged in and has a type
def has_session():
    if "user_type" in session and "user_id" in session:
        return "true"
    return redirect('/login')

def form1_clear(user_id):
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("DELETE FROM form1 WHERE user_id = %s", (user_id,))
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
    cursor = mydb.cursor(dictionary=True)

    # Select course_id, credits, grade on join of student courses and courses where course ids match, and user id for that course in sc is session userid
    cursor.execute("SELECT C.credits, SC.grade FROM student_course AS SC JOIN courses AS C ON SC.IP_course_ID = C.CourseID WHERE SC.student_id = %s AND SC.counts = 1", (session['user_id'],))
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

    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT SUM(C.credits) AS sum FROM student_course AS SC JOIN courses AS C ON SC.IP_course_ID = C.CourseID WHERE SC.student_id = %s AND SC.IP_course_ID LIKE 'CSCI%' AND SC.counts = 1", (session['user_id'],))
    results_cs = cursor.fetchone()
    total_cs = int(results_cs["sum"]) if results_cs["sum"] is not None else 0
    cursor.execute("""
        SELECT SUM(sub.credits) AS sum 
        FROM (
            SELECT C.credits 
            FROM student_course AS SC 
            JOIN courses AS C ON SC.IP_course_ID = C.CourseID 
            WHERE SC.student_id = %s AND SC.IP_course_ID NOT LIKE 'CSCI%' AND SC.counts = 1 
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

    cursor = mydb.cursor(dictionary=True)

    cursor.execute("SELECT SUM(C.credits) AS sum FROM student_course AS SC JOIN courses AS C ON SC.course_id = C.course_id WHERE SC.user_id = %s AND SC.course_id LIKE 'CSCI%' AND SC.counts = 1", (session['user_id'],))
    results_cs = cursor.fetchone()
    total_cs = int(results_cs['sum']) if results_cs['sum'] is not None else 0
    cursor.execute("SELECT SUM(C.credits) AS sum FROM student_course AS SC JOIN courses AS C ON SC.course_id = C.course_id WHERE SC.user_id = %s AND SC.course_id NOT LIKE 'CSCI%' AND SC.counts = 1", (session['user_id'],))
    results_noncs = cursor.fetchone()
    total_non_cs = results_noncs['sum'] if results_noncs['sum'] is not None else 0

    mydb.commit()

    if total_cs >= 30 and total_cs + total_non_cs >= 36:
        return True
    return False

def total_b_grades():
    total = 0
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(IP_course_ID) AS total FROM student_course WHERE student_id = %s AND grade IN ('F', 'C', 'C+', 'B-') AND counts = 1", (session['user_id'],))
    result = cursor.fetchone()
    # how many courses with worse than a B: integer
    if result:
        total = result['total']
    cursor.close()
    mydb.commit()
    return total

def ms_required_courses():
    has_required = False
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT IP_course_ID FROM student_course WHERE student_id = %s AND counts = 'T' AND IP_course_ID IN ('CSCI6212', 'CSCI6221', 'CSCI6461')", (session['user_id'],))
    matching_courses = cursor.fetchall() # how many of these required 3 the student has
    if len(matching_courses) == 3:
        has_required = True
    cursor.close()
    mydb.commit()
    return has_required
#------------------------HELPER FUNCTIONS END---------------------------------#

# Apps functions:
#-------------------------Apps functions--------------------------------#
@app.route('/sign_in', methods=['GET', 'POST'])
def login():
    cursor = mydb.cursor(dictionary=True)
    
    if request.method == 'GET':
        return render_template('sign_in.html', message=None)

    if request.method == 'POST':
        username = request.form['yourUsername']
        password = request.form['yourPassword']
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if not user or user['password'] != password:
            return render_template('sign_in.html', errorMessage="Invalid username or password")

        session.update({
            "username": user['username'],
            "user_type": user["user_type"],
            "user_id": user["user_id"],
            "fname": user["fname"],
            "lname": user["lname"],
            "email": user["email"]
        })
        if user['user_type'] == "applicant":
            return render_template("status.html")
          
        elif user['user_type'] == "CAC/Chair":
            return redirect(url_for('decisionList'))
        elif user['user_type'] == "reviewer":
            return redirect(url_for('decisionList'))
          
        elif user['user_type'] == "admin":
            return render_template("home.html")
          
        elif user['user_type'] == "student":
            cursor.execute("SELECT grad_status, uaf FROM students WHERE user_id = %s", (user["user_id"],))
            student_info = cursor.fetchone()
            if student_info:
                session['grad_status'] = student_info['grad_status']
                session['uaf'] = student_info['uaf']
            return render_template("home.html", user=user)
          
        elif user['user_type'] == "instructor":
            return render_template("home.html")
          
        elif user['user_type'] == "secretary":
            cursor.execute("""
                SELECT aa.student_id, aa.faculty_id, s.fname AS student_fname, s.lname AS student_lname, f.fname AS faculty_fname, f.lname AS faculty_lname 
                FROM advisor_assignments aa 
                JOIN users s ON aa.student_id = s.user_id 
                JOIN users f ON aa.faculty_id = f.user_id 
                WHERE s.user_type = 'student' AND f.user_type = 'faculty';
            """)
            advisors = cursor.fetchall()
            cursor.execute("SELECT user_id, fname, lname, email FROM users WHERE user_type = 'student';")
            students = cursor.fetchall()
            return render_template("home.html", username=user['fname'], students=students, advisors=advisors)
        elif user['user_type'] == "alumni":
            cursor.execute("SELECT fname, lname, email, address, password FROM users WHERE user_id = %s", (user['user_id'],))
            one_row_info = cursor.fetchone()
            return render_template('home.html', user=one_row_info)
        elif user['user_type'] == "faculty":
             
            cursor.execute("""
                SELECT fname, lname, email, address, password 
                FROM users 
                WHERE user_id IN (SELECT student_id FROM advisor_assignments WHERE faculty_id = %s)
            """, (user['user_id'],))
            students_info = cursor.fetchall()
            return render_template('home.html', user=user, students=students_info)

    return render_template('sign_in.html', errorMessage="Invalid request")

@app.route('/forgotpassword', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'GET':
        return render_template('forgotpassword.html')
    if request.method == 'POST':
     email = request.form['email']
    
     cur = mydb.cursor(dictionary=True)
     cur.execute("SELECT * FROM users WHERE username = %s", (email,))
     user = cur.fetchone()
       
    if user:
        temp_password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
        hashed_temp_password = generate_password_hash(temp_password)
        
        cur.execute("UPDATE users SET password = %s WHERE username = %s", (hashed_temp_password, email))
        mydb.commit()
        #msg = Message("Password Reset", recipients=[email])
        # msg.body =f'''
        # A password reset has been requested for your account. 
        # Your temporary password is: {temp_password}
        # Please use this temporary password to login and change your password immediately.

        # If you did not request a password reset, please ignore this email and contact support.
        # Wishing you all the best, 
        # Support Team
        # '''
        # mail.send(msg)
        
        return render_template('/send_reset_link')
    else:
        mydb.close()
        return render_template('forgotpassword.html', error="No account found with that email.")

@app.route('/send_reset_link')
def send_reset_link():
       return render_template('send_reset_link.html')

# This is for applicants 
@app.route('/apply', methods=['GET', 'POST'])
def apply():
  if request.method == 'POST':
   # Connect to database
   cur = mydb.cursor(dictionary=True)
   while True:
    uid = f"{int(random.uniform(10000000,99999999))}"
    cur.execute("select * from applicants where uid = %s"%uid)
    result = cur.fetchone()
    if result == None:
      break
   # Info for entering into form
   uid = f"{int(random.uniform(10000000,99999999))}"
   name = request.form['applicantName']
   address = request.form['applicantAddress']
   gender = request.form['applicantGender']
   program = request.form['degreeFromApplicant']
   semester = request.form['applicantSemesterAndYear']

   ssid = request.form['applicantSsid']
   contact_info = request.form['applicantContactInfo']
   
   username = request.form['applicantUsername']
   password = request.form['applicantPassword']
   ms_gpa = request.form['MS_GPA']
   bs_ba_gpa = request.form['BS_BA_GPA']
   ms_year = request.form['MS_year']
   bs_ba_year = request.form['BS_BA_year']
   ms_uni = request.form['MS_uni']
   bs_uni = request.form['BS_uni']
   gre_verbal = request.form['GRE_verbal']
   gre_quantitative = request.form['GRE_quantitative']
   gre_examyear = request.form['GRE_examyear']
   gre_advanced = request.form['GRE_advanced']
   gre_subject = request.form['GRE_subject']
   toefl = request.form['TOEFL']
   toefl_date = request.form['TOEFL_date']
   ms_major = request.form['MS_major']

   bs_ba_major = request.form['BS_BA_major']
   interests = request.form['applicantAreasOfInterest']
   experience = request.form['applicantExperience']
   
   cur.execute("INSERT INTO applicants(uid, password, name, address, gender, program, semester) VALUES(%s, %s, %s, %s, %s, %s, %s)", (uid, password, name, address, gender, program, semester,))
   # Insert academic information
   cur.execute("select * from applicants where uid = %s"%uid)
   result = cur.fetchone()
   print(result)
   cur.execute("INSERT INTO academicinformation(uid, MS_GPA, BS_BA_GPA, MS_year, BS_BA_year, MS_uni, BS_uni, GRE_verbal, GRE_quantitative, GRE_examyear, GRE_advanced, GRE_subject, TOEFL, TOEFL_date, recommendations, transcript) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, 0)", 
   (uid, ms_gpa, bs_ba_gpa, ms_year, bs_ba_year, ms_uni, bs_uni, gre_verbal, gre_quantitative, gre_examyear, gre_advanced, gre_subject, toefl, toefl_date,))

   # Insert personal information
   cur.execute("INSERT INTO personalinformation(uid, SSID, contact_info, MS_major, BS_BA_major, interests, experience) VALUES(%s, %s, %s, %s, %s, %s, %s)", 
   (uid, ssid, contact_info, ms_major, bs_ba_major, interests, experience,))
   # Insert status info for user
   cur.execute("INSERT INTO checkstatus(uid, status) VALUES(%s, 'Application Incomplete')", (uid,))
   # Update database
   # mydatabase.commit()
   # Redirect to login after we're done
   return redirect(url_for('login'))
  else:
    # Return the application form page
    return render_template("applicant.html")

@app.route('/applicationstatus', methods=['GET', 'POST'])
def application_status():
  if request.method == 'GET':
      uid = session.get('uid')
      uid = session['user_id']
      cursor = mydb.cursor(dictionary=True)
      cursor.execute("SELECT status FROM checkstatus WHERE uid = %s", (uid,))
      result = cursor.fetchone()
      session['status'] = result
      return render_template('status.html', checkstatus=result)

@app.route('/matriculate', methods=['GET', 'POST'])
def matriculate():
   if request.method == 'POST':
      cursor = mydb.cursor(dictionary=True)
      cursor.execute("UPDATE users SET user_type = 'student' WHERE user_id = %s", (session['user_id'],))
      cursor.execute("INSERT INTO students (user_id, program, status) VALUES (%s, %s, 'matriculated')", 
                     (session['user_id'], session['program']))
      mydb.commit()
      return redirect(url_for('home.html'))
   return render_template('matriculate.html')

@app.route('/recommendations', methods=['GET', 'POST'])
def submit_recommendations():
  if 'username' in session:
    if session.get('user_type') == "applicant" or session.get('user_type') == "admin":
      if request.method == 'GET':
        return render_template('recommendations.html')
      if request.method == 'POST':
        recommender_name = request.form['recommenderName']
        recommender_email = request.form['recommenderEmail']
        recommender_profession = request.form['recommenderProfession']
        recommender_affiliation = request.form['recommenderAffiliation']
              
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT transcript FROM academicinformation WHERE uid = %s", (session.get('uid'),))
        applicantInfo = cursor.fetchone()
      if applicantInfo and applicantInfo['transcript']:
        cursor.execute("INSERT INTO recommendations(uid, rec_name, rec_email, rec_prof, rec_affiliation) VALUES(%s, %s, %s, %s, %s)",
                       (session.get('uid'), recommender_name, recommender_email, recommender_profession, recommender_affiliation))

         # If so change status to pending review
        status = "Application Complete and Under Review"
      else:
          # If not change status to recommendations missing
        cursor.execute("UPDATE academicinformation SET recommendations = 1 WHERE uid = %s", (session.get('uid'),))
        cursor.execute("UPDATE checkstatus SET status = %s WHERE uid = %s", (status, session.get('uid'),))
        mydb.commit()
        cursor.close()
        flash("Recommendation submitted successfully.")
        return render_template('recommendation_success.html', message="Recommendation submitted successfully.")
    else:
      return redirect(url_for('facultyhome'))
    
    
@app.route('/recommendation_success')
def recommendation_success():
    return render_template('recommendation_success.html') 

@app.route('/review/<user_id>', methods=['GET', 'POST'])
def review(uid):

  if 'username' in session:
    if session.get('user_type') == 'faculty' or session.get('user_type') == 'admin':
      cur = mydb.cursor(dictionary=True)

      cur.execute(
        #need to update 
      "SELECT applicants.uid, applicants.name, applicants.program, applicants.semester, academicinformation.MS_GPA, academicinformation.BS_BA_GPA, academicinformation.MS_year, academicinformation.BS_BA_year, academicinformation.MS_uni, academicinformation.BS_uni, academicinformation.GRE_verbal, academicinformation.GRE_quantitative, academicinformation.GRE_examyear, academicinformation.GRE_advanced, academicinformation.GRE_subject, academicinformation.TOEFL, academicinformation.TOEFL_date FROM applicants INNER JOIN academicinformation ON applicants.uid = academicinformation.uid WHERE applicants.uid = %s", 
      (uid,))
      applicantData = cur.fetchone()
      cur.execute("SELECT * FROM personalinformation WHERE personalinformation.uid = %s", (uid,))    
      applicantPersonal = cur.fetchone()
      cur.execute("SELECT * FROM recommendations WHERE recommendations.uid = %s", (uid,))
      applicantRecommendations = cur.fetchone()
      if request.method == 'POST':
        gas_committeerating = request.form['finalDecision']
        deficiency_courses = request.form['deficiencyCourses']
        reasons_for_rejection = request.form['reasonsForReject']
        gas_reviewer_comments = request.form['comments']
        letter1rating = request.form['letter1Rating']
        letter1generic = request.form['letter1Generic']
        letter1credible = request.form['letter1Credible']

        cur.execute(
          "INSERT INTO reviewform(user_id, recommendation1rating, recommendation1generic, recommendation1credible, recommendation1from, gac_rating, deficiencycourses, reasonsforrejection, reviewer_comments) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
            (uid, letter1rating, letter1generic, letter1credible, applicantRecommendations['rec_name'], gas_committeerating, deficiency_courses, reasons_for_rejection, gas_reviewer_comments,)
          )
        mydb.commit()
        return redirect(url_for('facultyhome'))

      return render_template("reviewform.html", applicantData=applicantData, applicantPersonal=applicantPersonal, applicantRecommendations=applicantRecommendations)

@app.route('/applicantlist')
def applicantlist():
  
  if 'username' in session: 
    if session.get('permissions') == "Review" or session.get('user_type') == "admin":
      cur = mydb.cursor(dictionary=True)

      cur.execute("SELECT applicants.name, applicants.uid, checkstatus.status FROM applicants INNER JOIN checkstatus ON applicants.uid = checkstatus.uid WHERE checkstatus.status = 'Application Complete and Under Review' ORDER BY applicants.uid ASC")
      applicants = cur.fetchall()
      return render_template("listApplicants.html", applicants = applicants)
    elif session.get('user_type') == "faculty":
      return redirect(url_for('facultyhome'))
    else: 
      return redirect(url_for('application_status'))

@app.route('/search_users', methods=['GET', 'POST'])
def search_users():
    if request.method == 'POST':
        search_query = request.form['search_query']
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SHOW TABLES LIKE 'checkstatus'")
        checkstatus_exists = cursor.fetchone()
        
        if checkstatus_exists:
            query = '''
                SELECT 
                    COUNT(*) AS number,
                    COUNT(*) - SUM(CASE WHEN c.status = 'rejected' THEN 1 ELSE 0 END) AS admit,
                    AVG(ac.GRE_verbal + ac.GRE_quantitative) AS GRE
                FROM 
                    applicants a
                    JOIN checkstatus c ON a.uid = c.uid
                    JOIN academicinformation ac ON a.uid = ac.uid
                WHERE 
                    (a.semester LIKE %s OR a.year LIKE %s OR a.degree_program LIKE %s)
            '''
        else:
            query = '''
                SELECT
                    COUNT(*) AS number,
                    COUNT(*) AS admit,
                    AVG(ac.GRE_verbal + ac.GRE_quantitative) AS GRE
                FROM
                    applicants a
                    JOIN academicinformation ac ON a.uid = ac.uid
                WHERE
                    (a.semester LIKE %s OR a.year LIKE %s OR a.degree_program LIKE %s)
            '''
        params = ('%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%')
        cursor.execute(query, params)
        search_results = cursor.fetchall()
        print(search_results)
        return render_template('search_users.html', users=search_results)
    return render_template('search_users.html')

@app.route('/search_user_gs', methods=['GET', 'POST'])
def search_user_gs():
    if 'user_id' in session and session['user_type'] in ['GS', 'Faculty']:
        if request.method == 'POST':
            search_query = request.form['search_query']
            cursor = mydb.cursor(dictionary=True)
            print(search_query)
            cursor.execute("SELECT * FROM applicants WHERE uid LIKE %s OR name LIKE %s", ('%' + search_query + '%', '%' + search_query + '%'))
            applicants = cursor.fetchall()
            print(applicants)
            cursor.close()
            return render_template('search_applicant.html', users=applicants)
        return render_template('search_applicant.html', users=None)
    else:
        return redirect(url_for('login'))

@app.route('/search_applicant', methods=['GET', 'POST'])
def search_applicant():
    if request.method == 'POST':
        search_query = request.form['search_query']

        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM applicants WHERE name LIKE %s OR uid = %s", ('%' + search_query + '%', search_query))

        search_results = cursor.fetchall()
        print(search_results)
        return render_template('search_applicant.html', users=search_results)
    return render_template('search_applicant.html') 

@app.route('/review')    
def reviewList():  
    if session.get('type') in ["faculty", "CAC/Chair"]:
      cur = mydb.cursor(dictionary=True)
      cur.execute("SELECT applicants.name, applicants.uid, checkstatus.status FROM applicants INNER JOIN checkstatus ON applicants.uid = checkstatus.uid WHERE checkstatus.status = 'Application Complete and Under Review' ORDER BY applicants.uid ASC")
      applicants = cur.fetchall()
      return render_template("reviewList.html", applicants = applicants) 
      # return redirect(url_for('facultyhome'))
    else:
      return redirect(url_for('application_status'))

@app.route('/updatetranscript', methods=['GET','POST'])
def updatetranscript():
  if 'username' in session: 
    if session.get('permissions') == "AcceptTranscript" or session.get('user_type') == "admin":
      # Connect to database
      cur = mydb.cursor(dictionary=True)
      if request.method == 'GET':
        return render_template("transcript.html")
      # If submitted
      if request.method == 'POST':
        uid = request.form['applicantUid']
        # Get status of recommendations
        cur.execute("SELECT recommendations FROM academicinformation WHERE user_id = %s", (uid,))
        applicantInfo = cur.fetchone()

        # Check if recommendations are in
        if applicantInfo["recommendations"] == 1:
          # If so change status to pending review
          status = "Application Complete and Under Review"
        else:
          # If not change status to recommendations missing
          status = "Application Incomplete - Recommendations missing"
        # Change transcript status to received
        cur.execute("UPDATE academicinformation SET transcript = 1 WHERE user_id = %s", (uid,))
        # Change status of application
        cur.execute("UPDATE checkstatus SET status = %s WHERE user_id = %s", (status, uid,))
        # Update database
        mydb.commit()
        return render_template("transcript.html")
    else:
      if session.get('user_type') == "faculty":
        return redirect(url_for('facultyhome'))
      if session.get('user_type') == "applicant":
        return redirect(url_for('application_status'))
  
@app.route('/finaldecision/<user_id>', methods=['GET','POST'])
def finaldecision(user_id):
  if 'username' in session:
    if session.get('finalDecision') == "Yes":
      cur = mydb.cursor(dictionary=True)
      app_uid = user_id
      cur.execute(
      "SELECT applicants.uid, applicants.name, applicants.program, applicants.semester, academicinformation.MS_GPA, academicinformation.BS_BA_GPA, academicinformation.MS_year, academicinformation.BS_BA_year, academicinformation.MS_uni, academicinformation.BS_uni, academicinformation.GRE_verbal, academicinformation.GRE_quantitative, academicinformation.GRE_examyear, academicinformation.GRE_advanced, academicinformation.GRE_subject, academicinformation.TOEFL, academicinformation.TOEFL_date FROM applicants INNER JOIN academicinformation ON applicants.uid = academicinformation.uid WHERE applicants.uid = %s", 
      (user_id,))
      applicantData = cur.fetchone()
      cur.execute("SELECT * FROM personalinformation WHERE personalinformation.uid = %s", (user_id,))    
      applicantPersonal = cur.fetchone()
      cur.execute("SELECT * FROM recommendations WHERE recommendations.uid = %s", (user_id,))
      applicantRecommendations = cur.fetchone()
      cur.execute("SELECT * FROM reviewform WHERE uid = %s", (user_id,))
      reviewdata = cur.fetchone()
      if request.method == 'POST':
        final_decision = request.form['decisionType']
      
        cur.execute("UPDATE checkstatus SET status = %s WHERE uid = %s", (final_decision, user_id))
        mydb.commit()
        return render_template('gs_finalDecision.html', user = app_uid)
      return render_template("finaldecision.html", app_uid = app_uid, reviewdata = reviewdata, applicantData = applicantData, applicantPersonal = applicantPersonal, applicantRecommendations = applicantRecommendations)
    
    elif session.get('user_type') == "faculty":
      return redirect(url_for('faculty'))
    else:
      return redirect(url_for('application_status'))
     
@app.route('/finaldecision')
def decisionList():
  if 'user_id' in session and session['user_type'] == 'CAC/Chair':
    if session.get('finalDecision') == "Yes":
      cur = mydb.cursor(dictionary=True)

      cur.execute("SELECT applicants.name, applicants.uid, checkstatus.status FROM applicants INNER JOIN checkstatus ON applicants.uid = checkstatus.uid INNER JOIN reviewform ON checkstatus.uid = reviewform.uid WHERE checkstatus.status = 'Application Complete and Under Review' ORDER BY applicants.uid ASC")
      applicants = cur.fetchall()
      return render_template('finalList.html', applicants=applicants)
    else:
       return redirect(url_for('facultyhome'))
  
# Admin page ------------------------------------------
@app.route('/search_users', methods=['GET', 'POST'])
def search_users():
    if request.method == 'POST':
        search_query = request.form['search_query']
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT count(*) number, count(*) - count(status = 'reject') admit, avg(GRE_verbal+GRE_quantitative) GRE FROM applicants a, checkstatus c, academicinformation ac WHERE a.uid = c.uid and a.uid = ac.uid and (semester LIKE %s OR year LIKE %s OR degree_program LIKE %s)", ('%' + search_query + '%', '%'+search_query+'%', '%'+search_query+'%'))
        search_results = cursor.fetchall()
        print(search_results)
        return render_template('search_users.html', users=search_results)

    return render_template('search_users.html')

@app.route('/admin/reset_db', methods=['GET', 'POST'])
def reset_db():
    if 'user_id' in session and session['user_type'] == 'admin':
        if request.method == 'POST':
            try:
                cursor = mydb.cursor()
                
                # Drop existing tables
                tables_to_drop = [
                    "registrations", "reviewform", "checkstatus", "recommendations", 
                    "personalinformation", "academicinformation", "catalog", "courses_schedule",
                    "form1", "instructors", "student_course", "alumni", "students", "enrollments",
                    "applicants_info", "applicants", "facultymembers", "courses", "advisor_assignments",
                    "form1_requests", "messages", "graduation_requests", "users"
                ]
                
                for table in tables_to_drop:
                    cursor.execute(f"DROP TABLE IF EXISTS {table}")
                
                # Create tables
                cursor.execute("""
                    CREATE TABLE users (
                      user_id     INT AUTO_INCREMENT,
                      username    VARCHAR(20) NOT NULL,
                      password    VARCHAR(20) NOT NULL,
                      fname       VARCHAR(50) NOT NULL,
                      lname       VARCHAR(50) NOT NULL,
                      address     VARCHAR(100),
                      DOB         DATE,
                      email       VARCHAR(50) NOT NULL,
                      user_type   VARCHAR(20) NOT NULL,
                      uid         VARCHAR(50) NOT NULL,
                      PRIMARY KEY (user_id),
                      INDEX idx_username (username)
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE applicants (
                      uid            varchar(50) not null,
                      password       varchar(50) not null,
                      name           varchar(50) not null,
                      address        varchar(50) not null,
                      gender         varchar(50) not null,
                      program        varchar(50) not null,
                      semester       varchar(50) not null,
                      year           varchar(4) not null,
                      degree_program varchar(100) not null,
                      status         varchar(5),
                      PRIMARY KEY (uid)
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE students (
                      user_id     INT(8) NOT NULL,
                      program     VARCHAR(20) NOT NULL,
                      thesis      TEXT,
                      grad_status ENUM('T', 'F') DEFAULT 'F' NOT NULL,
                      grad_semester VARCHAR(20) NOT NULL,
                      grad_year VARCHAR(10) NOT NULL,
                      uaf VARCHAR(1) NOT NULL,
                      PRIMARY KEY (user_id),
                      FOREIGN KEY (user_id) REFERENCES users(user_id)
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE enrollments (
                      user_id     INT(8) NOT NULL,
                      course_id   INT(5) NOT NULL,
                      PRIMARY KEY (user_id, course_id),
                      FOREIGN KEY (user_id) REFERENCES students(user_id),
                      FOREIGN KEY (course_id) REFERENCES courses(CourseID)
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE alumni (
                      user_id int(8) not null,
                      grad_year int(4) not null,
                      degree varchar(50) not null,
                      major varchar(50) not null,
                      primary key (user_id)
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE applicants_info (
                      uid VARCHAR(50) NOT NULL,
                      MS_GPA DECIMAL(3,2),
                      BS_BA_GPA DECIMAL(3,2) NOT NULL,
                      MS_year INTEGER,
                      BS_BA_year INTEGER NOT NULL,
                      MS_uni VARCHAR(50),
                      BS_uni VARCHAR(50) NOT NULL,
                      GRE_verbal INTEGER NOT NULL,
                      GRE_quantitative INTEGER NOT NULL,
                      GRE_examyear INTEGER NOT NULL,
                      GRE_advanced INTEGER,
                      GRE_subject VARCHAR(50),
                      TOEFL INTEGER,
                      TOEFL_date VARCHAR(50),
                      recommendations BOOLEAN NOT NULL,
                      transcript BOOLEAN NOT NULL,
                      PRIMARY KEY (uid)
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE student_course (
                      student_id int(8) NOT NULL,
                      IP_course_ID int(5) NOT NULL,
                      dname varchar(50) NOT NULL,
                      course_number int(5) NOT NULL,
                      title varchar(50) NOT NULL,
                      credits int(1) NOT NULL,
                      course_prereq varchar(50),
                      course_prereq2 varchar(50),
                      grade varchar(2) NOT NULL,
                      counts enum('T', 'F') DEFAULT 'F' NOT NULL,
                      form1 enum('T', 'F') DEFAULT 'F' NOT NULL,
                      PRIMARY KEY (student_id, IP_course_ID),
                      FOREIGN KEY (student_id) REFERENCES students(user_id)
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE instructors (
                      user_id INT(8) NOT NULL,
                      course_ID INT(5) NOT NULL,
                      PRIMARY KEY (user_id, course_ID),
                      FOREIGN KEY (course_ID) REFERENCES courses(CourseID),
                      FOREIGN KEY (user_id) REFERENCES users(user_id)
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE courses_schedule (
                      semester              VARCHAR(20) NOT NULL,
                      course_ID             INT(5) NOT NULL,
                      course_dname          VARCHAR(50) NOT NULL,
                      course_number         INT(5) NOT NULL,
                      course_title          VARCHAR(50) NOT NULL,
                      course_credits        INT(1) NOT NULL,
                      section_number        INT(1) NOT NULL,
                      meeting_time          VARCHAR(50) NOT NULL,
                      instructor_username   VARCHAR(50) NOT NULL,
                      PRIMARY KEY (semester, course_ID),
                      INDEX idx_course_ID (course_ID),
                      INDEX idx_dname (course_dname),
                      INDEX idx_course_number (course_number),
                      INDEX idx_course_title (course_title),
                      INDEX idx_course_credits (course_credits),
                      FOREIGN KEY (instructor_username) REFERENCES users(username)
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE academicinformation (
                      uid VARCHAR(50) NOT NULL,
                      MS_GPA DECIMAL(3,2),
                      BS_BA_GPA DECIMAL(3,2) NOT NULL,
                      MS_year INTEGER(4),
                      BS_BA_year INTEGER(4) NOT NULL,
                      MS_uni VARCHAR(50),
                      BS_uni VARCHAR(50) NOT NULL,
                      GRE_verbal INTEGER(3) NOT NULL,
                      GRE_quantitative INTEGER(3) NOT NULL,
                      GRE_examyear INTEGER(4) NOT NULL,
                      GRE_advanced INTEGER(3),
                      GRE_subject VARCHAR(50),
                      TOEFL INTEGER(3),
                      TOEFL INTEGER(3),
                      TOEFL_date VARCHAR(50),
                      recommendations BOOLEAN NOT NULL,
                      transcript BOOLEAN NOT NULL,
                      PRIMARY KEY (uid),
                      FOREIGN KEY (uid) REFERENCES applicants(uid)
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE personalinformation (
                      uid varchar(50) not null,
                      SSID varchar(50) not null,
                      contact_info varchar(50) not null,
                      MS_major varchar(50),
                      BS_BA_major varchar(50) not null,
                      interests varchar(50) not null,
                      experience varchar(50) not null,
                      PRIMARY KEY (uid),
                      FOREIGN KEY (uid) REFERENCES applicants(uid)
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE recommendations (
                      rec_id SERIAL PRIMARY KEY,
                      uid varchar(50) NOT NULL,
                      rec_name varchar(50) NOT NULL,
                      rec_email varchar(100) NOT NULL,
                      rec_prof varchar(50) NOT NULL,
                      rec_affiliation varchar(100) NOT NULL,
                      FOREIGN KEY (uid) REFERENCES applicants(uid)
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE checkstatus (
                      uid varchar(50) NOT NULL,
                      status varchar(50) NOT NULL,
                      PRIMARY KEY (uid),
                      FOREIGN KEY (uid) REFERENCES applicants(uid)
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE reviewform (
                      uid  varchar(50) not null,
                      recommendation1rating integer(1),
                      recommendation1generic char(1),
                      recommendation1credible char(1),
                      recommendation1from varchar(100) not NULL,
                      gac_rating varchar(50),
                      deficiencycourses varchar(255),
                      reasonsforrejection varchar(255),
                      reviewer_comments varchar(40),
                      PRIMARY KEY (uid),
                      FOREIGN KEY (uid) REFERENCES applicants(uid)
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE facultymembers (
                      user_id INT(8) NOT NULL,
                      role VARCHAR(50) NOT NULL,
                      name VARCHAR(50) NOT NULL,
                      permissions VARCHAR(50) NOT NULL,
                      finalDecision VARCHAR(50) NOT NULL,
                      PRIMARY KEY (role),
                      FOREIGN KEY (user_id) REFERENCES users(user_id)
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE registrations (
                      registration_id INTEGER PRIMARY KEY AUTO_INCREMENT,
                      student_id INT(8) NOT NULL,
                      course_id INT(5) NOT NULL,
                      FOREIGN KEY (student_id) REFERENCES users(user_id),
                      FOREIGN KEY (course_id) REFERENCES courses_schedule(course_ID)
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE catalog (
                      department VARCHAR(50) NOT NULL,
                      course_number INT(5) NOT NULL,
                      course_title VARCHAR(50) NOT NULL,
                      course_credits INT(1) NOT NULL,
                      course_prereq VARCHAR(50),
                      course_prereq2 VARCHAR(50),
                      FOREIGN KEY (department) REFERENCES courses_schedule(course_dname),
                      FOREIGN KEY (course_number) REFERENCES courses_schedule(course_number),
                      FOREIGN KEY (course_title) REFERENCES courses_schedule(course_title),
                      FOREIGN KEY (course_credits) REFERENCES courses_schedule(course_credits)
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE courses (
                      CourseID        INT(5) NOT NULL,
                      dname           VARCHAR(50) NOT NULL,
                      course_number   INT(5) NOT NULL,
                      title           VARCHAR(50) NOT NULL,
                      credits         INT(1) NOT NULL,
                      course_prereq   VARCHAR(50),
                      course_prereq2  VARCHAR(50),
                      PRIMARY KEY (CourseID)
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE form1 (
                        user_id INT,
                        course_id INT(5),
                        PRIMARY KEY(user_id, course_id),
                        FOREIGN KEY(user_id) REFERENCES users(user_id),
                        FOREIGN KEY(course_id) REFERENCES courses(CourseID)
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE advisor_assignments (
                        student_id INT(8),
                        faculty_id INT(8),
                        PRIMARY KEY(student_id, faculty_id),
                        FOREIGN KEY(student_id) REFERENCES users(user_id),
                        FOREIGN KEY(faculty_id) REFERENCES users(user_id)
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE messages (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        sender_id INT NOT NULL,
                        receiver_id INT NOT NULL,
                        subject TEXT NOT NULL,
                        body TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE form1_requests (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        student_id INT NOT NULL,
                        faculty_advisor_id INT NOT NULL,
                        status VARCHAR(3) NOT NULL, -- FAC, FAD, GSC, GSD, or "Approved"
                        FOREIGN KEY (student_id) REFERENCES users(user_id),
                        FOREIGN KEY (faculty_advisor_id) REFERENCES users(user_id)
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE graduation_requests (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        student_id INT NOT NULL,
                        faculty_advisor_id INT NOT NULL,
                        status VARCHAR(3) NOT NULL, -- FAC, FAD, GSC, GSD, or "Approved"
                        FOREIGN KEY (student_id) REFERENCES users(user_id),
                        FOREIGN KEY (faculty_advisor_id) REFERENCES users(user_id)
                    )
                """)

                cursor.execute("""
                    INSERT INTO users (user_id, username, password, fname, lname, address, DOB, email, user_type, uid) VALUES
                    (88767547, 'sara.almaouf', 'pass', 'Sara', 'Almaouf', 'Vienna, VA', '2004-09-11', 'sara.almaouf@gwu.edu', 'applicant', ''),
                    (78276378, 'jake.kat', 'pass', 'Jake', 'Kat', 'Tysons, VA', '2003-07-07', 'jake.kate@gwu.edu', 'student', ''),
                    (78307381, 'kate.joe', 'pass', 'Kate', 'Joe', 'Alexandia, VA', '2005-05-20', 'kate@gwu.edu', 'student', ''),
                    (88888888, 'holiday', 'pass', 'Billie', 'Holiday', 'Washington, D.C.', '2003-10-10', 'holiday@gwu.edu', 'student', ''),
                    (99999999, 'krall', 'pass', 'Diana', 'Krall', 'Woodbridge, VA', '2001-01-01', 'krall@gwu.edu', 'student', ''),
                    (72801643, 'Ouska', 'pass', 'Emily', 'Ouska', NULL, NULL, 'email1@email.com', 'instructor', ''),
                    (09526719, 'Edwards', 'pass', 'Ed', 'Edwards', NULL, NULL, 'email2@email.com', 'instructor', ''),
                    (78153610, 'Ross', 'pass', 'Bob', 'Ross', NULL, NULL, 'email3@email.com', 'instructor', ''),
                    (98145283, 'Doubtfire', 'pass', 'Euphegenia', 'Doubtfire', NULL, NULL, 'email4@email.com', 'instructor', ''),
                    (56283619, 'Parmer', 'pass', 'Gabe', 'Parmer', NULL, NULL, 'email5@email.com', 'instructor', ''),
                    (17826492, 'N', 'pass', 'Bhagirath', 'Narahari', NULL, NULL, 'narahari@gwu.edu', 'instructor', ''),
                    (96732691, 'C', 'pass', 'HyeongAh', 'Choi', NULL, NULL, 'choi@gwu.edu', 'instructor', ''),
                    (63736329, 'review.faculty', 'pass', 'Faculty', 'Reviewer', 'TESt, MA', '2000-04-07', 'test2@gwu.edu', 'reviewer', ''),
                    (63736319, 'roh.justin', 'pass', 'Justin', 'Roh', 'TESt, MA', '2000-05-07', 'test@gwu.edu', 'faculty', ''),
                    (73736319, 'kim.david', 'pass', 'David', 'Kim', 'Add, VA', '2000-04-07', 'david@gwu.edu', 'faculty', ''),
                    (83736319, 'Johnson.Liam', 'pass', 'Liam', 'Johnson', 'Boston, MA', '2002-01-27', 'liam@gwu.edu', 'faculty', ''),
                    (89173620, 'emma.holand', 'pass', 'Emma', 'Holand', 'Herndon, VA', '2005-04-16', 'emma.holand@gwu.edu', 'admin', ''),
                    (74742839, 'GradSec', 'pass', 'Grad', 'Sec', 'Fairfax, VA', '2002-08-02', 'GradSec@gwu.edu', 'secretary', ''),
                    (89234234, 'Alumni', 'pass', 'Alu', 'Mni', 'Arlington, VA', '2003-05-04', 'Alumni@gwu.edu', 'alumni', ''),
                    (82341508, 'AdCAC', 'pass', 'Ad', 'CAC', 'woodbridge, VA', '2003-07-02', 'AdCAC@gwu.edu', 'CAC/Chair', ''),
                    (12345678, 'new.student1', 'newpass1', 'New', 'Student1', '123 Fake St, Springfield', '1995-08-01', 'new.student1@university.edu', 'student', ''),
                    (23456789, 'new.student2', 'newpass2', 'New', 'Student2', '321 Fake St, Springfield', '1996-09-02', 'new.student2@university.edu', 'student', ''),
                    (55555555, 'mccartney', 'pass', 'Paul', 'McCartney', '789 Penny Lane, Liverpool', '2002-06-18', 'mccartney@gwu.edu', 'student', ''),
                    (66666666, 'harrison', 'pass', 'George', 'Harrison', '321 Abbey Road, London', '2001-02-25', 'harrison@gwu.edu', 'student', ''),
                    (44444444, 'starr', 'pass', 'Ringo', 'Starr', '654 Yellow Submarine St, Liverpool', '2000-07-07', 'starr@gwu.edu', 'student', ''),
                    (77777777, 'clapton', 'pass', 'Eric', 'Clapton', '456 Layla Ln, Surrey', '1999-03-30', 'clapton@gwu.edu', 'alumni', '')
                """)
                
                cursor.execute("""
                    INSERT INTO students (user_id, program, grad_status, grad_semester, grad_year, uaf) VALUES 
                    (78276378, 'Masters Program', 'T', 'Fall', '2026','F'),
                    (78307381, 'PhD', 'T', 'Fall','2026','T'),
                    (88888888, 'Masters Program', 'T','Summer','2027','T'),
                    (99999999, 'Masters Program', 'T','Fall','2027','T'),
                    (12345678, 'PhD', 'T', 'Fall', '2026','T'),
                    (23456789, 'Masters Program', 'T', 'Summer', '2026','T'),
                    (55555555, 'Masters Program', 'F', 'Fall', '2024', 'F'),
                    (66666666, 'Masters Program', 'F', 'Fall', '2024', 'F'),
                    (44444444, 'PhD', 'F', 'Fall', '2026', 'F')
                """)
                
                cursor.execute("""
                    INSERT INTO enrollments (user_id, course_id) VALUES 
                    (78276378, 1),
                    (78276378, 5),
                    (78276378, 9),
                    (78276378, 13),
                    (78276378, 17),
                    (78307381, 2),
                    (78307381, 6),
                    (78307381, 10),
                    (78307381, 14),
                    (78307381, 18),
                    (88888888, 2),
                    (88888888, 3)
                """)
                
                cursor.execute("""
                    INSERT INTO alumni (user_id, grad_year, degree, major) VALUES
                    (89234234, 2022, 'MS', 'Data Analytics'),
                    (77777777, 2014, 'MS', 'Computer Science')
                """)
                
                cursor.execute("""
                    INSERT INTO applicants (uid, password, name, address, gender, program, semester, year, degree_program, status) VALUES
                    ('A0000001', 'appPass1', 'Tom Smith', '1234 Elm St, Springfield', 'Male', 'Computer Science', 'Fall', '2024', 'PhD',''),
                    ('A0000002', 'appPass2', 'Jane Doe', '5678 Oak St, Springfield', 'Female', 'Electrical Engineering', 'Fall', '2024', 'Masters',''),
                    ('12312312', 'lennon', 'John Lennon', '123 Penny Lane, Liverpool', 'Male', 'Computer Science', 'Fall', '2024', 'PhD', 'completed'),  
                    ('66666667', 'starr', 'Ringo Starr', '456 Abbey Road, London', 'Male', 'Computer Science', 'Fall', '2024', 'Masters', 'incomplete'),
                    ('A0000003', 'appPass3', 'Alice Johnson', '123 Apple St, Metropolis', 'Female', 'Mechanical Engineering', 'Fall', '2024', 'Masters', 'accepted'),
                    ('A0000004', 'appPass4', 'Bob Franklin', '456 Pear St, Metropolis', 'Male', 'Physics', 'Fall', '2024', 'PhD', 'rejected'),
                    ('A0000005', 'appPass5', 'Carol White', '789 Banana St, Metroville', 'Female', 'Biology', 'Fall', '2024', 'Masters', ''),
                    ('A0000006', 'appPass6', 'David Green', '321 Kiwi Ln, Smalltown', 'Male', 'Chemistry', 'Fall', '2024', 'PhD', ''),
                    ('A0000007', 'appPass7', 'Erica Brown', '654 Melon St, Bigtown', 'Female', 'Mathematics', 'Fall', '2024', 'Masters', ''),
                    ('A0000008', 'appPass8', 'Frank Maple', '987 Grape St, Rivertown', 'Male', 'Environmental Science', 'Fall', '2024', 'PhD', ''),
                    ('A0000009', 'appPass9', 'Grace Pine', '369 Cherry Ln, Lakecity', 'Female', 'Statistics', 'Fall', '2024', 'Masters', 'accepted'),
                    ('A0000010', 'appPass10', 'Henry Oak', '258 Plum St, Hilltown', 'Male', 'Astronomy', 'Fall', '2024', 'PhD', ''),
                    ('A0000011', 'appPass11', 'Isla Cedar', '147 Peach St, Beachtown', 'Female', 'Philosophy', 'Fall', '2024', 'Masters', 'rejected'),
                    ('A0000012', 'appPass12', 'Jason Birch', '963 Apple St, Metropolis', 'Male', 'Mechanical Engineering', 'Fall', '2024', 'PhD', ''),
                    ('A0000013', 'appPass13', 'Kelly Spruce', '784 Pear St, Metropolis', 'Female', 'Physics', 'Fall', '2024', 'Masters', ''),
                    ('A0000014', 'appPass14', 'Liam Teak', '321 Banana St, Metroville', 'Male', 'Biology', 'Fall', '2024', 'PhD', ''),
                    ('A0000015', 'appPass15', 'Monica Fir', '456 Kiwi Ln, Smalltown', 'Female', 'Chemistry', 'Fall', '2024', 'Masters', 'accepted'),
                    ('A0000016', 'appPass16', 'Noah Elm', '789 Melon St, Bigtown', 'Male', 'Mathematics', 'Fall', '2024', 'PhD', ''),
                    ('A0000017', 'appPass17', 'Olivia Pine', '321 Grape St, Rivertown', 'Female', 'Environmental Science', 'Fall', '2024', 'Masters', ''),
                    ('A0000018', 'appPass18', 'Peter Ash', '654 Cherry Ln, Lakecity', 'Male', 'Statistics', 'Fall', '2024', 'PhD', 'rejected'),
                    ('A0000019', 'appPass19', 'Quinn Willow', '987 Plum St, Hilltown', 'Female', 'Astronomy', 'Fall', '2024', 'Masters', ''),
                    ('A0000020', 'appPass20', 'Ryan Hazel', '369 Peach St, Beachtown', 'Male', 'Philosophy', 'Fall', '2024', 'PhD', ''),
                    ('A0000021', 'appPass21', 'Sophia Mahogany', '258 Apple St, Metropolis', 'Female', 'Mechanical Engineering', 'Fall', '2024', 'Masters', ''),
                    ('A0000022', 'appPass22', 'Tyler Redwood', '147 Pear St, Metropolis', 'Male', 'Physics', 'Fall', '2024', 'PhD', '')
                """)
                
                cursor.execute("""
                    INSERT INTO applicants_info (uid, MS_GPA, BS_BA_GPA, MS_year, BS_BA_year, MS_uni, BS_uni, GRE_verbal, GRE_quantitative, GRE_examyear, GRE_advanced, GRE_subject, TOEFL, TOEFL_date, recommendations, transcript) VALUES
                    ('A0000001', NULL, 3.85, NULL, 2018, NULL, 'GWU', 160, 168, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
                    ('A0000002', NULL, 3.60, NULL, 2019, NULL, 'GWU', 158, 170, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
                    ('A0000003', NULL, 3.70, NULL, 2020, NULL, 'MIT', 155, 165, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
                    ('A0000004', 3.50, 3.90, 2020, 2020, 'Stanford', 'Stanford', 160, 162, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
                    ('A0000005', NULL, 3.80, NULL, 2021, NULL, 'Harvard', 158, 160, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
                    ('A0000006', 3.60, 3.65, 2020, 2020, 'Caltech', 'Caltech', 155, 160, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
                    ('A0000007', NULL, 3.75, NULL, 2020, NULL, 'Princeton', 150, 155, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
                    ('A0000008', 3.80, 3.90, 2021, 2021, 'Yale', 'Yale', 162, 170, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
                    ('A0000009', NULL, 3.85, NULL, 2021, NULL, 'Columbia', 159, 167, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
                    ('A0000010', 3.45, 3.50, 2020, 2020, 'UChicago', 'UChicago', 154, 159, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
                    ('A0000011', NULL, 3.95, NULL, 2020, NULL, 'UPenn', 161, 169, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
                    ('A0000012', 3.70, 3.80, 2021, 2021, 'Duke', 'Duke', 156, 163, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
                    ('A0000013', NULL, 3.60, NULL, 2020, NULL, 'Northwestern', 152, 158, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
                    ('A0000014', 3.55, 3.65, 2021, 2021, 'JHU', 'JHU', 157, 161, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
                    ('A0000015', NULL, 3.80, NULL, 2020, NULL, 'WashU', 160, 165, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
                    ('A0000016', 3.90, 3.95, 2020, 2020, 'Cornell', 'Cornell', 163, 168, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
                    ('A0000017', NULL, 3.70, NULL, 2021, NULL, 'Brown', 155, 160, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
                    ('A0000018', 3.85, 3.90, 2021, 2021, 'Dartmouth', 'Dartmouth', 159, 164, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
                    ('A0000019', NULL, 3.60, NULL, 2020, NULL, 'Vanderbilt', 154, 159, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
                    ('A0000020', 3.50, 3.55, 2020, 2020, 'Rice', 'Rice', 152, 158, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
                    ('A0000021', NULL, 3.75, NULL, 2021, NULL, 'Notre Dame', 158, 166, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE),
                    ('A0000022', 3.80, 3.85, 2020, 2020, 'Emory', 'Emory', 160, 167, 2023, NULL, NULL, NULL, NULL, TRUE, TRUE)
                    """)
                
                cursor.execute("""
                INSERT INTO student_course VALUES 
                (78307381, 4, 'CSCI', 6232, 'Networks 1', 3, NULL, NULL, 'IP', 'F', 'F'),
                (78307381, 8, 'CSCI', 6246, 'Compilers', 3, 'CSCI 6461', 'CSCI 6212', 'IP', 'F', 'F'),
                (78307381, 12, 'CSCI', 6262, 'Graphics 1', 3, NULL, NULL, 'IP', 'F', 'F'),
                (78307381, 16, 'CSCI', 6384, 'Cryptography 2', 3, 'CSCI 6284', NULL, 'IP', 'F', 'F'),
                (78307381, 20, 'CSCI', 6339, 'Embedded Systems', 3, 'CSCI 6461', 'CSCI 6212', 'IP', 'F', 'F'),
                (78276378, 1, 'CSCI', 6221, 'SW Paradigms', 3, NULL, NULL, 'IP', 'F', 'F'),
                (78276378, 5, 'CSCI', 6233, 'Networks 2', 3, 'CSCI 6232', NULL, 'IP', 'F', 'F'),
                (78276378, 9, 'CSCI', 6251, 'Cloud Computing', 3, 'CSCI 6461', NULL, 'IP', 'F', 'F'),
                (78276378, 13, 'CSCI', 6283, 'Security 1', 3, 'CSCI 6212', NULL, 'IP', 'F', 'F'),
                (78276378, 17, 'ECE', 6241, 'Communication Theory', 3, NULL, NULL, 'IP', 'F', 'F'),
                (89173620, 2, 'CSCI', 6461, 'Computer Architecture', 3, NULL, NULL, 'IP', 'F', 'F'),
                (89173620, 6, 'CSCI', 6241, 'Database 1', 3, NULL, NULL, 'IP', 'F', 'F'),
                (89173620, 10, 'CSCI', 6254, 'SW Engineering', 3, 'CSCI 6221', NULL, 'IP', 'F', 'F'),
                (89173620, 14, 'CSCI', 6284, 'Cryptography', 3, 'CSCI 6212', NULL, 'IP', 'F', 'F'),
                (89173620, 18, 'ECE', 6242, 'Information Theory', 2, NULL, NULL, 'IP', 'F', 'F'),
                (88888888, 2, 'CSCI', 6461, 'Computer Architecture', 3, NULL, NULL, 'IP', 'F', 'F'),
                (88888888, 3, 'CSCI', 6212, 'Algorithms', 3, NULL, NULL, 'IP', 'F', 'F'),
                (55555555, 1, 'CSCI', 6221, 'SW Paradigms', 3, NULL, NULL, 'A', 'F', 'F'),
                (55555555, 2, 'CSCI', 6461, 'Computer Architecture', 3, NULL, NULL, 'A', 'F', 'F'),
                (55555555, 3, 'CSCI', 6212, 'Algorithms', 3, NULL, NULL, 'A', 'F', 'F'),
                (55555555, 4, 'CSCI', 6232, 'Networks 1', 3, NULL, NULL, 'A', 'F', 'F'),
                (55555555, 5, 'CSCI', 6233, 'Networks 2', 3, 'CSCI 6232', NULL, 'A', 'F', 'F'),
                (55555555, 6, 'CSCI', 6241, 'Database 1', 3, NULL, NULL, 'B', 'F', 'F'),
                (55555555, 7, 'CSCI', 6242, 'Database 2', 3, 'CSCI 6241', NULL, 'B', 'F', 'F'),
                (55555555, 8, 'CSCI', 6246, 'Compilers', 3, 'CSCI 6461', 'CSCI 6212', 'B', 'F', 'F'),
                (55555555, 12, 'CSCI', 6262, 'Graphics 1', 3, NULL, NULL, 'B', 'F', 'F'),
                (55555555, 13, 'CSCI', 6283, 'Security 1', 3, 'CSCI 6212', NULL, 'B', 'F', 'F'),
                (66666666, 1, 'CSCI', 6221, 'SW Paradigms', 3, NULL, NULL, 'B', 'F', 'F'),
                (66666666, 2, 'CSCI', 6461, 'Computer Architecture', 3, NULL, NULL, 'B', 'F', 'F'),
                (66666666, 3, 'CSCI', 6212, 'Algorithms', 3, NULL, NULL, 'B', 'F', 'F'),
                (66666666, 4, 'CSCI', 6232, 'Networks 1', 3, NULL, NULL, 'B', 'F', 'F'),
                (66666666, 5, 'CSCI', 6233, 'Networks 2', 3, 'CSCI 6232', NULL, 'B', 'F', 'F'),
                (66666666, 6, 'CSCI', 6241, 'Database 1', 3, NULL, NULL, 'B', 'F', 'F'),
                (66666666, 7, 'CSCI', 6242, 'Database 2', 3, 'CSCI 6241', NULL, 'B', 'F', 'F'),
                (66666666, 13, 'CSCI', 6283, 'Security 1', 3, 'CSCI 6212', NULL, 'B', 'F', 'F'),
                (66666666, 14, 'CSCI', 6284, 'Cryptography', 3, 'CSCI 6212', NULL, 'B', 'F', 'F'),
                (66666666, 18, 'ECE', 6242, 'Information Theory', 2, NULL, NULL, 'C', 'F', 'F'),
                (44444444, 1, 'CSCI', 6221, 'SW Paradigms', 3, NULL, NULL, 'A', 'F', 'F'),
                (44444444, 2, 'CSCI', 6461, 'Computer Architecture', 3, NULL, NULL, 'A', 'F', 'F'),
                (44444444, 3, 'CSCI', 6212, 'Algorithms', 3, NULL, NULL, 'A', 'F', 'F'),
                (44444444, 4, 'CSCI', 6232, 'Networks 1', 3, NULL, NULL, 'A', 'F', 'F'),
                (44444444, 5, 'CSCI', 6233, 'Networks 2', 3, 'CSCI 6232', NULL, 'A', 'F', 'F'),
                (44444444, 6, 'CSCI', 6241, 'Database 1', 3, NULL, NULL, 'A', 'F', 'F'),
                (44444444, 7, 'CSCI', 6242, 'Database 2', 3, 'CSCI 6241', NULL, 'A', 'F', 'F'),
                (44444444, 8, 'CSCI', 6246, 'Compilers', 3, 'CSCI 6461', 'CSCI 6212', 'A', 'F', 'F'),
                (44444444, 9, 'CSCI', 6251, 'Cloud Computing', 3, 'CSCI 6461', NULL, 'A', 'F', 'F'),
                (44444444, 10, 'CSCI', 6254, 'SW Engineering', 3, 'CSCI 6221', NULL, 'A', 'F', 'F'), 
                (44444444, 11, 'CSCI', 6260, 'Multimedia', 3, NULL, NULL, 'A', 'F', 'F'),
                (44444444, 12, 'CSCI', 6262, 'Graphics 1', 3, NULL, NULL, 'A', 'F', 'F'),
                (77777777, 1, 'CSCI', 6221, 'SW Paradigms', 3, NULL, NULL, 'B', 'F', 'F'),
                (77777777, 3, 'CSCI', 6212, 'Algorithms', 3, NULL, NULL, 'B', 'F', 'F'),
                (77777777, 2, 'CSCI', 6461, 'Computer Architecture', 3, NULL, NULL, 'B', 'F', 'F'), 
                (77777777, 4, 'CSCI', 6232, 'Networks 1', 3, NULL, NULL, 'B', 'F', 'F'),
                (77777777, 5, 'CSCI', 6233, 'Networks 2', 3, 'CSCI 6232', NULL, 'B', 'F', 'F'),
                (77777777, 6, 'CSCI', 6241, 'Database 1', 3, NULL, NULL, 'B', 'F', 'F'),
                (77777777, 7, 'CSCI', 6242, 'Database 2', 3, 'CSCI 6241', NULL, 'B', 'F', 'F'),
                (77777777, 13, 'CSCI', 6283, 'Security 1', 3, 'CSCI 6212', NULL, 'A', 'F', 'F'),  
                (77777777, 14, 'CSCI', 6284, 'Cryptography', 3, 'CSCI 6212', NULL, 'A', 'F', 'F'),
                (77777777, 15, 'CSCI', 6286, 'Network Security', 3, 'CSCI 6283', 'CSCI 6232', 'A', 'F', 'F')
                """)
                
                cursor.execute("""
                    INSERT INTO instructors VALUES 
                    (72801643, 1),
                    (72801643, 2),
                    (72801643, 3),
                    (72801643, 4),
                    (09526719, 5),
                    (09526719, 6),
                    (09526719, 7),
                    (09526719, 8),
                    (78153610, 9),
                    (78153610, 10),
                    (78153610, 11),
                    (78153610, 12),
                    (98145283, 13),
                    (98145283, 14),
                    (98145283, 15),
                    (98145283, 16),
                    (56283619, 17),
                    (56283619,18),
                    (56283619, 19),
                    (56283619, 20),
                    (17826492, 2),
                    (96732691, 3),
                    (63736319, 1),
                    (63736319, 2),
                    (63736319, 3)
                    """)

                cursor.execute("""
                    INSERT INTO courses (CourseID, dname, course_number, title, credits, course_prereq, course_prereq2) VALUES
                    (1, 'CSCI', 6221, 'SW Paradigms', 3, null, null),
                    (2, 'CSCI', 6461, 'Computer Architecture', 3, null, null),
                    (3, 'CSCI', 6212, 'Algorithms', 3, null, null),
                    (4, 'CSCI', 6232, 'Networks 1', 3, null, null),
                    (5, 'CSCI', 6233, 'Networks 2', 3, 'CSCI 6232', null),
                    (6, 'CSCI', 6241, 'Database 1', 3, null, null),
                    (7, 'CSCI', 6242, 'Database 2', 3, 'CSCI 6241', null),
                    (8, 'CSCI', 6246, 'Compilers', 3, 'CSCI 6461', 'CSCI 6212'),
                    (9, 'CSCI', 6251, 'Cloud Computing', 3, 'CSCI 6461', null),
                    (10, 'CSCI', 6254, 'SW Engineering', 3, 'CSCI 6221', null),
                    (11, 'CSCI', 6260, 'Multimedia', 3, null, null),
                    (12, 'CSCI', 6262, 'Graphics 1', 3, null, null),
                    (13, 'CSCI', 6283, 'Security 1', 3, 'CSCI 6212', null),
                    (14, 'CSCI', 6284, 'Cryptography', 3, 'CSCI 6212', null),
                    (15, 'CSCI', 6286, 'Network Security', 3, 'CSCI 6283', 'CSCI 6232'),
                    (16, 'CSCI', 6384, 'Cryptography 2', 3, 'CSCI 6284', null),
                    (17, 'ECE', 6241, 'Communication Theory', 3, null, null),
                    (18, 'ECE', 6242, 'Information Theory', 2, null, null),
                    (19, 'MATH', 6210, 'Logic', 2, null, null),
                    (20, 'CSCI', 6339, 'Embedded Systems', 3, 'CSCI 6461', 'CSCI 6212')
                    """)
                    
                cursor.execute("""
                        INSERT INTO form1 (user_id, course_id) VALUES
                        (78276378, 1),
                        (78276378, 3),
                        (78307381, 2),
                        (78307381, 4)
                    """)
                    
                cursor.execute("""
                        INSERT INTO advisor_assignments (student_id, faculty_id) VALUES
                        (78276378, 63736319),
                        (78307381, 73736319),
                        (88888888, 73736319),
                        (99999999, 63736319),
                        (12345678, 83736319),
                        (23456789, 83736319),
                        (55555555, 17826492),
                        (66666666, 56283619),
                        (44444444, 56283619)
                    """)
                mydb.commit()
                flash("Database reset successfully.", "success")
            except mydb.connector.Error as error:
                flash("An error occurred while resetting the database.", "error")
                print(error)  # Print the error for debugging purposes
            finally:
                cursor.close()
        
        return render_template('reset_db.html')
    else:
        return redirect(url_for('sign_in'))
        
@app.route('/admin/create_account', methods=['GET', 'POST'])
def create_account():
    if 'user_id' in session and session['user_type'] == 'admin':
        if request.method == 'POST':
            user_id = request.form['user_id']
            user_type = request.form['user_type']
            password = request.form['password']
            fname = request.form['fname']
            lname = request.form['lname']
            email = request.form['email']
            address = request.form['address']

            cursor = mydb.cursor(dictionary=True)
            cursor.execute("INSERT INTO users (user_id, user_type, password, fname, lname, email, address) VALUES (%s, %s, %s, %s, %s, %s, %s)", (user_id, user_type, password, fname, lname, email, address))
            mydb.commit()
            cursor.close()

            return redirect(url_for('home'))
        return render_template('create_account.html')
    else:
        return redirect(url_for('login'))

@app.route('/admin/delete_account/<user_id>', methods=['POST'])
def delete_account(user_id):
    if 'user_id' in session and session['user_type'] == 'admin':
        try:
            cursor = mydb.cursor(dictionary=True)
            cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
            mydb.commit()
            cursor.close()
            return redirect(url_for('home'))
        except Exception as e:
            return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))
@app.route('/student')
def student():
    if 'user_type' in session and session['user_type'] == 'student':
        return render_template('student_dashboard.html')
    return redirect(url_for('login'))

@app.route('/facultyhome', methods=['GET', 'POST'])
def facultyhome():
    cursor = mydb.cursor(dictionary=True)
    
    if 'user_type' not in session:
        return redirect(url_for('sign_in'))
        
    user_type = session['user_type']
    uid = session['user_id']

    if user_type in ['MS', 'PHD']:

        cursor.execute("SELECT * FROM users WHERE user_id = %s", (uid,))
        user = cursor.fetchone()
        session['email'] = user['email']
        cursor.execute("SELECT * FROM student_courses WHERE user_id = %s AND grade = 'IP'", (uid,))
        courses = cursor.fetchall()

        return render_template("home.html", user=user, courses=courses)

    if user_type in ['instructor']:
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (uid,))
        facultyData = cursor.fetchone()
        cursor.execute("SELECT * FROM facultymembers WHERE user_id = %s", (uid,))
        courses = cursor.fetchone()
        courses = (courses['course_id'])
        if courses != None:
            cursor.execute("SELECT department, course_number, course_title, course_id FROM catalog WHERE course_id = %s", (courses,))
            courses = cursor.fetchone()
        return render_template("faculty_home.html", user=facultyData, classes = courses) 
    
    if user_type in ['Faculty_advisor']:
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (uid,))
        facultyData = cursor.fetchone()
        cursor.execute("SELECT * FROM faculty_classes WHERE user_id = %s", (uid,))
        courses = cursor.fetchone()
        courses = int(courses['course_id'])
       
        if courses != None:
            cursor.execute("SELECT * FROM catalog WHERE course_id = %s", (courses,))
            courses = cursor.fetchone()
           
        return render_template("home.html", user=facultyData, classes = courses) 

    if user_type in ['secretary']:
        print(session)
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (uid,))
        gradinfo = cursor.fetchone()
        session['permissions'] = "Review" 
        session['type'] = "secretary"
        session['finalDecision'] = "Yes"
        return render_template("secretary_view.html", user=gradinfo)
    
    if user_type in ['CAC/Chair']:
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (uid,))
        gradinfo = cursor.fetchone()
        session['permissions'] = "AcceptTranscript" 
        session['type'] = "CAC/Chair"
        session['finalDecision'] = "Yes"
        return render_template("CAC.html", user=gradinfo)
    
    if user_type in ['Faculty']:
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (uid,))
        gradinfo = cursor.fetchone()
        session['type'] = "faculty"
        session['permissions'] = "Review"
        return render_template("faculty.html")
    
    if user_type in ['Admin']:
        return render_template("admin_dashboard.html")
    

@app.route('/faculty')
def faculty():
    
    if 'user_id' in session:
        if session.get('user_type') == "faculty" or session.get('user_type') == "admin":
            cur = mydb.cursor(dictionary=True)
            cur.execute("SELECT * FROM users WHERE user_id = %s and user_type = %s", (session.get('user_id'), "Faculty"))
            userTraits = cur.fetchone()
            
            if userTraits:
                # session["permissions"] = userTraits["permissions"]
                # session["role"] = userTraits["role"]
                # session["finalDecision"] = userTraits["finalDecision"]
                cur.close()  
                return render_template('faculty_home.html', user=userTraits)
            else:
                cur.close()  
                return "No faculty has been found", 404
        else:
            return redirect(url_for('facultyhome'))  
    else:
        return redirect(url_for('facultyhome')) 
    

@app.route('/admin/users')
def users():
  if 'username' in session: 
    if session.get('type') == "admin":
      cur = mydb.cursor(dictionary=True)

      cur.execute("SELECT * FROM users ORDER BY uid ASC")
      users = cur.fetchall()
      return render_template("userlist.html", users=users)
  else:
    if session.get('type') == "faculty":
      return redirect(url_for('facultyhome'))
    if session.get('type') == "applicant":
      return redirect(url_for('application_status'))
    
@app.route('/admin/createusers', methods=['GET', 'POST'])
def createusers():
  if 'username' in session: 
    if session.get('type') == "admin":
      cur = mydb.cursor(dictionary=True)
      if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        name = request.form['name']
        permissions = request.form['permissions']
        finalDecision = request.form['finalDecision']
        uid = f"{int(random.uniform(10000000,99999999))}"

        # Insert into users
        cur.execute("INSERT INTO users(username, password, type, uid) VALUES(%s, %s, 'faculty', %s)", (username, password, uid,))
        # Insert into facultymembers
        cur.execute("INSERT INTO facultymembers(uid, role, name, permissions, finalDecision) VALUES(%s, %s, %s, %s, %s)", (uid, role, name, permissions, finalDecision))

        mydb.commit()
      return render_template("createUser.html")
  else:
    if session.get('type') == "faculty":
      return redirect(url_for('facultyhome'))
    if session.get('type') == "applicant":
      return redirect(url_for('application_status'))

@app.route('/admin/userstatus', methods=['GET', 'POST'])
def userstatus():
  if 'username' in session: 
    if session.get('type') == "admin":
      cur = mydb.cursor(dictionary=True)

      cur.execute("SELECT applicants.name, applicants.uid, checkstatus.status FROM applicants INNER JOIN checkstatus ON applicants.uid = checkstatus.uid ORDER BY applicants.uid ASC")
      applicants = cur.fetchall()
      return render_template("adminStatus.html", applicants = applicants)
    else:
      if session.get('type') == "faculty":
        return redirect(url_for('facultyhome'))
      if session.get('type') == "applicant":
        return redirect(url_for('application_status'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


#------------------------------------------------------------------------------#
# Regs functions:

@app.route('/catalog')
def get_courses():
  cur = mydb.cursor(dictionary=True)
  cur.execute("SELECT * FROM catalog")
  courses = cur.fetchall()
  cur.close()
  return render_template('catalog.html', courses=courses)

@app.route('/schedule')
def get_schedule(): 
  cursor = mydb.cursor(dictionary=True)
  cursor.execute("SELECT * FROM courses_schedule")
  schedule = cursor.fetchall()
  return render_template('schedule.html', schedule=schedule)

@app.route('/gradeAssign', methods=['GET', 'POST'])
def assignGrades():
  if 'user_type' not in session or session['user_type'] not in ['instructor', 'secretary', 'admin']:
     return redirect (url_for('login'))
  
  cur = mydb.cursor(dictionary=True)

  if request.method == 'POST':
     user_id = request.form['student_id']
     course_title = request.form['title']
     grade = request.form['grade']

     valid_grades = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'F']
     if grade not in valid_grades:
        flash("Invalid grade submitted.", "error")
        return redirect(url_for('assignGrades'))
     
     if session['user_type'] == 'instructor':
        cur.execute("SELECT sc.grade FROM student_course sc JOIN courses_schedule cs ON sc.title = cs.course_title WHERE sc.student_id = %s AND sc.title  = %s AND cs.instructor_username = %s", (user_id, course_title, session['username']))
    #  else:
    #     cur.execute("SELECT * FROM student_course WHERE student_id = %s AND IP_course_ID  = %s", (user_id, course_id))
        record = cur.fetchone()
        if record is None:
            flash("No record found or you do not have permission to grade this student.", "error")
            return redirect(url_for('assignGrades'))
        if record['grade'] != 'IP':
           flash("You have already assigned a grade to this student and cannot change it.", "error")
           return redirect(url_for('assignGrades'))
        cur.execute("UPDATE student_course SET grade = %s WHERE student_id = %s AND title = %s", (grade, user_id, course_title))

     elif session['user_type'] == 'secretary':
        cur.execute("SELECT * FROM student_course WHERE student_id = %s AND title = %s", (user_id, course_title))
        record = cur.fetchone()

        if record is None:
           cur.execute("INSERT INTO student_course (student_id, title, grade) VALUES (%s, %s, %s)", (user_id, course_title, grade))

        else:
           cur.execute("UPDATE student_course SET grade = %s WHERE student_id = %s AND title = %s", (grade, user_id, course_title))

     mydb.commit()
     flash("Grade has been successfully assigned.", "success")
     return redirect(url_for('assignGrades'))

  cur.execute("SELECT sc.student_id, sc.IP_course_ID , c.title, sc.grade FROM student_course sc LEFT JOIN courses c ON sc.IP_course_ID  = c.CourseID")
  student_courses = cur.fetchall()
  cur.close()

  return render_template('gradeAssign.html', student_course=student_courses)

@app.route('/studentProfile', methods=['GET', 'POST'])
def student_profile():
   if 'username' not in session:
      return redirect(url_for('login'))
   
   cur = mydb.cursor(dictionary=True)

   if request.method == 'POST':
      address = request.form.get('address')
      email = request.form.get('email')
      password = request.form.get('password')
      user_id = session['user_id']

      #updating student information when edited
      cur.execute("UPDATE users SET address = %s, email = %s, password = %s WHERE user_id = %s", (address, email, password, user_id))
      mydb.commit()

   cur.execute("SELECT u.username, u.fname, u.lname, u.address, u.email, s.program FROM users u LEFT JOIN students s ON u.user_id = s.user_id WHERE u.user_id = %s", (session['user_id'],))
   student_data = cur.fetchone()
   cur.close()

   return render_template('studentProfile.html', student_data=student_data)

@app.route('/registration', methods=['GET', 'POST'])
def registration():
 #  checking that person logged in is a student and not instructor
   if 'username' not in session or session['user_type'] != 'student':
     return redirect(url_for('login'))
   
   cur = mydb.cursor(dictionary=True)

   if request.method == 'POST':
     chosen_courseID = request.form['course_id']
     user_id = session['user_id']

#already registered:

  # check if student is already registered into chosen course
     cur.execute("SELECT * FROM student_course WHERE student_id = %s AND IP_course_ID = %s", (user_id, chosen_courseID))
     registration_exists = cur.fetchone()

#time conflicts:

     # fetch meeting time of selected course
     cur.execute("SELECT meeting_time FROM courses_schedule WHERE course_ID = %s", (chosen_courseID,))
     chosen_course_time = cur.fetchone()
     if chosen_course_time:
        chosen_course_time = chosen_course_time['meeting_time']
        cur.execute("SELECT cs.meeting_time FROM courses_schedule cs JOIN registrations r ON cs.course_id = r.course_id WHERE r.student_id = %s", (user_id,))
        # fetch meeting times of courses already registered into by student
        registered_courses_data = cur.fetchall()
        registered_course_times = [course['meeting_time'] for course in registered_courses_data]


#prereqs:

     # check if student had taken all prerequisites for the chosen course
     cur.execute("SELECT course_prereq, course_prereq2 FROM courses WHERE courseID = %s", (chosen_courseID,))
     prereq_data = cur.fetchone()
     prereq1 = prereq_data['course_prereq']
     prereq2 = prereq_data['course_prereq2']

     if prereq1:
       # check if prereq1 has been taken by student
       cur.execute("SELECT * FROM student_course WHERE IP_course_ID = %s AND student_id = %s", (prereq1, user_id))
       prereq1_exists = cur.fetchone()
       if not prereq1_exists:
         flash(f"You have not taken the required prerequisite course {prereq1}.", "error")
         return redirect(url_for('registration'))
     if prereq2:
       cur.execute("SELECT * FROM student_course WHERE IP_course_ID = %s AND student_id = %s", (prereq2, user_id))
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
        cur.execute("INSERT INTO student_course (student_id, IP_course_ID, grade) VALUES (%s, %s, 'IP')", (user_id, chosen_courseID))
        # cur.execute("INSERT INTO student_course (user_id, IP_course_ID, IP_course_dname, IP_course_number, IP_course_title, grade, IP_instructor_username) SELECT %s, course_ID, course_dname, course_number, course_title, 'IP', instructor_username FROM courses_schedule WHERE course_ID = %s", (student_id, chosen_courseID))
        # cur.execute("SELECT faculty_id FROM advisor_assignments WHERE student_id = %s", (session['user_id'],))
        # faculty_id = cur.fetchone()
        # cur.execute("INSERT INTO form1_requests (student_id, faculty_advisor_id, status) VALUES (%s, %s, 'pending')",
                    # (session['user_id'], faculty_id['faculty_id']))
        mydb.commit()
        flash("You have successfully registered into the course", "success")
        return redirect(url_for('registration'))

     cur.close()
  
  # fetch available courses for registration
   cur = mydb.cursor(dictionary=True)

   cur.execute("SELECT * FROM courses_schedule WHERE semester = 'Spring 2024'")
   available_courses = cur.fetchall()
   cur.close()

   return render_template('registration.html', courses=available_courses)

@app.route('/dropCourse', methods=['GET', 'POST'])
def dropCourse():
  if 'username' not in session or session['user_type'] != 'student':
    return redirect(url_for('login'))
   
  student_id = session['user_id']
  cur = mydb.cursor(dictionary=True)

  if request.method == 'POST':
    course_id = request.form.get('course_id')
    cur.execute("DELETE FROM student_course WHERE student_id = %s AND IP_course_ID = %s", (student_id, course_id))
    mydb.commit()
    flash("Course removed successfully", "success")

  cur.execute("SELECT cs.course_ID, cs.course_dname, cs.course_number, cs.course_title, cs.course_credits, cs.meeting_time, cs.instructor_username, cs.semester FROM student_course sc JOIN courses_schedule cs ON sc.IP_course_ID = cs.course_ID WHERE sc.student_id = %s", (student_id,))
  registered_courses = cur.fetchall()

  cur.close()
  return render_template('dropCourse.html', courses_schedule=registered_courses)


@app.route('/transcript', methods=['GET', 'POST'])
def transcript():
   if 'username' not in session:
    return redirect(url_for('login'))
   
   cur = mydb.cursor(dictionary=True)
   transcript_info = None
   if session['user_type'] == 'student':
     user_id = session['user_id']
     cur.execute("SELECT cs.course_ID, cs.course_title, cs.semester, sc.grade, cs.instructor_username, cs.course_dname, cs.course_number FROM student_course sc JOIN courses_schedule cs ON sc.IP_course_ID = cs.course_ID WHERE sc.student_id = %s", (user_id,))
     transcript_info = cur.fetchall()
   return render_template('studentTranscript.html', transcript_info=transcript_info)

@app.route('/facultyView_transcript', methods=['GET', 'POST'])
def facultyView_transcript():
  if 'username' not in session:
    return redirect(url_for('login'))

  transcript_info = None
  if request.method == 'POST':
     student_id = request.form['student_UID']

     username = session['username']
     user_role = session['user_type']

     cur = mydb.cursor(dictionary=True)

     if user_role == 'instructor':
        cur.execute("SELECT sc.IP_course_ID, sc.title, cs.semester, sc.grade, cs.instructor_username FROM student_course sc LEFT JOIN courses_schedule cs ON sc.IP_course_ID = cs.course_ID WHERE sc.student_id = %s AND sc.IP_course_ID IN (SELECT course_ID FROM courses_schedule WHERE instructor_username = %s)", (student_id, username))
        transcript_info = cur.fetchall()
        cur.close()
     elif user_role == 'secretary':
        cur.execute("SELECT sc.IP_course_ID, sc.title, cs.semester, sc.grade, cs.instructor_username FROM student_course sc LEFT JOIN courses_schedule cs ON sc.IP_course_ID = cs.course_ID WHERE sc.student_id = %s", (student_id,))
        transcript_info = cur.fetchall()
        cur.close()

  return render_template('facultyView_transcript.html', transcript_info=transcript_info)

# def get_course_roster(instructor_username, course_id):
#    cur = mydb.cursor(dictionary=True)

#    cur.execute("SELECT s.user_id, s.fname, s.lname, s.email FROM student_course sc JOIN users s ON sc.student_id = s.user_id JOIN courses_schedule cs ON sc.IP_course_ID = cs.course_ID WHERE cs.instructor_username = %s AND sc.IP_course_ID = %s", (instructor_username, course_id))

#    roster = cur.fetchall()
#    cur.close()

#    return roster

# @app.route('/course_roster/<int:course_id>', methods=['GET'])
# def course_roster(course_id):
#    if 'username' not in session or session['user_type'] != 'instructor':
#       return redirect(url_for('login'))
   
#    instructor_username = session['username']
#    roster = get_course_roster(instructor_username, course_id)

#    return render_template('course_roster.html', roster=roster, course_id=course_id)


# Form 1 ----------------
# Form 1 takes as input a session user_id, collects a list of courses, and submits the combination for faculty advisor review.
# It can be called using a hyperlink in student, which for now doesn't exist since the most recent student code has not been pushed
@app.route('/form1', methods=['GET', 'POST'])
def form1():
    has_session()

    cursor = mydb.cursor(dictionary=True)
    cursor.execute('SELECT * FROM courses')

    course_titles = []
    course_ids = []
    hours = []
    for row in cursor.fetchall():
        hours.append(row['credits'])
        course_titles.append(row['title'])
        course_ids.append(str(row['CourseID']))

    if request.method == 'GET':
        cursor.close()
        return render_template('form1.html', course_titles=course_titles, course_ids=course_ids)
    else:
        form1_clear(session["user_id"])
        graduate_request = 1 if request.form.get('graduate') == 'on' else 0
        ms_required = 0
        cs_credits = 0
        noncs_credits = 0
        for i in range(len(course_ids)):
            course = course_ids[i]
            hour = hours[i]

            if request.form.get(str(course), 'False') == "true":
                if str(course) in ["CSCI6212", "CSCI6221", "CSCI6461"]:
                    ms_required += 1
                if str(course).startswith('CSCI'):
                    cs_credits += hour
                else:
                    noncs_credits += hour

                cursor.execute("UPDATE student_course SET form1 = TRUE WHERE IP_course_ID = %s AND student_id = %s AND counts = 1",
                               (str(course), session['user_id']))
                cursor.execute("INSERT INTO form1(user_id, course_id) VALUES(%s, %s)", (session["user_id"], course))
                rows_updated = cursor.rowcount
                if rows_updated == 0 and graduate_request == 1:
                    return render_template('form1-failure.html', error="You put a course you don't have!")
            else:
                cursor.execute("UPDATE student_course SET form1 = FALSE WHERE IP_course_ID = %s AND student_id = %s AND counts = 1",
                               (str(course), session['user_id']))

        if session["user_type"] == "student":
            cursor.execute("UPDATE students SET grad_status = %s WHERE user_id = %s", (graduate_request, session["user_id"]))

        mydb.commit()
        error_dic = {0: 'You must complete all 3 core courses required for MS: CSCI 6212, CSCI 6221, and CSCI 6461',
                     1: "A minimum GPA of 3.0 is required to graduate with an MS",
                     2: "You must have completed 30 credit hours of coursework, with at most 2 non-cs courses as part",
                     3: "No more than 2 grades below B to graduate!",
                     4: "Minimum 3.5 GPA required to graduate with a PHD",
                     5: "You must have completed at least 36 credit hours, with at least 30 in CS",
                     6: "Not more than one grade below B to graduate with a PHD",
                     -1: "Success!"}
        passes_auto_requirements = 0
        if session["user_type"] == "student" and graduate_request == 1:
            passes_auto_requirements = ms_graduates()
        elif graduate_request == 1:
            passes_auto_requirements = phd_graduates()
        elif session["user_type"] == "student":
            total_credits_count = 0
            if noncs_credits > 5:
                total_credits_count = cs_credits + 5
            else:
                total_credits_count = cs_credits + noncs_credits
            if total_credits_count >= 30 and ms_required == 3:
                passes_auto_requirements = -1
            elif total_credits_count >= 30 and ms_required < 3:
                passes_auto_requirements = 0
            else:
                passes_auto_requirements = 2
        else:
            if cs_credits + noncs_credits >= 36:
                passes_auto_requirements = -1
            else:
                passes_auto_requirements = 5

        if passes_auto_requirements == -1:
            faculty_advisor_id = get_faculty_advisor_id(session['user_id'])

            cursor.execute("INSERT INTO form1_requests (student_id, faculty_advisor_id, status) VALUES (%s, %s, %s)",
                           (session['user_id'], faculty_advisor_id, 'FAC'))
            mydb.commit()

            subject = "Form 1 Submission"
            body = f"Student {session['user_id']} has submitted Form 1 for your approval."
            send_notification(session['user_id'], faculty_advisor_id, subject, body)

            return render_template('form1-success.html')
        else:
            return render_template('form1-failure.html', error=error_dic.get(passes_auto_requirements))
        
  # add student side addmission decision function
@app.route('/applicant_admission_decision/<applicant_uid>', methods=['POST'])
def applicant_admission_decision(applicant_uid):
    decision = request.form.get('decision')  
    
    cursor = mydb.cursor(dictionary=True)
    
    if decision == 'accept':
        cursor.execute("UPDATE applicants SET application_status='accepted' WHERE uid=%s", (applicant_uid,))
        cursor.close()
        mydb.commit()
        flash('You have accepted the admission offer.Please make your deposit.')
        return redirect(url_for('deposit', applicant_uid=applicant_uid))
    
    elif decision == 'decline':
        cursor.execute("UPDATE applicants SET application_status='declined' WHERE uid=%s", (applicant_uid,))
        cursor.close()
        mydb.commit()
        flash('You have declined the admission offer.')
        return redirect(url_for('application_status', applicant_uid=applicant_uid))

    flash('Invalid decision.')
    return redirect(url_for('application_status', applicant_uid=applicant_uid))


@app.route('/accept_offer', methods=["GET", "POST"])
def accept_offer():
    if request.method == "POST":
        uid = request.form.get('uid')
        if not uid:
            return "Error: No UID provided", 400  

        cur = mydb.cursor(dictionary=True) 
        user_id = generate_user_id()
        cur.execute("UPDATE applicants SET user_id = %s WHERE uid = %s", (user_id, uid))
        cur.execute("UPDATE academicinformation SET user_id = %s WHERE uid = %s", (user_id, uid))
        cur.execute("UPDATE recommendations SET user_id = %s WHERE uid = %s", (user_id, uid))
        cur.execute("UPDATE checkstatus SET user_id = %s WHERE uid = %s", (user_id, uid))
        mydb.commit()
        cur.close()
        return redirect(url_for('home'))

    return "Invalid request", 405


# add pay deposit function 
@app.route('/pay_deposit', methods=['POST'])
def pay_deposit():
    amount = request.form['amount']
    if not amount:
        flash("Please enter an amount to pay.")
        return redirect(url_for('index'))
    flash(f"Deposit of ${amount} has been processed successfully!")
    return redirect(url_for('index'))

@app.route('/update_info', methods=['GET', 'POST'])
def update_info():
    if request.method == 'POST':
        new_password = request.form['newPassword']
        new_address = request.form['newAddress']
        user_id = session['user_id']
        cursor = mydb.cursor()
        cursor.execute('UPDATE users SET password = %s, address = %s WHERE user_id = %s', 
                       (new_password, new_address, user_id))
        mydb.commit()
        flash("Your information has been updated successfully.")
        cursor.close()
        return redirect(url_for('update_info'))
    return render_template('update_personal_information.html')


#------------------------------GS ----------------------
@app.route('/secretary_view')
def secretary_view():
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("""
        SELECT u.user_id, u.fname, u.lname, u.email, 
               CONCAT(a.fname, ' ', a.lname) AS advisor_name,
               s.grad_status, s.program
        FROM users u
        LEFT JOIN students s ON u.user_id = s.user_id
        LEFT JOIN advisor_assignments aa ON u.user_id = aa.student_id
        LEFT JOIN users a ON aa.faculty_id = a.user_id
        WHERE u.user_type = 'student' AND u.user_id NOT IN (SELECT user_id FROM alumni)
    """)
    students = cursor.fetchall()
    cursor.execute("SELECT user_id, fname, lname FROM users WHERE user_type = 'faculty'")
    advisors = cursor.fetchall()
    cursor.close()
    return render_template('secretary_view.html', students=students, advisors=advisors)

@app.route('/graduate_student', methods=['POST'])
def graduate_student():
    if request.method == 'POST':
        student_id = request.form['student_id']
        
        cursor = mydb.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM students WHERE user_id = %s", (student_id,))
        student = cursor.fetchone()
        
        if student:
            cursor.execute("INSERT INTO alumni (user_id, grad_year, degree, major) VALUES (%s, %s, %s, %s)",
                           (student_id, '2024', student['program'], 'Computer Science'))
            cursor.execute("DELETE FROM students WHERE user_id = %s", (student_id,))
            cursor.execute("DELETE FROM advisor_assignments WHERE student_id = %s", (student_id,))
            cursor.execute("DELETE FROM form1 WHERE user_id = %s", (student_id,))
            cursor.execute("DELETE FROM student_course WHERE student_id = %s", (student_id,))
            cursor.execute("DELETE FROM enrollments WHERE user_id = %s", (student_id,))
            mydb.commit()
            session.clear()
            flash("Congratulations! You have successfully graduated.")
            return redirect(url_for('login'))
        
        cursor.close()
        
    return redirect(url_for('home'))

@app.route('/graduate_applicants', methods=['GET', 'POST'])
def graduate_applicants():
    if request.method == 'POST':
        semester = request.form['semester']
        year = request.form['year']
        degree_program = request.form['degreeProgram']
        
        cursor = mydb.cursor(dictionary=True)
        query = "SELECT * FROM applicants WHERE 1=1"
        params = []
        
        if semester:
            query += " AND semester = %s"
            params.append(semester)
        if year:
            query += " AND year = %s"
            params.append(year)
        if degree_program:
            query += " AND program = %s"
            params.append(degree_program)
        
        cursor.execute(query, params)
        applicants = cursor.fetchall()
        cursor.close()
        
        return render_template('graduate_applicants.html', applicants=applicants)
    
    return render_template('graduate_applicants.html')

@app.route('/applicant_statistics', methods=['GET', 'POST'])
def applicant_statistics():
    if request.method == 'POST':
        semester = request.form.get('semester') or None
        year = request.form.get('year') or None
        degree_program = request.form.get('degreeProgram') or None
        query = """
        SELECT
            COUNT(*) AS total_applicants,
            SUM(CASE WHEN status = 'accepted' THEN 1 ELSE 0 END) AS total_admitted,
            SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) AS total_rejected,
            COALESCE(AVG(CASE WHEN status = 'accepted' THEN GRE_quantitative + GRE_verbal ELSE NULL END), 0) AS avg_gre_score
        FROM
            applicants
            LEFT JOIN applicants_info ON applicants.uid = applicants_info.uid
        WHERE
            (semester = %s OR %s IS NULL)
            AND (year = %s OR %s IS NULL)
            AND (degree_program = %s OR %s IS NULL)
        """
        cursor = mydb.cursor(dictionary=True)
        cursor.execute(query, (semester, semester, year, year, degree_program, degree_program))
        statistics = cursor.fetchone()
        cursor.close()
        
        return render_template('applicant_statistics.html', statistics=statistics)
    return render_template('applicant_statistics.html')

@app.route('/graduating_students', methods=['GET', 'POST'])
def graduating_students():
    if request.method == 'POST':
        semester = request.form['semester']
        year = request.form['year']
        degree_program = request.form['degreeProgram']
        
        cursor = mydb.cursor(dictionary=True)
        query = "SELECT u.fname, u.lname, u.email FROM users u JOIN students s ON u.user_id = s.user_id WHERE s.grad_status = 'T' AND 1=1"
        params = []
        
        if semester:
            query += " AND s.grad_semester = %s"
            params.append(semester)
        if year:
            query += " AND s.grad_year = %s"
            params.append(year)
        if degree_program:
            query += " AND s.program = %s"
            params.append(degree_program)
        
        cursor.execute(query, params)
        graduating_students = cursor.fetchall()
        cursor.close()
        
        return render_template('graduating_students.html', graduating_students=graduating_students)
    
    return render_template('graduating_students.html')

@app.route('/change_advisor', methods=['POST'])
def change_advisor():
    if request.method == 'POST':
        student_id = request.form['student_id']
        new_advisor_id = request.form['new_advisor_id']
        
        cursor = mydb.cursor()
        cursor.execute("UPDATE advisor_assignments SET faculty_id = %s WHERE student_id = %s", (new_advisor_id, student_id))
        mydb.commit()
        cursor.close()
        
        return redirect(url_for('secretary_view'))
    
@app.route('/alumni', methods=['GET', 'POST'])
def alumni():
    if request.method == 'POST':
        year = request.form.get('year', '').strip()
        degree_program = request.form.get('degreeProgram', '').strip()
        
        cursor = mydb.cursor(dictionary=True)
        query = "SELECT u.fname, u.lname, u.email FROM users u JOIN alumni a ON u.user_id = a.user_id WHERE 1=1"
        params = []
        
        if year:
            query += " AND a.grad_year = %s"
            params.append(year)
        if degree_program:
            query += " AND a.degree = %s"
            params.append(degree_program)
        
        cursor.execute(query, params)
        alumni = cursor.fetchall()
        cursor.close()
        
        return render_template('alumni.html', alumni=alumni)
    
    return render_template('alumni.html')

#---------------------UAF---------------------
@app.route('/uaf', methods=['GET', 'POST'])
def uaf():
    if 'username' in session and session['user_type'] == 'student':
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT CourseID, title FROM courses")
        courses = cursor.fetchall()
        cursor.close()
        return render_template('uaf.html', courses=courses)
    return redirect(url_for('home'))

@app.route('/submit_uaf', methods=['POST'])
def submit_uaf():
    if 'username' in session and session['user_type'] == 'student':
        selected_courses = request.form.getlist('selected_courses')
        student_id = session['user_id']
        
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT faculty_id FROM advisor_assignments WHERE student_id = %s", (student_id,))
        advisor = cursor.fetchone()
        
        if advisor:
            advisor_id = advisor['faculty_id']
            subject = "UAF Form Submission"
            body = f"Student {student_id} has submitted the UAF form with the following courses: {', '.join(selected_courses)}"
            cursor.execute("INSERT INTO messages (sender_id, receiver_id, subject, body) VALUES (%s, %s, %s, %s)",
                           (student_id, advisor_id, subject, body))
            mydb.commit()
            flash("UAF form submitted successfully. Waiting for faculty advisor approval.")
        else:
            flash("No faculty advisor assigned. Please contact the administration.")
        
        cursor.close()
    
    return redirect(url_for('home'))

@app.route('/approve_uaf/<int:message_id>/<decision>', methods=['POST'])
def approve_uaf(message_id, decision):
    if 'username' in session and session['user_type'] == 'faculty':
        cursor = mydb.cursor(dictionary=True)
        
        cursor.execute("SELECT sender_id FROM messages WHERE id = %s", (message_id,))
        message = cursor.fetchone()
        
        if message:
            student_id = message['sender_id']
            
            if decision == 'approve':
                cursor.execute("UPDATE students SET uaf = 'T' WHERE user_id = %s", (student_id,))
                subject = "UAF Form Approved"
                body = "Your UAF form has been approved by your faculty advisor."
            else:
                subject = "UAF Form Declined"
                body = "Your UAF form has been declined by your faculty advisor. Please submit a new form."
            
            cursor.execute("INSERT INTO messages (sender_id, receiver_id, subject, body) VALUES (%s, %s, %s, %s)",
                           (session['user_id'], student_id, subject, body))
            mydb.commit()
        cursor.close()
    
    return redirect(url_for('home'))

# ------------------inbox system ------------------
@app.route('/inbox')
def inbox():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    user_type = session['user_type']

    cursor = mydb.cursor(dictionary=True)

    cursor.execute('SELECT * FROM messages WHERE receiver_id = %s ORDER BY timestamp DESC', (user_id,))
    messages = cursor.fetchall()

    if user_type == 'faculty':
        cursor.execute("SELECT m.id, m.sender_id, m.subject, m.body FROM messages m "
                       "JOIN advisor_assignments aa ON m.sender_id = aa.student_id "
                       "WHERE aa.faculty_id = %s AND m.subject LIKE 'UAF Form%'", (user_id,))
        uaf_messages = cursor.fetchall()

        cursor.execute("SELECT fr.id, fr.student_id, fr.status, CONCAT(s.fname, ' ', s.lname) AS student_name "
                       "FROM form1_requests fr "
                       "JOIN users s ON fr.student_id = s.user_id "
                       "WHERE fr.faculty_advisor_id = %s AND fr.status = 'FAC'", (user_id,))
        form1_requests = cursor.fetchall()

        cursor.execute("SELECT gr.id, gr.student_id, gr.status, CONCAT(s.fname, ' ', s.lname) AS student_name "
                       "FROM graduation_requests gr "
                       "JOIN users s ON gr.student_id = s.user_id "
                       "WHERE gr.faculty_advisor_id = %s AND gr.status = 'FAC'", (user_id,))
        graduation_requests = cursor.fetchall()
    elif user_type == 'secretary':
        uaf_messages = []

        cursor.execute("SELECT fr.id, fr.student_id, fr.status, CONCAT(s.fname, ' ', s.lname) AS student_name "
                       "FROM form1_requests fr "
                       "JOIN users s ON fr.student_id = s.user_id "
                       "WHERE fr.status = 'GSC'")
        form1_requests = cursor.fetchall()

        cursor.execute("SELECT gr.id, gr.student_id, gr.status, CONCAT(s.fname, ' ', s.lname) AS student_name "
                       "FROM graduation_requests gr "
                       "JOIN users s ON gr.student_id = s.user_id "
                       "WHERE gr.status = 'GSC'")
        graduation_requests = cursor.fetchall()
    else:
        uaf_messages = []
        form1_requests = []
        graduation_requests = []

    cursor.close()

    return render_template('inbox.html', messages=messages, uaf_messages=uaf_messages, form1_requests=form1_requests,
                           graduation_requests=graduation_requests, user_type=user_type)

@app.route('/approve_form1/<int:request_id>/<decision>', methods=['POST'])
def approve_form1(request_id, decision):
    if 'user_id' not in session or session['user_type'] not in ['faculty', 'secretary']:
        return redirect(url_for('login'))
    
    cursor = mydb.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM form1_requests WHERE id = %s", (request_id,))
    request = cursor.fetchone()
    
    if request:
        student_id = request['student_id']
        faculty_advisor_id = request['faculty_advisor_id']
        
        if decision == 'approve':
            if session['user_type'] == 'faculty':
                cursor.execute("UPDATE form1_requests SET status = 'GSC' WHERE id = %s", (request_id,))
                subject = "Form 1 Approved by Faculty Advisor"
                body = f"Your Form 1 has been approved by your faculty advisor."
                send_notification(faculty_advisor_id, student_id, subject, body)
                
                graduate_secretary_id = find_graduate_secretary_id()
                subject = "Form 1 Approval Request"
                body = f"Faculty advisor {faculty_advisor_id} has approved Form 1 for student {student_id}. Please review and make a decision."
                send_notification(faculty_advisor_id, graduate_secretary_id, subject, body)
            else:
                cursor.execute("UPDATE form1_requests SET status = 'Approved' WHERE id = %s", (request_id,))
                cursor.execute("UPDATE students SET grad_status = 'T' WHERE user_id = %s", (student_id,))
                subject = "Form 1 Approved by Graduate Secretary"
                body = "Your Form 1 has been approved by the graduate secretary."
                send_notification(session['user_id'], student_id, subject, body)
                send_notification(session['user_id'], faculty_advisor_id, subject, body)
        else:
            if session['user_type'] == 'faculty':
                cursor.execute("UPDATE form1_requests SET status = 'FAD' WHERE id = %s", (request_id,))
                subject = "Form 1 Declined by Faculty Advisor"
                body = "Your Form 1 has been declined by your faculty advisor."
                send_notification(faculty_advisor_id, student_id, subject, body)
            else:  # graduate secretary
                reason = request.form.get('reason', '')
                cursor.execute("UPDATE form1_requests SET status = 'GSD' WHERE id = %s", (request_id,))
                subject = "Form 1 Declined by Graduate Secretary"
                body = f"Your Form 1 has been declined by the graduate secretary for the following reason: {reason}"
                send_notification(session['user_id'], student_id, subject, body)
                send_notification(session['user_id'], faculty_advisor_id, subject, body)
        
        mydb.commit()
    
    cursor.close()
    
    return redirect(url_for('inbox'))

@app.route('/request_graduation')
def request_graduation():
    if 'user_id' not in session or session['user_type'] != 'student':
        return redirect(url_for('login'))
    
    cursor = mydb.cursor(dictionary=True)
    
    cursor.execute("SELECT grad_status FROM students WHERE user_id = %s", (session['user_id'],))
    student = cursor.fetchone()
    
    if student and student['grad_status'] == 'T':
        faculty_advisor_id = get_faculty_advisor_id(session['user_id'])
        
        subject = "Graduation Request"
        body = f"Student {session['user_id']} has requested graduation. Please review and make a decision."
        send_notification(session['user_id'], faculty_advisor_id, subject, body)
        
        cursor.execute("INSERT INTO graduation_requests (student_id, faculty_advisor_id, status) VALUES (%s, %s, %s)",
                       (session['user_id'], faculty_advisor_id, 'FAC'))
        mydb.commit()
        
        flash("Graduation request submitted successfully. Waiting for faculty advisor approval.")
    else:
        flash("You are not eligible to request graduation.")
    
    cursor.close()
    
    return redirect(url_for('home'))

@app.route('/approve_graduation/<int:request_id>/<decision>', methods=['POST'])
def approve_graduation(request_id, decision):
    if 'user_id' not in session or session['user_type'] not in ['faculty', 'secretary']:
        return redirect(url_for('login'))
    
    cursor= mydb.cursor(dictionary=True)
    cursor.execute("SELECT * FROM graduation_requests WHERE id = %s", (request_id,))
    request =cursor.fetchone()
    
    if request:
        student_id = request['student_id']
        faculty_advisor_id = request['faculty_advisor_id']
        
        if decision == 'approve':
            if session['user_type'] == 'faculty':
                cursor.execute("UPDATE graduation_requests SET status = 'GSC' WHERE id = %s", (request_id,))
                subject = "Graduation Request Approved by Faculty Advisor"
                body = f"Your graduation request has been approved by your faculty advisor."
                send_notification(faculty_advisor_id, student_id, subject, body)
                
                graduate_secretary_id = find_graduate_secretary_id()
                if graduate_secretary_id is not None:
                    subject = "Graduation Approval Request"
                    body = f"Faculty advisor {faculty_advisor_id} has approved the graduation request for student {student_id}. Please review and make a decision."
                    send_notification(faculty_advisor_id, graduate_secretary_id, subject, body)
                else:
                    print("No graduate secretary found.")
            else:
                cursor.execute("UPDATE graduation_requests SET status = 'Approved' WHERE id = %s", (request_id,))
                cursor.execute("UPDATE students SET grad_status = 'T' WHERE user_id = %s", (student_id,))
                subject ="Graduation Request Approved by Graduate Secretary"
                body = "Your graduation request has been approved by the graduate secretary."
                send_notification(session['user_id'], student_id, subject, body)
                
                if faculty_advisor_id is not None:
                    send_notification(session['user_id'], faculty_advisor_id, subject, body)
                else:
                    # Handle the case when faculty advisor is not found
                    print("Faculty advisor not found.")
        else:
            if session['user_type'] == 'faculty':
                cursor.execute("UPDATE graduation_requests SET status = 'FAD' WHERE id = %s", (request_id,))
                subject = "Graduation Request Declined by Faculty Advisor"
                body = "Your graduation request has been declined by your faculty advisor."
                send_notification(faculty_advisor_id, student_id, subject, body)
            else:
                reason = request.form.get('reason', '')
                cursor.execute("UPDATE graduation_requests SET status = 'GSD' WHERE id = %s", (request_id,))
                subject = "Graduation Request Declined by Graduate Secretary"
                body = f"Your graduation request has been declined by the graduate secretary for the following reason: {reason}"
                send_notification(session['user_id'], student_id, subject, body)
                
                if faculty_advisor_id is not None:
                    send_notification(session['user_id'], faculty_advisor_id, subject, body)
                else:
                    # Handle the case when faculty advisor is not found
                    print("Faculty advisor not found.")
        
        mydb.commit()
    else:
        # Handle the case when the graduation request is not found
        print("Graduation request not found.")
    
    cursor.close()
    
    return redirect(url_for('inbox'))

@app.route('/send_message', methods=['GET', 'POST'])
def send_message():
    if request.method == 'POST':
        if 'user_id' in session:
            sender_id = session['user_id']
            receiver_id = request.form['receiver_id']
            subject = request.form['subject']
            body = request.form['body']
            cursor = mydb.cursor(dictionary=True)

            cursor.execute("INSERT INTO messages (sender_id, receiver_id, subject, body) VALUES (%s, %s, %s, %s)",
                           (sender_id, receiver_id, subject, body))
            mydb.commit()

            return redirect(url_for('inbox', user_id=sender_id))
        else:
            return redirect(url_for('login'))
    else:
        return render_template('send_message.html', user_id=session['user_id'])

@app.route('/message/<int:message_id>')
def view_message(message_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT * FROM messages WHERE id = %s AND receiver_id = %s", (message_id, session['user_id']))
    message = cursor.fetchone()

    if message:
        return render_template('view_message.html', message=message)
    else:
        return redirect(url_for('inbox', user_id=session['user_id']))

@app.route('/respond_form1/<int:request_id>/<action>', methods=['POST'])
def respond_form1(request_id, action):
    if 'user_id' not in session or session['user_type'] != 'FA':
        return "Unauthorized access", 401
    new_status = 'FAD' if action == 'decline' else 'GSC'
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("UPDATE form1_requests SET status = %s WHERE request_id = %s", (new_status, request_id))
    mydb.commit()
    return redirect(url_for('faculty_view_form1'))

@app.route('/faculty_student', methods=['GET', 'POST'])
def faculty_student():
    if 'user_id' in session and session['user_type'] == 'faculty':
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT u.user_id, u.fname, u.lname, u.email FROM users u WHERE u.user_id IN (SELECT student_id FROM advisor_assignments WHERE faculty_id = %s)", (session['user_id'],))
        students_info = cursor.fetchall()
        
        selected_student = None
        if request.method == 'POST':
            student_id = request.form['student_id']
            cursor.execute("SELECT u.fname, u.lname, u.email, u.address, s.program, s.grad_status FROM users u JOIN students s ON u.user_id = s.user_id WHERE u.user_id = %s", (student_id,))
            selected_student = cursor.fetchone()
        
        cursor.close()
        
        return render_template('faculty_student.html', fname=session['fname'], users=students_info, selected_student=selected_student)
    else:
        return redirect(url_for('login'))
    
@app.route('/edit_alumni_profile', methods=['GET', 'POST'])
def edit_alumni_profile():
    if 'user_id' in session and session['user_type'] == 'alumni':
        if request.method == 'POST':
            fname = request.form['fname']
            lname = request.form['lname']
            email = request.form['email']
            address = request.form['address']
            
            cursor = mydb.cursor(dictionary=True)
            cursor.execute("UPDATE users SET fname = %s, lname = %s, email = %s, address = %s WHERE user_id = %s",
                           (fname, lname, email, address, session['user_id']))
            mydb.commit()
            cursor.close()
            
            flash("Profile updated successfully.")
            return redirect(url_for('edit_alumni_profile'))
        
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (session['user_id'],))
        alumni = cursor.fetchone()
        cursor.close()
        
        return render_template('edit_alumni_profile.html', alumni=alumni)
    else:
        return redirect(url_for('login'))

@app.route('/alumni_transcript')
def alumni_transcript():
    if 'user_id' in session and session['user_type'] == 'alumni':
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT cs.course_ID, cs.course_title, cs.semester, sc.grade, cs.instructor_username, cs.course_dname, cs.course_number FROM student_course sc JOIN courses_schedule cs ON sc.IP_course_ID = cs.course_ID WHERE sc.student_id = %s", (session['user_id'],))
        transcript_info = cursor.fetchall()
        cursor.close()
        
        return render_template('alumni_transcript.html', transcript_info=transcript_info)
    else:
        return redirect(url_for('login'))

app.run(host='0.0.0.0', port=9097, debug=True)

