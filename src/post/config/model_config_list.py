from abc import ABC, abstractmethod
from logging import Logger
from pathlib import Path
from typing import Dict, List, Union, Optional

from typing_extensions import Self

from post.connection.model_connector import ModelConnector


class ModelConfigList(ABC):

    @classmethod
    @abstractmethod
    def from_connections(cls, connections: List[ModelConnector], files: Union[Union[str, Path], List[Union[str, Path]]],
                         sudo_passwds: Optional[Union[str, List[str]]] = None, logger: Optional[Logger] = None) -> Self:
        """Creates a Self from connection list"""

    @abstractmethod
    def __setitem__(self, key: str, value: Dict[str, str]) -> None:
        """Updates the dict on add/update to representing the config file on all ModelConnection"""

    @abstractmethod
    def __delitem__(self, key: str) -> None:
        """Updates the dict on delete to representing the config file on all ModelConnection"""

    @abstractmethod
    def update(self, *args, **kwargs) -> None:
        """Updates the dict on update method to representing the config file on all ModelConnection"""
