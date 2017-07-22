import sys
import os
import pymysql
import pymysql.cursors
from flask import Flask
from flask import render_template
from flask_socketio import SocketIO
from flask_socketio import emit
from flask_socketio import join_room
from flask_socketio import leave_room
from flask_socketio import close_room
from flask_socketio import rooms
from flask_socketio import disconnect


__version__ = 0.1


PORT = 8000
HOST = '0.0.0.0'

#Set socketio async mode explicitly, or NONE to let the application decide
ASYNC_MODE = "eventlet"
DEBUG = False
LOG = True

#Initialize DB object
db = pymysql.connect(
    user='root',
    password='testpass',
    host='db',
    database='challenge',
)

# Initiallize Data Model if not already initialized
db.cursor().execute('''CREATE TABLE IF NOT EXISTS accounts (
        id INT NOT NULL AUTO_INCREMENT,
        PRIMARY KEY(id),
        username varchar(16),
        password varchar(40),
        salt varchar(16)
        )ENGINE=InnoDB''')

db.cursor().execute('''CREATE TABLE IF NOT EXISTS room (
        id INT NOT NULL AUTO_INCREMENT,
        PRIMARY KEY(id),
        uid INT,
        name varchar(16),
        messages varchar(512),
        FOREIGN KEY USER_INDEX (uid) REFERENCES accounts (id)
        ON DELETE CASCADE 
        ON UPDATE CASCADE
        )ENGINE=InnoDB''')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
socketio = SocketIO(app, async_mode=ASYNC_MODE)


@socketio.on('/login')
def handle_my_custom_event(json):
    print('received json: ' + str(json))

@app.route('/chat/')
def chat():
    return render_template('chat.html', name=None)

socketio.run(app, host=HOST, port=PORT, debug=DEBUG, log_output=LOG)
