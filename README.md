# chat-socketio
A simple Flask_Socketio app with a MySQL database as the backend, used to store credentials and messages
    
Installation
============

Using docker-compose run:
    docker-compose up chatapp
This will download the required docker images, and creates the docker containers required to run the app.
On statrup, the app creates the schema and runs the application in the foreground.
To stop the application, either from another terminal, or send the foreground process to the background, and run:
    docker-compose down


### API Documentation

#### JSON SCHEMA
{ meta : {
           rows : <rows per page>,
           page : <page #>
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
