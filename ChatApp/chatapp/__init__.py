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
from binascii import a2b_base64
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
    password='testpass',
    host='db',
    database='chatapp',
)

# Initiallize Data Model if not already initialized
db.cursor().execute('''CREATE TABLE IF NOT EXISTS accounts (
        id INT UNSIGNED UNSIGNED NOT NULL AUTO_INCREMENT,
        PRIMARY KEY(id),
        username varchar(16),
        password varchar(96),
        salt varchar(16)
        )ENGINE=InnoDB''')

db.cursor().execute('''CREATE TABLE IF NOT EXISTS messages (
        id INT UNSIGNED UNSIGNED NOT NULL AUTO_INCREMENT,
        PRIMARY KEY(id),
        sid INT,
        rid INT,
        message varchar(512),
        attributes JSON NOT NULL,
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
socketio = SocketIO(app, sync_mode=ASYNC_MODE, engineio_logger=LOG)

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
        else:
            return hexlify(hashlib.pbkdf2_hmac("sha256", hexlify(passwd.encode("utf8")), salt, 100000)), salt
    raise Exception("Password is empty, failed to salt password: {0}".formtat(salt))


def user_auth(uid, passwd):

    if not passwd:
        raise Exception("Password is empty")

    with db.cursor() as cursor:
        sql = "SELECT `salt`, `password` FROM `accounts` WHERE `id`=%s"
        cursor.execute(sql, (uid))
        result = cursor.fetchone()

    try:
        prov_pass = salt_pass(passwd, result[0].encode("utf8"))
    except Exception as e:
        raise Exception("Failed to calculate password for authentication: {0}".format(e))
    else:
        if prov_pass[0]  == result[1].encode("utf8"):
            return True
        raise Exception("Failed to Authenticate: hashes do not match {0} - {1}".format(prov_pass[0], result[1]))
 

def store_msg(msg, s_user, r_user, attrib=None):
    if not msg and not s_user and not r_user:
        raise Exception("message arguments are not complete")

    try:
        sid = chk_user(s_user)
        rid = chk_user(r_user)
    except Exception as e:
        raise Exception("Failed to find user in Database: {0}".format(e))
    else:
        if not attrib:
            attrib = '''{ "attributes" : { 
                                         "image" : "null",
                                         "video" : "null"
                                       }
                      }'''

        with db.cursor() as cursor:
            sql = """INSERT INTO `messages` (`sid`,
                                           `rid`,
                                           `message`,
                                           `attributes`)
                                           VALUES (%s, %s, %s, JSON_MERGE(%s))"""
            cursor.execute(sql, (sid, rid, msg, attrib))
            db.commit()
            cursor.close()
        return msg_fetch(sid, rid)

def _json_parse(_json):
    if not _json:
        return None

    for k,v in _json.iteritems():
        if not v:
            return None
    return True

def msg_fetch(sid, rid, page=None, limit=None):
    if not limit:
        limit = 10**24
    if not page:
        page = 0

        
        with db.cursor() as cursor:
            sql = '''SELECT `date`, `message`, attributes` 
                     FROM `messages` 
                     WHERE `sid` AND `rid` IN (%s, %s)
                     LIMIT %s %s 
                     ORDER BY UNIX_TIMESTAMP(date) DESC'''
            cursor.execute(sql, (sid, rid, page, limit))
            result = cursor.fetchall()

            cursor.close()

        return result

@socketio.on('login')
def handle_logins(data):
    uid = None
    
    try:
        username = json.loads(json.dumps(data))['data']["user_auth"]['username']
        password = json.loads(json.dumps(data))['data']["user_auth"]["password"]
    except Exception as e:
        sys.stderr.write("Empty fields in JSON string: {0}".format(e))
        emit('login', str({ 'errors' : {
                                    'code' : '400',
                                    'detail': 'Bad Request, username or password cannot be empty'
                                   }})
            )
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
            emit('login', str({'errors' : {
                                        'code' : '401',
                                        'detail': 'User Authentication failed'
                                       }})
                )
        else:
            print("User: {0} logged in successfully".format(username))
            emit('login', str({ 'data' : {
                                            'type' : 'login',
                                            'user_auth' : {
                                                            'username' : username
                                                          }
                                         }
                              })
                )
    else:
        try:
            password, salt = salt_pass(password)
        except Exception as e:
            sys.stderr.write("Failed to salt password: {0}".format(e))
            emit('login', str({ 'errors' : {
                                        'code' : '500',
                                        'detail': 'Internal Server error'
                                       }})
                )
        else:
            try:
                useradd(username, password, salt) 
            except Exception as e:
                sys.stderr.write("Failed to create new user: {0}".format(e))
                emit('login', str({ 'errors' : {
                                            'code' : '500',
                                            'detail': 'Internal Server error occurred while trying to add user to the database'
                                           }})
                    )
            else:
                emit('login', str({ 'data' : {
                                                'type' : 'login',
                                                'user_auth' : {
                                                                'username' : username
                                                              }
                                             }
                                  })
                    )


@socketio.on('msg')
def handle_txt_msg_event(json_str):
    date_format = '%Y-%m-%d %H:%M:%S'

    if json_str['data']['type'] == 'msg':

        try:
            entry = store_msg(
                              json_str['data']['message']['sid'], 
                              json_str['data']['message']['rid'],
                              json_str['data']['message']['message_data'],
                                      ['attributes']['image'],
                                      ['attributes']['video']
                             )
        except Exception as e:
            sys.stderr.write("Failed to save message: {0}".format(e))
        else:
            print(entry[0][0].strftime(date_format), entry[0][1])
            emit('client event', str({ 'data' : {
                                           'type' : 'msgs',
                                           'id' : entry[0][4],
                                           'attributes' : {
                                                            'date' : entry[0][0].strftime(date_format),
                                                            'message': entry[0][1],
                                                            'image' : entry[0][2],
                                                            'video' : entry[0][3]
                                                          }
                                           }
                                      }))
#@socketio.on('/msgsearch')
#def handle_search_event():
#    if json_str['data']['type'] = 'search':
#        if json_str['data']['attributes']['num_row'] and json_str['data']['attributes']['page']:
#            limit = json_str['data']['attributes']['num_row']
#            page = json_str['data']['attributes']['page']
#            sid = json_str['data']['attributes']['sid'] 
#            rid = json_str['data']['attributes']['rid']
#            msgs = msg_fetch(sid, rid, page, limit)
#            emit('search event', str({'data' : {
#                                                   'type' : 'search',
#                                                   'attributes' : {
#                                                       "message"
#                                                   
#                                    }))
#                                                  
           
            



@app.route('/login/')
def login():
    return render_template('login.html', name=None)

@app.route('/chat/')
def chat():
    return render_template('chat.html', name=None)



socketio.run(app, host=HOST, port=PORT, use_reloader=RELDR, debug=DEBUG, log_output=LOG)
