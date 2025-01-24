from logging import Logger
from typing import Optional, Literal
from typing_extensions import Self

import re

from post import SSHConnector, Config, ConfigRaw
from post.connection.model_connector import ModelConnector
from post.utils.common import GLOBAL_LOGGER, random_filename
from post.utils.error import NotFound, CommandError, AlreadyExist, NumberOfElementsError


def gpo_parser(text: str) -> dict[str, dict[str, str]]:
    gpo_blocks = text.strip().split("\n\n")

    gpos = {}
    for block in gpo_blocks:
        gpo = {}
        lines = block.split("\n")

        for line in lines:
            key, _, value = line.partition(":")
            key = key.strip().lower().replace(" ", "_")
            value = value.strip()
            gpo[key] = value

        if "gpo" in gpo:
            gpo_id = gpo.pop("gpo")
            gpos[gpo_id] = gpo

    return gpos


def parse_ldif(ldif_str):
    data = []
    line_list = ldif_str.split("\n")

    the_line = line_list[0]

    for line in line_list[1:]:
        if line.startswith(" "):
            the_line += line.strip()
        else:
            data.append(the_line)
            the_line = line

    def parse_to_dict(text):
        parsed_dict = {}
        current_key = None

        for line in text.splitlines():
            if line.strip():
                if ": " in line:
                    key, value = line.split(": ", 1)
                    if key in parsed_dict:
                        if not isinstance(parsed_dict[key], list):
                            parsed_dict[key] = [parsed_dict[key]]
                        parsed_dict[key].append(value)
                    else:
                        parsed_dict[key] = value
                    current_key = key
                elif current_key:
                    if isinstance(parsed_dict[current_key], list):
                        parsed_dict[current_key][-1] += "\n" + line.strip()
                    else:
                        parsed_dict[current_key] += "\n" + line.strip()

        return parsed_dict

    return parse_to_dict("\n".join(data))


class GPO:
    def __init__(self, connector: ModelConnector, ad_passwd: Optional[str] = None, sudo_passwd: Optional[str] = None,
                 logger: Optional[Logger] = None):
        if logger is None:
            self.logger = GLOBAL_LOGGER
        else:
            self.logger = logger

        self.ad_passwd = ad_passwd
        self.sudo_passwd = sudo_passwd
        self.connector = connector

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(connector: {self.connector})"

    def __repr__(self) -> str:
        return self.__str__()

    def __password_check(self, ad_passwd: Optional[str] = None) -> str:
        if ad_passwd is None:
            ad_passwd_to_use = self.ad_passwd
        else:
            ad_passwd_to_use = ad_passwd

        if ad_passwd_to_use is None:
            raise NotFound("I need AD's Administrator password")

        return ad_passwd_to_use

    def get_realm(self):
        self.logger.info("Getting the realm")

        stdout = self.connector.sudo_run(
            "samba-tool domain info 127.0.01|grep 'Domain'|cut -d':' -f2",
            passwd=self.sudo_passwd
        )
        domain = stdout.read().decode().strip()
        return domain

    def dash_b(self, upper: bool = False):
        realm = self.get_realm()
        return ",".join([f"dc={each if not upper else each.upper()}" for each in realm.split(".")])

    @classmethod
    def from_ssh_connector(cls, address: str, port: int, user: str, passwd: str,
                           logger: Optional[Logger] = None) -> Self:
        """
        Constructs a GPO object using an ssh connection information.

        Args:
            address (str): An IP address or hostname.
            port (int): The ssh port. Most probably is 22.
            user (str): The ssh username.
            passwd (str): The ssh user's password.
            logger (Logger, optional): A logger to log. Defaults to None.

        Returns:
            Self: A GPO object.

        Raises:
            ValueError: If a connection cannot be established
        """
        ssh_connector = SSHConnector(address, port, user, passwd, logger=logger)
        return cls(ssh_connector, logger=logger)

    def list(self) -> dict[str, dict[str, str]]:
        self.logger.info("Getting GPO list")

        stdout = self.connector.sudo_run("samba-tool gpo listall", passwd=self.sudo_passwd)
        gpo_list_as_text = stdout.read().decode()
        return gpo_parser(gpo_list_as_text)

    def create(self, name: str, ad_passwd: Optional[str] = None) -> str:
        self.logger.info("Creating a GPO")

        ad_passwd_to_use = self.__password_check(ad_passwd)

        stdout = self.connector.sudo_run(
            f"samba-tool gpo create {name} -UAdministrator --password='{ad_passwd_to_use}'",
            passwd=self.sudo_passwd
        )
        gpo_creation_text = stdout.read().decode()

        match = re.search(r"\{[0-9A-Fa-f\-]+\}", gpo_creation_text)

        if match:
            return match.group(0)
        else:
            raise CommandError("Couldn't get the GPO's GUID. Most probably it could not be created.")

    def delete(self, gpo: str, ad_passwd: Optional[str] = None):
        self.logger.info("Delete a GPO")

        ad_passwd_to_use = self.__password_check(ad_passwd)

        stdout = self.connector.sudo_run(
            f"samba-tool gpo del {gpo} -UAdministrator --password='{ad_passwd_to_use}'",
            passwd=self.sudo_passwd
        )
        _ = stdout.read().decode()

    def link(self, gpo: str, container_dn: str, ad_passwd: Optional[str] = None):
        self.logger.info("Link a GPO")

        ad_passwd_to_use = self.__password_check(ad_passwd)

        stdout = self.connector.sudo_run(
            f"samba-tool gpo setlink '{container_dn}' {gpo} -UAdministrator --password='{ad_passwd_to_use}'",
            passwd=self.sudo_passwd
        )
        _ = stdout.read().decode()

    def unlink(self, gpo: str, container_dn: str, ad_passwd: Optional[str] = None):
        self.logger.info("Link a GPO")

        ad_passwd_to_use = self.__password_check(ad_passwd)

        stdout = self.connector.sudo_run(
            f"samba-tool gpo dellink '{container_dn}' {gpo} -UAdministrator --password='{ad_passwd_to_use}'",
            passwd=self.sudo_passwd
        )
        _ = stdout.read().decode()

    def info(self, gpo: str):
        realm = self.get_realm()
        dash_b = self.dash_b()
        stdout = self.connector.sudo_run(
            f"ldapsearch -H ldaps://{realm} -D 'administrator@{realm}' -w Qq123456 -b '{dash_b}' '(cn={gpo})' "
            "| grep -v -e '^#' -e '^$'",
            passwd=self.sudo_passwd
        )
        _ = stdout.read().decode()
        return parse_ldif(_)

    def ldap_add(self, gpo: str, key: str, value: str, ad_passwd: Optional[str] = None) -> None:

        ad_passwd_to_use = self.__password_check(ad_passwd)

        info = self.info(gpo)
        if key in info.keys():
            raise AlreadyExist("The given key already exist. Use edit.")

        ldif_content = f"dn: {info['dn']}\nchangetype: modify\nadd: {key}\n{key}: {value}"

        ldif_file_name_stdout = self.connector.sudo_run(
            f"mktemp /tmp/post.XXXXXX",
            passwd=self.sudo_passwd
        )
        ldif_file_name = ldif_file_name_stdout.read().decode()

        ldif_file_write_stdout = self.connector.sudo_run(
            f"echo '{ldif_content}' > {ldif_file_name}",
            passwd=self.sudo_passwd
        )
        _ = ldif_file_write_stdout.read().decode()

        add_command = f"ldapmodify -x -D 'cn=Administrator,cn=Users,{self.dash_b(upper=True)}'" \
                      f" -w '{ad_passwd_to_use}' " \
                      f"-H ldaps://{self.get_realm()} -f {ldif_file_name}"
        add_stdout = self.connector.sudo_run(add_command, passwd=self.sudo_passwd)
        _ = add_stdout.read().decode()

        delete_temp_file_stdout = self.connector.sudo_run(f"rm {ldif_file_name}", passwd=self.sudo_passwd)
        _ = delete_temp_file_stdout.read().decode()

        if key not in self.info(gpo):
            raise ValueError("Couldn't add the given key/value")

    def ldap_edit(self, gpo: str, key: str, value: str, ad_passwd: Optional[str] = None) -> None:

        ad_passwd_to_use = self.__password_check(ad_passwd)

        info = self.info(gpo)
        if key not in info.keys():
            raise NotFound("The given key does not exist. Use add.")

        ldif_content = f"dn: {info['dn']}\nchangetype: modify\nreplace: {key}\n{key}: {value}"

        ldif_file_name_stdout = self.connector.sudo_run(
            f"mktemp /tmp/post.XXXXXX",
            passwd=self.sudo_passwd
        )
        ldif_file_name = ldif_file_name_stdout.read().decode()

        ldif_file_write_stdout = self.connector.sudo_run(
            f"echo '{ldif_content}' > {ldif_file_name}",
            passwd=self.sudo_passwd
        )
        _ = ldif_file_write_stdout.read().decode()

        add_command = f"ldapmodify -x -D 'cn=Administrator,cn=Users,{self.dash_b(upper=True)}'" \
                      f" -w '{ad_passwd_to_use}' " \
                      f"-H ldaps://{self.get_realm()} -f {ldif_file_name}"
        add_stdout = self.connector.sudo_run(add_command, passwd=self.sudo_passwd)
        _ = add_stdout.read().decode()

        delete_temp_file_stdout = self.connector.sudo_run(f"rm {ldif_file_name}", passwd=self.sudo_passwd)
        _ = delete_temp_file_stdout.read().decode()

    def ldap_delete(self, gpo: str, key: str, ad_passwd: Optional[str] = None) -> None:

        ad_passwd_to_use = self.__password_check(ad_passwd)

        info = self.info(gpo)
        if key not in info.keys():
            raise NotFound("The given key does not exist. Consider it deleted")

        ldif_content = f"dn: {info['dn']}\nchangetype: modify\ndelete: {key}"

        ldif_file_name_stdout = self.connector.sudo_run(
            f"mktemp /tmp/post.XXXXXX",
            passwd=self.sudo_passwd
        )
        ldif_file_name = ldif_file_name_stdout.read().decode()

        ldif_file_write_stdout = self.connector.sudo_run(
            f"echo '{ldif_content}' > {ldif_file_name}",
            passwd=self.sudo_passwd
        )
        _ = ldif_file_write_stdout.read().decode()

        add_command = f"ldapmodify -x -D 'cn=Administrator,cn=Users,{self.dash_b(upper=True)}'" \
                      f" -w '{ad_passwd_to_use}' " \
                      f"-H ldaps://{self.get_realm()} -f {ldif_file_name}"
        add_stdout = self.connector.sudo_run(add_command, passwd=self.sudo_passwd)
        _ = add_stdout.read().decode()

        delete_temp_file_stdout = self.connector.sudo_run(f"rm {ldif_file_name}", passwd=self.sudo_passwd)
        _ = delete_temp_file_stdout.read().decode()

    def startup_script(self, gpo: str, script_path: str, parameters: str = "", ad_passwd: Optional[str] = None):
        root_dir = f"/var/lib/samba/sysvol/{self.get_realm()}/Policies/{gpo}"

        dir_exist_stdout = self.connector.sudo_run(
            f"ls {root_dir} &>/dev/null && echo 1 || echo 0",
            passwd=self.sudo_passwd
        )
        dir_exist_output = dir_exist_stdout.read().decode().strip()

        if dir_exist_output == "0":
            raise NotFound("GPO Path does not exist. Maybe GPO does not exist?")

        scripts_dir = f"{root_dir}/Machine/Scripts"
        startup_dir = f"{scripts_dir}/Startup"
        psscripts_file = f"{scripts_dir}/psscripts.ini"
        script_file_name = random_filename()

        with open(script_path, "r") as script_2_read:
            info = self.info(gpo)

            psscripts = Config(self.connector, psscripts_file, create=True, backup=False)

            if "Startup" in psscripts.keys():
                orders = [int(each[0]) for each in psscripts.get("Startup").keys()]
                if len(orders) != len(set(orders)) * 2:
                    raise NumberOfElementsError("Looks like you psscripts file is incorrect")

                order = max(orders) + 1
                current = psscripts["Startup"]
                current.update({f"{order}CmdLine": f"{script_file_name}", f"{order}Parameters": f"{parameters}"})
                psscripts["Startup"] = current
            else:
                psscripts["Startup"] = {f"0CmdLine": f"{script_file_name}", f"0Parameters": f"{parameters}"}

            script = ConfigRaw(self.connector, f"{startup_dir}/{script_file_name}", create=True, backup=False)
            script.data = script_2_read.read()

            chmod_stdout = self.connector.sudo_run(
                f"chmod -R 770 {root_dir}",
                passwd=self.sudo_passwd
            )
            _ = chmod_stdout.read().decode().strip()

            try:
                self.ldap_add(
                    gpo,
                    "gPCMachineExtensionNames",
                    "[{42B5FAAE-6536-11D2-AE5A-0000F87571E3}{40B6664F-4972-11D1-A7CA-0000F87571E3}]",
                    ad_passwd
                )
            except AlreadyExist as e:
                self.logger.warning(e)

            version_number = info["versionNumber"]
            self.ldap_edit(gpo, "versionNumber", str(int(version_number) + 1), ad_passwd)

    def script(self, gpo: str, script_path: str, to: Literal["user", "machine"],
               on: Literal["startup", "shutdown", "login", "logoff"], ad_passwd: Optional[str] = None):
        pass
