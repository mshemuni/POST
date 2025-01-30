from logging import Logger
from typing import Optional
from typing_extensions import Self

from post import SSHConnector
from post.connection.model_connector import ModelConnector
from post.utils.common import GLOBAL_LOGGER
from post.utils.error import NotFound


class User:
    def __init__(self, connector: ModelConnector, ad_passwd: Optional[str] = None, sudo_passwd: Optional[str] = None,
                 logger: Optional[Logger] = None) -> None:
        if logger is None:
            self.logger = GLOBAL_LOGGER
        else:
            self.logger = logger

        self.ad_passwd = ad_passwd
        self.sudo_passwd = sudo_passwd
        self.connector = connector

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(connector: {self.connector})"

    def __repr__(self) -> str:
        return self.__str__()

    def __password_check(self, ad_passwd: Optional[str] = None) -> str:
        """
        Raises an error if both of the password provided in object creation and given to here are None.
        Otherwise, returns the password

        Args:
            ad_passwd (str): a password

        Returns:
            str: the password

        """
        if ad_passwd is None:
            ad_passwd_to_use = self.ad_passwd
        else:
            ad_passwd_to_use = ad_passwd

        if ad_passwd_to_use is None:
            raise NotFound("I need AD's Administrator password")

        return ad_passwd_to_use

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

    def __list(self):
        stdout = self.connector.sudo_run("samba-tool user list", passwd=self.sudo_passwd)
        user_list_as_text = stdout.read().decode()
        return [each.strip() for each in user_list_as_text.split("\n") if each]

    def show(self, name: str):
        stdout = self.connector.sudo_run(f"samba-tool user show {name}", passwd=self.sudo_passwd)
        user_show_as_text = stdout.read().decode()
        user_info = {}
        for each in user_show_as_text.split("\n"):
            if each:
                key, value = each.split(":")
                user_info[key.strip()] = value.strip()

        return user_info

    def list(self):
        return {user: self.show(user) for user in self.__list()}

    def create(self, name: str, ad_passwd: Optional[str] = None):

        ad_passwd_to_use = self.__password_check(ad_passwd)

        stdout = self.connector.sudo_run(f"samba-tool create {name} -UAdministrator --password='{ad_passwd_to_use}'",
                                         passwd=self.sudo_passwd)
        _ = stdout.read().decode()

    def rm(self, name: str, ad_passwd: Optional[str] = None):

        ad_passwd_to_use = self.__password_check(ad_passwd)

        stdout = self.connector.sudo_run(f"samba-tool create {name} -UAdministrator --password='{ad_passwd_to_use}'",
                                         passwd=self.sudo_passwd)
        _ = stdout.read().decode()

    def set_password(self, name: str, new_password: str, ad_passwd: Optional[str] = None):

        ad_passwd_to_use = self.__password_check(ad_passwd)

        stdout = self.connector.sudo_run(
            f"samba-tool user setpassword {name} --newpassword='{new_password}' -UAdministrator --password='{ad_passwd_to_use}'",
            passwd=self.sudo_passwd
        )
        _ = stdout.read().decode()

    def enable(self, name: str, ad_passwd: Optional[str] = None):

        ad_passwd_to_use = self.__password_check(ad_passwd)

        stdout = self.connector.sudo_run(
            f"samba-tool user enable {name} -UAdministrator --password='{ad_passwd_to_use}'",
            passwd=self.sudo_passwd
        )
        _ = stdout.read().decode()

    def disable(self, name: str, ad_passwd: Optional[str] = None):

        ad_passwd_to_use = self.__password_check(ad_passwd)

        stdout = self.connector.sudo_run(
            f"samba-tool user disable {name} -UAdministrator --password='{ad_passwd_to_use}'",
            passwd=self.sudo_passwd
        )
        _ = stdout.read().decode()
