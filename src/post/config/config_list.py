from logging import Logger
from pathlib import Path
from typing import List, Optional, Union, Dict, Any

from typing_extensions import Self

from post import Config
from post.config.model_config_list import ModelConfigList
from post.connection.model_connector import ModelConnector
from post.utils.common import GLOBAL_LOGGER
from post.utils.error import NumberOfElementsError


class ConfigList(dict[Any, Any], ModelConfigList):
    """
    Multiple Config manager.

    This object does everything Config does but on multiple of Config objects.

    Args:
        configs (List[Config]): A list of Config objects
        logger (Logger, optional): A logger to log. Defaults to None.

    Raises:
        NumberOfElementsError: If length of configs is 0
    """

    def __init__(self, configs: List[Config], logger: Optional[Logger] = None):
        if logger is None:
            self.logger = GLOBAL_LOGGER
        else:
            self.logger = logger

        if len(configs) == 0:
            raise NumberOfElementsError("configs can not be empty")

        self.configs = configs

        for each in self.configs:
            each.create_backup()
            each.clear()

        super().__init__({})

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(noc: {len(self)})"

    def __repr__(self) -> str:
        return self.__str__()

    def __setitem__(self, key: str, value: Dict["str", "str"]) -> None:
        super().__setitem__(key, value)
        for each in self.configs:
            each[key] = value

    def __delitem__(self, key) -> None:
        super().__delitem__(key)
        for each in self.configs:
            del each[key]

    @classmethod
    def from_connections(cls, connections: List[ModelConnector], files: Union[Union[str, Path], List[Union[str, Path]]],
                         sudo_passwds: Optional[Union[str, List[str]]] = None, logger: Optional[Logger] = None) -> Self:
        """
        Creates a Self using list of connections and files

        Args:
            connections (List[ModelConnector]): A list of connections
            files (Union[Union[str, Path], List[Union[str, Path]]]): A list of files
            sudo_passwds: (Optional[Union[str, List[str]]]): A list of sudo passwords, useful if connection is done
                via ssh-keys and no actual password is available. Defaults to None.
            logger (Logger, optional): A logger to log. Defaults to None.

        Returns:
            Self: ConfigList

        Returns:

        """
        if isinstance(files, list):
            files_to_use = files
        else:
            files_to_use = [files] * len(connections)

        sudo_passwds_to_use: Union[List[str], List[None], List[Union[str, None]]]

        if isinstance(sudo_passwds, list):
            sudo_passwds_to_use = sudo_passwds
        else:
            sudo_passwds_to_use = [sudo_passwds] * len(connections)

        return cls(
            [
                Config(connection, file, create=True, backup=True, force=True, sudo_passwd=sudo_passwd, logger=logger)
                for connection, file, sudo_passwd in zip(connections, files_to_use, sudo_passwds_to_use)
            ]
        )

    def update(self, *args, **kwargs) -> None:
        """See Config.update"""

        super().update(*args, **kwargs)
        for each in self.configs:
            each.update(*args, **kwargs)

    def length(self) -> int:
        """
        Returns length of config list

        Could not alter __len__ since it's used for number of key-value paires.

        Returns:
            int: length of config list
        """

        return len(self.configs)

    def take_element(self, index: int) -> None:
        """
        Removes an element from all config files

        Could not alter __delitem__ since it's used for deleting key-value pairs.
        """

        del self.configs[index]

    def get_element(self, key: Union[int, slice]) -> Union[Config, Self]:
        """
        Returns an element from all config files

        Could not alter __item__ since it's used for getting key-value pairs.
        """

        if isinstance(key, int):
            return self.configs[key]
        elif isinstance(key, slice):
            return self.__class__(self.configs[key])

    def clear(self) -> None:
        """See Config.update"""

        for config in self.configs:
            try:
                config.clear()
            except Exception as e:
                self.logger.error(e)
