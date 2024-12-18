import re
from datetime import datetime

from logging import Logger
from typing import List, Optional, Dict, Union, Any

from typing_extensions import Self

from post import SSHConnector
from post.apt.model_apt import ModelApt
from post.connection.model_connector import ModelConnector
from post.utils.common import escape_string, GLOBAL_LOGGER
from post.utils.error import AlreadyExist, NotFound


def is_valid_source_line(line: str) -> None:
    """
    Check if a line is a valid source line.
    """
    pattern = re.compile(r'^(deb|deb-src)\s+'
                         r'(\[.*?\]\s+)?'
                         r'https?://\S+\s+'
                         r'\S+\s+'
                         r'(\S+.*)?$')

    if not bool(pattern.match(line.strip())):
        raise ValueError("Wrong repo line")


def option_matcher(option: str) -> Optional[Dict[str, str]]:
    """
    Matches options of a repository from source list line
    """
    if not option:
        return None

    options_to_return = {}
    options = option.strip().lstrip("[").rstrip("]")

    for option in options.split():
        key, value = option.split("=")
        options_to_return[key] = value

    return options_to_return


class Apt(ModelApt):
    """
    APT package manager.

    Args:
        connector (ModelConnector): A connector that extends from ModelConnector abstract class.
        sudo_passwd (str, optional): The sudo password of the user if the connection is done by an ssh key. Defaults to None.
        logger (Logger, optional): A logger to log. Defaults to None.
    """

    def __init__(self, connector: ModelConnector, sudo_passwd: Optional[str] = None,
                 logger: Optional[Logger] = None) -> None:
        """
        Constructs an Apt object

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
        Constructs an Apt object using an ssh connection information.

        Args:
            address (str): An IP address or hostname.
            port (int): The ssh port. Most probably is 22.
            user (str): The ssh username.
            passwd (str): The ssh user's password.
            logger (Logger, optional): A logger to log. Defaults to None.

        Returns:
            Self: An Apt object.

        Raises:
            ValueError: If a connection cannot be established
        """
        ssh_connector = SSHConnector(address, port, user, passwd, logger=logger)
        return cls(ssh_connector, logger=logger)

    def repositories(self) -> List[Dict[str, Any]]:
        """
        Returns a list of repositories.

        Raises:
            CommandError: If standard error is not empty
        """
        self.logger.info("Getting repositories")

        output = self.connector.run("grep --no-filename -r '^deb ' /etc/apt/sources.list /etc/apt/sources.list.d/")

        pattern = re.compile(r'^(deb|deb-src)\s+'
                             r'(\[.*?\]\s+)?'
                             r'(\S+)\s+'
                             r'(\S+)\s+'
                             r'(.+)$')
        repositories = []

        repos = output.read().decode().split("\n")
        for repo in repos:
            line = repo.strip()
            match = pattern.match(line)
            if match:
                entry = {
                    'kind': match.group(1),
                    'options': option_matcher(match.group(2)),
                    'url': match.group(3),
                    'distribution': match.group(4),
                    'components': match.group(5).strip()
                }
                repositories.append(entry)

        return repositories

    def add_repository(self, repository: str) -> None:
        """
        Adds a new repository to the system.

        Args:
            repository (str): The string line to be added to `/etc/apt/sources.list.d/`.

        Raises:
            CommandError: If standard error is not empty
        """
        self.logger.info("Adding repository")

        return
        is_valid_source_line(repository)

        repos = self.repositories()

        search = re.search(r'https?://\S+', repository)
        if search is None:
            return

        if search.group(0) in [r["url"] for r in repos]:
            raise AlreadyExist("Repo Already exist")

        stdout = self.connector.sudo_run(f"echo '# Added By POST @ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}'"
                                    " >> /etc/apt/sources.list.d/post.list", passwd=self.sudo_passwd)

        _ = stdout.read().decode()
        stdout = self.connector.sudo_run(f"echo {repository} >> /etc/apt/sources.list.d/post.list",
                                         passwd=self.sudo_passwd)
        _ = stdout.read().decode()

    def update(self) -> None:
        """
        Downloads package information from all configured sources

        Raises:
            CommandError: If standard error is not empty
        """
        self.logger.info("Updating repos")

        stdout = self.connector.sudo_run("apt update", passwd=self.sudo_passwd)
        _ = stdout.read().decode()

    def upgrade(self, package_name: Optional[str] = None) -> None:
        """
        Installs available upgrades of all packages currently installed on the system from the sources configured via
        sources.list

        Args:
            package_name (str, optional): if given upgrades only the package(s) with the given name.
            otherwise upgrades all packages. Defaults to None.

        Raises:
            CommandError: If standard error is not empty
        """
        self.logger.info("Upgrading either a package or all packages")

        if isinstance(package_name, str):
            escape_string(package_name)
            stdout = self.connector.sudo_run(
                f"sudo apt upgrade -y --only-upgrade {package_name}", passwd=self.sudo_passwd
            )
            _ = stdout.read().decode()
            return

        stdout = self.connector.sudo_run("sudo apt upgrade -y", passwd=self.sudo_passwd)
        _ = stdout.read().decode()

    def list(self, installed: bool = False, upgradeable: bool = False) -> List[Dict[str, str]]:
        """
        Installs available upgrades of all packages currently installed on the system from the sources configured via
        sources.list

        Args:
            installed (bool): Filters only installed packages. Defaults to False
            upgradeable (bool): Filters only upgradeable packages. Defaults to False.

        Raises:
            CommandError: If standard error is not empty
        """
        self.logger.info("Listing all available packages")

        command = "apt list"
        if installed:
            command += " --installed"

        if upgradeable:
            command += " --upgradeable"

        packages = self.connector.sudo_run(command, passwd=self.sudo_passwd)

        parsed_data = []
        for line in packages.read().decode().split("\n"):
            try:

                if "/" not in line.strip():
                    continue
                package, rest = line.strip().split("/")
                exp = re.findall(r'\[[^\]]*\]|\S+', rest)
                if len(exp) == 3:
                    repo, version, arch = exp
                    tags = ""
                else:
                    repo, version, arch, tags = exp

                parsed_data.append(
                    {
                        "package": package,
                        "repo": repo,
                        "version": version,
                        "arch": arch,
                        "tags": [each.strip() for each in tags.lstrip("[").rstrip("]").split(",") if each.strip()]
                    }
                )
            except Exception as e:
                self.logger.warning(e)

        return parsed_data

    def install(self, package_name: Union[str, List[str]]) -> None:
        """
        Installs the given package(s) on the system.

        Args:
            package_name (str or List[str]): Package names to be installed.

        Raises:
            CommandError: If standard error is not empty
            NotFound: If there is nothing to install
        """
        self.logger.info("Installing packages")

        available_packages = {p["package"]: p["tags"] for p in self.list()}

        if isinstance(package_name, list):
            package_names = package_name
        else:
            package_names = [package_name]

        package_to_be_installed = []
        for p in package_names:
            if p not in available_packages.keys():
                self.logger.warning(f"Package `{p}` not found. Skipping")
                continue

            if "installed" in available_packages[p]:
                self.logger.warning(f"Package `{p}` already installed. Use `reinstall`. Skipping")
                continue

            escape_string(p)
            package_to_be_installed.append(p)


        if len(package_to_be_installed) == 0:
            self.logger.error("No packages were found")
            raise NotFound("No packages were found")

        command = f"DEBIAN_FRONTEND=noninteractive apt install {' '.join(package_to_be_installed)} -y"
        print(command)

        stdout = self.connector.sudo_run(command, passwd=self.sudo_passwd)
        _ = stdout.read().decode()

    def reinstall(self, package_name: Union[str, List[str]]) -> None:
        """
        Reinstalls the given package(s) on the system.

        Args:
            package_name (str or List[str]): Package names to be reinstalled.

        Raises:
            CommandError: If standard error is not empty
            NotFound: If there is nothing to install
        """
        self.logger.info("Reinstalling packages")

        available_packages = {p["package"]: p["tags"] for p in self.list()}
        if isinstance(package_name, list):
            package_names = package_name
        else:
            package_names = [package_name]

        package_to_be_installed = []
        for p in package_names:
            if p not in available_packages.keys():
                self.logger.warning(f"Package `{p}` not found. Skipping")
                continue

            if "installed" not in available_packages[p]:
                self.logger.warning(f"Package `{p}` already installed. Use `install`. Skipping")
                continue

            escape_string(p)
            package_to_be_installed.append(p)

        if len(package_to_be_installed) == 0:
            self.logger.error("No packages were found")
            raise NotFound("No packages were found")

        command = f"apt reinstall {' '.join(package_to_be_installed)} -y"
        stdout = self.connector.sudo_run(command, passwd=self.sudo_passwd)
        _ = stdout.read().decode()

    def remove(self, package_name: Union[str, List[str]]) -> None:
        """
        Removes the given package(s) from the system.

        Args:
            package_name (str or List[str]): Package names to be removed/uninstalled.

        Raises:
            CommandError: If standard error is not empty
            NotFound: If there is nothing to install
        """
        self.logger.info("Removing packages")

        available_packages = {p["package"]: p["tags"] for p in self.list()}
        if isinstance(package_name, list):
            package_names = package_name
        else:
            package_names = [package_name]

        package_to_be_installed = []
        for p in package_names:
            if p not in available_packages.keys():
                self.logger.warning(f"Package `{p}` not found. Skipping")
                continue

            if "installed" not in available_packages[p]:
                self.logger.warning(f"Package `{p}` is not installed. Skipping")
                continue

            escape_string(p)
            package_to_be_installed.append(p)

        if len(package_to_be_installed) == 0:
            self.logger.error("No packages were found")
            raise NotFound("No packages were found")

        command = f"apt remove {' '.join(package_to_be_installed)} -y"
        stdout = self.connector.sudo_run(command, passwd=self.sudo_passwd)
        _ = stdout.read().decode()

    def purge(self, package_name: Union[str, List[str]]) -> None:
        """
        Purges the given package(s) from the system.

        Args:
            package_name (str or List[str]): Package names to be purged.

        Raises:
            CommandError: If standard error is not empty
            NotFound: If there is nothing to install
        """
        self.logger.info("Purging packages")

        available_packages = {p["package"]: p["tags"] for p in self.list()}
        if isinstance(package_name, list):
            package_names = package_name
        else:
            package_names = [package_name]

        package_to_be_installed = []
        for p in package_names:
            if p not in available_packages.keys():
                self.logger.warning(f"Package `{p}` not found. Skipping")
                continue

            if "installed" not in available_packages[p]:
                self.logger.warning(f"Package {p} is not installed. Skipping")
                continue

            escape_string(p)
            package_to_be_installed.append(p)

        if len(package_to_be_installed) == 0:
            self.logger.error("No packages were found")
            raise NotFound("No packages were found")

        command = f"apt purge {' '.join(package_to_be_installed)} -y"
        stdout = self.connector.sudo_run(command, passwd=self.sudo_passwd)
        _ = stdout.read().decode()

    def search(self, package_name: str) -> List[Dict[str, str]]:
        """
        Searches for the given package name in the list of available packages and display matches.

        Args:
            package_name (str): Package names to be searched.

        Raises:
            CommandError: If standard error is not empty
            NotFound: If there is nothing to install
        """
        self.logger.info("Searching package")

        available_packages = {p["package"]: p["tags"] for p in self.list()}

        escape_string(package_name)

        if package_name not in available_packages.keys():
            self.logger.warning(f"Package `{package_name}` not found")

        command = f"apt search {package_name}"
        stdout = self.connector.run(command)

        lines = stdout.read().decode().strip().split('\n')
        packages_to_return = []

        while lines:
            name_version_arch = lines.pop(0).strip()
            description_lines = []

            match = re.match(r'(.+?)/(.+?)\s+([\d\w.:+-]+)\s+(\S+)(?:\s+\[.*\])?', name_version_arch)
            if match:
                name, repo, version, arch = match.groups()
                description = ''

                while lines and not lines[0].startswith(' '):
                    description_lines.append(lines.pop(0).strip())

                if lines:
                    description = lines.pop(0).strip()

                packages_to_return.append({
                    'name': name,
                    'repo': repo,
                    'version': version,
                    'architecture': arch,
                    'description': description
                })

        return packages_to_return

    def show(self, package_name: str) -> Dict[Union[str, None], Any]:
        """
        Shows information about the given package including its dependencies, installation and download size,
        sources the package is available from, the description of the packages content and much more.

        Args:
            package_name (str): Package names to be shown.

        Raises:
            CommandError: If standard error is not empty
            NotFound: If there is nothing to install
        """
        self.logger.info("Showing package")

        available_packages = {p["package"]: p["tags"] for p in self.list()}

        escape_string(package_name)

        if package_name not in available_packages.keys():
            self.logger.warning(f"Package `{package_name}` not found")
            raise NotFound(f"Package `{package_name}` not found")

        command = f"apt show {package_name}"
        stdout = self.connector.run(command)

        lines = stdout.read().decode().strip().split('\n')
        parsed_dict: dict[Union[str, None], Any] = {}

        current_key = None
        for line in lines:
            if line.startswith(' '):
                parsed_dict[current_key] += '\n' + line.strip()
            else:
                key, value = line.split(': ', 1)
                current_key = key.strip()
                if current_key == 'Depends':
                    parsed_dict[current_key] = [dep.strip() for dep in value.split(',')]
                else:
                    parsed_dict[current_key] = value.strip()

        return parsed_dict

    def auto_remove(self):
        command = "apt autoremove -y"
        stdout = self.connector.run(command)
        _ = stdout.read().decode()
