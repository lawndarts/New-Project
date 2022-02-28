from urllib import request
from flask import Flask, request, redirect
from flask import render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from gevent import reinit

# auth imports
import random
import socket
import sys
import praw, requests, json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

scope_input = '*'
scopes = [scope.strip() for scope in scope_input.strip().split(",")]

reddit = praw.Reddit(
    client_id = 'tC-RStYYMyOXAVgtuVy3cA',
    client_secret = 'XIJwrc-zKpm-kMB7aR0MCE3DvDGpRw',
    redirect_uri="http://127.0.0.1:5000/auth",
    user_agent="obtain_refresh_token testing by u/Solid-Guidance1826 Im sorry, Im bad at this. contact:henryp959@gmail.com",
)
state = str(random.randint(0, 65000))


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<Task %r>' % self.id 

@app.route('/')
def index():
    return render_template('index.html')

# authorization page
@app.route('/auth')
def auth():
    thing = request.args.get('code')
    print('code:', thing)
    print(reddit.auth.authorize(thing))
    print(reddit.user.me())

    return render_template('something.html')

# def revokeToken(token, tokentype):
#     r = requests.post('https://www.reddit.com/api/v1/revoke_token',
#                       auth = (app.config['CLIENT_ID'],app.config['CLIENT_SECRET']),
#                       headers = {'User-agent':app.config['USER_AGENT'],'Content-Type':'application/x-www-form-urlencoded'},
#                       data = {'token':token,'token_type_hint':tokentype})


@app.route('/login')
def login():
    return redirect(reddit.auth.url(scopes, state, "permanent"))

#doesnt do anything yet
@app.route('/logout')
def logout():
    return redirect(url_for('app.index'))

@app.route('/chart')
def showChart():
    jsdict = postingActivityDay()
    topSubs = topTenSubreddits()
    return render_template('showSomething.html', jsdict=jsdict, topSubs = topSubs)

def postingActivityDay():
    supportSubs = ['test', 'videos','pcgaming']
    DoTW = {'Sunday': 0, 'Monday': 0, 'Tuesday': 0, 'Wednesday': 0, 'Thursday': 0, 'Friday': 0, 'Saturday': 0,}
    comments =  reddit.user.me().comments.new(limit=50)
    for comment in comments:
        if(str(comment.subreddit) in supportSubs):
            unix_val = datetime.fromtimestamp(comment.created)
            day = unix_val.weekday()
            if(day == 0): day = 'Sunday'
            elif(day == 1): day = 'Monday'
            elif(day == 2): day = 'Tuesday'
            elif(day == 3): day = 'Wednesday'
            elif(day == 4): day = 'Thursday'
            elif(day == 5): day = 'Friday'
            elif(day == 6): day = 'Saturday'
            if(day in DoTW):
                DoTW[day] += 1
    return DoTW


def topTenSubreddits():
    subList = {}
    comments =  reddit.user.me().comments.new(limit=500)
    for comment in comments:
        if(str(comment.subreddit) in subList):
            subList[str(comment.subreddit)] += 1
        else:
            subList[str(comment.subreddit)] = 1
    topSubs = sorted(subList, key=subList.get, reverse=True)[:10]
    return topSubs
    #now theres a list of the top 10 subs and their values can be retrieved from a dictionary. Find out best way to return data

if __name__ == "__main__":
    app.run(debug=True)

