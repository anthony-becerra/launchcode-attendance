from app import app, db
from flask import request, redirect, render_template, session, flash 
from models import Student, Teacher, Attendance
from datetime import datetime, date 
# from sqlalchemy import desc
# from sqlalchemy.sql import func 
from app import app, db
from models import Student, Teacher, Attendance
from hash_tools import make_hash, check_hash
import val

# Main View
@app.route('/')
def index():
    return render_template('index.html')

session['username'] = username

# Teacher Signup
@app.route('/teacher_signup', methods=["POST", "GET"])
def login():
    return render_template('/teacher_login.html')


# Logout
@app.route('/logout')
def logout():
  del session['email']
  return redirect('/')


# Student Login
@app.route('/student_login', methods=["POST", "GET"])
def student_login():
    if request.method == 'POST':
        first_last = request.form['name'].split()
        first = first_last[0]
        last = first_last[1]
        pin = request.form['pin']
        student = Student.query.filter_by(first = first, last = last).first()

        if student and student.pin == pin:
            # push student into attendance table
            new_attendee =  Attendance(student)
            db.session.add( new_attendee)
            db.session.commit()
        elif student and student.pin != pin:
            return render_template('student_login.html', title = 'Student Login', 
                pin_err = 'Wrong Pin')
    else:
        students = Student.query.order_by(Student.last_name).all()
        return render_template('student_login.html', title = 'Student Login', students = students)


# Attendance List
@app.route('/attendance_list', methods=["POST", "GET"])
def attendance_list():
    return render_template('attendance_list.html')


# Student List
@app.route('/student_list', methods=["POST", "GET"])
def student_list():
    return render_template('student_list.html')

@app.before_request
def require_login():
    blocked_routes = ['index', 'student_login', 'edit_student', 'attendance', 'add_student', 'students']
    allowed_routes = ['teacher_login']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/teacher_login')

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/teacher_login", methods=['GET', 'POST'])
def teacher_login():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        teacher = Teacher.query.filter_by(email = email).first()

        if teacher and check_hash(password, teacher.password):
            session['email'] = email
            return redirect('/')
        elif teacher and not check_hash(password, teacher.password):
            return render_template('teacher_login.html', title = 'Login', login='active',
                password_err = 'Wrong password')
        else:
            return render_template('teacher_login.html', title = 'Login', login='active', 
                email_err = 'Wrong username')
    else:
        return render_template('teacher_login.html', title = 'Signup', signup='active')


@app.route("/teacher_signup", methods=['POST'])
def teacher_signup():

    if request.method == 'POST':
        first = request.form['firstname']
        last = request.form['lastname']
        email = request.form['email']
        password = request.form['password']
        confirm_pass = request.form['confirm']
        # email_DB will be None if email not in DB.
        email_DB = Teacher.query.filter_by(email=email).first()
        
        #### VALIDATION ####

        # check for empty fields
        if val.is_empty(first):
            return render_template('teacher_login.html', title = 'Signup', signup='active', 
                firstname_err = 'Please fill in the first name')
        elif val.is_empty(last):
            return render_template('teacher_login.html', title = 'Signup', signup='active', 
                lastname_err = 'Please fill in the last name')
        elif val.is_empty(email):
            return render_template('teacher_login.html', title = 'Signup', signup='active', 
                email_err = 'Please fill in the email')
        elif val.is_empty(password):
            return render_template('teacher_login.html', title = 'Signup', signup='active', 
                password_err = 'Please fill in the password')

        # check for spaces
        if val.space(email):
            return render_template('teacher_login.html', title = 'Signup', signup='active', 
                email_err = 'Email can\'t have space')

        #check if email already exists
        if email_DB:
            if email_DB.email:
                return render_template('teacher_login.html', title = 'Signup', signup='active', 
                email_err = 'Email already in use')
        
        # check for match
        if password != confirm_pass:
            return render_template('teacher_login.html', title = 'Signup', signup='active', 
                password_err = 'Email already in use', confirm_err = 'Passwords must match')

        # checks length is bigger than 3 characters.
        if val.wrong_len(password) or val.wrong_len(confirm_pass):
            return render_template('teacher_login.html', title = 'Signup', signup='active', 
                password_err = 'Password must be longer than 3 characters')
        
        # Checks that email contains only one period after @ and only one @
        if val.wrong_email(email):
            flash()
            return render_template('teacher_login.html', title = 'Signup', signup='active', 
                email_err = 'Email must contain only one @, one " . " after @')

        new_teacher = Teacher(first, last, email, password)
        db.session.add(new_teacher)
        db.session.commit()
        session['email'] = username
        
if __name__ == "__main__":
    app.run()