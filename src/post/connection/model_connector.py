from abc import ABC, abstractmethod
from typing import Optional

from paramiko.channel import ChannelFile


class ModelConnector(ABC):

    @abstractmethod
    def run(self, command: str) -> ChannelFile:
        """Run a command"""

    @abstractmethod
    def sudo_run(self, command: str, passwd: Optional[str] = None) -> ChannelFile:
        """Run a command as root"""
