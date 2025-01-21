from datetime import datetime
from logging import Logger
from typing import Optional, List, Dict, Union

from typing_extensions import Self

from post import SSHConnector
from post.connection.model_connector import ModelConnector
from post.service.model_service import ModelService
from post.utils.common import escape_string, GLOBAL_LOGGER
from post.utils.error import NotFound


class Service(ModelService):
    """
    Service package manager.

    Args:
        connector (ModelConnector): A connector that extends from ModelConnector abstract class.
        sudo_passwd (str, optional): The sudo password of the user if the connection is done by an ssh key. Defaults to None.
        logger (Logger, optional): A logger to log. Defaults to None.
    """
    def __init__(self, connector: ModelConnector, sudo_passwd: Optional[str] = None,
                 logger: Optional[Logger] = None) -> None:
        """
        Constructs an Service object

        Args:
            connector (ModelConnector): A connector that extends from ModelConnector abstract class.
            sudo_passwd (str, optional): The sudo password of the user if the connection is done by an ssh key. Defaults to None.
            logger (Logger, optional): A logger to log. Defaults to None.
        """
        if logger is None:
            self.logger = GLOBAL_LOGGER
        else:
            self.logger = logger

        self.sudo_passwd = sudo_passwd
        self.connector = connector

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(connector: {self.connector})"

    def __repr__(self) -> str:
        return self.__str__()

    @classmethod
    def from_ssh_connector(cls, address: str, port: int, user: str, passwd: str,
                           logger: Optional[Logger] = None) -> Self:
        """
                Constructs a Service object using an ssh connection information.

                Args:
                    address (str): An IP address or hostname.
                    port (int): The ssh port. Most probably is 22.
                    user (str): The ssh username.
                    passwd (str): The ssh user's password.
                    logger (Logger, optional): A logger to log. Defaults to None.

                Returns:
                    Self: A Service object.

                Raises:
                    ValueError: If a connection cannot be established
                """
        ssh_connector = SSHConnector(address, port, user, passwd, logger=logger)
        return cls(ssh_connector, logger=logger)

    def check(self, service: str) -> None:
        """
        Check if the service is available

        Args:
            service (str): The name of the service to be checked.

        Raises:
            NotFound: If the service is not found.
        """
        self.logger.info("Checking if service exists")

        services = [service["unit"] for service in self.list()]
        if service not in services:
            raise NotFound("No service was found with the given name")

    def list(self) -> List[Dict[str, str]]:
        """
        Returns a list of services as a dictionary

        Returns:
            List[Dict[str, str]]: The list of services as a dictionary.
        """
        self.logger.info("Listing all services")

        command = "systemctl list-units -all --no-pager --no-legend | tr -cd '\11\12\15\40-\176'"
        stdout = self.connector.run(command)

        table_to_return = []
        for row in stdout.read().decode().split("\n"):
            if row:
                columns = row.split()
                table_to_return.append(
                    {
                        "unit": columns[0],
                        "load": columns[1],
                        "active": columns[2],
                        "substate": columns[3],
                        "description": " ".join(columns[4:])
                    }
                )

        return table_to_return

    def start(self, service: str) -> None:
        """
        Starts a service

        Args:
            service (str): The name of the service to be started.

        Raises:
            NotFound: If the service is not found.
        """
        self.logger.info("Starting a service")

        self.check(service)

        escape_string(service)
        command = f"systemctl start {service}"

        stdout = self.connector.sudo_run(command, passwd=self.sudo_passwd)
        _ = stdout.read().decode().strip().splitlines()

    def stop(self, service: str) -> None:
        """
        Stops a service

        Args:
            service (str): The name of the service to be stopped.

        Raises:
            NotFound: If the service is not found.
        """
        self.logger.info("Stopping a service")

        self.check(service)

        escape_string(service)
        command = f"systemctl stop {service}"
        stdout = self.connector.sudo_run(command, passwd=self.sudo_passwd)
        _ = stdout.read().decode().strip().splitlines()

    def restart(self, service: str) -> None:
        """
        Restarts a service

        Args:
            service (str): The name of the service to be restarted.

        Raises:
            NotFound: If the service is not found.
        """
        self.logger.info("Restarting a service")

        self.check(service)

        escape_string(service)
        command = f"systemctl restart {service}"

        stdout = self.connector.sudo_run(command, passwd=self.sudo_passwd)
        _ = stdout.read().decode().strip().splitlines()

    def enable(self, service: str) -> None:
        """
        Enables a service

        Args:
            service (str): The name of the service to be enabled.

        Raises:
            NotFound: If the service is not found.
        """
        self.logger.info("Enabling a service")

        self.check(service)

        escape_string(service)
        command = f"systemctl enable {service}"

        stdout = self.connector.sudo_run(command, passwd=self.sudo_passwd)
        _ = stdout.read().decode().strip().splitlines()

    def disable(self, service: str) -> None:
        """
        Disables a service

        Args:
            service (str): The name of the service to be disabled.

        Raises:
            NotFound: If the service is not found.
        """
        self.logger.info("Disabling a service")

        self.check(service)

        escape_string(service)
        command = f"systemctl disable {service}"

        stdout = self.connector.sudo_run(command, passwd=self.sudo_passwd)
        _ = stdout.read().decode().strip().splitlines()

    def logs(self, service: str) -> List[str]:
        """
        Returns logs of a service.

        Args:
            service (str): The name of the service.

        Returns:
            List[Dict[str, Union[str, datetime]]]: each log line by line

        Raises:
            NotFound: If the service is not found.
        """
        self.logger.info("Getting logs of a service")

        self.check(service)

        escape_string(service)
        command = f"sudo journalctl -u {service} -b -o short-iso"

        stdout = self.connector.sudo_run(command, passwd=self.sudo_passwd)

        return stdout.read().decode().strip().splitlines()

    def daemon_reload(self) -> None:
        stdout = self.connector.sudo_run("sudo systemctl daemon-reload", passwd=self.sudo_passwd)
        _ = stdout.read().decode().strip().splitlines()
