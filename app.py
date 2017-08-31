from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] =  "mysql+pymysql://lc-attendance:root@localhost:8889/lc-attendance"
db = SQLAlchemy(app)
app.secret_key = "y337kGcys&zP3D4"