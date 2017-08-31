from flask import Flask, request, redirect, render_template, session, flash 
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date 
# from sqlalchemy import desc
# from sqlalchemy.sql import func 
from app import app, db
from models import Student, Teacher, Attendance

# Main View
@app.route('/')
def index():
    return render_template('index.html')


# Teacher Login
@app.route('/teacher_login', methods=["POST", "GET"])
def login():
    return render_template('/teacher_login.html')


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



if __name__ == "__main__":
    app.run()