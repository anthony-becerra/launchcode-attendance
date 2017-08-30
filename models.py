from app import db
from flask_sqlalchemy import SQLAlchemy  
from datetime import datetime, date

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(120))
    lastName = db.Column(db.String(120))
    pin = db.Column(db.Integer)
    cohort = db.Column(db.Integer)
    city = db.Column(db.String(120))
    attendance_date = db.relationship("Attendance", backref="owner")
    

    def __init__(self, firstName, lastName, pin=0000, cohort=1,city="Miami"):
        self.firstName = firstName
        self.lastName = lastName
        self.pin = pin
        self.cohort = cohort
        self.city = city
        
        
        # if pub_date == None:
        #     pub_date = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
        # self.pub_date = pub_date

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstName = db.Column(db.String(120))
    lastName = db.Column(db.String(120))
    email = db.Column(db.String(120))
    password = db.Column(db.String(120))

    def __init__(self, firstName, lastName, email, password):
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.password = password


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    time = db.Column(db.Time)
    owner_id = db.Column(db.Integer, db.ForeignKey("student.id"))
    

    def __init__(self, owner, date=None, time=None):
        if date == None:
            date = date.today()
        if time == None:
            time = datetime.time()
        self.time = time 
        self.date = date 
        self.owner = owner

