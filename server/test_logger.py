# Copyright 2016 Jarrod N. Bakker
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import os
import sys
import time

__author__ = "Jarrod N. Bakker"


class TestLogger:
    """A class for handling the specific logging requirements for the
    test server.
    """

    def __init__(self, class_name, log_file):
        """Initialise.

        :param class_name: Name of the registering class.
        :param log_file: Name of the file to write log info to.
        """
        self._name = class_name
        work_dir = os.path.dirname(__file__)
        self._logf = os.path.join(work_dir, log_file)
        # Initialise object for console logging
        min_lvl = logging.DEBUG
        console_handler = logging.StreamHandler()
        console_handler.setLevel(min_lvl)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s: "
                                      "%(name)s - %(message)s")
        console_handler.setFormatter(formatter)
        self._logging = logging.getLogger(self._name)
        self._logging.setLevel(min_lvl)
        #self._logging.propagate(False)
        self._logging.addHandler(console_handler)
        # Initialise file for writing logging to. This is NOT syslog.
        if not os.path.isfile(self._logf):
            self._logging.info("Creating logging file: %s", self._logf)
            try:
                open(self._logf, 'a').close()
            except IOError as err:
                self._logging.critical("Unable to create logging file: "
                                       "%s. Exception: "
                                       "%s.\nExiting...", self._logf,
                                       err)
                sys.exit(1)

    def critical(self, msg):
        """Log with critical level.

        :param msg: String of the message to log.
        """
        self._logging.critical(msg)
        file_log = None
        try:
            file_log = open(self._logf, 'a')
            cur_t = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            file_log.write("{0} - CRITICAL: {1} - {2}"
                           "\n".format(cur_t, self._name, msg))
        except IOError as err:
            self._logging.error("Unable to write logging message to "
                                "file: %s. Exception: %s", self._logf,
                                err)
        finally:
            if file_log is not None:
                file_log.close()

    def error(self, msg):
        """Log with error level.

        :param msg: String of the message to log.
        """
        self._logging.error(msg)
        file_log = None
        try:
            file_log = open(self._logf, 'a')
            cur_t = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            file_log.write("{0} - ERROR: {1} - {2}"
                           "\n".format(cur_t, self._name, msg))
        except IOError as err:
            self._logging.error("Unable to write logging message to "
                                "file: %s. Exception: %s", self._logf,
                                err)
        finally:
            if file_log is not None:
                file_log.close()

    def info(self, msg):
        """Log with info level.

        :param msg: String of the message to log.
        """
        self._logging.info(msg)
        file_log = None
        try:
            file_log = open(self._logf, 'a')
            cur_t = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            file_log.write("{0} - INFO: {1} - {2}"
                           "\n".format(cur_t, self._name, msg))
        except IOError as err:
            self._logging.error("Unable to write logging message to "
                                "file: %s. Exception: %s", self._logf,
                                err)
        finally:
            if file_log is not None:
                file_log.close()
