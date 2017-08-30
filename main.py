from flask import Flask, request, redirect, render_template, session, flash 
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date 
# from sqlalchemy import desc
# from sqlalchemy.sql import func 
from app import app, db
from models import Student, Teacher, Attendance



if __name__ == "__main__":
    app.run()