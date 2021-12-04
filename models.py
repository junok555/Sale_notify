from .app import db
from flask_login import UserMixin

#Userクラス
class User(UserMixin, db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50),nullable=False)
    password = db.Column(db.String(25))
    mail     = db.Column(db.String(100),nullable=False, unique=True)
    USER_ID  = db.Column(db.String(255))
    CHANNEL_ACCESS_TOKEN = db.Column(db.String(255))

#Line用Postクラス 
class Post(db.Model):
    id    = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    mail  = db.Column(db.String(100), nullable=False)
    url   = db.Column(db.String(255), nullable=False)

#DBのクリエイト宣言
db.create_all()