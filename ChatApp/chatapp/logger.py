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

import os
import sys
import logging
import logging.handlers

logformat = '%(asctime)s - %(name)s - %(levelname)s: %(message)s'
dateformat = '%b %d %Y %I:%M:%S'

class Logger(object):
    def __init__(self, logfile, level, loggingfmt=logformat, datefmt=dateformat):
        ''' Setup Logging::

        param logfile string: absolute path of logfile location
        param level string: CRITICAL|ERROR|WARNING|INFO|DEBUG|NOTSET
        param loggingfmt string: <defaults logformat above> 
        param datefmt string: <Complies to ISO8601> 
        

        '''

        self.__loggingfmt = loggingfmt
        self.__datefmt = datefmt
        self.__logger = self.get_logger()
        self.__logfile = logfile
        self.__level = level.decode(level).upper()


    def write(self, buf):
        ''' Creates a write() for interfacing with open construct 

        param buf: buffer object
        
        '''

        for line in buf.rstrip().splitlines():
            self.log_handle().log(self.log_level(), linerstrip())

    def get_logger(self):
        ''' Return module name for logging origination '''

        return __name__.split(".")[0]

    def log_handle(self):
        ''' Set log handle 
        
        return: logger | raise Exception

        '''

        logger = logging.getLogger(self.__logger)
        f_handler = logging.handler.TimedRotatingFileHandler(self.__logfile, when='midnight', backupCount=5)
        c_handler = logging.StreamHandler()
        formatter = logging.Formatter(self.__loggingfmt, self.__datefmt)

        try:
            logger.setLevel(self.log_level())
            f_handler.setLEvel(self.log_level())
            logger.addHandler(self.console_handler(logger, formatter))
        except Exception as e:
            raise Exception("Failed to set logging handle: {0}".format(e))
        else:
            logger.addHandler(f_handler)
            return logger

    def log_level(self):
        ''' Returns logging levels
        
        return: logging.<LEVEL>
    
        '''

        if self.__level == "DEBUG":
            return logging.DEBUG
        elif self.__level == "CRITICAL":
            return logging.CRITICAL
        elif self.__level == "ERROR":
            return logging.ERROR
        elif self.__level == "WARNING":
            return logging.WARNING
        elif self.__level == "INFO":
            return logging.INFO
        else:
            return logging.NOTSET

    def console_hndler(self, logger, h_format):
        ''' Return the console handler

        param logger: logger object
        param h_format: Formatter object
        return ch: Console loghandler

        '''
        if self.__level == 'DEBUG':
            try:
                ch  = logging.StreamHandler()
                ch.setLevel(logging.DEBUG)
                ch.setFormatter(h_format)
            except Exception as e:
                raise Exception("Unable to set the Console logger handler")
            else:
                return ch
