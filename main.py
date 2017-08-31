from app import app, db
from flask import request, redirect, render_template, session, flash 
from models import Student, Teacher, Attendance
from datetime import datetime, date 
# from sqlalchemy import desc
# from sqlalchemy.sql import func 
from app import app, db
from models import Student, Teacher, Attendance
from hash_tools import make_hash, check_hash

# Main View
@app.route('/')
def index():
    return render_template('index.html')



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
    return render_template('student_login.html')


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
        

        return redirect("/")
    else:
        return render_template("teacher_login.html")

@app.route("/teacher_login", methods=['GET', 'POST'])
def teacher_signup():
    if request.method == 'POST':
        


        return redirect("/")
    else:
        return render_template("teacher_login.html")


if __name__ == "__main__":
    app.run()