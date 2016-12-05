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

import os
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
            self._logger.info("Received data: {0}".format(data))
            if data == self._DPAE_DONE:
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

    # Other constants
    _ANS_PLYBK = "ansible-playbook ~/AutomatedTests/playbooks/"

    def __init__(self, log_file):
        """Initialise.

        :param log_file: Name of the file to write logging info to.
        """
        # Set up logging interface
        self._log_file = log_file
        self._logger = TestLogger("TestServer", self._log_file)

    def start_experiments(self, exp_data):
        """Start a set of experiments.

        :param exp_data: Dict containing parameters for the experiments.
        """
        self._logger.info("Starting experiment.")

        self._logger.info("Killing any existing evaluation processes "
                          "on testbed hosts.")
        playbook_cmd = self._ANS_PLYBK + "kill_processes.yaml"
        os.system(playbook_cmd)

        self._logger.info("Copying files to the controller and DPAE.")
        playbook_cmd = (self._ANS_PLYBK + "copy_config_policy.yaml "
                                         "--extra-vars "
                                         "\"contr_config={0} "
                                         "contr_main_policy={1} "
                                         "dpae_dataset={2}\"".format(
            exp_data["contr_config"], exp_data["contr_main_policy"], 
            exp_data["dpae_dataset"]))
        os.system(playbook_cmd)

        self._logger.info("Starting controller application.")
        playbook_cmd = self._ANS_PLYBK + "start_controller.yaml"
        os.system(playbook_cmd)

        self._logger.info("Starting DPAE application.")
        playbook_cmd = (self._ANS_PLYBK + "start_dpae.yaml "
                       "--extra-vars \"mosp_outfile={0}\"".format(
                           exp_data["mosp_outfile"]))
        os.system(playbook_cmd)

        self._logger.info("Waiting for DPAE notification...")
        server = DPAEHandler(self._log_file)
        result = server.handle(self._HOST, self._PORT)
        if not result:
            self._logger.critical("DPAE classifier training completion "
                                  "notification failed. Exiting...")
            sys.exit(1)

        self._logger.info("Starting traffic replay.")
        playbook_cmd = self._ANS_PLYBK + "start_replay.yaml"
        os.system(playbook_cmd)

        self._logger.info("Killing all running evaluation processes "
                          "on testbed hosts.")
        playbook_cmd = self._ANS_PLYBK + "kill_processes.yaml"
        os.system(playbook_cmd)

        self._logger.info("Test server shutting down...")


if __name__ == "__main__":
    log_file = "test_server.log"
    ts = TestServer(log_file)
    exp_data = {"contr_config": "config_active.yaml",
                "contr_main_policy": "main_policy_nothing_active.yaml",
                "dpae_dataset": "iscx_2012_ddos_fold_1.py",
                "mosp_outfile": "active_nothing_fold_1"}
    ts.start_experiments(exp_data)
