from logging import Logger
from typing import Iterator, Union, Optional, List

from typing_extensions import Self

from post.connection.model_connector import ModelConnector
from post.user.model_user_list import ModelUserList
from post.user.user import User
from post.utils.common import GLOBAL_LOGGER


class UserList(ModelUserList):
    """
    UserList package manager.

    Args:
        users (List[ModelUSer]): A list of users
        logger (Logger, optional): A logger to log. Defaults to None.
    """
    def __init__(self, users: List[User], logger: Optional[Logger] = None):
        """
        UserList package manager.

        Args:
            users (List[ModelUSer]): A list of users
            logger (Logger, optional): A logger to log. Defaults to None.

        Returns:
            Self: an instance of self
        """
        if logger is None:
            self.logger = GLOBAL_LOGGER
        else:
            self.logger = logger

        self.users = users

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(noc: {len(self)})"

    def __iter__(self) -> Iterator[User]:
        for x in self.users:
            yield x

    def __getitem__(self, key: Union[int, slice]) -> Union[User, Self]:

        if isinstance(key, int):
            return self.users[key]
        elif isinstance(key, slice):
            return self.__class__(self.users[key])

        self.logger.error("Wrong slice")
        raise ValueError("Wrong slice")

    def __delitem__(self, key) -> None:
        del self.users[key]

    def __len__(self) -> int:
        return len(self.users)

    @classmethod
    def from_connections(cls, connections: List[ModelConnector], sudo_passwds: Optional[Union[str, List[str]]],
                         logger: Optional[Logger] = None) -> Self:
        """
        Creates a Self from a given SSH information.

        Args:
            connections (List[ModelConnector]): A list of connections
            sudo_passwds: (Optional[Union[str, List[str]]]): A list of sudo passwords, useful if connection is done
                via ssh-keys and no actual password is available. Defaults to None.
            logger (Logger, optional): A logger to log. Defaults to None.

        Returns:
            Self: an instance of the self.
        """
        if isinstance(sudo_passwds, list):
            sudo_passwds_to_use = sudo_passwds
        else:
            sudo_passwds_to_use = [sudo_passwds] * len(connections)

        return cls(
            [
                User(connection, sudo_passwd=sudo_passwd, logger=logger)
                for connection, sudo_passwd in zip(connections, sudo_passwds_to_use)
            ]
        )

    def list(self) -> List[List[User]]:
        """
        See User.list
        """
        users = []
        for user in self.users:
            try:
                users.append(user.list())
            except Exception as e:
                self.logger.warning(e)

        return users


    def list_groups(self) -> List[List[str]]:
        """
        See User.list_groups
        """
        groups = []
        for user in self.users:
            try:
                groups.append(user.groups())
            except Exception as e:
                self.logger.warning(e)

        return groups

    def exist(self, username: str) -> List[bool]:
        """
        See User.exist
        """
        user_existence = []
        for user in self.users:
            try:
                user_existence.append(user.exist(username))
            except Exception as e:
                self.logger.warning(e)

        return user_existence

    def add(self, username: str, home_dir: Optional[str] = None, shell: Optional[str] = None,
            full_name: Optional[str] = None) -> None:
        """
        See User.add
        """
        for user in self.users:
            try:
                user.add(username, home_dir=home_dir, shell=shell, full_name=full_name)
            except Exception as e:
                self.logger.warning(e)

    def rm(self, username: str, remove_all_files: bool = False, remove_home_dir: bool = False) -> None:
        """
        See User.rm
        """
        for user in self.users:
            try:
                user.rm(
                    username,
                    remove_all_files=remove_all_files,
                    remove_home_dir=remove_home_dir,
                )
            except Exception as e:
                self.logger.warning(e)

    def groups(self, username: str) -> List[List[str]]:
        """
        See User.groups
        """
        groups = []
        for user in self.users:
            try:
                groups.append(user.groups(username))
            except Exception as e:
                self.logger.warning(e)

        return groups

    def group_set(self, username: str, group_names: List[str]) -> None:
        """
        See User.group_set
        """
        for user in self.users:
            try:
                user.group_set(username, group_names)
            except Exception as e:
                self.logger.warning(e)


    def group_add(self, username: str, group_name: str):
        """
        See User.group_add
        """
        for user in self.users:
            try:
                user.group_add(username, group_name)
            except Exception as e:
                self.logger.warning(e)

    def group_rm(self, username: str, group_name: str) -> None:
        """
        See User.group_rm
        """
        for user in self.users:
            try:
                user.group_rm(username, group_name)
            except Exception as e:
                self.logger.warning(e)

    def enable(self, username:str) -> None:
        """
        See User.enable
        """
        for user in self.users:
            try:
                user.enable(username)
            except Exception as e:
                self.logger.warning(e)

    def disable(self, username:str) -> None:
        """
        See User.disable
        """
        for user in self.users:
            try:
                user.disable(username)
            except Exception as e:
                self.logger.warning(e)

    def is_enabled(self, username: str) -> List[bool]:
        """
        See User.is_enabled
        """
        is_enableds = []
        for user in self.users:
            try:
                is_enableds.append(user.is_enabled(username))
            except Exception as e:
                self.logger.warning(e)

        return is_enableds

    def set_password(self, username: str, password: str) -> None:
        """
        See User.set_password
        """
        for user in self.users:
            try:
                user.set_password(username, password)
            except Exception as e:
                self.logger.warning(e)

    def info(self, username: str) -> List[str]:
        """
        See User.info
        """
        informations = []
        for user in self.users:
            try:
                informations.append(user.info(username))
            except Exception as e:
                self.logger.warning(e)

        return informations
