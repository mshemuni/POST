from abc import ABC, abstractmethod
from datetime import datetime
from logging import Logger

from typing import List, Dict, Union, Optional

from typing_extensions import Self


class ModelService(ABC):

    @classmethod
    @abstractmethod
    def from_ssh_connector(cls, address: str, port: int, user: str, passwd: str,
                           logger: Optional[Logger] = None) -> Self:
        """Creates a Self"""

    @abstractmethod
    def list(self) -> List[Dict[str, str]]:
        """Lists all services"""

    @abstractmethod
    def start(self, service: str) -> None:
        """Activates a service"""

    @abstractmethod
    def stop(self, service: str) -> None:
        """Stops a service"""

    @abstractmethod
    def restart(self, service: str) -> None:
        """Restarts a service"""

    @abstractmethod
    def enable(self, service: str) -> None:
        """Enables a service"""

    @abstractmethod
    def disable(self, service: str) -> None:
        """Disables a service"""

    @abstractmethod
    def logs(self, service) -> List[str]:
        """Retrieves logs of a service"""
