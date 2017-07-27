import sys
import json
from flask_socketio import SocketIO
from flask_socketio import emit
from .functions import * 
from . import app

ASYNC_MODE = 'eventlet'
LOG = True
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
socketio = SocketIO(app, sync_mode=ASYNC_MODE, engineio_logger=LOG)



#SocketIO event handlers
@socketio.on('login', namespace='/chat')
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


@socketio.on('msg', namespace = "/chat")
def handle_txt_msg_event(json_str):
    json_str = json.loads(json.dumps(json_str))

    if json.loads(json.dumps(json_str))['data']['type'] == 'msg':

        try:
            entry = store_msg(
                              json_str['data']['message']['message_data'],
                              json_str['data']['message']['sid'], 
                              json_str['data']['message']['rid'],
                              json_str['data']['message']['attributes']
                             )
        except Exception as e:
            sys.stderr.write("Failed to save message: {0}\n".format(e))
            emit('msgsearch', str({ 'errors' : {
                                                'code' : '400',
                                                'detail': 'Message object cannot be empty'
                                               }})
                )
        else:
            emit('msg', str({ 'data' : {
                                           'type' : 'msg',
                                           'id' : entry[0][3],
                                           'message' : {
                                                         'date' : entry[0][0].strftime(DATE_FORMAT),
                                                         'message_data' : entry[0][1],
                                                         'attributes' : entry[0][2] 
                                                       }
                                      }
                            }))
@socketio.on('msgsearch', namespace = "/chat")
def handle_search_event(json_str):

    json_str = json.loads(json.dumps(json_str))

    if json_str['meta']['rows'] and json_str['meta']['page']:
        rows = json_str['meta']['rows']
        page = json_str['meta']['page']

    try:
        msgs = msg_fetch(
                            json_str['data']['message']['sid'], 
                            json_str['data']['message']['rid'],
                            page,
                            rows
                        )
    except Exception as e:
        sys.stderr.write("Failed to retrieve messages: {0}".format(e))
        emit('msgsearch', str({ 'errors' : {
                                            'code' : '500',
                                            'detail': 'Internal Error while fetching messages'
                                           }
                              }
                             )
            )


    else:
        for i in range(len(msgs)):
            emit('msgsearch', str({ 'data' : {
                                           'type' : 'msg',
                                           'id' : msgs[i][3],
                                           'message' : {
                                                         'date' : msgs[i][0].strftime(DATE_FORMAT),
                                                         'message_data' : msgs[i][1],
                                                         'attributes' : msgs[i][2] 
                                                       }
                                      }
                            }
                           )
                )
