import sys
import os
import pymysql
import pymysql.cursors
import json
import hashlib
import eventlet
import datetime
import flask
from binascii import hexlify
from flask import Flask
from flask import render_template
from flask_socketio import SocketIO
from flask_socketio import emit
from flask_socketio import send


__version__ = 0.1


PORT = 8000
HOST = '0.0.0.0'

#Set socketio async mode explicitly, or NONE to let the application decide
ASYNC_MODE = 'eventlet'
DEBUG = False
RELDR = False
LOG = True

#Initialize DB object
db = pymysql.connect(
    user='root',
    password='Env91gve',
    host='localhost',
    database='challenge',
)

# Initiallize Data Model if not already initialized
db.cursor().execute('''CREATE TABLE IF NOT EXISTS accounts (
        id INT NOT NULL AUTO_INCREMENT,
        PRIMARY KEY(id),
        username varchar(16),
        password varchar(96),
        salt varchar(16)
        )ENGINE=InnoDB''')
db.cursor().execute('''CREATE TABLE IF NOT EXISTS images (
        id INT NOT NULL AUTO_INCREMENT,
        PRIMARY KEY(id),
        url TEXT,
        width SMALLINT,
        height SMALLINT
        )ENGINE=InnoDB''')

db.cursor().execute('''CREATE TABLE IF NOT EXISTS videos (
        id INT NOT NULL AUTO_INCREMENT,
        PRIMARY KEY(id),
        url TEXT,
        source TEXT,
        length TIME
        )ENGINE=InnoDB''')


db.cursor().execute('''CREATE TABLE IF NOT EXISTS messages (
        id INT NOT NULL AUTO_INCREMENT,
        PRIMARY KEY(id),
        sid INT,
        rid INT,
        message varchar(512),
        image INT NULL,
        video INT NULL,
        date DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY SEND_INDEX (sid) REFERENCES accounts (id)
        ON DELETE CASCADE 
        ON UPDATE CASCADE,
        FOREIGN KEY RECV_INDEX (rid) REFERENCES accounts (id)
        ON DELETE CASCADE 
        ON UPDATE CASCADE
        )ENGINE=InnoDB''')


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
socketio = SocketIO(app, sync_mode=ASYNC_MODE)

def chk_user(username):
    if not username:
        raise Exception("Username is empty\n")

    with db.cursor() as cursor:
        sql = "SELECT `id` FROM `accounts` WHERE `username`=%s"
        cursor.execute(sql, (username))
        result = cursor.fetchone()
        if result:
            return result[0]
    raise Exception("Failed to get id for {0}".format(username))

def useradd(user, passwd, salt):
    with db.cursor() as cursor:
        sql = "INSERT INTO `accounts` (`username`, `password`, `salt`) VALUES (%s, %s, %s)"
        cursor.execute(sql, (user, passwd, salt))
        result = cursor.fetchone()
    db.commit()
    return result

def salt_pass(passwd, salt=None):

    if passwd:
        try:
            if not salt:
                salt = hexlify(os.urandom(8))
        except Exception as e:
            raise Exception("failed to salt password: {0}".format(e))
            
        return hexlify(hashlib.pbkdf2_hmac("sha256", hexlify(passwd), salt, 100000)), salt
    raise Exception("Password is empty, failed to salt password")


def user_auth(uid, passwd):

    if not passwd:
        raise Exception("Password is empty")

    with db.cursor() as cursor:
        sql = "SELECT `salt`, `password` FROM `accounts` WHERE `id`=%s"
        cursor.execute(sql, (uid))
        result = cursor.fetchone()

    try:
        prov_pass = salt_pass(passwd, result[0])
    except Exception as e:
        raise Exception("Failed to calculate password for authentication")
    else:
        if prov_pass[0]  == result[1]:
            return True
        raise Exception("Failed to Authenticate: hashes do not match")
 

def store_msg(msg, s_user, r_user, images=None, video=None):
    if not msg and not s_user and not r_user:
        raise Exception("message arguments are not complete")

    try:
        sid = chk_user(s_user)
        rid = chk_user(r_user)
    except Exception as e:
        raise Exception("Failed to find user in Database: {0}".format(e))
    else:
        with db.cursor() as cursor:
            if images:
                sql = 'SELECT `id` FROM `images` WHERE `url`=%s AND `width`=%s AND `height`=%s'
                cursor.execute(sql, (images[0], images[1], images[2]))
                image_id = cursor.fetchone()
                if not image_id:
                    sql = "INSERT INTO `images` (`url`, `width`, `height`) VALUES (%s, %s, %s)"
                    cursor.execute(sql, (images[0], images[1], images[2]))
                    db.commit()
                    sql = 'SELECT `id` FROM `images` WHERE `url`=%s AND `width`=%s AND `height`=%s'
                    cursor.execute(sql, (images[0], images[1], images[2]))
                    image_id = cursor.fetchone()
            else:
                image_id = images

            if video:
                sql = 'SELECT `id` FROM `video` WHERE `url`=%s AND `source`=%s AND `length`=%s'
                cursor.execute(sql, (video[0], video[1], video[2]))
                vid_id = cursor.fetchone()
                if not vid_id:
                    sql = "INSERT INTO `video` (`url`, `source`, `length`) VALUES (%s, %s, %s)"
                    cursor.execute(sql, (video[0], video[1], video[2]))
                    db.commit()
                    sql = 'SELECT `id` FROM `video` WHERE `url`=%s AND `source`=%s AND `length`=%s'
                    cursor.execute(sql, (video[0], video[1], video[2]))
                    vid_id = cursor.fetchone()
            else:
                vid_id = video

            sql = "INSERT INTO `messages` (`sid`, `rid`, `message`, `image`, `video`) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (sid, rid, msg, image_id, vid_id))
            db.commit()
            cursor.close()
        return msg_fetch(sid, rid)

def msg_fetch(sid, rid):
        with db.cursor() as cursor:
            sql = 'SELECT `date`, `message`, `image`, `video` FROM `messages` WHERE `sid` AND `rid` IN (%s, %s) ORDER BY UNIX_TIMESTAMP(date) DESC'
            cursor.execute(sql, (sid, rid))
            result = cursor.fetchall()

            cursor.close()


        return result


@socketio.on('login')
def handle_logins(data):
    uid = None
    
    try:
        username = json.loads(json.dumps(data))["username"]
        password = json.loads(json.dumps(data))["password"]
    except Exception as e:
        sys.stderr.write("Empty fields in JSON string: {0}".format(e))
        emit('login', False)
    else:
        try:
            uid = chk_user(username)
        except Exception as e:
            sys.stderr.write("User doesn't exist: {0}, adding user {1}".format(e, username))


    if uid:
        try:
            user_auth(uid, password)
        except Exception as e:
            sys.stderr.write("Failed verify user: {0}".format(e))
            emit('login', False)
        else:
            print("User: {0} logged in successfully".format(username))
            emit('login', True)
    else:
        try:
            password, salt = salt_pass(password)
        except Exception as e:
            sys.stderr.write("Failed to salt password: {0}".format(e))
            emit('login', False)
        else:
            try:
                useradd(username, password,  salt) 
            except Exception as e:
                sys.stderr.write("Failed to create new user: {0}".format(e))
                emit('login', False)
                return
            else:
                emit('login', True)

def _json_parse(_json):
    if not _json:
        return None

    for k,v in _json.iteritems():
        if not v:
            return None
    return True



        


@socketio.on('msg')
def handle_txt_msg_event(json_str):
    date_format = '%Y-%m-%d %H:%M:%S'

    if json_str['data']:

        if _json_parse(json_str['data']['image']):
            image = (
                    json_str['data']['image']['url'],
                    json_str['data']['image']['Width'],
                    json_str['data']['image']['Height']
                    )
        else:
            image = None

        if _json_parse(json_str['data']['video']):
            video = (
                    json_str['data']['video']['url'],
                    json_str['data']['video']['source'],
                    json_str['data']['video']['length']
                    )
        else:
            video = None

        try:
            entry = store_msg(
                              json_str['data']['msg'], 
                              json_str['data']['sid'], 
                              json_str['data']['rid'],
                              image,
                              video
                             )
        except Exception as e:
            sys.stderr.write("Failed to save message: {0}".format(e))
        else:
            print(entry[0][0].strftime(date_format), entry[0][1])
            emit('client event', str({'date' : entry[0][0].strftime(date_format),
                                      'message': entry[0][1],
                                      'image' : entry[0][2],
                                      'video' : entry[0][3]}))
    elif json_str['msg_search']:
        if _json_parse(json_str['msg_search']):
            msgs = msg_fetch(
                    json_str['msg_search']['sid'], 
                    json_str['msg_search']['rid']
                    )
            print(msgs)



@app.route('/login/')
def login():
    return render_template('login.html', name=None)

@app.route('/chat/')
def chat():
    return render_template('chat.html', name=None)



socketio.run(app, host=HOST, port=PORT, use_reloader=RELDR, debug=DEBUG, log_output=LOG)
