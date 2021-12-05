import os,requests, re
from flask import Flask, render_template, request,json, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from linebot import LineBotApi
from linebot.models import TextSendMessage
from flask_sqlalchemy import SQLAlchemy

from bs4 import BeautifulSoup
from time import localtime, sleep
import time,datetime

app = Flask(__name__)

# datebase
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ssense.db'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.urandom(24)
db = SQLAlchemy(app)

# login
login_manager = LoginManager()
login_manager.init_app(app)

# Line message API
# info = json.load(open('info.json', 'r'))
# CHANNEL_ACCESS_TOKEN = info['CHANNEL_ACCESS_TOKEN']
# line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)

# def main(price):
    # USER_ID = info['USER_ID']
    # USER_ID = "TEST"
    # messages = TextSendMessage(text='セール開始\n価格は'+price+'です。')
    # line_bot_api.push_message(USER_ID,messages=messages)
# def main_b():
    # USER_ID = info['USER_ID']
    # USER_ID = "TEST"
    # messages = TextSendMessage(text='セールはまだです')
    # line_bot_api.push_message(USER_ID,messages=messages)

# Line用Postクラス
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    mail = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(255), nullable=False)

# Userクラス
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50),nullable=False)
    password = db.Column(db.String(25))
    mail = db.Column(db.String(100),nullable=False)
    CHANNEL_ACCESS_TOKEN = db.Column(db.String(255))
    USER_ID = db.Column(db.String(255))

# item Class
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(100))
    name = db.Column(db.String(100))
    price = db.Column(db.String(255))

#DBのクリエイト宣言
db.create_all()

# DBが空の状態(最初の1回)はtestuserを作成する
user = User.query.filter_by(username='testuser').first()
if user is None:
    testuser = User(username='TestUser01', mail='test@test.com',password='sha256$ITdMryiUiW7zJlDG$7c916a108872ab5efaf8f8e46acf7a38c7df15375860c0f31335b7deef2b5c4f')
    db.session.add(testuser)
    db.session.commit()

# Userクラスからユーザー情報を読み込む際にuser_idを識別子として使用
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#スクレイピング
# class Scr():
#     def __init__(self, urls):
#         self.urls=urls

#     def geturl(self):
#         all_text=[]
#         for url in self.urls:
#             r=requests.get(url)
#             c=r.content
#             soup=BeautifulSoup(c,"html.parser")
#             article1_content=soup.find_all("p")
#             temp=[]
#             for con in article1_content:
#                 out=con.text
#                 temp.append(out)
#             text=''.join(temp)
#             all_text.append(text)
#             sleep(1)
#         return all_text

@app.route('/', methods=['GET'])
def index():
    url_a = 'https://www.farfetch.com/jp/shopping/men/maison-margiela-x-reebok-classic-tabi-item-16261856.aspx?storeid=12850'
    # url_b = 'https://www.farfetch.com/jp/shopping/men/our-legacy--item-16135241.aspx'
    res = requests.get(url_a)
    soup_price = BeautifulSoup(res.text, 'html.parser').find_all(attrs={"data-tstid": "priceInfo-onsale"})
    soup_name = BeautifulSoup(res.text, 'html.parser').find_all(attrs={"data-tstid": "cardInfo-description"})
    soup_type = type(soup_price)
    price = soup_price[0].contents[0]
    item_name = soup_name[0].contents[0]

    dt_now = datetime.datetime.now()
    items = Item(date=dt_now,name=item_name, price=price)
    db.session.add(items)
    db.session.commit()

    items = Item.query.all()

    if type(soup_price) == str:
        # main(price=price)
        a=11
        return render_template('index.html', a=a,soup=soup_price, soup_type=soup_type,price=price, name=item_name)
    else:
        # main_b()
        a=13
        return render_template('index.html', a=a,soup=soup_price,soup_type=soup_type,price=price,name=item_name,items=items)

@app.route('/register', methods=['GET','POST'])
def signup():
    if request.method == "POST":
        try:
            username = request.form.get('username')
            mail     = request.form.get('mail')
            password = request.form.get('password')
            # new_user = User(username=username, mail=mail, password=password)
            # db.session.add(new_user)
            # db.session.commit()

            # users = db.session.query(User)
            # for u in users:
            #     print("id = {}, username = {}, mail = {}, password = {}".format(u.id, u.username, u.mail, u.password))
            user = User(username=username,mail=mail, password=generate_password_hash(password, method='sha256'))
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("member"))
        except Exception as e:
            return redirect(url_for('index'))
    else:
        return render_template('register.html')
    

@app.route('/login', methods=['GET','POST'])
def loginUser():
    if request.method == "POST":
        mail     = request.form.get('mail')
        password = request.form.get('password')
        user = User.query.filter_by(mail=mail).first()
        if user == None:
            return render_template('login.html', error="指定のユーザーは存在しません")
        else:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                return redirect(url_for('member'))

    else:
        return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('login.html')

@app.route('/member')
@login_required
def member():
    username = current_user.username
    return render_template('member.html',username=username)


if __name__ == '__main__':
    app.run(debug=True)