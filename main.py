from app import app, db
from flask import request, redirect, render_template, session, flash 
from models import Student, Teacher, Attendance
from datetime import datetime, date 
from models import Student, Teacher, Attendance
from hash_tools import make_hash, check_hash
from random import choice
import val

def bg_image(key=None):
    bg_images = {'index':'cover_banner_blue-8152795f6794e4bbb9fae2a63ad5bb01.jpg',
                'teacher':'learn_banner_blue-105e0234e99f61dcc8f06852d653d617.jpg',
                'student':'apply_banner_blue-1340ee49156f5f7ac7a4b9bb0ce8ef5c.jpg',
                'settings':'hire_banner_blue-8e55ca145435f6a988067be969412c24.jpg'}
    if key == None:
        return choice(list(bg_images.values()))
    else:
        return bg_images[key]

# Main View
@app.route('/')
def index():
    session['email'] = "lol@gmail.com"
    return render_template('index.html', title = 'LaunchCode Attendance', bg_image = bg_image())

# Logout
@app.route('/logout')
def logout():
  del session['email']
  return redirect('/')

# Attendance List
@app.route('/attendance_list', methods=["POST", "GET"])
def attendance_list():
    return render_template('attendance_list.html', title = 'LaunchCode Attendance', bg_image = bg_image('settings'))

#TODO
@app.route('/students', methods=["POST", "GET"])
def students():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']

        student = Student(first_name, last_name)
        db.session.add(student)
        db.session.commit()
        return redirect('/students')

    students = Student.query.all()
    return render_template('students.html', students = students, bg_image = bg_image('settings'))

@app.route("/teacher_signup", methods=['POST'])
def teacher_signup():

    if request.method == 'POST':
        first = request.form['firstname']
        last = request.form['lastname']
        email = request.form['email']
        password = request.form['password']
        confirm_pass = request.form['confirm']
        # email_DB will be None if email not in DB.
        email_DB = Teacher.query.filter_by(email = email).first()
        
        #### VALIDATION ####
        err = False
        # check for empty fields
        if val.is_empty(first):
            flash('Please fill in the first name', 'error')
            err = True
        elif val.is_empty(last):
            flash('Please fill in the last name', 'error')
            err = True
        elif val.is_empty(email):
            flash('Please fill in the email', 'error')
            err = True
        elif val.is_empty(password):
            flash('Please fill in the password', 'error')
            err = True
        
        # check for spaces
        if val.space(email):
            flash('Email can\'t have space', 'error')
            err = True

        #check if email already exists
        if email_DB:
            if email_DB.email:
                flash('Email already in use', 'error')
                err = True
        
        # check for match
        if password != confirm_pass:
            flash('Passwords must match', 'error')
            err = True

        # checks length is bigger than 3 characters.
        if val.wrong_len(password) or val.wrong_len(confirm_pass):
            flash('Password must be longer than 3 characters', 'error')
            err = True
        
        # Checks that email contains only one period after @ and only one @
        if val.wrong_email(email):
            flash('Email must contain only one @, one " . " after @', 'error')
            err = True
        
        if err == True:
            return render_template('teacher_login.html', title = 'Signup', signup ='active', bg_image = bg_image('teacher'))

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
            flash("Wrong Password!", 'error')

    return render_template('teacher_login.html', title = 'Login', login = 'active', bg_image = bg_image('teacher'))

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
            flash('Today\'s attendance hasn\'t been created yet.', 'error')
            return redirect('/')
    else:
        # the day's list already created
        flash('Today\'s attendance already created', 'error')
        return redirect('/')


@app.route('/student_login', methods=["POST", "GET"])
def student_login():
    students = Student.query.order_by(Student.last_name).all()

    if request.method == 'POST':
        student_id = request.form['student_id']
        pin = request.form['pin']
        student = Student.query.get(student_id)
        student_att = Attendance.query.filter_by(owner_id = student_id,
                 date_now = date.today()).first()
        
        ### Validation ###
        err = False

        if not pin:
            flash("Please enter your Pin!", 'error')
            err = True
        elif not pin.isdigit():
            flash("Your Pin cannot have Letters!", 'error')
            err = True
        elif student and student.pin == 0 and student.pin == int(pin):
            # Redirect student to change pin if it's the first time the sign in.
            flash("Please change your pin", 'error')
            return redirect('/change_pin?id=' + student_id)
        elif student and student.pin != int(pin):
            flash("Wrong Pin!", 'error')
            err = True
        if err == True:
            return render_template('student_login.html', tit l e = 'Student Login', students = students, bg_image = bg_image('student'))
        else:
            # no validation error
            # make student present in attendance table
            student_att.present = True     
            db.session.commit()
            flash(student.first_name.title()+" Signed in!", 'info')
            return render_template('student_login.html', tit l e = 'Student Login', students=students, bg_image = bg_image('student'))
    else:
        attendance_exists = Attendance.query.filter_by(date_now = date.today()).first()

        # Validate if today's date exists in database
        if attendance_exists is None:
            flash('Please create today\'s attendance list first (Press \'START DAY\' button)' , 'error')
            return redirect('/')
        
        return render_template('student_login.html', tit l e = 'Student Login', students=students, bg_image = bg_image('student'))

# Allows students to change their pin the very first time
# (first time an attendance list is created) the sign in.
@app.route('/change_pin', methods = ['GET', 'POST'])
def change_pin():

    if request.method == 'GET':
        student_id = request.args.get('id')
        student = Student.query.get(student_id)

        return render_template('change_pin.html', student=student, title = 'Change Pin', bg_image = bg_image('student'))
    else:
        student_id = request.form['student_id']
        student = Student.query.get(student_id)
        student_att = Attendance.query.filter_by(owner_id=student_id,
            date_now = date.today()).first()
        pin = request.form['pin']
        confirm_pin = request.form['confirm_pin']

        ### Validation ###
        err = False
        if val.is_empty(pin) or val.is_empty(confirm_pin):
            flash('Please enter a pin', 'error')
            err = True
        elif pin != confirm_pin:
            flash('Pins must match', 'error')
            err = True
        elif len(pin) != 4 or not pin.isdigit():
            flash('Pin must be 4 digits long and can only contain integers', 'error')
            err = True
        elif int(pin) == 0:
            flash('Your pin can\'t be 0000', 'error')
            err = True

        if err == True:
            return render_template('change_pin.html',student=student, title = 'Change Pin', bg_image = bg_image('student'))

        # change pin in the user table
        student.pin = pin
        # sign in students for the day, attendance table
        student_att.present = True     
        db.session.commit()
        flash(student.first_name.title() +' Signed in!', 'info')
        return redirect('/student_login')

@app.route("/attendance", methods=['GET', 'POST'])
def attendance():
    if request.method == 'POST':
        date_now = request.form['date_now']
        attendance = Attendance.query.filter_by(date_now=date_now).all()
        return render_template("attendance.html", attendance = attendance, bg_image = bg_image('settings'))
    else:
        dates = Attendance.query.filter_by().all()
        return render_template("attendance.html", dates = dates, bg_image = bg_image('settings'))


@app.route("/edit_student", methods=['GET', 'POST'])
def edit_student():
    if request.method == 'POST':
        id = request.form['student_id']
        student = Student.query.filter_by(id=id).first()

        first_name = request.form['first_name']
        last_name = request.form['last_name']
        pin = request.form['pin']
        cohort = request.form['cohort']
        city = request.form['city']

        student.first_name = first_name
        student.last_name= last_name
        student.pin = pin
        student.cohort = cohort
        student.city = city

        db.session.commit()
        return redirect('/students')
    else:
        id = request.args.get('id')  
        student = Student.query.filter_by(id=id).first()
        return render_template("edit_student.html", student=student, bg_image = bg_image('settings'))

if __name__ == "__main__":
    app.run()