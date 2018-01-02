#!/usr/bin/env python
# Copyright (C) 2017-2018 Pedro J, Aguayo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from db.connpool import ConnectionPool

class DB(object):
   def  __init__(self, minpool=5, host, user, password, database, port=None):
       ''' Setup Database connection

       param minpool int: Minimum number startup for connection pool
       param host string: containing host settings for the connection
       param user string: mysql user
       param password string: mysql user password
       param database string: Name of the selected database
       param port int: mysql connection port

       '''

       self.__host = host
       self.__user = user
       self.__password = password
       self.__database = database
       self.__port = (port if not port else 3306)
       self.pool = ConnectionPool(self, self.__host, self.__user, self.__password, self.__database, self.__port)




#Initialize DB object
db = pymysql.connect(
    user='root',
    password='testpass',
    host='db',
    database='chatapp',
)

# Initiallize Data Model if not already initialized
db.cursor().execute('''CREATE TABLE IF NOT EXISTS accounts (
        id INT UNSIGNED NOT NULL AUTO_INCREMENT,
        PRIMARY KEY(id),
        username varchar(16),
        password varchar(96),
        salt varchar(16)
        )ENGINE=InnoDB''')

db.cursor().execute('''CREATE TABLE IF NOT EXISTS messages (
        id INT UNSIGNED NOT NULL AUTO_INCREMENT,
        PRIMARY KEY(id),
        sid INT UNSIGNED
        rid INT UNSIGNED,
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


###
# TODO: Move Database operations here
