# chat-socketio
A simple Flask_Socketio app with a MySQL database as the backend, used to store credentials and messages
    
Installation
============

Using docker-compose run:
    docker-compose up chatapp
This will download the required docker images creating the docker containers required to run the app.
On statrup, the app creates the schema and runs the application in the foreground.
To stop the application, from another terminal, or by sending the foreground process to the background (Ctrl+Z in Unix),  run:
    docker-compose down


### API Documentation

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
