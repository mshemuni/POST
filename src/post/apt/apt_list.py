from logging import Logger

from typing import List, Dict, Optional, Union, Iterator, Any
from typing_extensions import Self

from post import Apt
from post.apt.model_apt_list import ModelAptList
from post.connection.model_connector import ModelConnector
from post.utils.common import GLOBAL_LOGGER
from post.utils.error import NumberOfElementsError


class AptList(ModelAptList):
    """
    Multiple APT package manager.

    This object does everything Apt does but on multiple of Apt objects.

    Args:
        apts (List[Apt]): A list of Apt objects
        logger (Logger, optional): A logger to log. Defaults to None.
    """

    def __init__(self, apts: List[Apt], logger: Optional[Logger] = None) -> None:
        """
        Constructs an AptList object

        Args:
            apts (List[Apt]): A list of Apt objects
            logger (Logger, optional): A logger to log. Defaults to None.

        Raises:
            NumberOfElementsError: If length of apts is 0
        """
        if logger is None:
            self.logger = GLOBAL_LOGGER
        else:
            self.logger = logger

        if len(apts) == 0:
            self.logger.error("apts can not be empty")
            raise NumberOfElementsError("apts can not be empty")

        self.apts = apts

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(noc: {len(self)})"

    def __iter__(self) -> Iterator[Apt]:
        for x in self.apts:
            yield x

    def __getitem__(self, key: Union[int, slice]) -> Union[Apt, Self]:

        if isinstance(key, int):
            return self.apts[key]
        elif isinstance(key, slice):
            return self.__class__(self.apts[key])

        self.logger.error("Wrong slice")
        raise ValueError("Wrong slice")

    def __delitem__(self, key) -> None:
        del self.apts[key]

    def __len__(self) -> int:
        return len(self.apts)

    @classmethod
    def from_connections(cls, connections: List[ModelConnector], sudo_passwds: Optional[Union[str, List[str]]],
                         logger: Optional[Logger] = None) -> Self:
        """
        Creates a Self using list of connections

        Args:
            connections (List[ModelConnector]): A list of connections
            sudo_passwds: (Optional[Union[str, List[str]]]): A list of sudo passwords, useful if connection is done
                via ssh-keys and no actual password is available. Defaults to None.
            logger (Logger, optional): A logger to log. Defaults to None.

        Returns:
            Self: AptList

        Raises:
            NumberOfElementsError: If length of connections is 0
        """

        if isinstance(sudo_passwds, list):
            sudo_passwds_to_use = sudo_passwds
        else:
            sudo_passwds_to_use = [sudo_passwds] * len(connections)

        return cls(
            [
                Apt(connection, sudo_passwd=sudo_passwds, logger=logger)
                for connection, sudo_password in zip(connections, sudo_passwds_to_use)
            ]
        )

    def repositories(self) -> Dict[Apt, List[Dict[str, str]]]:
        """See Apt.repositories"""
        repositories = {}
        for apt in self.apts:
            try:
                repositories[apt] = apt.repositories()
            except Exception as e:
                self.logger.warning(e)

        return repositories

    def add_repository(self, repository: str) -> None:
        """See Apt.add_repository"""
        for apt in self.apts:
            try:
                apt.add_repository(repository)
            except Exception as e:
                self.logger.warning(e)

    def update(self) -> None:
        """See Apt.update"""
        for apt in self.apts:
            try:
                apt.update()
            except Exception as e:
                self.logger.warning(e)

    def upgrade(self, package_name: Optional[str] = None) -> None:
        """See Apt.upgrade"""
        for apt in self.apts:
            try:
                apt.upgrade(package_name=package_name)
            except Exception as e:
                self.logger.warning(e)

    def list(self, installed: bool = False, upgradeable: bool = False) -> Dict[Apt, List[Dict[str, str]]]:
        """See Apt.list"""
        list_of_available = {}
        for apt in self.apts:
            try:
                list_of_available[apt] = apt.list(installed=installed, upgradeable=upgradeable)
            except Exception as e:
                self.logger.warning(e)

        return list_of_available

    def install(self, package_name: Union[str, List[str]]) -> None:
        """See Apt.install"""
        for apt in self.apts:
            try:
                apt.install(package_name=package_name)
            except Exception as e:
                self.logger.warning(e)

    def reinstall(self, package_name: Union[str, List[str]]) -> None:
        """See Apt.reinstall"""
        for apt in self.apts:
            try:
                apt.reinstall(package_name=package_name)
            except Exception as e:
                self.logger.warning(e)

    def remove(self, package_name: Union[str, List[str]]) -> None:
        """See Apt.remove"""
        for apt in self.apts:
            try:
                apt.remove(package_name=package_name)
            except Exception as e:
                self.logger.warning(e)

    def purge(self, package_name: Union[str, List[str]]) -> None:
        """See Apt.purge"""
        for apt in self.apts:
            try:
                apt.purge(package_name=package_name)
            except Exception as e:
                self.logger.warning(e)

    def search(self, package_name: str) -> Dict[Apt, List[Dict[str, str]]]:
        """See Apt.search"""
        list_of_available = {}
        for apt in self.apts:
            try:
                list_of_available[apt] = apt.search(package_name)
            except Exception as e:
                self.logger.warning(e)

        return list_of_available

    def show(self, package_name: str) -> Dict[Apt, Dict[Union[str, None], Any]]:
        """See Apt.show"""
        list_of_available = {}
        for apt in self.apts:
            try:
                list_of_available[apt] = apt.show(package_name)
            except Exception as e:
                self.logger.warning(e)

        return list_of_available
