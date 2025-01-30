from logging import Logger
from typing import Optional

from .gpo import GPO
from .user import User
from post.connection.model_connector import ModelConnector
from post.utils.common import GLOBAL_LOGGER


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