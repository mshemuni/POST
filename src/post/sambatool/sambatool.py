from logging import Logger
from typing import Optional

from typing_extensions import Self

from .gpo import GPO
from .user import User
from post.connection.model_connector import ModelConnector
from post.utils.common import GLOBAL_LOGGER
from .. import SSHConnector


class SambaTool:
    def __init__(self, connector: ModelConnector, ad_passwd: Optional[str] = None, sudo_passwd: Optional[str] = None,
                 logger: Optional[Logger] = None):
        if logger is None:
            self.logger = GLOBAL_LOGGER
        else:
            self.logger = logger

        self.ad_passwd = ad_passwd
        self.sudo_passwd = sudo_passwd
        self.connector = connector

        self.gpo = GPO(self.connector, ad_passwd=self.ad_passwd, sudo_passwd=self.sudo_passwd, logger=self.logger)
        self.user = User(self.connector, ad_passwd=self.ad_passwd, sudo_passwd=self.sudo_passwd, logger=self.logger)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(connector: {self.connector})"

    def __repr__(self) -> str:
        return self.__str__()

    @classmethod
    def from_ssh_connector(cls, address: str, port: int, user: str, passwd: str,
                           ad_passwd: Optional[str] = None, sudo_passwd: Optional[str] = None,
                           logger: Optional[Logger] = None) -> Self:
        """
        Constructs a GPO object using an ssh connection information.

        Args:
            address (str): An IP address or hostname.
            port (int): The ssh port. Most probably is 22.
            user (str): The ssh username.
            passwd (str): The ssh user's password.
            ad_passwd (str): password of the administrator of AD
            sudo_passwd (str): sudo password
            logger (Logger, optional): A logger to log. Defaults to None.

        Returns:
            Self: A GPO object.

        Raises:
            ValueError: If a connection cannot be established
        """
        ssh_connector = SSHConnector(address, port, user, passwd, logger=logger)
        return cls(ssh_connector, ad_passwd=ad_passwd, sudo_passwd=sudo_passwd, logger=logger)