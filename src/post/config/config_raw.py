from logging import Logger
from pathlib import Path
from typing import Union, Optional

from typing_extensions import Self

from post import SSHConnector
from post.connection.model_connector import ModelConnector
from post.utils.common import GLOBAL_LOGGER


class ConfigRaw:
    """
    Config ConfigRaw manager.

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

    def __init__(
        self,
        connector: ModelConnector,
        path: Union[str, Path],
        create: bool = False,
        backup: bool = False,
        force: bool = False,
        sudo_passwd: Optional[str] = None,
        logger: Optional[Logger] = None,
    ) -> None:
        """
        Constructs a ConfigRaw object

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

        self.__data = self.read()

    def __str__(self) -> str:
        return self.data

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(connector: {self.connector}, path: {self.path})"
        )

    def __len__(self) -> int:
        return len(self.data)

    @classmethod
    def from_ssh_connector(
        cls,
        address: str,
        port: int,
        user: str,
        passwd: str,
        path: Union[str, Path],
        create: bool = False,
        backup: bool = False,
        force: bool = False,
        logger: Optional[Logger] = None,
    ) -> Self:
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
        return cls(ssh_connector, path, create=create, backup=backup, force=force)

    @property
    def data(self) -> str:
        """
        Returning the data (RAM)

        Returns:
            str: The data of config file
        """
        self.logger.info("Returning data (RAM)")

        return self.__data

    @data.setter
    def data(self, data: str) -> None:
        """
        Writing data to config file

        Args:
            data (str): The data to write to the config file
        """
        self.logger.info("Updating the data")

        self.__data = data
        self.__update()

    def read(self) -> str:
        """
        Reading the data from the config file

        Returns:
            str: The data of config file
        """
        self.logger.info("Reading the data from the config file")

        stdout = self.connector.sudo_run(
            f"cat {self.path.absolute().__str__()}", passwd=self.sudo_passwd
        )
        return str(stdout.read().decode())

    def exist(self, the_file: Optional[Union[str, Path]] = None) -> bool:
        """
        Checks if the file exist

        Args:
            the_file (Union[str, Path], optional): The path to the file. Defaults to None.

        Returns:
            bool: True if the file exists
        """
        self.logger.info("Checking if the config files exists")

        if the_file is None:
            file_to_check = self.path
        else:
            if isinstance(the_file, Path):
                file_to_check = the_file
            else:
                file_to_check = Path(the_file)

        stdout = self.connector.run(f"test -e {file_to_check} && echo exist")
        return "e" in stdout.read().decode()

    def create_backup(self) -> None:
        """Creates a backup before each update"""
        self.logger.info("Creating a backup for the config file")

        backup_base = self.path.parent / (self.path.name + ".0")

        counter = 1
        while self.exist(backup_base):
            backup_base = backup_base.parent / (backup_base.stem + f".{counter}")
            counter += 1

        stdout = self.connector.sudo_run(
            f"cp {self.path.absolute().__str__()} {backup_base.absolute().__str__()}",
            passwd=self.sudo_passwd,
        )
        _ = stdout.read().decode()

    def touch(self) -> None:
        """Creates the config file"""
        self.logger.info("Creating the config file")

        stdout = self.connector.sudo_run(
            f"mkdir -p {self.path.parent.absolute().__str__()}", passwd=self.sudo_passwd
        )
        _ = stdout.read().decode()
        stdout = self.connector.sudo_run(
            f"touch {self.path.absolute().__str__()}", passwd=self.sudo_passwd
        )
        _ = stdout.read().decode()

    def __update(self) -> None:
        """Updates the config file"""
        self.logger.info("Updating the config file")

        stdout = self.connector.sudo_run(
            f"echo '{self.data}' > {self.path.absolute().__str__()}", passwd=self.sudo_passwd
        )
        _ = stdout.read().decode()
