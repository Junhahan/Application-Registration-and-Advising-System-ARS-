from flask import Flask, session, render_template, redirect, url_for, request
from werkzeug.security import generate_password_hash
#from flask import mail, message
import mysql.connector
import random
import string

app = Flask('app')
app.secret_key = "e36B24rA"
#mail = Mail(app)
mydb = mysql.connector.connect(
  host = "apps24-te.co4jpltb2l3p.us-east-1.rds.amazonaws.com",
  user = "adminNTE",
  password = "S1-Khld678",
  database = "university"
)
@app.route('/login', methods=['GET', 'POST'])
def login():
    cur = mydb.cursor(dictionary=True)

    if request.method == 'GET':
      return render_template('login.html', message=None)

    if request.method == 'POST':
      username = (request.form['yourUsername'])
      password = (request.form['yourPassword'])
      cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
      user = cur.fetchone()
      if user != None:
          session['username'] = user['username']
          session['type'] = user['type']
          session['uid'] = user['uid']
          if session.get('type') == "faculty":
            # Redirect to faculty home if faculty
            return redirect(url_for('facultyhome'))
          if session.get('type') == 'applicant':
            # Redirect to applicant status if applicant
            return redirect(url_for('application_status'))
          if session.get('type') == 'admin':
            # Redirect to applicant status if applicant
            return redirect(url_for('admin'))
    else:
      print('Invalid username or password')
      return render_template('login.html', message="Invalid username or password")
    
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

@app.route('/', methods=['GET', 'POST'])
def home():
  if 'username' in session:
    if session.get('type') == "faculty":
      # Redirect to faculty home if faculty
      return redirect(url_for('facultyhome'))   
    if session.get('type') == 'applicant':  
      # Redirect to applicant status if applicant
      return redirect(url_for('application_status'))
    if session.get('type') == 'admin':
     # Redirect to applicant status if applicant
       return redirect(url_for('admin'))
  else:
    return render_template("home.html")

@app.route('/apply', methods=['GET', 'POST'])
def apply():
  if request.method == 'POST':
   # Connect to database
   cur = mydb.cursor(dictionary=True)

   
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
   
   # Insert username and password along with uid
   cur.execute("INSERT INTO users(username, password, type, uid) VALUES(%s, %s, 'applicant', %s)", (username, password, uid,))
   # Insert applicant info
   cur.execute("INSERT INTO applicants(uid, name, address, gender, program, semester) VALUES(%s, %s, %s, %s, %s, %s)", (uid, name, address, gender, program, semester,))
   # Insert academic information
   cur.execute("INSERT INTO academicinformation(uid, MS_GPA, BS_BA_GPA, MS_year, BS_BA_year, MS_uni, BS_uni, GRE_verbal, GRE_quantitative, GRE_examyear, GRE_advanced, GRE_subject, TOEFL, TOEFL_date, recommendations, transcript) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, 0)", 
   (uid, ms_gpa, bs_ba_gpa, ms_year, bs_ba_year, ms_uni, bs_uni, gre_verbal, gre_quantitative, gre_examyear, gre_advanced, gre_subject, toefl, toefl_date,))
   # Insert personal information
   cur.execute("INSERT INTO personalinformation(uid, SSID, contact_info, MS_major, BS_BA_major, interests, experience) VALUES(%s, %s, %s, %s, %s, %s, %s)", 
   (uid, ssid, contact_info, ms_major, bs_ba_major, interests, experience,))
   # Insert status info for user
   cur.execute("INSERT INTO checkstatus(uid, status) VALUES(%s, 'Application Incomplete')", (uid,))
   # Update database
   mydb.commit()
   # Redirect to login after we're done
   return redirect(url_for('login'))
  else:
    # Return the application form page
    return render_template("applicant.html")
  
@app.route('/applicationstatus')
def application_status():
  if 'username' in session:
    if session.get('type') == 'applicant':
      uid = session.get('uid')
     
      cursor = mydb.cursor(dictionary=True)

      cursor.execute("SELECT status FROM checkstatus WHERE uid = %s", (uid,))
      result = cursor.fetchone()
      mydb.close()

      if result:
        checkstatus = result['status']
      else:
        checkstatus = "Nothing found for the provided UID"
      return render_template('status.html', checkstatus = checkstatus)
    elif session.get('type') == 'admin':
      return redirect(url_for('admin'))
    else:
      return redirect(url_for('facultyhome'))

@app.route('/recommendations', methods=['GET', 'POST'])
def submit_recommendations():
  if 'username' in session:
    if session.get('type') == "applicant" or session.get('type') == "admin":
      if request.method == 'GET':
        return render_template('recommendations.html')
      if request.method == 'POST':
        recommender_name = request.form['recommenderName']
        recommender_email = request.form['recommenderEmail']
        recommender_profession = request.form['recommenderProfession']
        recommender_affiliation = request.form['recommenderAffiliation']
              
        cur = mydb.cursor(dictionary=True)
        cur.execute("SELECT transcript FROM academicinformation WHERE uid = %s", (session.get('uid'),))
        applicantInfo = cur.fetchone()

        cur.execute("INSERT INTO recommendations(uid, rec_name, rec_email, rec_prof, rec_affiliation) VALUES(%s, %s, %s, %s, %s)", (session.get('uid'), recommender_name, recommender_email, recommender_profession, recommender_affiliation,))
        if applicantInfo["transcript"] == 1:
          # If so change status to pending review
          status = "Application Complete and Under Review"
        else:
          # If not change status to recommendations missing
          status = "Application Incomplete - Transcript missing"
        # Change recommendation status to received
        cur.execute("UPDATE academicinformation SET recommendations = 1 WHERE uid = %s", (session.get('uid'),))
        # Change status of application
        cur.execute("UPDATE checkstatus SET status = %s WHERE uid = %s", (status, session.get('uid'),))
        mydb.commit()
        return render_template('recommendations.html')
    else:
      return redirect(url_for('facultyhome'))

@app.route('/facultyhome')
def facultyhome():
  # If user not faculty redirect to applicant status
  if 'username' in session:
    if session.get('type') == "faculty" or session.get('type') == "admin":
      cur = mydb.cursor(dictionary=True)

      
      cur.execute("SELECT * FROM facultymembers WHERE uid = %s", (session.get('uid'),))
      userTraits = cur.fetchone()
      if userTraits != None:
        session["permissions"] = userTraits["permissions"]
        session["role"] = userTraits["role"]
        session["finalDecision"] = userTraits["finalDecision"]
      return render_template('faculty.html')
  else: 
    return redirect(url_for('home'))
  
@app.route('/review/<uid>', methods=['GET', 'POST'])
def review(uid):

  if 'username' in session:
    if session.get('type') == 'faculty' or session.get('type') == 'admin':
      cur = mydb.cursor(dictionary=True)

      cur.execute(
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
          "INSERT INTO reviewform(uid, recommendation1rating, recommendation1generic, recommendation1credible, recommendation1from, gac_rating, deficiencycourses, reasonsforrejection, reviewer_comments) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
            (uid, letter1rating, letter1generic, letter1credible, applicantRecommendations['rec_name'], gas_committeerating, deficiency_courses, reasons_for_rejection, gas_reviewer_comments,)
          )
        mydb.commit()
        return redirect(url_for('facultyhome'))

      return render_template("reviewform.html", applicantData = applicantData, applicantPersonal = applicantPersonal, applicantRecommendations = applicantRecommendations)

@app.route('/applicantlist')
def applicantlist():
  # If user not faculty redirect to applicant status
  if 'username' in session: 
    if session.get('permissions') == "Review" or session.get('type') == "admin":
      cur = mydb.cursor(dictionary=True)

      cur.execute("SELECT applicants.name, applicants.uid, checkstatus.status FROM applicants INNER JOIN checkstatus ON applicants.uid = checkstatus.uid WHERE checkstatus.status = 'Application Complete and Under Review' ORDER BY applicants.uid ASC")
      applicants = cur.fetchall()
      return render_template("listApplicants.html", applicants = applicants)
    elif session.get('type') == "faculty":
      return redirect(url_for('facultyhome'))
    else: 
      return redirect(url_for('application_status'))
  
@app.route('/updatetranscript', methods=['GET','POST'])
def updatetranscript():
  if 'username' in session: 
    if session.get('permissions') == "AcceptTranscript" or session.get('type') == "admin":
      # Connect to database
      cur = mydb.cursor(dictionary=True)
      if request.method == 'GET':
        return render_template("transcript.html")
      # If submitted
      if request.method == 'POST':
        uid = request.form['applicantUid']
        # Get status of recommendations
        cur.execute("SELECT recommendations FROM academicinformation WHERE uid = %s", (uid,))
        applicantInfo = cur.fetchone()

        # Check if recommendations are in
        if applicantInfo["recommendations"] == 1:
          # If so change status to pending review
          status = "Application Complete and Under Review"
        else:
          # If not change status to recommendations missing
          status = "Application Incomplete - Recommendations missing"
        # Change transcript status to received
        cur.execute("UPDATE academicinformation SET transcript = 1 WHERE uid = %s", (uid,))
        # Change status of application
        cur.execute("UPDATE checkstatus SET status = %s WHERE uid = %s", (status, uid,))
        # Update database
        mydb.commit()
        return render_template("transcript.html")
    else:
      if session.get('type') == "faculty":
        return redirect(url_for('facultyhome'))
      if session.get('type') == "applicant":
        return redirect(url_for('application_status'))
     
@app.route('/admin')
def admin():
  if 'username' in session: 
    if session.get('type') == "admin":
      return render_template("admin.html")
  else:
    if session.get('type') == "faculty":
      return redirect(url_for('facultyhome'))
    if session.get('type') == "applicant":
      return redirect(url_for('application_status'))
    
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
        
@app.route('/finaldecision/<uid>', methods=['GET','POST'])
def finaldecision(uid):
  if 'username' in session:
    if session.get('finalDecision') == "Yes":
      cur = mydb.cursor(dictionary=True)
      app_uid = uid
      cur.execute(
      "SELECT applicants.uid, applicants.name, applicants.program, applicants.semester, academicinformation.MS_GPA, academicinformation.BS_BA_GPA, academicinformation.MS_year, academicinformation.BS_BA_year, academicinformation.MS_uni, academicinformation.BS_uni, academicinformation.GRE_verbal, academicinformation.GRE_quantitative, academicinformation.GRE_examyear, academicinformation.GRE_advanced, academicinformation.GRE_subject, academicinformation.TOEFL, academicinformation.TOEFL_date FROM applicants INNER JOIN academicinformation ON applicants.uid = academicinformation.uid WHERE applicants.uid = %s", 
      (uid,))
      applicantData = cur.fetchone()
      cur.execute("SELECT * FROM personalinformation WHERE personalinformation.uid = %s", (uid,))    
      applicantPersonal = cur.fetchone()
      cur.execute("SELECT * FROM recommendations WHERE recommendations.uid = %s", (uid,))
      applicantRecommendations = cur.fetchone()
      cur.execute("SELECT * FROM reviewform WHERE uid = %s", (uid,))
      reviewdata = cur.fetchone()
      if request.method == 'POST':
        final_decision = request.form['decisionType']
      
        cur.execute("UPDATE checkstatus SET status = %s WHERE uid = %s", (final_decision, uid))
        mydb.commit()
        return redirect(url_for('facultyhome'))
      return render_template("finaldecision.html", app_uid = app_uid, reviewdata = reviewdata, applicantData = applicantData, applicantPersonal = applicantPersonal, applicantRecommendations = applicantRecommendations)
    
    elif session.get('type') == "faculty":
      return redirect(url_for('facultyhome'))
    else:
      return redirect(url_for('application_status'))
    
@app.route('/finaldecision')
def decisionList():
  if 'username' in session:
    if session.get('finalDecision') == "Yes":
      cur = mydb.cursor(dictionary=True)

      cur.execute("SELECT applicants.name, applicants.uid, checkstatus.status FROM applicants INNER JOIN checkstatus ON applicants.uid = checkstatus.uid INNER JOIN reviewform ON checkstatus.uid = reviewform.uid WHERE checkstatus.status = 'Application Complete and Under Review' ORDER BY applicants.uid ASC")
      applicants = cur.fetchall()
      return render_template("finalList.html", applicants = applicants)
    elif session.get('type') == "faculty":
      return redirect(url_for('facultyhome'))
    else:
      return redirect(url_for('application_status'))
    
@app.route('/reset')
def reset():
  if session.get('type') == 'admin':
    mydb = mysql.connector.connect(
      host = "apps24-te.co4jpltb2l3p.us-east-1.rds.amazonaws.com",
      user = "adminNTE",
      password = "S1-Khld678",
      database = "university"
    )
    cursor = mydb.cursor(dictionary=True)

    cursor.execute("DELETE FROM facultymembers")
    cursor.execute("DELETE FROM academicinformation")
    cursor.execute("DELETE FROM personalinformation")
    cursor.execute("DELETE FROM recommendations")
    cursor.execute("DELETE FROM checkstatus")
    cursor.execute("DELETE FROM reviewform")
    cursor.execute("DELETE FROM applicants")
    cursor.execute("DELETE FROM users")

    mydb.commit()

    cursor.execute("INSERT INTO users VALUES('SystemAdmin', 'Op-!2234AC', 'admin', '11112222')")

    cursor.execute("INSERT INTO users VALUES('GradSec', 'A4-kjNE687', 'faculty', '22121234')")
    cursor.execute("INSERT INTO users VALUES('AdCAC', 'WL$09a2ef', 'faculty', '11234532')")
    cursor.execute("INSERT INTO users VALUES('Narahari', 'DLR243-86H', 'faculty', '11132346')")
    cursor.execute("INSERT INTO users VALUES('Wood', '12345678', 'faculty', '11134455')")
    cursor.execute("INSERT INTO users VALUES('Heller', '12345879', 'faculty', '11134424')")

    cursor.execute("INSERT INTO facultymembers VALUES('22121234', 'GS', 'GradSec', 'AcceptTranscript', 'Yes')")
    cursor.execute("INSERT INTO facultymembers VALUES('11234532', 'CAC', 'Chair', 'Review', 'Yes')")
    cursor.execute("INSERT INTO facultymembers VALUES('11132346', 'Faculty', 'Narahari', 'Review', 'No')")
    cursor.execute("INSERT INTO facultymembers VALUES('11134455', 'Faculty', 'Wood', 'Review', 'No')")
    cursor.execute("INSERT INTO facultymembers VALUES('11134424', 'Faculty', 'Heller', 'Review', 'No')")

    mydb.commit()

    cursor.execute("INSERT INTO users VALUES('JLennon', '11111178', 'applicant', '12312312')")
    cursor.execute("INSERT INTO applicants VALUES('12312312', 'Lennon, John', '22224 Beatle Drive', 'Male', 'MS', 'Fall 2024')")
    cursor.execute("INSERT INTO academicinformation VALUES('12312312', NULL, 3.5, NULL, 2023, NULL, 'Cornell University', 170, 170, 2023, NULL, NUll, NULL, NULL, 1, 1)")
    cursor.execute("INSERT INTO personalinformation VALUES('12312312', '111-11-1111', '202-445-2786', NULL, 'Computer Science', 'Algorithms', '1 year at IBM')")
    cursor.execute("INSERT INTO recommendations VALUES('12312312', 'Nathan Te', 'nathanmte03@gmail.com', 'Senior Software Engineer', 'RTX Corporation')")
    cursor.execute("INSERT INTO checkstatus VALUES('12312312', 'Application Complete and Under Review')")
    
    mydb.commit()
    
    cursor.execute("INSERT INTO users VALUES('RingStarr', '11111199', 'applicant', '66666666')")
    cursor.execute("INSERT INTO applicants VALUES('66666666', 'Starr, Ringo', '22224 Beatle Drive', 'Male', 'PHD', 'Spring 2024')")
    cursor.execute("INSERT INTO academicinformation VALUES('66666666', 4.0, 3.9, 2023, 2021, 'University of Maryland', 'University of Viriginia', 165, 150, 2023, NULL, NUll, NULL, NULL, 0, 0)")
    cursor.execute("INSERT INTO personalinformation VALUES('66666666', '222-11-1111', '202-545-2787', 'Cybersecurity', 'Computer Science', 'Software Development', '2 years at Google')")
    cursor.execute("INSERT INTO checkstatus VALUES('66666666', 'Application Incomplete')")
    
    mydb.commit()

    session.clear()
    return redirect('/')
  else: 
    return redirect(url_for('home'))
  

@app.route('/logout', methods=['GET', 'POST'])
def logout():
  # Log the user out and redirect them to the home page

  session.clear()
  return redirect('/')

app.run(host='0.0.0.0', port=8080)
