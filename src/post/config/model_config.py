from abc import ABC, abstractmethod
from logging import Logger
from pathlib import Path
from typing import Dict, Union, Optional

from typing_extensions import Self


class ModelConfig(ABC):

    @classmethod
    @abstractmethod
    def from_ssh_connector(cls, address: str, port: int, user: str, passwd: str,
                           path: Union[str, Path], create: bool = False, backup: bool = False, force: bool = False,
                           logger: Optional[Logger] = None) -> Self:
        """Creates a Self"""

    @abstractmethod
    def __setitem__(self, key: str, value: Dict[str, str]) -> None:
        """Updates the dict on add/update to representing the config file"""

    @abstractmethod
    def __delitem__(self, key: str) -> None:
        """Updates the dict on delete to representing the config file"""

    @abstractmethod
    def update(self, *args, **kwargs) -> None:
        """Updates the dict on update method to representing the config file"""
