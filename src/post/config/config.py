import configparser
import io
from logging import Logger
from pathlib import Path
from typing import Optional, Union, Dict, Any

from typing_extensions import Self

from post import SSHConnector
from post.config.model_config import ModelConfig
from post.connection.model_connector import ModelConnector
from post.utils.common import GLOBAL_LOGGER
from post.utils.error import CommandError


class Config(Dict[str, Any], ModelConfig):
    """
    Config file manager.

    Args:
        connector (ModelConnector): An ssh connector that extends from ModelConnector
        path (str): The path to the config file
        create (bool): Whether to create the config file if it does not exist. Defaults to False.
        backup (bool): Whether to create a backup of config file before updating. Defaults to False.
        force (bool): Whether create directory path (`mkdir -p`) if the parent path does not exist.
            Not implemented yet. Defaults to False.
        sudo_passwd: (str, optional): The sudo password of the user if the connection is done by an ssh key.
        logger (Logger, optional): The logger to log. Defaults to None.
    """
    def __init__(self, connector: ModelConnector, path: Union[str, Path], create: bool = False,
                 backup: bool = False, force: bool = False,
                 sudo_passwd: Optional[str] = None, logger: Optional[Logger] = None) -> None:
        """
        Constructs a Config File object

        Args:
            connector (ModelConnector): An ssh connector that extends from ModelConnector
            path (str): The path to the config file
            create (bool): Whether to create the config file if it does not exist. Defaults to False.
            backup (bool): Whether to create a backup of config file before updating. Defaults to False.
            force (bool): Whether create directory path (`mkdir -p`) if the parent path does not exist.
                Not implemented yet. Defaults to False.
        sudo_passwd: (str, optional): The sudo password of the user if the connection is done by an ssh key.
            logger (Logger, optional): The logger to log. Defaults to None.

        Raises:
            FileNotFoundError: if the config file does not exist and create is False.
        """

        if logger is None:
            self.logger = GLOBAL_LOGGER
        else:
            self.logger = logger

        if isinstance(path, Path):
            self.path = path
        else:
            self.path = Path(path)

        self.connector = connector
        self.sudo_passwd = sudo_passwd
        if not self.exist():
            if not create:
                raise FileNotFoundError("Config file does not exist")
            else:
                self.touch()

        if backup:
            self.create_backup()

        self.config = configparser.ConfigParser(interpolation=None)
        self.config.read_string(self.read())

        super().__init__({section: dict(self.config.items(section)) for section in self.config.sections()})

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(connector: {self.connector}, path: {self.path})"

    def __setitem__(self, key: str, value: Dict[str, str]) -> None:
        super().__setitem__(key, value)
        self.__update()

    def __delitem__(self, key: str) -> None:
        super().__delitem__(key)
        self.__update()

    @classmethod
    def from_ssh_connector(cls, address: str, port: int, user: str, passwd: str,
                           path: Union[str, Path], create: bool = False, backup: bool = False, force: bool = False,
                           logger: Optional[Logger] = None) -> Self:
        """
        Creates a Self with given ssh information

        Args:
            address (str): The address of the ssh server
            port (int): The port of the ssh server
            user  (str): The username of the ssh server
            passwd (str): The password of the ssh server
            path (str): The path to the config file
            create (bool): Whether to create the config file if it does not exist.
            backup (bool): Whether to create a backup of config file before updating.
            force (bool): Whether create directory path (`mkdir -p`) if the parent path does not exist.
            logger (Logger, optional): The logger to log. Defaults to None.

        Returns:
            Self: A Self object

        Raises:
            FileNotFoundError: if the config file does not exist and create is False.
        """
        ssh_connector = SSHConnector(address, port, user, passwd, logger=logger)
        return cls(ssh_connector, path, create=create, backup=backup, force=force, logger=logger)

    def clear(self) -> None:
        """
        Clearing the config file.
        """
        self.logger.info("Clear config file")

        super().clear()
        self.__update()

    def update(self, *args, **kwargs) -> None:
        self.logger.info("Updating config file")

        super().update(*args, **kwargs)
        self.__update()

    def touch(self) -> None:
        """
        Creates a config file.
        """
        self.logger.info("Creating config file")

        stdout = self.connector.sudo_run(
            f"mkdir -p {self.path.parent.absolute().__str__()}", passwd=self.sudo_passwd
        )
        _ = stdout.read().decode()

        stdout = self.connector.sudo_run(f"touch {self.path.absolute().__str__()}", passwd=self.sudo_passwd)
        _ = stdout.read().decode()

    def exist(self, the_file: Optional[Union[str, Path]] = None) -> bool:
        """
        Checks if the given config file exists.

        Args:
            the_file (str, optional): The path to the config file. Defaults to None.
        """
        self.logger.info("Checking if config file exists")

        if the_file is None:
            file_to_check = self.path
        else:
            if isinstance(the_file, Path):
                file_to_check = the_file
            else:
                file_to_check = Path(the_file)

        try:
            stdout = self.connector.run(f"test -e {file_to_check} && echo exist")
            if stdout.read().decode().strip() == "":
                return False
        except CommandError as e:
            self.logger.warning(e)
            return False

        return True

    def create_backup(self) -> None:
        """
        Creates a backup file of the config file.
        """
        self.logger.info("Creating backup of config file")

        backup_base = self.path.parent / (self.path.name + ".0")

        counter = 1
        while self.exist(backup_base):
            backup_base = backup_base.parent / (backup_base.stem + f".{counter}")
            counter += 1

        stdout = self.connector.sudo_run(
            f"cp {self.path.absolute().__str__()} {backup_base.absolute().__str__()}", passwd=self.sudo_passwd
        )
        _ = stdout.read().decode()

    def read(self) -> str:
        """
        Reads the config file.
        """
        self.logger.info("Reading config file")

        stdout = self.connector.sudo_run(f"cat {self.path.absolute().__str__()}", passwd=self.sudo_passwd)
        return str(stdout.read().decode())

    def __update(self) -> None:
        """
        Updates the file each time the dict object updated
        """
        self.logger.info("Writing config file")

        self.config.clear()

        for section, options in self.items():
            if isinstance(options, dict):
                pass
            else:
                pass
            self.config[section] = options

        with io.StringIO() as ss:
            self.config.write(ss)
            ss.seek(0)
            stdout = self.connector.sudo_run(f"echo '{ss.read()}' > {self.path.absolute().__str__()}",
                                             passwd=self.sudo_passwd)
            _ = stdout.read().decode()
