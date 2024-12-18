from abc import ABC, abstractmethod
from logging import Logger
from typing import List, Dict, Optional, Union, Any

from typing_extensions import Self


class ModelApt(ABC):

    @classmethod
    @abstractmethod
    def from_ssh_connector(cls, address: str, port: int, user: str, passwd: str,
                           logger: Optional[Logger] = None) -> Self:
        """Creates a Self"""

    @abstractmethod
    def repositories(self) -> List[Dict[str, Any]]:
        """Returns available repositories"""

    @abstractmethod
    def add_repository(self, repository: str) -> None:
        """Adds a single apt repository"""

    @abstractmethod
    def update(self) -> None:
        """Updates repositories (`apt update`)"""

    @abstractmethod
    def upgrade(self, package_name: Optional[str] = None) -> None:
        """Upgrades either the whole system of a specified package"""

    @abstractmethod
    def list(self, installed: bool = False, upgradeable: bool = False) -> List[Dict[str, str]]:
        """Lists either all, installed, or upgradable (Or combination) packages"""

    @abstractmethod
    def install(self, package_name: Union[str, List[str]]) -> None:
        """Installs a specified package(s) (`apt install package_name`)"""

    @abstractmethod
    def reinstall(self, package_name: Union[str, List[str]]) -> None:
        """Reinstalls a specified package(s) (`apt reinstall package_name`)"""

    @abstractmethod
    def remove(self, package_name: Union[str, List[str]]) -> None:
        """Removes a specified package(s) (`apt remove package_name`)"""

    @abstractmethod
    def purge(self, package_name: Union[str, List[str]]) -> None:
        """Purges a specified package(s) (`apt purge package_name`)"""

    @abstractmethod
    def search(self, package_name: str) -> List[Dict[str, str]]:
        """Searches the given package (`apt search package_name`)"""

    @abstractmethod
    def show(self, package_name: str) -> Dict[Union[str, None], Any]:
        """Shows information about the given package(s) (`apt show package_name`)"""

    @abstractmethod
    def auto_remove(self):
        """runs `apt autoremove` on the machine"""
