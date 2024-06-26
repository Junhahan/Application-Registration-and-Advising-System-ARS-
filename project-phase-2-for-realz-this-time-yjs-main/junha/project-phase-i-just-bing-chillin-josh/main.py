
from flask import Flask, session, render_template, redirect, url_for, request
import mysql.connector
from datetime import datetime

app = Flask('app')
app.secret_key = "wf389f9j3fji898wdfnnnnnn"
errorMessage = "Incorrect Username or Password"

mydb = mysql.connector.connect(
    host="database3.cmhgh9l8chvx.us-east-1.rds.amazonaws.com",
    user="admin",
    password="z1GG14ABZhd7EyHWjfB",
    database="mydb"
)

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
    
def graduation(user_id):
    new_user_type = 'AL'
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("DELETE FROM students WHERE student_id = %s",(user_id,))
    cursor.execute("UPDATE users SET user_type = %s WHERE user_id = %s", (new_user_type,user_id,))
    mydb.commit()
    return 1

def make_john_ms_again(user_id):
    new_user_type = 'MS'
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("UPDATE users SET user_type= %s WHERE user_id = %s", (new_user_type, user_id))

def gpa():
    cursor = mydb.cursor(dictionary=True)

    # Select course_id, credits, grade on join of student courses and courses where course ids match, and user id for that course in sc is session userid
    cursor.execute("SELECT C.credits, SC.grade FROM student_courses AS SC JOIN courses AS C ON SC.course_id = C.course_id WHERE SC.user_id = %s AND SC.counts = 1", (session['user_id'],))
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

    cursor.execute("SELECT SUM(credits) AS sum FROM student_courses AS SC JOIN courses AS C ON SC.course_id = C.course_id WHERE SC.user_id = %s AND SC.course_id LIKE 'CSCI%' AND SC.counts = 1", (session['user_id'],))
    results_cs = cursor.fetchone()
    total_cs = int(results_cs["sum"]) if results_cs["sum"] is not None else 0
    cursor.execute("""
        SELECT SUM(sub.credits) AS sum 
        FROM (
            SELECT C.credits 
            FROM student_courses AS SC 
            JOIN courses AS C ON SC.course_id = C.course_id 
            WHERE SC.user_id = %s AND SC.course_id NOT LIKE 'CSCI%' AND SC.counts = 1 
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

    cursor.execute("SELECT SUM(C.credits) AS sum FROM student_courses AS SC JOIN courses AS C ON SC.course_id = C.course_id WHERE SC.user_id = %s AND SC.course_id LIKE 'CSCI%' AND SC.counts = 1", (session['user_id'],))
    results_cs = cursor.fetchone()
    total_cs = int(results_cs['sum']) if results_cs['sum'] is not None else 0
    cursor.execute("SELECT SUM(C.credits) AS sum FROM student_courses AS SC JOIN courses AS C ON SC.course_id = C.course_id WHERE SC.user_id = %s AND SC.course_id NOT LIKE 'CSCI%' AND SC.counts = 1", (session['user_id'],))
    results_noncs = cursor.fetchone()
    total_non_cs = results_noncs['sum'] if results_noncs['sum'] is not None else 0

    mydb.commit()

    if total_cs >= 30 and total_cs + total_non_cs >= 36:
        return True
    return False

def total_b_grades():
    total = 0
    cursor = mydb.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(course_id) AS total FROM student_courses WHERE user_id = %s AND grade IN ('F', 'C', 'C+', 'B-') AND counts = 1", (session['user_id'],))
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
    cursor.execute("SELECT course_id FROM student_courses WHERE user_id = %s AND counts = 1 AND course_id IN ('CSCI6212', 'CSCI6221', 'CSCI6461')", (session['user_id'],))
    matching_courses = cursor.fetchall() # how many of these required 3 the student has
    if len(matching_courses) == 3:
        has_required = True
    cursor.close()
    mydb.commit()
    return has_required


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = (request.form["user_id"])
        password = (request.form["password"])
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT user_id, password, user_type, fname, lname FROM users WHERE user_id = %s AND password = %s", (user_id, password))
        user = cursor.fetchone()

        if user:
            session["user_type"] = user["user_type"]
            session["user_id"] = user_id
            session["fname"] = user["fname"]


            if user['user_type'] == "AD":
                return render_template("admin_dashboard.html", username = user['fname'])

            elif user['user_type'] == "MS" or user['user_type'] == "PHD":
                return render_template("student_main_page.html", fname = user['fname'], lname = user['lname'], user_id=user_id)

            elif user['user_type'] == "GS":
                cursor.execute("SELECT aa.student_id, aa.faculty_id, u.fname AS faculty_fname, u.lname AS faculty_lname FROM advisor_assignments AS aa JOIN users AS u ON aa.faculty_id = u.user_id;")
                advisors = cursor.fetchall()

                cursor.execute("SELECT u.fname, u.lname, u.email, s.grad_status FROM users u JOIN students s ON u.user_id = s.user_id;")
                students = cursor.fetchall()
                return render_template("secretary_view.html", username = user['fname'], students = students, advisors = advisors)

            elif user['user_type'] == "AL":
                cursor.execute("SELECT fname, lname, email, address, password FROM users WHERE user_id = %s", (session['user_id'],))
                one_row_info = cursor.fetchone()
                fname = one_row_info['fname']
                lname = one_row_info['lname']
                email = one_row_info['email']
                address = one_row_info['address']
                password = one_row_info['password']
                courses = get_student_courses(session["user_id"])
                gpa_al = gpa()

                return render_template('alumnus.html', fname = fname, lname = lname, email = email, address = address, password = password, courses = courses, gpa = gpa_al)

            elif user['user_type'] == "FA":
                cursor.execute("SELECT fname FROM users WHERE user_id = %s", (session["user_id"],))
                fname_result = cursor.fetchone()
                fname = fname_result["fname"]

                cursor.execute("SELECT student_id FROM advisor_assignments WHERE faculty_id = %s", (session['user_id'],))
                assigned_students_ids = [row['student_id'] for row in cursor.fetchall()]
                fnames = []
                lnames = []
                emails = []
                addresses = []
                passwords = []

                for student_id in assigned_students_ids:
                    cursor.execute("SELECT fname, lname, email, address, password FROM users WHERE user_id = %s", (student_id,))
                    student_info = cursor.fetchone()
                    if student_info is not None:
                        fnames.append(student_info['fname'])
                        lnames.append(student_info['lname'])
                        emails.append(student_info['email'])
                        addresses.append(student_info['address'])
                        passwords.append(student_info['password'])
                cursor.close()
                mydb.commit()
                return render_template('faculty.html', fname = fname, fnames = fnames, lnames = lnames, emails = emails, addresses = addresses, passwords = passwords, users = assigned_students_ids)
            else:
                print("Login unsuccessful. Try Again.")
                return render_template("sign_in.html", incorrectlogin=True, d=errorMessage)
        else:
            errorMessage2 = "Failed to sign in, check username and/or password."
            return render_template('sign_in.html', errorMessage = errorMessage2)

    else:
        return render_template('sign_in.html')
        
@app.route('/graduate_student', methods=['POST'])
def graduate_student():
    if request.method == 'POST':
        student_id = request.form.get('student_id')

        cursor = mydb.cursor(dictionary=True)
        cursor.execute("UPDATE users SET user_type = 'AL' WHERE user_id = %s", (student_id,))

        cursor.execute("SELECT aa.student_id, aa.faculty_id, u.fname AS faculty_fname, u.lname AS faculty_lname FROM advisor_assignments AS aa JOIN users AS u ON aa.faculty_id = u.user_id;")
        advisors = cursor.fetchall()
        cursor.execute("SELECT u.fname, u.lname, u.email, s.grad_status FROM users u JOIN students s ON u.user_id = s.user_id;")
        students = cursor.fetchall()

        return render_template("secretary_view.html", username = session["fname"], students = students, advisors = advisors)

@app.route('/assign_advisor', methods=['POST'])
def assign_advisor():
    if request.method == 'POST':
        selected_advisor = request.form.get('advisor')
        student_id = request.form.get('student_id')

        cursor = mydb.cursor(dictionary=True)

        #cursor.execute("INSERT INTO advisor_assignments (student_id, faculty_id) VALUES (%s, %s)", (student_id, selected_advisor))


        cursor.execute("SELECT aa.student_id, aa.faculty_id, u.fname AS faculty_fname, u.lname AS faculty_lname FROM advisor_assignments AS aa JOIN users AS u ON aa.faculty_id = u.user_id;")
        advisors = cursor.fetchall()
        cursor.execute("SELECT u.fname, u.lname, u.email, s.grad_status FROM users u JOIN students s ON u.user_id = s.user_id;")
        students = cursor.fetchall()
        return render_template("secretary_view.html", username = session["fname"], students = students, advisors = advisors)
    
@app.route('/create_acc', methods=['GET', 'POST'])
def create_acc():
    session.clear()
    print('here')
    return render_template("sign_up.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    c = mydb.cursor(dictionary=True)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        address = request.form['address']

        c.execute("SELECT user_id FROM users WHERE user_id = %s", (username,))
        results = c.fetchall()
        if results:
            return redirect('/register')
    
        c.execute("SELECT email FROM users")
        users = c.fetchall()
        c.execute("INSERT INTO users (user_id, user_type, password, fname, lname, email, address) VALUES (%s, 'student', %s, %s, %s, %s, %s)",
                  (username, password, fname, lname, email, address))
        mydb.commit()


        return render_template('sign_in.html', message='Registration successful! Please log in.')

    return render_template('sign_up.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/back_to_sign_in', methods=['GET', 'POST'])
def back_to_sign_in():
    session.clear()
    return redirect('/')


@app.route("/class_info/<int:user_id>")
def class_info(user_id):
    if 'user_id' in session and session['user_id'] == str(user_id):
        courses = get_student_courses(user_id)
        return render_template("class_info.html", courses=courses)
    else:
        return redirect(url_for('login'))

@app.route('/inbox')
def inbox():
    if 'user_ireturnd' not in session:
         redirect(url_for('login'))

    user_id = session['user_id']
    user_type = get_user_role(user_id)

    cursor = mydb.cursor(dictionary=True)

    cursor.execute('SELECT * FROM messages WHERE receiver_id = %s ORDER BY timestamp DESC', (user_id,))
    messages = cursor.fetchall()
    if user_type == 'FA':
        cursor.execute('SELECT * FROM form1_requests WHERE faculty_advisor_id = %s ORDER BY id DESC', (user_id,))
        form1_requests = cursor.fetchall()
    elif user_type == 'GS':
        cursor.execute('SELECT * FROM form1_requests WHERE status IN ("FAC", "GSC") ORDER BY id DESC')
        form1_requests = cursor.fetchall()
    else:
        form1_requests = []

    cursor.close()

    return render_template('inbox.html', messages=messages, form1_requests=form1_requests, user_type=user_type, user_id=user_id)

@app.route('/form1_request/<int:request_id>/approve')
def approve_form1_request(request_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    user_role = get_user_role(user_id)
    cursor = mydb.cursor(dictionary=True)
    cursor.execute('SELECT * FROM form1_requests WHERE id = %s', (request_id,))
    request = cursor.fetchone()

    if not request:
        return redirect(url_for('inbox'))

    if (user_role == 'FA' and request['status'] == 'FAC') or (user_role == 'GS' and request['status'] == 'GSC'):
        new_status = 'GSC' if user_role == 'FA' else 'Approved'
        cursor.execute('UPDATE form1_requests SET status = %s WHERE id = %s', (new_status, request_id))
        mydb.commit()

        subject = 'Form 1 Request Approved'
        body = f'Your Form 1 request has been approved by {user_role}.'
        send_notification(user_id, request['student_id'], subject, body)

        if user_role == 'FA':
            gs_user_id = find_graduate_secretary_id()
            send_notification(user_id, gs_user_id, subject, body)
        if user_role =='GS':
            graduation(request['student_id'])



    return redirect(url_for('inbox'))

@app.route('/form1_request/<int:request_id>/decline')
def decline_form1_request(request_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    user_role = get_user_role(user_id)

    cursor = mydb.cursor(dictionary=True)
    cursor.execute('SELECT * FROM form1_requests WHERE id = %s', (request_id,))
    request = cursor.fetchone()

    if not request:
        return redirect(url_for('inbox'))

    if (user_role == 'FA' and request['status'] == 'FAC') or (user_role == 'GS' and request['status'] == 'GSC'):
        new_status = 'FAD' if user_role == 'FA' else 'GSD'
        cursor.execute('UPDATE form1_requests SET status = %s WHERE id = %s', (new_status, request_id))
        mydb.commit()

        subject = 'Form 1 Request Declined'
        body = f'Your Form 1 request has been declined by {user_role}.'
        send_notification(user_id, request['student_id'], subject, body)


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

@app.route('/submit_form1', methods=['GET', 'POST'])
def submit_form1():
    if 'user_id' in session and request.method == 'POST':
        student_id = session['user_id']
        
        try:
            cursor = mydb.cursor(dictionary=True)
            cursor.execute("SELECT faculty_id FROM advisor_assignments WHERE student_id = %s", (student_id,))
            row = cursor.fetchone()
            
            if row:
                faculty_id = row[0]
                cursor.execute("INSERT INTO form1_requests (student_id, faculty_id, status) VALUES (%s, %s, 'FAC')", (student_id, faculty_id))
                mydb.commit()
            else:
                return redirect(url_for('student_main_page'))
        
        except mydb.connector.Error as error:
            print(f"Error: {error}")
            mydb.rollback()
        
        finally:
            cursor.close()
        
        return redirect(url_for('student_main_page'))
    
    else:
        return render_template('submit_form1.html')

@app.route('/faculty_view_form1')
def faculty_view_form1():
    if 'user_id' in session and session['user_type'] == 'FA':
        cursor = mydb.cursor(dictionary=True)
        faculty_id = session['user_id']
        cursor.execute("""
            SELECT r.request_id, u.fname, u.lname, u.user_id, r.status 
            FROM form1_requests r 
            JOIN users u ON r.student_id = u.user_id 
            WHERE r.faculty_id = %s AND r.status = 'FAC'
        """, (faculty_id,))
        requests = cursor.fetchall()
        return render_template('faculty_view_form1.html', requests=requests)
    else:
        return "Unauthorized access", 401

@app.route('/update_personal_info/<int:user_id>', methods=['GET', 'POST'])
def update_personal_info(user_id):
    cursor = mydb.cursor(dictionary=True)
    
    if 'user_id' in session and int(session['user_id']) == user_id:
        if request.method == 'POST':
            email = request.form['email']
            address = request.form['address']
            cursor.execute("UPDATE users SET email = %s, address = %s WHERE user_id = %s", (email, address, user_id))
            mydb.commit()
            return redirect(url_for('student_main_page'))
        else:
            cursor.execute("SELECT email, address FROM users WHERE user_id = %s", (user_id,))
            user_info = cursor.fetchone()
            if user_info:
                return render_template('update_personal_info.html', email=user_info["email"], address = user_info["address"])
            else:
                return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))

@app.route('/form1_requests')
def form1_requests():
    if 'user_id' in session and session['user_type'] == 'FA':
        faculty_id = session['user_id']
        cursor = mydb.cursor(dictionary=True)

        cursor.execute("SELECT f.request_id, u.fname, u.lname, f.student_id, f.status FROM form1_requests f JOIN users u ON f.student_id = u.user_id WHERE f.faculty_id = %s AND f.status = 'FAC'", (faculty_id,))
        requests = cursor.fetchall()

        return render_template('form1_requests.html', requests=requests)
    else:
        return redirect(url_for('login'))


@app.route('/student_main_page')
def student_main_page():
    if 'user_id' in session and session['user_type'] in ['MS', 'PHD']:
        user_id = session['user_id']
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT fname, lname, user_type FROM users WHERE user_id = %s", (user_id,))
        student_info = cursor.fetchone()
        if student_info:
            fname = student_info['fname']
            lname = student_info['lname']
            user_role = student_info['user_type']
            return render_template("student_main_page.html", fname=fname, lname=lname, user_id=user_id, user_role=user_role)
        else:
            return "Student information not found. Please log in again.", 404
    else:
        return redirect(url_for('login'))
    
@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' in session and session['user_type'] == 'AD':
        return render_template('admin_dashboard.html', username=session.get('fname'))
    else:
        return redirect(url_for('login'))
    
@app.route('/admin/go_back_to_studying')
def go_back_to_studying():
    if 'user_id' in session and session['user_type'] == 'AD':
        if request.method == 'POST':
            search_query = request.form['search_query']
            cursor = mydb.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE user_id LIKE %s OR fname LIKE %s OR lname LIKE %s", ('%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%'))
            users = cursor.fetchall()
            cursor.close()
            return render_template('go_back_to_studying.html', users=users)
        return render_template('go_back_to_studying.html', users = None)
    else:
        return redirect(url_for('login'))

@app.route('/admin/make_ms/<user_id>', methods=['POST'])
def make_ms(user_id):
    if 'user_id' in session and session['user_type'] == 'AD':
        try:
            new_student_role = 'MS'
            cursor = mydb.cursor(dictionary=True)
            cursor.execute("UPDATE users SET user_type = %s WHERE user_id = %s", (new_student_role, user_id,))
            mydb.commit()
            cursor.close()
        except Exception as e:
            return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('login'))

@app.route('/admin/search_user', methods=['GET', 'POST'])
def search_user():
    if 'user_id' in session and session['user_type'] == 'AD':
        if request.method == 'POST':
            search_query = request.form['search_query']
            cursor = mydb.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE user_id LIKE %s OR fname LIKE %s OR lname LIKE %s", ('%' + search_query + '%', '%' + search_query + '%', '%' + search_query + '%'))
            users = cursor.fetchall()
            cursor.close()
            return render_template('search_user.html', users=users)
        return render_template('search_user.html', users=None)
    else:
        return redirect(url_for('login'))

@app.route('/admin/reset_db', methods = ['GET', 'POST'])
def reset_db():
    if 'user_id' in session and session['user_type'] == 'AD':
        if request.method == 'POST':
            try:
                cursor = mydb.cursor()
                cursor.execute("DROP TABLE IF EXISTS users")
                cursor.execute("DROP TABLE IF EXISTS students")
                cursor.execute("DROP TABLE IF EXISTS form1")
                cursor.execute("DROP TABLE IF EXISTS messages")
                cursor.execute("DROP TABLE IF EXISTS form1_requests")
                cursor.execute("DROP TABLE IF EXISTS prereqs")
                cursor.execute("DROP TABLE IF EXISTS advisor_assignments")
                cursor.execute("DROP TABLE IF EXISTS student_courses")
                cursor.execute("""
                    CREATE TABLE users (
                    user_id VARCHAR(255),
                    user_type VARCHAR(255),
                    password VARCHAR(255),
                    fname VARCHAR(255),
                    lname VARCHAR(255),
                    email VARCHAR(255),
                    address VARCHAR(255),
                    PRIMARY KEY(user_id)
                    )
                """)
                cursor.execute("""
                    CREATE TABLE prereqs (
                    required_for VARCHAR(255),
                    prereq VARCHAR(255),
                    PRIMARY KEY(required_for, prereq),
                    FOREIGN KEY(required_for) REFERENCES courses(course_id),
                    FOREIGN KEY(prereq) REFERENCES courses(course_id)
                )
                """)
                cursor.execute("""
                    CREATE TABLE student_courses (
                    course_id VARCHAR(255),
                    user_id VARCHAR(255),
                    semester INT(8),
                    grade enum('IP', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'F'),
                    counts enum('T', 'F') DEFAULT 'F' NOT NULL,
                    form1 enum('T', 'F') DEFAULT 'F' NOT NULL,
                    PRIMARY KEY(course_id, user_id, semester),
                    FOREIGN KEY(course_id) REFERENCES courses(course_id),
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                )
                """)
                cursor.execute("""
                    CREATE TABLE students (
                    user_id VARCHAR(255),
                    grad_status enum('T', 'F') DEFAULT 'F' NOT NULL,
                    thesis TEXT,
                    PRIMARY KEY(user_id),
                    FOREIGN KEY(user_id) REFERENCES users(user_id)
                )
                """)
                cursor.execute("""
                    CREATE TABLE advisor_assignments (
                    student_id VARCHAR(255),
                    faculty_id VARCHAR(255),
                    PRIMARY KEY(student_id, faculty_id),
                    FOREIGN KEY(student_id) REFERENCES users(user_id),
                    FOREIGN KEY(faculty_id) REFERENCES users(user_id)
                )
                """)
                cursor.execute("""
                    CREATE TABLE form1 (
                    user_id VARCHAR(255),
                    course_id VARCHAR(255),
                    PRIMARY KEY(user_id, course_id),
                    FOREIGN KEY(user_id) REFERENCES users(user_id),
                    FOREIGN KEY(course_id) REFERENCES courses(course_id)
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
                    student_id VARCHAR(255) NOT NULL,
                    faculty_advisor_id VARCHAR(255) NOT NULL,
                    status VARCHAR(3) NOT NULL, -- FAC, FAD, GSC, GSD, or "Approved"
                    FOREIGN KEY(student_id) REFERENCES users(user_id),
                    FOREIGN KEY(faculty_advisor_id) REFERENCES users(user_id)
                )
                """)
            except mydb.connector.Error as error:
                return "An error Occurred"
            finally:
                cursor.close()
        else:
            return render_template('reset_db.html')
    else:
        return render_template('login')
        
@app.route('/admin/create_account', methods=['GET', 'POST'])
def create_account():
    if 'user_id' in session and session['user_type'] == 'AD':
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

            return redirect(url_for('admin_dashboard'))
        return render_template('create_account.html')
    else:
        return redirect(url_for('login'))

@app.route('/admin/delete_account/<user_id>', methods=['POST'])
def delete_account(user_id):
    if 'user_id' in session and session['user_type'] == 'AD':
        try:
            cursor = mydb.cursor(dictionary=True)
            cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
            mydb.commit()
            cursor.close()
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('login'))


# Info update is used by alumni that update their personal information
@app.route('/info-update', methods=["POST"])
def info_update():
    cursor = mydb.cursor(dictionary=True)

    user_id = session["user_id"]
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()

    fname_existing = result["fname"]
    lname_existing = result["lname"]
    email_existing = result["email"]
    address_existing = result["address"]
    password_existing = result["password"]

    fname = request.form.get("fname", fname_existing)
    lname = request.form.get("lname", lname_existing)
    email = request.form.get("email", email_existing)
    address = request.form.get("address", address_existing)
    password = request.form.get("password", password_existing)

    cursor.execute("UPDATE users SET fname = %s, lname = %s, email = %s, address = %s, password = %s WHERE user_id = %s", (fname, lname, email, address, password, user_id))
    mydb.commit()
    cursor.close()
    return redirect(url_for('profile'))


# Profile displays user information for logged in alumni and faculty advisor.
# The current plan is to merge the alumni and student pages, mostly by Jack but with help from me
@app.route('/profile')
def profile():
    has_session()
    
    # THIS CONDITION IS JUST FOR TESTING AND IS NOT TO BE MERGED
    if session["user_type"] == "MS" or session["user_type"] == "PHD":
        return redirect('/form1')

    elif session['user_type'] == "AL":
        cursor = mydb.cursor(dictionary=True)

        cursor.execute("SELECT fname, lname, email, address, password FROM users WHERE user_id = %s", (session['user_id'],))
        one_row_info = cursor.fetchone()
        fname = one_row_info['fname']
        lname = one_row_info['lname']
        email = one_row_info['email']
        address = one_row_info['address']
        password = one_row_info['password']
        courses = get_student_courses(session["user_id"])
        gpa_al = gpa()

        mydb.commit()
        cursor.close()
        return render_template('alumnus.html', fname = fname, lname = lname, email = email, address = address, password = password, courses = courses, gpa = gpa_al)

    elif session['user_type'] == "FA":
        cursor = mydb.cursor(dictionary=True)
        cursor.execute("SELECT fname FROM users WHERE user_id = %s", (session['user_id'],))
        fname_get = cursor.fetchone()
        fname = fname_get['fname']
        cursor.execute("SELECT student_id FROM advisor_assignments WHERE faculty_id = %s", (session['user_id'],))
        fnames = []
        lnames = []
        emails = []
        addresses = []
        passwords = []
        results = cursor.fetchall()

        if results:
            assigned_students_ids = [row['student_id'] for row in results]
            for student_id in assigned_students_ids:
                cursor.execute("SELECT fname, lname, email, address, password FROM users WHERE user_id = %s", (student_id,))
                student_info = cursor.fetchone()
                if student_info:
                    fnames.append(student_info['fname'])
                    lnames.append(student_info['lname'])
                    emails.append(student_info['email'])
                    addresses.append(student_info['address'])
                    passwords.append(student_info['password'])

        cursor.close()
        return render_template('faculty.html', fnames = fnames, lnames = lnames, emails = emails, addresses = addresses, passwords = passwords, users = assigned_students_ids, fname = fname)

    else:
        return "Internal service error"


# Faculty-students is accessed when a faculty clicks a student
@app.route('/faculty-students', methods = ["GET", "POST"])
def faculty_students():
    has_session()
    if request.method == "POST" and session['user_type'] == "FA":
        user_id = request.form["student_id"]
        cursor = mydb.cursor(dictionary=True)

        # SELECT INFO FOR THIS STUDENT, FROM Users
        cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
        student_info = cursor.fetchone()
        fname = student_info['fname']
        lname = student_info['lname']
        email = student_info['email']
        address = student_info['address']
        password = student_info['password']
        program = student_info["user_type"]

        # SELECT ALL COURSES WITH THIS STUDENT'S user_id
        cursor.execute("SELECT course_id, semester, grade, counts, form1 FROM student_courses WHERE user_id = %s", (user_id,))

        courses = []
        semesters = []
        grades = []
        counts = []
        form1 = []

        for row in cursor.fetchall():
            courses.append(row['course_id'])
            semesters.append(row['semester'])
            grades.append(row['grade'])
            counts.append(row['counts'])
            form1.append(row['form1'])

        form1_courses = []
        form1_titles = []
        form1_credits = []

        cursor.execute(
            """
            SELECT c.course_id, c.credits, c.title
            FROM form1 AS f
            JOIN courses AS c ON c.course_id = f.course_id
            WHERE user_id = %s
            """, (user_id,))
        found_courses = cursor.fetchall()
        for found_course in found_courses:
            form1_course = found_course["course_id"] if found_course["course_id"] is not None else "Unknown Course ID"
            form1_credit = found_course["credits"] if found_course["credits"] is not None else "Unknown Hours"
            form1_title = found_course["title"] if found_course["title"] is not None else "Unknown Title"

            form1_courses.append(form1_course)
            form1_titles.append(form1_title)
            form1_credits.append(form1_credit)

        cursor.execute("SELECT thesis FROM students WHERE user_id = %s", (user_id,))
        result_thesis = cursor.fetchone()
        thesis = result_thesis["thesis"]

        cursor.close()
        return render_template('student.html', user_id = user_id, fname = fname, lname = lname, email = email, address = address, password = password, courses = courses, semesters = semesters, grades = grades, counts = counts, form1 = form1, form1_courses = form1_courses, form1_titles = form1_titles, form1_credits = form1_credits, program = program, thesis = thesis)
    else:
        return redirect("/")
    

# Form 1 takes as input a session user_id, collects a list of courses, and submits the combination for faculty advisor review.
# It can be called using a hyperlink in student, which for now doesn't exist since the most recent student code has not been pushed
@app.route('/form1', methods = ["GET", "POST"])
def form1():
    # collect all courses available and send them to form1.html, then allow selection by student of these
    # when the student submits the form, the POST for the form is directed here, an auto-check is applied,
    # and if passed, the form is sent to the student's FA

    # authorized only
    has_session()

    # Only PHD and Grad students can access form1
    if session['user_type'] != "PHD" and session['user_type'] != "MS":
        return redirect('/profile')

    cursor = mydb.cursor(dictionary = True)
    cursor.execute('SELECT * FROM courses')

    course_titles = []
    course_ids = []
    hours = []
    for row in cursor.fetchall():
        hours.append(row['credits'])
        course_titles.append(row['title'])
        course_ids.append(row['course_id'])

    # GET REQUESTS
    if request.method == "GET":
        cursor.close()
        return render_template('form1.html', course_titles = course_titles, course_id = course_ids)

    # POST REQUESTS
    else:
        # clears old entries in DB
        form1_clear(session["user_id"])
        # set form1 attribute for all courses
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
                if course.startswith('CS'):
                    cs_credits += hour
                else:
                    noncs_credits += hour

                cursor.execute("UPDATE student_courses SET form1 = TRUE WHERE course_id = %s AND user_id = %s AND counts = 1", (str(course), session['user_id']))
                cursor.execute("INSERT INTO form1(user_id, course_id) VALUES(%s, %s)", (session["user_id"], course))
                # If no updates were made, the student specified a course they did not yet take.
                # an error is returned if they clicked the option to send to grad secretary
                rows_updated = cursor.rowcount
                if rows_updated == 0 and graduate_request == 1:
                    return render_template('form1-failure.html', error = "You put a course you don't have!")
            else:
                cursor.execute("UPDATE student_courses SET form1 = FALSE WHERE course_id = %s AND user_id = %s AND counts = 1", (str(course), session['user_id']))

        
        # Set grad status for the student to true. When viewing form1, faculty advisor sees only those with this set as true
        if session["user_type"] == "PHD" or session["user_type"] == "MS":
            cursor.execute("UPDATE students SET grad_status = %s WHERE user_id = %s", (graduate_request,session["user_id"]))

        mydb.commit()
        # Check requirements, return error if one not met, and prevent sending to GS in scenario where that option is selected
        error_dic = {0: 'You must complete all 3 core courses required for MS: CSCI 6212, CSCI 6221, and CSCI 6461', 1: "A minimum GPA of 3.0 is required to graduate with an MS", 2: "You must have completed 30 credit hours of coursework, with at most 2 non-cs courses as part", 3: "No more than 2 grades below B to graduate!", 4: "Minimum 3.5 GPA required to graduate with a PHD", 5:"You must have completed at least 36 credit hours, with at least 30 in CS", 6: "Not more than one grade below B to graduate with a PHD", -1: "Success!"}
        passes_auto_requirements = 0
        if session["user_type"] == "MS" and graduate_request == 1:
            passes_auto_requirements = ms_graduates()
        elif graduate_request == 1:
            passes_auto_requirements = phd_graduates()
        # For these two conditions, need just check that all required are present if MS,
        # and total credits is above threshold for both
        elif session["user_type"] == "MS":
            total_credits_count = 0
            if noncs_credits > 5: # if all 3, just add 5 (max 2 of the 3)
                total_credits_count = cs_credits + 5
            else: # else only 2 or less of them, so add their total (all allowed to count)
                total_credits_count = cs_credits + noncs_credits
            if total_credits_count >= 30 and ms_required == 3:
                passes_auto_requirements = -1
            elif total_credits_count >= 30 and ms_required <3:
                passes_auto_requirements = 0
            else:
                passes_auto_requirements = 2
        else:
            if cs_credits + noncs_credits >= 36:
                passes_auto_requirements = -1
            else:
                passes_auto_requirements = 5

        # Result based on the auto-checker
        if passes_auto_requirements == -1:
            faculty_advisor_id = get_faculty_advisor_id(session['user_id'])

        # Insert the Form 1 request into the form1_requests table
            cursor.execute("INSERT INTO form1_requests (student_id, faculty_advisor_id, status) VALUES (%s, %s, %s)",(session['user_id'], faculty_advisor_id, 'FAC'))
            mydb.commit()

        # Send notification to the faculty advisor
            send_notification_to_faculty_advisor(session['user_id'], faculty_advisor_id)
            return render_template('form1-success.html')

        else:
            return render_template('form1-failure.html', error = error_dic.get(passes_auto_requirements))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)