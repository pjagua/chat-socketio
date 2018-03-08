#!/usr/bin/env python
# Copyright (C) 2017-2018 Pedro J. Aguayo
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
import threading
import logging
import queue
import pymysql
from pymysql import err as pymErr
from pymysql.connections import Connection as pymConn


class Connection(pymConn):
    _pool = None
    _reusable_exception = (pymErr.ProgrammingError, pymErr.IntegrityError, pymErr.NotSupportedError)
    def __init__(self, host, user, password, database, port=None):
        self.__user = user
        self.__host = host
        self.__password = password
        self.__database = database
        self.__port = (port if not port else 3306)
        super(Connection, self).__init__(host=self.__host, user=self.__user,
                password=self.__password, database=self.__database, port=self.__port)

    def __exit__(self, exc, value, traceback):
        super(Connection, self).__exit__(exc, value, traceback)
        if not exc or exc in self._reusable_exception:
            self._pool.put_connection(self)
        else:
            self._pool.put_connection(self._recreate(self, host=self.__host, user=self.__user, 
                password=self.__password, database=self.__database, port=self.__port))
            self._pool = None
            try:
                self.close()
            except Exception:
                pass

    def _recreate(self, host, user, password, database, port):
        conn = Connection(host=self.__host, user=self.__user, password=self.__password, 
                database=self.__database, port=self.__port)
        return conn

    def close(self):
        if self._pool:
            self._pool.put_connection(self)
        else:
            self.cusrsor().close(self)

    def execute_query(self, query, args=()):
        cur = self.cursor()
        try:
            sys.stderr.write("QUERY: {0}".format(query))
            cur.execute(query)
        except Exception as e:
            raise Exception(e)
        else:
            try:
                result = cur.fetchall()
                #sys.stderr.write(str(result))
            except Exception as e:
                raise RuntimeError(e)
            else:
                return result


class ConnectionPool(object):
    MAX_CONN = 20
    THREAD_LOCAL = threading.local()
    THREAD_LOCAL.retry_counter = 0

    def __init__(self, host, user, password, database, port, minsize, name=None):
        self._pool = queue.Queue(self.MAX_CONN)
        self.name = (name if name else '-'.join([host, user, database]))
        print(host, user, password, database, port, minsize)
        for _ in range(minsize if minsize < self.MAX_CONN else self.MAX_CONN):
            conn = Connection(host, user, password, database, port)
            conn._pool = self
            self._pool.put(conn)

    def get_connection(self, timeout=1, retry_num=1):
        ''' 
        TODO: verify args
        '''
        try:
            conn = self._pool.get(timeout=timeout) if timeout > 0 else self._pool.get_nowait()
            return conn
        except queue.Empty:
            if retry_num > 0:
                self.THREAD_LOCAL.retry_counter += 1
                retry_num -= 1
                return get_connection(timeout, retry_num)
            else:
                total_retries = self.THREAD_LOCAL.retry_counter + 1
                self.THREAD_LOCAL.retry_counter = 0
                raise GetConnectionFromPoolError("can't get connection from pool({}) within {}*{} second(s)".format(
                                            self.name, timeout, total_times))

    def put_connection(self, conn):
        if not conn._pool:
            conn._pool = self
            conn.close()
        try:
            self._pool.put_nowait(conn)
        except queue.Full:
            '''
            log error
            '''
            pass

    def size(self):
        return self._pool.qsize()


class GetConnectionFromPoolError(object):
    '''
    Write exception object for processing connections errors
    '''
    pass

