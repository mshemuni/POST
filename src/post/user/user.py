from logging import Logger
from typing import Optional, List

from typing_extensions import Self

from post import SSHConnector
from post.connection.model_connector import ModelConnector
from post.user.model_user import ModelUser
from post.utils.common import GLOBAL_LOGGER


class User(ModelUser):
    """
    User package manager.

    Args:
        connector (ModelConnector): A connector that extends from ModelConnector abstract class.
        sudo_passwd (str, optional): The sudo password of the user if the connection is done by an ssh key. Defaults to None.
        logger (Logger, optional): A logger to log. Defaults to None.
    """
    def __init__(self, connector: ModelConnector, sudo_passwd: Optional[str] = None,
                 logger: Optional[Logger] = None) -> None:
        """
        User package manager.

        Args:
            connector (ModelConnector): A connector that extends from ModelConnector abstract class.
            sudo_passwd (str, optional): The sudo password of the user if the connection is done by an ssh key. Defaults to None.
            logger (Logger, optional): A logger to log. Defaults to None.

        Returns:
            Self: an instance of the self.
        """

        if logger is None:
            self.logger = GLOBAL_LOGGER
        else:
            self.logger = logger

        self.sudo_passwd = sudo_passwd
        self.connector = connector

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.connector})"

    def __repr__(self) -> str:
        return self.__str__()

    @classmethod
    def from_ssh_connector(cls, address: str, port: int, user: str, passwd: str,
                           logger: Optional[Logger] = None) -> Self:
        """
        Creates a Self from a given SSH information.
        
        Args:
            address (str): The address of the SSH connection.
            port (int): The port of the SSH connection.
            user (str): The username of the SSH connection.
            passwd (str): The password of the SSH connection.
            logger (Logger, optional): A logger to log. Defaults to None.
           
        Returns:
            Self: an instance of the self.         
        """
        ssh_connector = SSHConnector(address, port, user, passwd, logger=logger)
        return cls(ssh_connector, logger=logger)

    def list(self) -> List[str]:
        """
        Returns a list of all users.

        Returns:
            List[str]: A list of all users.
        """
        result = self.connector.sudo_run(
            f"cat /etc/passwd | cut -d: -f1", passwd=self.sudo_passwd
        )
        users = result.read().decode().split()
        return users

    def list_groups(self) -> List[str]:
        """
        A list of all groups.

        Returns:
            List[str]: A list of all groups.
        """
        result = self.connector.sudo_run(
            f"cat /etc/group|cut -d: -f1", passwd=self.sudo_passwd
        )
        users = result.read().decode().split()
        return users

    def exist(self, username: str) -> bool:
        """
        Checks if a user exists.

        Args:
            username (str): The username of the user.

        Returns:
            bool: True if the user exists.
        """
        result = self.connector.sudo_run(
            f"id '{username}' &>/dev/null && echo 1", passwd=self.sudo_passwd
        )
        return result.read().decode().strip() == "1"

    def add(self, username: str, home_dir: Optional[str] = None, shell: Optional[str] = None,
            full_name: Optional[str] = None):
        """
        Adds a new user.

        Args:
            username (str): The username of the user.
            home_dir (str, optional): The home directory of the user.
            shell (str, optional): The shell command of the user.
            full_name (str, optional): The full name of the user.
        """
        if self.exist(username):
            raise ValueError("User already exists")

        command = "useradd -m"

        if home_dir is not None:
            command += f" -d {home_dir}"

        if shell is not None:
            command += f" -s {shell}"

        if full_name is not None:
            command += f" -c '{full_name}'"

        command += f" {username}"

        stdout = self.connector.sudo_run(command, passwd=self.sudo_passwd)
        _ = stdout.read().decode()

    def rm(self, username: str, remove_all_files: bool = False, remove_home_dir: bool = False) -> None:
        """
        Removes a user.

        Args:
            username (str): The username of the user.
            remove_all_files (bool, optional): Remove all files. Defaults to False.
            remove_home_dir (bool, optional): Remove home directory. Defaults to False.

        """
        if not self.exist(username):
            raise ValueError("User does not exist")

        command = "deluser --backup --backup-to='/root'"

        if remove_all_files:
            command += " --remove-all-files"

        if remove_home_dir:
            command += " --remove-home"

        command += f" {username}"

        stdout = self.connector.sudo_run(command, passwd=self.sudo_passwd)
        _ = stdout.read().decode()

    def groups(self, username: str) -> List[str]:
        """
        Lists all groups owned by a user.

        Args:
            username (str): The username of the user.

        Returns:
            List[str]: A list of all groups.
        """
        if not self.exist(username):
            raise ValueError("User does not exist")

        result = self.connector.sudo_run(f"groups {username}", passwd=self.sudo_passwd)
        groups_as_string = result.read().decode().split(":")[-1].strip()
        return groups_as_string.split()

    def group_add(self, username: str, group_name: str) -> None:
        """
        Adds a new group.

        Args:
            username (str): The username of the user.
            group_name (str): The name of the new group.
        """
        if not self.exist(username):
            raise ValueError("User does not exist")

        if group_name in self.groups(username):
            raise ValueError("Already in the group")

        stdout = self.connector.sudo_run(
            f"adduser {username} {group_name}", passwd=self.sudo_passwd
        )
        _ = stdout.read().decode()

    def group_set(self, username: str, group_names: List[str]) -> None:
        """
        Sets groups to user. Removes previously added groups.

        Args:
            username (str): The username of the user.
            group_names (List[str]): The names of the new groups.
        """

        if not self.exist(username):
            raise ValueError("User does not exist")


        stdout = self.connector.sudo_run(
            f"sudo usermod -G {','.join(group_names)} {username}", passwd=self.sudo_passwd
        )
        _ = stdout.read().decode()

    def group_rm(self, username: str, group_name: str) -> None:
        """
        Removes group from user.

        Args:
            username (str): The username of the user.
            group_name (str): The name of the new group.
        """
        if not self.exist(username):
            raise ValueError("User does not exist")

        if group_name not in self.groups(username):
            raise ValueError("User is not in the group")

        stdout = self.connector.sudo_run(
            f"deluser {username} {group_name}", passwd=self.sudo_passwd
        )
        _ = stdout.read().decode()

    def enable(self, username: str) -> None:
        """
        Enables a user.

        Args:
            username (str): The username of the user.
        """
        if not self.exist(username):
            raise ValueError("User does not exist")

        stdout = self.connector.sudo_run(
            f"passwd --lock {username}", passwd=self.sudo_passwd
        )
        _ = stdout.read().decode()

    def disable(self, username: str) -> None:
        """
        Disables a user.

        Args:
            username (str): The username of the user.
        """
        if not self.exist(username):
            raise ValueError("User does not exist")

        stdout = self.connector.sudo_run(
            f"passwd --unlock {username}", passwd=self.sudo_passwd
        )
        _ = stdout.read().decode()

    def is_enabled(self, username: str) -> bool:
        """
        Checks if a user is enabled.

        Args:
            username (str): The username of the user.

        Returns:
            bool: Whether the user is enabled.
        """
        command = f"passwd -S '{username}' | awk '{{print \$2}}'"
        result = self.connector.sudo_run(command, passwd=self.sudo_passwd)
        return result.read().decode().strip() != "L"

    def set_password(self, username: str, password: str) -> None:
        """
        Sets the password for a user. Does not require previous password

        Args:
            username (str): The username of the user.
            password (str): The new password.
        """
        if not self.exist(username):
            raise ValueError("User does not exist")

        stdout = self.connector.sudo_run(
            f"echo '{username}:{password}' | sudo chpasswd", passwd=self.sudo_passwd
        )
        _ = stdout.read().decode()

    def info(self, username: str) -> List[str]:
        """
        Returns information about a user.

        Args:
            username (str): The username of the user.

        Returns:
            List[str]: A list of information about the user.
        """
        if not self.exist(username):
            raise ValueError("User does not exist")

        stdout = self.connector.sudo_run(
            f"getent passwd {username}", passwd=self.sudo_passwd
        )
        info = stdout.read().decode().strip().split(":")
        return [info[0], self.is_enabled(username), int(info[2]), int(info[3]), info[4], info[5]]
