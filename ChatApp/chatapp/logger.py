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

class Logger(objecct):
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
        for line in buf.rstrip().splitlines():
            self.log_handle().log(self.log_level(), linerstrip())

    def get_logger(self):
        return __name__.split(".")[0]

    def log_handle(self):
        logger = logging.getLogger(self.__logger)
        f_handler = logging.handler.TimedRotatingFileHandler(self.__logfile, when='midnight', backupCount=5)
        c_handler = logging.StreamHandler()
        formatter = logging.Formatter(self.__loggingfmt, self.__datefmt)

    def log_level(self):
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
        if self.__level == 'DEBUG':
            ch  = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(h_format)
            logger.addHandler(ch)
