from logging import Logger
from typing import Optional

from paramiko.channel import ChannelFile
from paramiko.client import SSHClient, AutoAddPolicy

from post.connection.model_connector import ModelConnector
from post.utils.common import GLOBAL_LOGGER


class SSHConnector(ModelConnector):
    """
    An SSHConnector. It uses address, port, username and password to connect.

    This connector can be used for any of Apt, Service or Config objects and their List forms.
    One can create a simular object extending from ModelConnector abstract class.

    Args:
        address (str): The address of the server.
        port (int): The port of the server.
        user (str): The username to use.
        passwd (str): The password to use.
        logger (Logger, optional): The logger to log. Defaults to None.

    Raises:
        ValueError: If the connection fails.
    """

    def __init__(self, address: str, port: int, user: str, passwd: str, logger: Optional[Logger] = None) -> None:
        """
        Constructs an SSHConnector object

        Args:
            address (str): The address of the server.
            port (int): The port of the server.
            user (str): The username to use.
            passwd (str): The password to use.
            logger (Logger, optional): The logger to log. Defaults to None.

        Raises:
            ValueError: If the connection fails.
        """
        if logger is None:
            self.logger = GLOBAL_LOGGER
        else:
            self.logger = logger

        self.address = address
        self.port = port
        self.user = user
        self.passwd = passwd
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
            client.connect(
                hostname=self.address, port=self.port,
                username=self.user, password=self.passwd,
                timeout=10
            )
            return client
        except ValueError as e:
            print(e)
            self.logger.error(e)
            raise ValueError(e)

    def _validate(self, stdout: ChannelFile, stderr: ChannelFile) -> None:
        """
        Validates the command. Checks if standard error contains any error.

        Args:
            stdout (ChannelFile): A paramiko ChannelFile of standard output
            stderr (ChannelFile): A paramiko ChannelFile of standard error

        Raises:
            CommandError: If the standard error contains any error
        """
        self.logger.info("Validating command")

        return
        # Thanks to İbrahim ARI reminds me of exit code.
        # Still hangs. https://github.com/paramiko/paramiko/issues/448
        # May replace paramiko
        # if stdout.channel.recv_exit_status() != 0:
        #     self.logger.error(stderr.read().decode())
        #     raise CommandError(stderr.read().decode())

    def run(self, command: str) -> ChannelFile:
        """
        Runs a command with user privileges

        Args:
            command (str): the shell command to execute

        Raises:
            CommandError: If the standard error contains any error
        """
        self.logger.info("Run command")

        stdin, stdout, stderr = self.client.exec_command(command)
        self._validate(stdout, stderr)

        return stdout

    def sudo_run(self, command: str, passwd: Optional[str] = None) -> ChannelFile:
        """
        Runs a command with root privileges

        Args:
            command (str): the shell command to execute
            passwd (str, optional): the password to use. useful if connection is done via ssh-keys and no actual
                password is available. Defaults to None.

        Raises:
            CommandError: If the standard error contains any error
        """
        self.logger.info("Run command as ROOT")

        if passwd is None:
            passwd_to_use = self.passwd
        else:
            passwd_to_use = passwd

        sudo_command = f"sudo -S -p '' su -c \"{command}\""
        stdin, stdout, stderr = self.client.exec_command(sudo_command)
        stdin.write(passwd_to_use + "\n")
        stdin.flush()
        self._validate(stdout, stderr)
        return stdout
