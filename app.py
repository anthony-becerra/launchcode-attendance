from flask import Flask, request, redirect, render_template, session, flash 
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date 
# from sqlalchemy import desc
# from sqlalchemy.sql import func 


app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] =  "mysql+pymysql://lc-attendance:root@localhost:8889/lc-attendance"
db = SQLAlchemy(app)
app.secret_key = "y337kGcys&zP3D4"