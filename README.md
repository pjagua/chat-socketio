# chat-socketio

Description
===========
A simple WebSocket chat app using flask_socketio (Flask SocketIO implementation), a MySQL database backend, storing the relevant data, such as credentials, messages and message attribures like image and video links.
    
Installation
============

+ Requirements:
    - docker-compose 
    - pip
+ Installing the app using docker-compose run:
    - docker-compose up chatapp
Running docker-compose will automatically download the required docker images and creates the docker containers required to run the app.
On statrup, the app creates the database schema and runs the application in the foreground of running terminal.
To stop the application, open another terminal, or by sending the process to the background (Ctrl+Z in Unix), and run:
    docker-compose down


### API Documentation
SocketIO event handlers are implemented in order to handle client/server events within the SocketIO implementation.
Using the jsonapi.org specification, JSON objects are used to emit request/response between client and server.
Error notification are sent using JSON error objects

#### Event Handlers
Each event handler return a JSON top-level object, and a return value designated for client callback functions
+ "login" 
    - Handles credential authentication events for users
    - Creates users and authenticates against the stored account records.
    - A JSON "errors" top-level object will be returned upon error with a corresponding error code and details object 

+ "messages"
    - Handles message events, storing the JSON data object in the MYSQL "chatapp" database.
	- This includes the message data, URLs to image and video including metadata

- "msgsearch"
    - Handles search events, where messages between 2 users with optional rows per page and page request are sent to the server by JSON object 

 

#### JSON SCHEMA
```json
{ meta : {
           rows : <rows per page>,
           page : <page #>
	 }
}, 
{ data : {
           type : [login | msg],
           id : [user id | msg_id],
           user_auth : {
		           username : <usernamme>,
		           password : <password>
		       } 
	   message : {
			 message_data : <data>,
			 date : <date>,
			 sid : <sender user>,
			 rid : <receiver user >,
			 attributes : { 
					image : {
				        	url : <http link>
				   		width : image width
				    		height : image height
				      		},
				        video : {
				    		url : <http link>
				    		source : <source name>
				    		length : video length 
				      		},
				        }
		        }
	   }
}	
{ errors : {
	    code : <error code>
	    detail : <Error Message>
	   }
}
```
