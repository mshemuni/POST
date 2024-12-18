from abc import ABC, abstractmethod
from logging import Logger
from typing import List, Dict, Optional, Union, Any

from typing_extensions import Self


class ModelUser(ABC):

    @classmethod
    @abstractmethod
    def from_ssh_connector(cls, address: str, port: int, user: str, passwd: str,
                           logger: Optional[Logger] = None) -> Self:
        """Creates a Self"""

    @abstractmethod
    def list(self) -> List[str]:
        """Lists all the users"""

    @abstractmethod
    def list_groups(self) -> List[str]:
        """Lists all the groups"""

    @abstractmethod
    def exist(self, username: str) -> bool:
        """Check if user exists"""

    @abstractmethod
    def add(self, username: str, home_dir: Optional[str] = None, shell: Optional[str] = None,
            full_name: Optional[str] = None):
        """Adds a user"""

    @abstractmethod
    def rm(self, username: str, remove_all_files: bool = False, remove_home_dir: bool = False) -> None:
        """Remove a user"""

    @abstractmethod
    def groups(self, username: str) -> List[str]:
        """Get list of groups that user is a part of"""

    @abstractmethod
    def group_add(self, username: str, group_name: str) -> None:
        """Add user to a group"""

    @abstractmethod
    def group_set(self, username: str, group_names: List[str]) -> None:
        """Set user to a group"""

    @abstractmethod
    def group_rm(self, username: str, group_name: str) -> None:
        """remove user from a group"""

    @abstractmethod
    def enable(self, username: str):
        """Enables a user"""

    @abstractmethod
    def disable(self, username: str):
        """Disables a user"""

    @abstractmethod
    def is_enabled(self, username: str):
        """Disables a user"""

    @abstractmethod
    def set_password(self, username: str, password: str):
        """Change password"""

    @abstractmethod
    def info(self, username: str) -> List[str]:
        """Get info about a user"""