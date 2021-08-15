import os,requests, re
from flask import Flask, render_template, request,json, redirect
from linebot import LineBotApi
from linebot.models import TextSendMessage
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import INTEGER, VARCHAR
from bs4 import BeautifulSoup

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ssense.db'
db = SQLAlchemy(app)

info = json.load(open('info.json', 'r'))
CHANNEL_ACCESS_TOKEN = info['CHANNEL_ACCESS_TOKEN']
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)

def main():
    USER_ID = info['USER_ID']
    messages = TextSendMessage(text='test message \n test message')
    line_bot_api.push_message(USER_ID,messages=messages)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), nullable=False)
    mail = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(255), nullable=False)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        posts = Post.query.all()
        url = 'https://www.farfetch.com/jp/shopping/men/our-legacy-air-kiss-t-item-16134350.aspx?storeid=12080'
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser').find_all(attrs={"data-tstid": "priceInfo-onsale"})
        value = soup[0].contents[0]
        if value:
            main()
            return render_template('index.html', posts=posts, soup=soup, value=value)
    else:
        title = request.form.get('title')
        mail = request.form.get('mail')
        url = request.form.get('url')
        new_post = Post(title=title, mail=mail, url=url)
        db.session.add(new_post)
        db.session.commit()

        return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)