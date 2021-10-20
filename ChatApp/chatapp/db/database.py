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

import sys
from .connpool import ConnectionPool

class DB(object):
    def  __init__(self, host, user, password, _database, minpool=5, port=None):
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
       self.__database = _database
       self.__minpool = minpool
       self.__port = (port if port else 3306)
       self.__conn = None
       self.__db = None
       self.initialize()

    def initialize(self):
        # Initiallize Data Model if not already initialized
        if self.__conn:
            self.__db = self.__conn.get_connection()
        else:
            self.__conn = ConnectionPool(
                    self.__host,
                    self.__user, 
                    self.__password,
                    self.__database, 
                    self.__port,
                    self.__minpool
                    )
            try:
                self.__db = self.__conn.get_connection()
            except Exception as e:
                raise RuntimeError(e)
            else:
                self.__db.execute_query('''CREATE TABLE IF NOT EXISTS accounts (
                    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
                    PRIMARY KEY(id),
                    username varchar(16),
                    password varchar(96),
                    salt varchar(16)
                    )ENGINE=InnoDB''')

                self.__db.execute_query('''CREATE TABLE IF NOT EXISTS messages (
                    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
                    PRIMARY KEY(id),
                    sid INT UNSIGNED,
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
            finally:
                self.__conn.put_connection(self.__db)



    def select_query(self, *columns, **kwargs):
        ''' SELECT QUERY for cursor
        param *columns list: List of columns in the 
        param **kwargs dict: Dictionary of SELECT conditionals as keyword/value pairs
        '''

        SELECT = []
        if columns:
            columns = ", ".join(columns)
        else:
            columns = '*'

        SELECT.append(columns)

        for key, value in kwargs.items():
            if key == "FROM":
                SELECT.append("{0} {1} ".format(key, value))
            elif key == "WHERE":
                SELECT.append("{0} {1} ".format(key, value))
            elif key == "ORDER BY":
                SELECT.append("{0} {1} ".format(key, value))
            elif key == "LIMIT":
                SELECT.append("{0} {1} ".format(key, value))

        stmt = " ".join(SELECT)

        if self.__conn:
            try:
                self.__db = self.__conn.get_connection()
            except Exception as e:
                raise RuntimeError(e)
            else:
                select_stmt = "SELECT {0}".format(stmt)
                try:
                    return self.__db.execute_query(select_stmt)
                except Exception as e:
                    raise RuntimeError("ERROR: {0} - {1}".format(select_stmt, e))
            finally:
                try:
                    self.__conn.put_connection(self.__db)
                except Exception as e:
                    raise RuntimeError(e)

    def insert(self, **kwargs):
        '''
        param **kwargs dict: Should contain at least two keys INSERT INTO and VALUES
        '''

        INSERT = []
        if not kwargs:
            raise RuntimeError("INSERT values missing from mysql transaction")

        for key, value in kwargs.items():
            if key == "INTO":
                INSERT.append("{0} {1} ".format(key, value))
            elif key == "VALUES":
                INSERT.append("{0} {1} ".format(key, value))

        insrt = " ".join(INSERT)

        if self.__conn:
            try:
                self.__db = self.__conn.get_connection()
            except Exception as e:
                raise RuntimeError(e)
            else:
                insrt_stmt = "INSERT {0}".format(insrt)
                try:
                   rc = self.__db.execute_query(insrt_stmt)
                except Exception as e:
                    raise RuntimeError("ERROR: {0} - {1}".format(insrt_stmt, e))
            finally:
                try:
                    self.__conn.put_connection(self.__db)
                except Exception as e:
                    raise RuntimeError(e)
