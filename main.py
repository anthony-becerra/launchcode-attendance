from app import app, db
from flask import request, redirect, render_template, session, flash 
from models import Student, Teacher, Attendance
from datetime import datetime, date 
from app import app, db
from models import Student, Teacher, Attendance
from hash_tools import make_hash, check_hash
import val

# Main View
@app.route('/')
def index():
    session['email'] = "lol@gmail.com"
    return render_template('index.html')

# Logout
@app.route('/logout')
def logout():
  del session['email']
  return redirect('/')

# Attendance List
@app.route('/attendance_list', methods=["POST", "GET"])
def attendance_list():
    return render_template('attendance_list.html')

# TODO
# Student List
# @app.route('/student_list', methods=["POST", "GET"])
# def student_list():
#     return render_template('student_list.html')
#     else:
#         return render_template('teacher_login.html', title = 'Signup', signup='active')

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
            return render_template('teacher_login.html', title = 'Signup', 
            signup='active', firstname_err = 'Please fill in the first name')
        elif val.is_empty(last):
            return render_template('teacher_login.html', title = 'Signup',  
                signup='active', lastname_err = 'Please fill in the last name')
        elif val.is_empty(email):
            return render_template('teacher_login.html', title = 'Signup', 
                signup='active',  email_err = 'Please fill in the email')
        elif val.is_empty(password):
            return render_template('teacher_login.html', title = 'Signup',  
                signup='active', password_err = 'Please fill in the password')
        
        # check for spaces
        if val.space(email):
            return render_template('teacher_login.html', title = 'Signup',  
                signup='active', email_err = 'Email can\'t have space')

        #check if email already exists
        if email_DB:
            if email_DB.email:
                return render_template('teacher_login.html', title = 'Signup', 
                signup='active', email_err = 'Email already in use')
        
        # check for match
        if password != confirm_pass:
            return render_template('teacher_login.html', title = 'Signup',  
                signup='active', confirm_err = 'Passwords must match')

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
        return render_template('teacher_login.html', title = 'Login', login='active')

@app.route('/start_day')
def start_day():
    students = Student.query.all()
    students_att = Attendance.query.filter_by(date_now = date.today()).all()
    
    # checks if not attendace list has been created for the day.
    if not students_att:
        if students:
        # pushes all students into the attendance table, creating 
        # a list for today's date.
            for student in students:
                record = Attendance(student)
                db.session.add(record)
            db.session.commit()
            return redirect('/student_login')
        else:
             # the day's list has not been created
            return render_template('student_login.html', title = 'Student Login',
                day_err = 'Today\'s attendance has\'s been created yet.')
    else:
        # the day's list already created
        return render_template('index.html', title = 'Attendance App',
            day_err = 'Today\'s attendance already created')


@app.route('/student_login', methods=["POST", "GET"])
def student_login():
    students = Student.query.order_by(Student.last_name).all()


    if request.method == 'POST':
        student_id = request.form['student_id']
        pin = request.form['pin']
        confirm_pin = request.form['confirm_pin']
        student = Student.query.get(student_id)
        student_att = Attendance.query.filter_by(owner_id = student_id,
                 date_now = date.today())

        if student_id == "":
            return render_template('student_login.html', title ='Student Login', 
                login_err = "Please select your Name!", students = students)
        elif not pin:
            return render_template('student_login.html', title ='Student Login', 
                pin_err = "Please enter your Pin!", students = students)
        elif not pin.isdigit():
            return render_template('student_login.html', title ='Student Login', 
                pin_err = "Your Pin cannot have Letters!", students = students)
        elif student and student.pin != int(pin):
            return render_template('student_login.html', title ='Student Login', 
                pin_err = "Wrong Pin!", students = students)
        else:
            # make student present in attendance table
            student_att.present = True
            db.session.commit()
            return render_template('student_login.html', title ='Student Login', 
                login_success="Signed in!", students = students)

    else:
        attendance_exists = Attendance.query.filter_by(date_now = date.today()).first()

        # Validate if today's date exists in database
        if attendance_exists is None:
            return render_template('index.html', title = 'Attendance App',
                student_err = 'Please create today\'s attendance list first (Press \'START DAY\' button)')
        
        return render_template('student_login.html', title = 'Student Login', students = students)

@app.route("/attendance", methods=['GET', 'POST'])
def attendance():
    if request.method == 'POST':
        date_now = request.form['date_now']
        attendance = Attendance.query.filter_by(date_now=date_now).all()
        return render_template("attendance.html", attendance=attendance)
    else:
        dates = Attendance.query.filter_by().all()
        return render_template("attendance.html", dates=dates)



if __name__ == "__main__":
    app.run()