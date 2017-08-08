import sys
import json
from flask_socketio import SocketIO
from flask_socketio import emit
from .functions import * 
from . import app



#Set socketio async mode explicitly, or NONE to let the application decide
ASYNC_MODE = 'eventlet'

LOG = True
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
socketio = SocketIO(app, sync_mode=ASYNC_MODE, engineio_logger=LOG)



#SocketIO event handlers
@socketio.on('login', namespace='/chat')
def handle_logins(data):
    """
    Login event handler expects a top-level object of type = data
    with a "user_auth" member populated with username and password sub-members.

    Returns a JSON top-level object of type = data 
    with a "user_auth" member populated with the authenticated username

    On error, a top-level Error object is returned with error code and details members
    """



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
        return 1
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
            return 2
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
            return 0
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
            return 1
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
                return 1
            else:
                emit('login', str({ 'data' : {
                                                'type' : 'login',
                                                'user_auth' : {
                                                                'username' : username
                                                              }
                                             }
                                  })
                    )
                return 0


@socketio.on('msg', namespace = "/chat")
def handle_txt_msg_event(json_str):
    """
    msg event handler expects a top-level object of type = data
    with a "message" member populated with "message_data", sid (Send userID), rid(Receiving userID) and attribute members..

    On error, a top-level Error object is returned with error code and details members
    """

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
            return 1
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
            return 0
@socketio.on('msgsearch', namespace = "/chat")
def handle_search_event(json_str):
    """
    msgsearch event handler expects a top-level object of type = data
    Optional top-level object of "meta-data" with  member "rows" as rows of messages per page, and members "page" as page # designating the page
    that should be displayed.

    On error, a top-level Error object is returned with error code and details members
    """

    json_str = json.loads(json.dumps(json_str))

    rows = (json_str['meta']['rows'] if json_str['meta']['rows'] else None)
    page = (json_str['meta']['page'] if json_str['meta']['page'] else None) 

    try:
        msgs = msg_fetch(
                            chk_user(json_str['data']['message']['sid']), 
                            chk_user(json_str['data']['message']['rid']),
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
        return 1


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
            return 0
