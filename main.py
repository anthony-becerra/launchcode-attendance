from app import app, db, ALLOWED_EXTENSIONS
from flask import request, redirect, render_template, session, flash, send_file
from models import Student, Teacher, Attendance
from datetime import datetime, date 
from models import Student, Teacher, Attendance
from hash_tools import make_hash, check_hash
from random import choice
import val
import pandas as pd 
from io import BytesIO # built-in in python, no need to install
import xlsxwriter

def bg_image(key=None):
    bg_images = {'index':'cover_banner_blue-8152795f6794e4bbb9fae2a63ad5bb01.jpg',
                'teacher':'learn_banner_blue-105e0234e99f61dcc8f06852d653d617.jpg',
                'student':'apply_banner_blue-1340ee49156f5f7ac7a4b9bb0ce8ef5c.jpg',
                'settings':'hire_banner_blue-8e55ca145435f6a988067be969412c24.jpg'}
    if key == None:
        return choice(list(bg_images.values()))
    else:
        return bg_images[key]

def allowed_file(filename):
    '''Checks that file extension is in ALLOWED_EXTENSIONS'''
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.before_request 
def require_login():
    allowed_routes = ['teacher_login', 'teacher_signup'] # List of routes user can see without logging in.
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/teacher_login')

# Main View
@app.route('/')
def index():
    #session['email'] = "lol@gmail.com" >>> Test for session without using teacher account
    return render_template('index.html')

# Logout
@app.route('/logout')
def logout():
  del session['email']
  return redirect('/teacher_login')

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
    return render_template('students.html', title = 'Students View', students = students, bg_image = bg_image('settings'))

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
        session['email'] = email
        return redirect("/")

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
            return render_template('teacher_login.html', title = 'Login', login='active')
        elif not teacher:
            flash("Wrong Email!", 'error')
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
        student_att = Attendance.query.filter_by(owner_id = student_id, date_now = date.today()).first()
        
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
            return render_template('student_login.html', title = 'Student Login', student_err = student, students = students, bg_image = bg_image('student'))
        else:
            # no validation error
            # make student present in attendance table
            student_att.present = True     
            db.session.commit()
            flash(student.first_name.title()+" Signed in!", 'info')
            return render_template('student_login.html', title = 'Student Login', students = students, bg_image = bg_image('student'))
    else:
        attendance_exists = Attendance.query.filter_by(date_now = date.today()).first()

        # Validate if today's date exists in database
        if attendance_exists is None:
            flash('Please create today\'s attendance list first (Press \'START DAY\' button)' , 'error')
            return redirect('/')
        
        return render_template('student_login.html', title = 'Student Login', students = students, bg_image = bg_image('student'))

# Allows students to change their pin the very first time
# (first time an attendance list is created) the sign in.
@app.route('/change_pin', methods = ['GET', 'POST'])
def change_pin():

    if request.method == 'GET':
        student_id = request.args.get('id')
        student = Student.query.get(student_id)

        return render_template('change_pin.html', title = 'Change Pin', student = student, bg_image = bg_image('student'))
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
            return render_template('change_pin.html', title = 'Change Pin', student = student, bg_image = bg_image('student'))

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
        return render_template("attendance.html", title = 'Attendance View', attendance = attendance, bg_image = bg_image('settings'))
    else:
        # dates = Attendance.query.distinct(Attendance.date_now)
        dates = db.session.query(Attendance.date_now).distinct()
        return render_template("attendance.html", title = 'Attendance View', dates = dates, bg_image = bg_image('settings'))
        

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
        return render_template("edit_student.html", title = 'Edit Student', student = student, bg_image = bg_image('settings'))

# Adds all the cohorts students at once into the student table
# only accepts .xlsx files
@app.route('/upload_file', methods = ['POST'])
def upload_file():

    if request.method == 'POST':     
        file = request.files['file']
        # checks if user uploads no file
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect('/students')
        if file and allowed_file(file.filename):
            # TODO prevent people from uploading malicious files with the 
            # function below
            # file = secure_filename(file.filename)

            # ----------- Reads Files and pushes to student table -------------
            df = pd.read_excel(file)
            # df.columns is a list of all the table headings, 'First Name' and 'Last Name'
            # in this case.
            first_name = list(df[df.columns[0]])
            last_name = list(df[df.columns[1]])
            #  names is a list of tupples in the form of (first_name, last_name)
            names = zip(first_name,last_name)

            # creates a record for row in students.xlsx into the student table.
            for name in names:
                student = Student(name[0].title(), name[1].title())
                db.session.add(student)
            db.session.commit()
            flash('Students entered in the system!', 'info')
            return redirect('/students')
        else:
            #  User uploaded the wrong type of files
            flash('You can only upload excel files with .xlsx extension', 'error')
            return redirect('/students')


@app.route('/download_att', methods=['GET'])
def download_list():
        
        date_att = request.args.get('date_att')
        att_list = Attendance.query.filter_by(date_now=date_att).all()
        first_names = []
        last_names = []
        date = []
        present =[]
        
        # Get the information from attedance table and populates the arrays above
        for att in att_list:
            first_names.append(att.owner.first_name)
            last_names.append(att.owner.last_name)
            date.append(att.date_now)
            present.append(att.present)
        
        # creates a dictionary where names,date, present, will be the headers for the spreadsheet
        # and the values(lists, see above) are rows for each column.
        df = pd.DataFrame({'First Name': first_names, 'Last Name': last_names, 
            'Date': date, 'Present': present})
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        df.to_excel(writer, 'Sheet1', index=False)
        writer.save()
        output.seek(0)

        return send_file(output, attachment_filename = 'attendance:' + str(att.date_now) + '.xlsx', as_attachment=True)

@app.route('/view_att', methods = ['GET'])
def view_att():
    if request.method == 'GET':
        date_selected = request.args.get('date_selected')
        
        att_list = Attendance.query.filter_by(date_now = date_selected).all()
        return render_template('view_att.html', att_list = att_list, bg_image = bg_image('settings'))
    

@app.route('/edit_att', methods = ['GET','POST'])
def edit_att():
    if request.method == 'GET':
        student_id= request.args.get('student_id')
        date_selected = request.args.get('date_selected')
        
        att_student = Attendance.query.filter_by(owner_id = student_id,
            date_now = date_selected).first()
        flash('Select an option from below', 'info')
        return render_template('edit_att.html', att_student = att_student, bg_image = bg_image('settings'))
    else:
        att_id = request.form['att_id']
        present = request.form['present']
        if present == 'Present':
            present = True
        else:
            present = False
        att = Attendance.query.filter_by(id=att_id).first()
        att_list = Attendance.query.filter_by(date_now = att.date_now).all()

        att.present = present
        db.session.commit()
        flash(att.owner.first_name.title() + '\'s attendance changed!', 'info')
        return render_template('view_att.html', att_list = att_list, bg_image = bg_image('settings'))


if __name__ == "__main__":
    app.run()