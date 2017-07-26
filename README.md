# chat-socketio

Description
===========
A simple WebSocket chat app using flask_socketio, a MySQL database backend, which stores credentials, and message image and video as attributes.
    
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
+ "login" -- event handler
    - Handles credential authentication events for users
    - Creates a user for every non existent user using the JSON "type : login" and "user_auth" objects
    - A JSON "errors" top-level object will be returned upon error with a corresponding error code and details object 

+ "messages" -- event handler
    - Handles message events, storing the JSON data object in the MYSQL "chatapp" database.
 
    - Member of the "/chat" namespace

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
