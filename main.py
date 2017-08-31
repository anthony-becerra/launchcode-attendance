from app import app, db
from flask import request, redirect, render_template, session, flash 
from models import Student, Teacher, Attendance
from datetime import datetime, date 
# from sqlalchemy import desc
# from sqlalchemy.sql import func 

@app.before_request
def require_login():
    blocked_routes = ['index', 'student_login', 'edit_student', 'attendance', 'add_student', 'students']
    allowed_routes = ['teacher_login', 'teacher_signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/teacher_login')

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/teacher_login", methods=['GET', 'POST'])
def teacher_login():
    if request.method == 'POST':
        return redirect("/")
    else:
        session['email'] = "blah@gmail.com"
        return render_template("teacher_login.html", title="Login", login="active")

@app.route("/teacher_signup", methods=['POST'])
def teacher_signup():
    if request.method == 'POST':
        return render_template("teacher_login.html", title="Signup", signup="active")

if __name__ == "__main__":
    app.run()