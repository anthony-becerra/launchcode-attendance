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
            flash('Please fill in the first name')
            return render_template('teacher_login.html', title = 'Signup', signup='active')
        elif val.is_empty(last):
            flash('Please fill in the last name')
            return render_template('teacher_login.html', title = 'Signup', signup='active')
        elif val.is_empty(email):
            flash('Please fill in the email')
            return render_template('teacher_login.html', title = 'Signup', signup='active')
        elif val.is_empty(password):
            flash('Please fill in the password')
            return render_template('teacher_login.html', title = 'Signup', signup='active')
        
        # check for spaces
        if val.space(email):
            flash('Email can\'t have space')
            return render_template('teacher_login.html', title = 'Signup', signup='active')

        #check if email already exists
        if email_DB:
            if email_DB.email:
                flash('Email already in use')
                return render_template('teacher_login.html', title = 'Signup', signup='active')
        
        # check for match
        if password != confirm_pass:
            flash('Passwords must match')
            return render_template('teacher_login.html', title = 'Signup')

        # checks length is bigger than 3 characters.
        if val.wrong_len(password) or val.wrong_len(confirm_pass):
            flash('Password must be longer than 3 characters')
            return render_template('teacher_login.html', title = 'Signup', signup='active')
        
        # Checks that email contains only one period after @ and only one @
        if val.wrong_email(email):
            flash('Email must contain only one @, one " . " after @')
            return render_template('teacher_login.html', title = 'Signup', signup='active')

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
            flash("Wrong Password!")
            return render_template('teacher_login.html', title = 'Login', login='active')
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
            flash('Today\'s attendance has\'s been created yet.')
            return render_template('student_login.html', title = 'Student Login')
    else:
        # the day's list already created
        flash('Today\'s attendance already created')
        return render_template('index.html', title = 'Attendance App')


@app.route('/student_login', methods=["POST", "GET"])
def student_login():
    students = Student.query.order_by(Student.last_name).all()


    if request.method == 'POST':
        student_id = request.form['student_id']
        pin = request.form['pin']
        student = Student.query.get(student_id)
        student_att = Attendance.query.filter_by(owner_id = student_id,
                 date_now = date.today()).first()
        
        if not pin:
            flash("Please enter your Pin!")
            return render_template('student_login.html', title ='Student Login', students = students)
        elif not pin.isdigit():
            flash("Your Pin cannot have Letters!")
            return render_template('student_login.html', title ='Student Login', students = students)
        elif student and int(student.pin) == 0:
            # Redirect student to change pin if it's the first time the sign in.
            flash("Please change your pin")
            return redirect('/change_pin?id=' + student_id)
        elif student and student.pin != int(pin):
            flash("Wrong Pin!")
            return render_template('student_login.html', title ='Student Login', students = students)
        else:
            # no validation error
            # make student present in attendance table
            student_att.present = True     
            db.session.commit()
            flash("{0} Signed in!".format(student.first_name.title()))
            return render_template('student_login.html', title ='Student Login', students = students)

    else:
        attendance_exists = Attendance.query.filter_by(date_now = date.today()).first()

        # Validate if today's date exists in database
        if attendance_exists is None:
            flash('Please create today\'s attendance list first (Press \'START DAY\' button)')
            return render_template('index.html', title = 'Attendance App')
        
        return render_template('student_login.html', title = 'Student Login', students = students)

# Allows students to change their pin the very first time
# (first time an attendance list is created) the sign in.
@app.route('/change_pin', methods = ['GET', 'POST'])
def change_pin():

    if request.method == 'GET':
        student_id = request.args.get('id')
        student = Student.query.get(student_id)
        # return render_template('change_pin.html', name = name, student = student)
        return render_template('change_pin.html',student = student,
            title = 'Change Pin')
    else:
        student_id = request.form['student_id']
        student = Student.query.get(student_id)
        pin = request.form['pin']
        confirm_pin = request.form['confirm_pin']

        # Validation
        if val.is_empty(pin) or val.is_empty(confirm_pin):
            flash('Please enter a pin')
            return render_template('change_pin.html',student = student,
            title = 'Change Pin')
        elif pin != confirm_pin:
            flash('Pins must match')
            return render_template('change_pin.html',student = student,
            title = 'Change Pin')
        elif len(pin) != 4 or not pin.isdigit():
            flash('Pin must be 4 digits long and can only contain integers')
            return render_template('change_pin.html',student = student,
            title = 'Change Pin')
        
        # change pin in the user table
        student.pin = pin
        db.session.commit()
        flash(student.first_name.title() + ' Logged in!')
        return redirect('/student_login')

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