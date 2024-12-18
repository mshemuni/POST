from datetime import datetime
from logging import Logger
from typing import List, Optional, Iterator, Union, Dict

from typing_extensions import Self

from post import Service
from post.connection.model_connector import ModelConnector
from post.service.model_service_list import ModelServiceList
from post.utils.common import GLOBAL_LOGGER
from post.utils.error import NumberOfElementsError


class ServiceList(ModelServiceList):
    """
    ServiceList package manager.

    Args:
        services (List[Service]): A list of service objects
        logger (Logger, optional): A logger to log. Defaults to None.
    """
    def __init__(self, services: List[Service], logger: Optional[Logger] = None) -> None:
        if logger is None:
            self.logger = GLOBAL_LOGGER
        else:
            self.logger = logger

        if len(services) == 0:
            NumberOfElementsError("services can not be empty")

        self.services = services

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(noc: {len(self)})"

    def __repr__(self) -> str:
        return self.__str__()

    def __iter__(self) -> Iterator[Service]:
        for x in self.services:
            yield x

    def __getitem__(self, key: Union[int, slice]) -> Union[Service, Self]:

        if isinstance(key, int):
            return self.services[key]
        elif isinstance(key, slice):
            return self.__class__(self.services[key])

        self.logger.error("Wrong slice")
        raise ValueError("Wrong slice")

    def __delitem__(self, key) -> None:
        del self.services[key]

    def __len__(self) -> int:
        return len(self.services)

    @classmethod
    def from_connections(cls, connections: List[ModelConnector], sudo_passwds: Optional[Union[str, List[str]]],
                         logger: Optional[Logger] = None) -> Self:
        """
        Creates a Self from a list of connections.

        Args:
            connections (List[ModelConnector]): A list of service objects
            sudo_passwds (str, optional): The sudo passwords of the user if the connection is done by an ssh key. Defaults to None.
            logger (Logger, optional): A logger to log. Defaults to None.

        Returns:
            Self: A Self instance
        """

        if isinstance(sudo_passwds, list):
            sudo_passwds_to_use = sudo_passwds
        else:
            sudo_passwds_to_use = [sudo_passwds] * len(connections)

        return cls(
            [
                Service(connection, sudo_passwd=sudo_passwd, logger=logger)
                for connection, sudo_passwd in zip(connections, sudo_passwds_to_use)
            ]
        )

    def list(self) -> Dict[Service, List[Dict[str, str]]]:
        """
        Lists all available services.

        Returns:
            List[Dict[str, str]]]: list of available services
        """
        lists = {}
        for each_service in self.services:
            try:
                lists[each_service] = each_service.list()
            except Exception as e:
                self.logger.error(e)
        return lists

    def start(self, service: str) -> None:
        """See Service.start"""
        for each_service in self.services:
            try:
                each_service.start(service)
            except Exception as e:
                self.logger.error(e)

    def stop(self, service: str) -> None:
        """See Service.stop"""
        for each_service in self.services:
            try:
                each_service.stop(service)
            except Exception as e:
                self.logger.error(e)

    def restart(self, service: str) -> None:
        """See Service.restart"""
        for each_service in self.services:
            try:
                each_service.restart(service)
            except Exception as e:
                self.logger.error(e)

    def enable(self, service: str) -> None:
        """See Service.enable"""
        for each_service in self.services:
            try:
                each_service.enable(service)
            except Exception as e:
                self.logger.error(e)

    def disable(self, service: str) -> None:
        """See Service.disable"""
        for each_service in self.services:
            try:
                each_service.disable(service)
            except Exception as e:
                self.logger.error(e)

    def logs(self, service) -> dict[Service, List[str]]:
        """See Service.logs"""
        lists = {}
        for each_service in self.services:
            try:
                lists[each_service] = each_service.logs(service)
            except Exception as e:
                self.logger.error(e)
        return lists
