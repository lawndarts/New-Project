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
import praw

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '<Task %r>' % self.id #Okay, I think 

@app.route('/')
def index():
    return render_template('index.html')

# authorization page
@app.route('/auth/')
def something():
    """Provide the program's entry point when directly executed.""" 
    scope_input = '*'
    scopes = [scope.strip() for scope in scope_input.strip().split(",")]

    reddit = praw.Reddit(
        client_id = 'tC-RStYYMyOXAVgtuVy3cA',
        client_secret = 'XIJwrc-zKpm-kMB7aR0MCE3DvDGpRw',
        redirect_uri="http://localhost:8080",
        user_agent="obtain_refresh_token/v0 by u/bboe",
    )
    state = str(random.randint(0, 65000))
    url = reddit.auth.url(scopes, state, "permanent")

    print(f"Now open this url in your browser: {url}")
    
    #none of this is running below. I think it needs the user input before it continues
    client = receive_connection()
    data = client.recv(1024).decode("utf-8")
    param_tokens = data.split(" ", 2)[1].split("?", 1)[1].split("&")
    params = {
        key: value for (key, value) in [token.split("=") for token in param_tokens]
    }
    
    if state != params["state"]:
        send_message(
            client,
            f"State mismatch. Expected: {state} Received: {params['state']}",
        )
        return 1
    elif "error" in params:
        send_message(client, params["error"])
        return 1
    
    refresh_token = reddit.auth.authorize(params["code"])
    send_message(client, f"Refresh token: {refresh_token}")
    # print('refresh token:', refresh_token)
    return 0
    # return render_template('auth.html')  where does this go?

def receive_connection():
    """Wait for and then return a connected socket..

    Opens a TCP connection on port 8080, and waits for a single client.

    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("localhost", 8080))
    server.listen(1)
    client = server.accept()[0]
    server.close()
    return client

def send_message(client, message):
    """Send message to client and close the connection."""
    print(message)
    client.send(f"HTTP/1.1 200 OK\r\n\r\n{message}".encode("utf-8"))
    client.close()


if __name__ == "__main__":
    app.run(debug=True)

