import subprocess
from logging import Logger
from typing import Optional

from post.connection.model_connector import ModelConnector
from post.utils.common import GLOBAL_LOGGER
from post.utils.error import CommandError


class LocalChannelFile:
    def __init__(self, text):
        self.text = text

    def read(self):
        return self.text.encode('utf-8')


class LocalConnector(ModelConnector):
    """
    A LocalConnector.


    Args:
        passwd (str): The password to use.
        logger (Logger, optional): The logger to log. Defaults to None.
    """

    def __init__(self, passwd: str, logger: Optional[Logger] = None):
        """
        Constructs a LocalConnector object

        Args:
            passwd (str): The password to use.
            logger (Logger, optional): The logger to log. Defaults to None.
        """
        if logger is None:
            self.logger = GLOBAL_LOGGER
        else:
            self.logger = logger

        self.passwd = passwd

    def __str__(self):
        return f"{self.__class__.__name__}()"

    def run(self, command: str) -> LocalChannelFile:
        """
        Runs a command with user privileges

        Args:
            command (str): the shell command to execute

        Raises:
            CommandError: If the standard error contains any error
        """
        self.logger.info("Run command")
        try:
            result = subprocess.run(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            return LocalChannelFile(result.stdout.decode())
        except FileNotFoundError as _:
            raise CommandError("Command not found")
        except Exception as e:
            raise ValueError(f"An error occurred: {e}")

    def sudo_run(self, command: str, passwd: Optional[str] = None) -> LocalChannelFile:
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
        try:

            if passwd is None:
                passwd_to_use = self.passwd
            else:
                passwd_to_use = passwd

            sudo_command = f"echo {passwd_to_use} | sudo -S -p '' su -c  \"{command}\""
            result = subprocess.run(
                sudo_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            return LocalChannelFile(result.stdout.decode())
        except FileNotFoundError as _:
            raise CommandError("Command not found")
        except Exception as e:
            raise ValueError(f"An error occurred: {e}")
