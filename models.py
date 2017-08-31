from app import db
from flask_sqlalchemy import SQLAlchemy  
from datetime import datetime, date
from hash_tools import make_hash, check_hash

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))
    pin = db.Column(db.Integer)
    cohort = db.Column(db.Integer)
    city = db.Column(db.String(120))
    attendance_date = db.relationship("Attendance", backref="owner")
    

    def __init__(self, first_name, last_name, pin=0000, cohort=1, city="Miami"):
        self.first_name = first_name
        self.last_name = last_name
        self.pin = pin
        self.cohort = cohort
        self.city = city


class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(120))
    last_name = db.Column(db.String(120))
    email = db.Column(db.String(120))
    password = db.Column(db.String(120))

    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = make_hash(password)


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_now = db.Column(db.Date)
    time_now = db.Column(db.Time)
    present = db.Column(db.Boolean)
    owner_id = db.Column(db.Integer, db.ForeignKey("student.id"))
    

    def __init__(self, owner, date_now=None, time_now=None):
        if date_now == None:
            date_now = date.today()
        if time_now == None:
            time_now = datetime.time(datetime.now()).strftime("%H:%M:%S")
        self.time_now = time_now
        self.date_now = date_now
        self.owner = owner
        self.present = False

