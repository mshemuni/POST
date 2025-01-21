import re
import uuid
from logging import getLogger, basicConfig
from typing import Dict, Optional, List

import socket

from post.utils.error import Nope

log_format = "[%(asctime)s, %(levelname)s], [%(filename)s, %(funcName)s, %(lineno)s]: %(message)s"
basicConfig(level=20, format=log_format)
GLOBAL_LOGGER = getLogger(__name__)

NOPES = [
    "/", " -", "- ", '"',
    " ", "'", "(", ")" ",",
    ";", "&", ">", "<", "|",
    "=", "[", "]", "#", "!",
    "?", ":", "{", "}", "%",
    "~", "*",
]


def clear(text: str) -> str:
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_escape.sub("", text)


def is_valid_source_line(line: str) -> None:
    pattern = re.compile(
        r"^(deb|deb-src)\s+" r"(\[.*?\]\s+)?" r"https?://\S+\s+" r"\S+\s+" r"(\S+.*)?$"
    )

    if not bool(pattern.match(line.strip())):
        raise ValueError("Bad source")


def option_matcher(option: str) -> Optional[Dict[str, str]]:
    if not option:
        return None

    options_to_return = {}
    options = option.strip().lstrip("[").rstrip("]")

    for option in options.split():
        key, value = option.split("=")
        options_to_return[key] = value

    return options_to_return


def escape_string(name: str) -> None:
    if any(nope in name for nope in NOPES):
        GLOBAL_LOGGER.error(f"Not cool! {name}")
        raise Nope(f"Not cool! {name}")


def check_ssh(ip: str, port: int = 22) -> bool:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except socket.error as e:
        GLOBAL_LOGGER.warning(e)
        return False


def nmap(first_octet: int = 192, second_octet: int = 168, third_octet: int = 1, start_ip: int = 0, end_ip: int = 255,
         port: int = 22) -> List[str]:
    ip_list = []
    for last_octet in range(start_ip, end_ip + 1):
        ip = f"{first_octet}.{second_octet}.{third_octet}.{last_octet}"

        check = check_ssh(ip, port=port)
        if check:
            ip_list.append(ip)

    return ip_list


def random_filename(extension="ps1", prefix="post_", suffix=""):
    unique_id = uuid.uuid4().hex
    return f"{prefix}{unique_id}{suffix}.{extension}"