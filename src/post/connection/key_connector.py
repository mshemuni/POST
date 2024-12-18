from logging import Logger
from pathlib import Path
from typing import Optional, Union

from paramiko import RSAKey, ChannelFile
from paramiko.client import SSHClient, AutoAddPolicy


from post.connection.model_connector import ModelConnector
from post.utils.common import GLOBAL_LOGGER


class KeyConnector(ModelConnector):
    def __init__(self, address: str, port: int, user: str, private_key: Union[Path, str], logger: Optional[Logger] = None) -> None:

        if logger is None:
            self.logger = GLOBAL_LOGGER
        else:
            self.logger = logger

        self.address = address
        self.port = port
        self.user = user
        self.private_key = private_key
        self.client = self.connect()

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(address: {self.address}:{self.port}, user: {self.user})"

    def __repr__(self) -> str:
        return self.__str__()

    def __del__(self):
        self.close()

    def close(self) -> None:
        """Closes the connection"""
        self.logger.info("Closing Connection")

        try:
            if self.client is not None:
                self.client.close()
                del self.client
        except Exception as e:
            self.logger.warning(e)

    def connect(self) -> SSHClient:
        """
        Connects to the server

        Raises:
            ValueError: If the connection fails.
        """
        self.logger.info("Connecting")

        client = SSHClient()
        client.set_missing_host_key_policy(AutoAddPolicy())
        try:
            private_key = RSAKey.from_private_key_file(self.private_key)
            client.connect(hostname=self.address, port=self.port, username=self.user, pkey=private_key)
            return client
        except ValueError as e:
            print(e)
            self.logger.error(e)
            raise ValueError(e)

    def _validate(self, stdout: ChannelFile, stderr: ChannelFile) -> None:
        self.logger.info("Validating command")

        return
        # Thanks to İbrahim ARI reminds me of exit code.
        # Still hangs. https://github.com/paramiko/paramiko/issues/448
        # May replace paramiko
        # if stdout.channel.recv_exit_status() != 0:
        #     self.logger.error(stderr.read().decode())
        #     raise CommandError(stderr.read().decode())

    def run(self, command: str) -> ChannelFile:
        self.logger.info("Run command")

        stdin, stdout, stderr = self.client.exec_command(command)
        self._validate(stdout, stderr)

        return stdout

    def sudo_run(self, command: str, passwd: str) -> ChannelFile:
        self.logger.info("Run command as ROOT")

        sudo_command = f"sudo -S -p '' su -c \"{command}\""
        stdin, stdout, stderr = self.client.exec_command(sudo_command)
        stdin.write(passwd + "\n")
        stdin.flush()
        self._validate(stdout, stderr)
        return stdout
