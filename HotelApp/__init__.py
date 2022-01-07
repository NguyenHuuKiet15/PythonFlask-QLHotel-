from flask import Flask
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import cloudinary

app = Flask(__name__)

app.secret_key = 'abcd^&(JADJLFAIq128HADHJKvavnhae12345!@#$%'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/cnpmhoteldb?charset=utf8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['COMMENT_SIZE'] = 6

cloudinary.config(
    cloud_name='hk123456',
    api_key='536869117489884',
    api_secret='HCYxvDXunQ9R4POyxQuu3nywoxk',
)

db = SQLAlchemy(app=app)
login = LoginManager(app=app)
