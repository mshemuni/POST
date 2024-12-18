from abc import ABC, abstractmethod
from datetime import datetime
from logging import Logger
from typing import Iterator, Union, List, Optional, Dict

from typing_extensions import Self

from post import Service
from post.connection.model_connector import ModelConnector


class ModelServiceList(ABC):
    @abstractmethod
    def __iter__(self) -> Iterator[Service]:
        """Makes sure one can iterate through Service"""

    @abstractmethod
    def __getitem__(self, key: Union[int, slice]) -> Union[Service, Self]:
        """Returns the given slice of the Service"""

    @abstractmethod
    def __delitem__(self, key) -> None:
        """Removes the given Apt from the ModelServiceService"""

    @abstractmethod
    def __len__(self) -> int:
        """Returns the length of the Service"""

    @classmethod
    @abstractmethod
    def from_connections(cls, connections: List[ModelConnector], sudo_passwds: Optional[Union[str, List[str]]],
                         logger: Optional[Logger] = None) -> Self:
        """Returns a Service from a given connection list"""

    @abstractmethod
    def list(self) -> Dict[Service, List[Dict[str, str]]]:
        """Lists all services of Service"""

    @abstractmethod
    def start(self, service: str) -> None:
        """Activates a service on all Service"""

    @abstractmethod
    def stop(self, service: str) -> None:
        """Stops a service on all ServiceList"""

    @abstractmethod
    def restart(self, service: str) -> None:
        """Restart a service on all ServiceList"""

    @abstractmethod
    def enable(self, service: str) -> None:
        """Enables a service on all ServiceList"""

    @abstractmethod
    def disable(self, service: str) -> None:
        """Disables a service on all ServiceList"""

    @abstractmethod
    def logs(self, service) -> dict[Service, List[dict[str, str | datetime]]]:
        """Retrieves logs of a service of ServiceList"""
