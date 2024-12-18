from abc import ABC, abstractmethod
from logging import Logger
from typing import Iterator, Union, List, Optional, Dict, Any

from typing_extensions import Self

from post import Apt
from post.connection.model_connector import ModelConnector


class ModelAptList(ABC):
    @abstractmethod
    def __iter__(self) -> Iterator[Apt]:
        """Makes sure one can iterate through AptList"""

    @abstractmethod
    def __getitem__(self, key: Union[int, slice]) -> Union[Apt, Self]:
        """Returns the given slice of the AptList"""

    @abstractmethod
    def __delitem__(self, key) -> None:
        """Removes the given Apt from the AptList"""

    @abstractmethod
    def __len__(self) -> int:
        """Returns the length of the AptList"""

    @classmethod
    @abstractmethod
    def from_connections(cls, connections: List[ModelConnector], sudo_passwds: Optional[Union[str, List[str]]],
                         logger: Optional[Logger] = None) -> Self:
        """Returns a AptList from a given connection list"""

    @abstractmethod
    def repositories(self) -> Dict[Apt, List[Dict[str, str]]]:
        """Returns a dict of list of available apt repositories"""

    @abstractmethod
    def add_repository(self, repository: str) -> None:
        """Adds a new apt repository to all AptList"""

    @abstractmethod
    def update(self) -> None:
        """Updates repository of all AptList"""

    @abstractmethod
    def upgrade(self, package_name: Optional[str] = None) -> None:
        """Upgrades either the whole system of a specified package of all AptList"""

    @abstractmethod
    def list(self, installed: bool = False, upgradeable: bool = False) -> Dict[Apt, List[Dict[str, str]]]:
        """Lists either all, installed, or upgradable (Or combination) packages of all AptList"""

    @abstractmethod
    def install(self, package_name: Union[str, List[str]]) -> None:
        """Installs a specified package(s) (`apt install package_name`) on all AptList"""

    @abstractmethod
    def reinstall(self, package_name: Union[str, List[str]]) -> None:
        """Reinstalls a specified package(s) (`apt install package_name`) on all AptList"""

    @abstractmethod
    def remove(self, package_name: Union[str, List[str]]) -> None:
        """Removes a specified package(s) (`apt install package_name`) from all AptList"""

    @abstractmethod
    def purge(self, package_name: Union[str, List[str]]) -> None:
        """Purges a given page"""

    @abstractmethod
    def search(self, package_name: str) -> Dict[Apt, List[Dict[str, str]]]:
        """Search a specified package (`apt install package_name`) on all AptList"""

    @abstractmethod
    def show(self, package_name: str) -> Dict[Apt, Dict[Union[str, None], Any]]:
        """Shows information about the given package(s) (`apt show package_name`) on all AptList"""
