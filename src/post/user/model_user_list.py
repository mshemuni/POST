from abc import ABC, abstractmethod
from logging import Logger
from typing import Iterator, Union, List, Optional

from typing_extensions import Self

from post.connection.model_connector import ModelConnector
from post.user.model_user import ModelUser


class ModelUserList(ABC):

    @abstractmethod
    def __iter__(self) -> Iterator[ModelUser]:
        """Returns an iterator of users"""

    @abstractmethod
    def __getitem__(self, key: Union[int, slice]) -> Union[ModelUser, Self]:
        """Returns a user by index or slice"""

    @abstractmethod
    def __delitem__(self, key) -> None:
        """Removes a user by index or slice from the list"""

    @abstractmethod
    def __len__(self) -> int:
        """Returns the length of the list"""

    @classmethod
    @abstractmethod
    def from_connections(cls, connections: List[ModelConnector], sudo_passwds: Optional[Union[str, List[str]]],
                         logger: Optional[Logger] = None) -> Self:
        """Creates a Self of users from a list of connections and usernames"""

    @abstractmethod
    def list(self) -> List[List[ModelUser]]:
        """Returns a list of users"""

    @abstractmethod
    def list_groups(self) -> List[List[str]]:
        """Returns a list of groups"""

    @abstractmethod
    def exist(self, username:str) -> List[bool]:
        """Checks if users exist"""

    @abstractmethod
    def add(self, username: str, home_dir: Optional[str] = None, shell: Optional[str] = None,
            full_name: Optional[str] = None) -> None:
        """Adds users"""

    @abstractmethod
    def rm(self, username: str, remove_all_files: bool = False, remove_home_dir: bool = False) -> None:
        """Removes users"""

    @abstractmethod
    def groups(self, username:str) -> List[List[str]]:
        """Returns a list of groups that users are a part of"""

    @abstractmethod
    def group_set(self, username: str, group_names: List[str]) -> None:
        """Sets groups to a user"""

    @abstractmethod
    def group_add(self, username:str, group_name: str):
        """Adds all users to a group"""

    @abstractmethod
    def group_rm(self, username:str, group_name: str) -> None:
        """Removes all users from a group"""

    @abstractmethod
    def enable(self, username: str) -> None:
        """Enables all users"""

    @abstractmethod
    def disable(self, username: str) -> None:
        """Disables all users"""

    @abstractmethod
    def is_enabled(self, username: str) -> List[bool]:
        """Checks if a user is enabled"""

    @abstractmethod
    def set_password(self, username: str, password: str) -> None:
        """Sets a user's password'"""

    @abstractmethod
    def info(self, username: str) -> List[str]:
        """Returns info about a user"""
