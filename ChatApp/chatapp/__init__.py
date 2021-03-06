import sys
import json
import eventlet
import datetime
import flask
from flask import Flask
from flask import render_template


__version__ = 0.1


PORT = 8000
HOST = '0.0.0.0'

DEBUG = False
RELDR = False


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'



@app.route('/login/')
def login():
    return render_template('login.html', name=None)

@app.route('/chat/')
def chat():
    return render_template('chat.html', name=None)

@app.route('/messages/')
def msg_search():
    return render_template('search.html', name=None)


from .event_handlers import *
socketio.run(app, host=HOST, port=PORT, use_reloader=RELDR, debug=DEBUG, log_output=LOG)
