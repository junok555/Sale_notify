import os,requests, re
from flask import Flask, render_template, request,json, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from linebot import LineBotApi
from linebot.models import TextSendMessage
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR
from bs4 import BeautifulSoup

login_manager = LoginManager()

app = Flask(__name__)
login_manager.init_app(app)

# datebase
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ssense.db'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

# Line message API
# info = json.load(open('info.json', 'r'))
# CHANNEL_ACCESS_TOKEN = info['CHANNEL_ACCESS_TOKEN']
# line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)

# login
#sessionを使う際にSECRET_KEYを設定
app.config['SECRET_KEY'] = 'secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader

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

#Line用Postクラス 
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    mail = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(255), nullable=False)

#Userクラス
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50),nullable=False)
    mail = db.Column(db.String(100),nullable=False)
    CHANNEL_ACCESS_TOKEN = db.Column(db.String(255))
    USER_ID = db.Column(db.String(255))


#DBのクリエイト宣言
db.create_all()

#DBが空の状態(最初の1回)はtestuserを作成する
user = User.query.filter_by(username='testuser').first()
if user is None:
    testuser = User(username='testuser', mail='test@test')
    db.session.add(testuser)
    db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        posts = Post.query.all()
        url_a = 'https://www.farfetch.com/jp/shopping/men/our-legacy-air-kiss-t-item-16134350.aspx?storeid=12080'
        # url_b = 'https://www.farfetch.com/jp/shopping/men/our-legacy--item-16135241.aspx'
        res = requests.get(url_a)
        soup = BeautifulSoup(res.text, 'html.parser').find_all(attrs={"data-tstid": "priceInfo-onsale"})
        soup_type = type(soup)
        price = soup[0].contents[0]
        if type(soup) == str:
            price = soup[0].contents[0]
            # main(price=price)
            return render_template('index.html', posts=posts, soup=soup, soup_type=soup_type,price=price)
        else:
            # main_b()
            return render_template('index.html', posts=posts, soup=soup, value='',soup_type=soup_type,price=price)

    else:
        title = request.form.get('title')
        mail = request.form.get('mail')
        url = request.form.get('url')
        new_post = Post(title=title, mail=mail, url=url)
        db.session.add(new_post)
        db.session.commit()

        return redirect('/')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/user_register', methods=['GET','POST'])
def userregister():
    username = request.form.get('username')
    mail = request.form.get('mail')
    new_user = User(username=username, mail=mail)
    db.session.add(new_user)
    db.session.commit()

    users = db.session.query(User)
    for u in users:
        print("id = {}, username = {}, mail = {}".format(u.id, u.username, u.mail))

    return redirect(url_for("register"))

@app.route('/login')
def login():
    # user = User.query.filter_by(username='jun').first()
    # login_user(user)
    return render_template('login.html')

@app.route('/login_user', methods=['POST'])
def loginUser():
    mail = request.form.get('mail')
    try:
        user = User.query.filter(User.mail == mail).first()
        if user == None:
            return render_template('login.html', error="指定のユーザーは存在しません")
        else:
            login_user(user, remember=True)
    except Exception as e:
        return redirect(url_for('index'))
    return redirect(url_for('member'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('logout.html')

@app.route('/member')
@login_required
def member():
    username = current_user.username
    return render_template('member.html',username=username)

if __name__ == '__main__':
    app.run(debug=True)