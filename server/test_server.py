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

import socket
import sys
from test_logger import TestLogger

__author__ = "Jarrod N. Bakker"


class DPAEHandler:
    """TCP request handler for DPAE classifier training completion
    notification.
    """

    _DPAE_DONE = "Training complete."
    _RECV_BUF = 1024

    def __init__(self, log_file):
        """Initialise.

        :param log_file: Name of the file to write logging info to.
        """
        self._logger = TestLogger(__name__, log_file)

    def handle(self, host, port):
        """Handle completion notification requests on TCP port 8088.

        :return: True if the DPAE has complete training, False if an
        error occurred.
        """
        sckt = None
        try:
            sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sckt.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except socket.error as err:
            self._logger.error("Unable to create socket: "
                               "{0}".format(err))
            return False
        try:
            sckt.bind((host, port))
            sckt.listen(1)
        except socket.error as err:
            self._logger.error("Unable to bind socket: {0}".format(err))
            sckt.close()
            return False
        while True:
            data = None
            try:
                conn, addr = sckt.accept()
                self._logger.info("Client connected: {0}".format(addr))
                data = conn.recv(self._RECV_BUF).strip()
                sckt.close()
            except socket.error as err:
                self._logger.error("Unable to accept connections on "
                                   "socket: {0}".format(err))
                sckt.close()
                return False
            if data == self._DPAE_DONE:
                print(data)
                return True
        sckt.close()
        return False


class TestServer:
    """Responsible for starting experiments as well as listening out
    for feedback that may be necessary for moving forward through an
    experiment.
    """

    # Constants for TCP request handler
    _HOST = ""  # Symbolic for all available interfaces
    _PORT = 8088

    def __init__(self, log_file):
        """Initialise.

        :param log_file: Name of the file to write logging info to.
        """
        # Set up logging interface
        self._log_file = log_file
        self._logger = TestLogger("TestServer", self._log_file)

    def start_experiments(self):
        """Start a set of experiments.
        """
        self._logger.info("Waiting for DPAE notification...")
        server = DPAEHandler(self._log_file)
        result = server.handle(self._HOST, self._PORT)
        if not result:
            self._logger.critical("DPAE classifier training completion "
                                  "notification failed. Exiting...")
            sys.exit(1)
        print("It works!")


if __name__ == "__main__":
    log_file = "test_server.txt"
    ts = TestServer(log_file)
    ts.start_experiments()
