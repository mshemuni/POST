import json
from logging import getLogger, DEBUG, FileHandler, Formatter, Logger
from pathlib import Path
from time import time
from typing import Tuple

from post import Apt, SSHConnector, ConfigRaw, Service, LocalConnector
from post.utils.error import NotFound

from flask import Flask, jsonify, request, Response
from flasgger import Swagger

import argparse

app = Flask("POST")

app.config['SWAGGER'] = {
    'title': 'Pardus Orchestration SysTem',
    'uiversion': 3,
    'description': 'POST (Pardus Orchestration SysTem) is a python package used for orchestrate a low level system fleet.'
                   '<br><a href="https://github.com/mshemuni/POST/">https://github.com/mshemuni/POST/</a>',
    'version': '0.0.1B',
    'tos': 'asd'
}
swagger = Swagger(app)

def to_lower(text: str) -> str:
    return text.lower()

def to_upper(text: str) -> str:
    return text.upper()

def create_logger() -> Tuple[Logger, Path]:
    """Create a logger with a file named using the current Unix timestamp."""
    unix_time = int(time())
    directory = Path("./logs/")

    if not directory.exists():
        directory.mkdir()

    log_filename = directory / f"post_logger_{unix_time}.log"

    logger = getLogger(str(unix_time))
    logger.setLevel(DEBUG)

    file_handler = FileHandler(log_filename)
    file_handler.setLevel(DEBUG)

    formatter = Formatter("[%(asctime)s, %(levelname)s], [%(filename)s, %(funcName)s, %(lineno)s]: %(message)s")
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger, log_filename

def purge_samba(connector: SSHConnector) -> None:
    """
    Purges all packages installed on join

    Args:
        connector: A connector.
    """
    connector.logger.info("Uninstalling Samba")

    packages = ["winbind", "samba", "samba-common-bin", "krb5-user",
                "sssd", "sssd-tools", "realmd", "adcli", "ntpsec-ntpdate"]

    apt = Apt(connector)
    try:
        apt.purge(packages)
    except NotFound:
        connector.logger.error("Looks like samba is already not installed")

    installed_apts = apt.list(installed=True)
    installed_apts_name = [each_installed_apt.get("package", None) for each_installed_apt in installed_apts]

    if not all([each_package not in installed_apts_name for each_package in packages]):
        connector.logger.error("Cannot uninstall samba packages")
        raise Exception("Cannot uninstall samba packages")

    apt.auto_remove()


def disable_services(connector: SSHConnector) -> None:
    """
    Disables services enabled by joining

    Args:
        connector:  A connector.
    """
    connector.logger.info(f"Restarting services")
    services = ["winbind"]
    service = Service(connector)
    for serv in services:
        try:
            service.stop(serv)
            service.disable(serv)
        except Exception as e:
            connector.logger.warning(e)


def install_samba(connector: SSHConnector) -> None:
    """
    Installs everything needed to join to an AD as either DC or MEMBER

    Args:
        connector:  A connector.
    """
    connector.logger.info("Installing Samba")

    packages = ["winbind", "samba", "samba-common-bin", "krb5-user",
                "sssd", "sssd-tools", "realmd", "adcli", "ntpsec-ntpdate"]

    apt = Apt(connector)
    try:
        apt.install(packages)
    except NotFound:
        connector.logger.error("Looks like samba is already installed")

    installed_apts = apt.list(installed=True)
    installed_apts_name = [each_installed_apt.get("package", None) for each_installed_apt in installed_apts]

    if not all([each_package in installed_apts_name for each_package in packages]):
        connector.logger.error("Cannot install samba packages")
        raise Exception("Cannot install samba packages")


def ensure_realm(connector: SSHConnector, realm: str) -> None:
    """
    Ensures the realm exists. If not raises an error so the code won't resume

    Args:
        connector:  A connector.
        realm: the realm. It must be discoverable by machine pointed by connector.
    """
    connector.logger.info(f"Ensuring Realm: {realm} exists")

    output = connector.sudo_run(f"realm discover {realm} &>/dev/null && echo 1 || echo 0")
    if output.read().decode().strip() == "0":
        connector.logger.error(f"Realm {realm} is not reachable. Check the file /etc/resolv.conf")
        raise ValueError(f"Realm {realm} is not reachable. Check the file /etc/resolv.conf")


def set_hostname(connector: SSHConnector, hostname: str, force: bool = False) -> str:
    """
    Sets host name on machine pointed by connector. Returns the hostname

    Args:
        connector:  A connector.
        hostname: hostname
        force: Force change it even if the hostname already is set

    Returns:
        str: hostname

    """
    connector.logger.info(f"Setting hostname to {hostname}")

    current_hostname = connector.run("hostname").read().decode().strip()
    if current_hostname:
        connector.logger.warning("Already set hostname")

        if current_hostname == hostname:
            connector.logger.warning("Current and set hostname is the same. Skipping...")
            return current_hostname

        if not force:
            connector.logger.error("Wont force set hostname")
            return current_hostname

    output = connector.sudo_run("cp /etc/hosts /etc/hosts.bak")
    _ = output.read().decode().strip()

    output = connector.sudo_run(
        f"hostnamectl set-hostname {hostname}; grep -q '^127\.0\.1\.1' /etc/hosts && sed -i "
        f"'/^127\.0\.1\.1/c\\127.0.1.1 {hostname}' /etc/hosts || echo '127.0.1.1 {hostname}' | tee -a /etc/hosts",
    )
    _ = output.read().decode().strip()

    return hostname


def synchronize_time(connector: SSHConnector, realm: str) -> None:
    """
    synchronizes the time on the machine pointed by connector with the machine on realm

    Args:
        connector: A connector.
        realm: The realm
    """
    connector.logger.info(f"synchronizing the time with the server")

    command = f"ntpdate -u {to_lower(realm)} &>/dev/null && echo 1 || echo 0"
    output = connector.sudo_run(command)
    _ = output.read().decode().strip()
    if output.read().decode().strip() == "0":
        connector.logger.error(f"Cannot update the time to {realm}")
        raise ValueError(f"Cannot update the time to {realm}")


def kerberos_configuration(connector: SSHConnector, realm: str) -> None:
    """
    Creates the krb5.conf file on the machine pointed by connector

    Args:
        connector: A connector
        realm: the realm

    Returns:

    """
    connector.logger.info(f"Setting kerberos configuration")

    connector.sudo_run("cp /etc/krb5.conf /etc/krb5.conf.bak")

    server_s_name_command = connector.sudo_run(f"samba-tool domain info {realm}|grep 'DC name'|cut -d':' -f2")
    server_s_name = server_s_name_command.read().decode().strip().lower()

    config = ConfigRaw(connector, "/etc/krb5.conf", create=True, backup=True)
    config.data = f"""[libdefaults]
    default_realm = {to_upper(realm)}
    default_tkt_enctypes = des3-hmac-sha1 des-cbc-crc
    default_tgs_enctypes = des3-hmac-sha1 des-cbc-crc
    dns_lookup_kdc = true
    dns_lookup_realm = false

[realms]
    NIAEI.PRD = {{
        kdc = {to_lower(server_s_name)}
        admin_server = {to_lower(server_s_name)}
        master_kdc = {to_lower(server_s_name)}
        default_domain = {to_lower(realm)}
    }}

[domain_realm]
    .{to_lower(realm)} = {to_upper(realm)}
    {to_lower(realm)} = {to_upper(realm)}

[logging]
    kdc = SYSLOG:DEBUG
    admin_server = FILE=/var/log/kadm5.log
"""


def samba_configuration(connector: SSHConnector) -> None:
    """
    Backups the samba configuration

    Args:
        connector: A connector
    """
    connector.logger.info(f"Setting samba configuration")
    connector.sudo_run("mv /etc/samba/smb.conf /etc/samba/smb.conf.bak")


def join_ad(connector: SSHConnector, realm: str, password: str, secondary: bool = False) -> None:
    """
    Joins the AD

    Args:
        connector: A connector
        realm: the realm
        password: password for Administrator of AD
        secondary: Is the machine pointed by the connector a DC or MEMBER
    """
    connector.logger.info(f"Joining Active Directory")

    membership = "MEMBER"
    if secondary:
        membership = "DC"

    command = (
        f"samba-tool domain join {realm} {membership} -U Administrator --password='{password}' &>/dev/null && echo 1 || echo 0")
    output = connector.sudo_run(command)
    if output.read().decode().strip() == "0":
        raise Exception("Cannot join AD")


def restart_services(connector: SSHConnector):
    """
    Restarts the winbind service

    Args:
        connector: A connector
    """
    connector.logger.info(f"Restarting services")
    command = "sudo systemctl restart smbd nmbd winbind"
    output = connector.sudo_run(command)
    connector.logger.info(output.read().decode())
    services = ["winbind"]
    service = Service(connector)
    for serv in services:
        try:
            service.restart(serv)
        except Exception as e:
            connector.logger.warning(e)


def test_join_as_member(connector: SSHConnector):
    """
    Tests if the machine pointed by the connector did join as a MEMBER or not. Prints `wbinfo --ping-dc`s output

    Args:
        connector: A connector
    """
    connector.logger.info(f"Testing the join as a MEMBER")

    command = "wbinfo --ping-dc"
    output = connector.sudo_run(command)
    connector.logger.info(output.read().decode())


def test_join_as_server(connector: SSHConnector, realm: str, ad_admin_password: str):
    """
    Tests if the machine pointed by the connector did join as a DC or not.
    Prints `samba-tool user list` and `ldapsearch ***`s output

    Args:
        connector: A connector
        realm: the realm
        ad_admin_password: AD's administrator password
    """
    connector.logger.info(f"Testing the join as a DC")

    command = "samba-tool user list"
    output = connector.sudo_run(command)
    connector.logger.info(output.read().decode())

    dash_b = ",".join([f"dc={each}" for each in realm.split(".")])
    command2 = f"ldapsearch -H ldap://{to_lower(realm)} -D 'administrator@{to_lower(realm)}' -w {ad_admin_password} -b '{dash_b}' '(objectClass=user)'"
    output2 = connector.sudo_run(command2)
    connector.logger.info(output2.read().decode())


def remove_secrets(connector: SSHConnector):
    """
    Removes secret files in samba private. Connecting as a DC after demoting as a MEMBER would result on an error.
    So this files must be checked and removed if trying to connect as a DC

    Args:
        connector: A connector
    """
    connector.logger.info("Removing secrets")
    connector.sudo_run("rm -f /var/lib/samba/private/secrets.ldb")
    connector.sudo_run("rm -f /var/lib/samba/private/secrets.tdb")

@app.route('/', methods=['DELETE', 'POST'])
def serve() -> Tuple[Response, int]:
    """
        Join a samba to and AD either as MEMBER or DC or demote the member
        ---
        tags:
          - All
        post:
          description: Join a Pardus Machine to an AD.
          parameters:
            - data: json
              in: body
              type: string
              required: true
              example: '{"run_mode": "remote", "address": "192.168.1.1", "port": 22, "user": "pardus", "passwd": "password", "uninstall": true}'
          responses:
            200:
              description: Joined
        delete:
          description: Demotes the Pardus Machine from an AD
          parameters:
            - data: json
              in: body
              type: string
              required: true
              example: '{"run_mode": "remote", "address": "192.168.1.1", "port": 22, "user": "pardus", "passwd": "password", "uninstall": true}'
          responses:
            200:
              description: Demotes the machine
        """

    logger, logger_file = create_logger()

    data = request.get_json()
    logger.info(json.dumps(data))
    run_mode = data.get("run_mode", None)

    if run_mode is None:
        logger.error("Run mode is required")
        return jsonify({"status": "error", "message": "Run mode is required"}), 400

    passwd = data.get("passwd", None)

    if run_mode.lower() == "local":
        if passwd is None:
            logger.error("passwd is required")
            return jsonify({"status": "error", "message": "passwd is required"}), 400

        connector = LocalConnector(passwd, logger=logger)

    elif run_mode.lower() == "remote":
        address = data.get("address", None)
        port = data.get("port", 22)
        user = data.get("user", None)

        if address is None:
            logger.error("address is required since run mode is remote")
            return jsonify({"status": "error", "message": "address is required since run mode is remote"}), 400

        if user is None:
            logger.error("user is required since run mode is remote")
            return jsonify({"status": "error", "message": "user is required since run mode is remote"}), 400

        if passwd is None:
            logger.error("passwd is required")
            return jsonify({"status": "error", "message": "passwd is required"}), 400

        connector = SSHConnector(address, port, user, passwd, logger=logger)
    else:
        logger.error("Run mode must be either local or remote")
        return jsonify({"status": "error", "message": "Run mode must be either local or remote"}), 400

    ad_admin_password = data.get("adAdminPassword", None)

    if request.method == 'POST':
        realm = data.get("realm", None)
        hostname = data.get("hostname", None)
        server = data.get("server", False)

        if realm is None:
            logger.error("realm is required to join")
            return jsonify({"status": "error", "message": "realm is required"}), 400

        if hostname is None:
            logger.error("hostname is required to join")
            return jsonify({"status": "error", "message": "hostname is required"}), 400

        if passwd is None:
            logger.error("AD's Administrator password is required to join")
            return jsonify({"status": "error", "message": "AD's Administrator password is required"}), 400
        try:
            join(connector, realm, hostname, ad_admin_password, server)
        except Exception as e:
            logger.error(e)
            return jsonify({"status": "error", "message": "e"}), 400

        return jsonify({"status": "success", "message": "Joining started", "logger": f"{logger_file}"}), 200

    elif request.method == 'DELETE':
        uninstall = data.get("uninstall", False)

        if passwd is None:
            logger.error("AD's Administrator password is required to leave")
            return jsonify({"error": "AD's Administrator password is required"}), 400
        try:
            leave(connector, ad_admin_password, uninstall)
        except Exception as e:
            logger.error(e)
            return jsonify({"status": "error", "message": "e"}), 400

        return jsonify({"status": "success", "message": "Demoting started", "logger": f"{logger_file}"}), 200

    logger.warning("Nothing to do")
    return jsonify({"status": "error", "message": "Nothing to do"}), 200


def join(connector: SSHConnector, realm: str, hostname: str, ad_admin_password: str, secondary: bool = False) -> None:
    """
    Runs a needed functions to join  an AD either as a MEMBER or DC

    Args:
        connector: A connector
        realm: the realm
        hostname: hostname of the machine pointed by the connector
        ad_admin_password: AD's administrator password
        secondary: is the machine pointed by connector a DC, otherwise it's a MEMBER
    """
    install_samba(connector)
    ensure_realm(connector, realm)
    _ = set_hostname(connector, hostname, force=True)
    synchronize_time(connector, realm)
    kerberos_configuration(connector, realm)
    samba_configuration(connector)

    if secondary:
        remove_secrets(connector)

    join_ad(connector, realm, ad_admin_password, secondary=secondary)
    restart_services(connector)

    if secondary:
        test_join_as_server(connector, realm, ad_admin_password)

    else:
        test_join_as_member(connector)


def leave(connector: SSHConnector, ad_admin_password: str, uninstall: bool):
    """
    Demotes the machine pointed by the connector.

    Args:
        connector: A connector
        ad_admin_password: AD's administrator password
        uninstall: Uninstall the packages installed by join. Otherwise, leave them

    Returns:

    """
    command = f"samba-tool domain demote -UAdministrator --password='{ad_admin_password} &>/dev/null && echo 1 || echo 0"
    output = connector.sudo_run(command)
    if output.read().decode().strip() == "0":
        raise Exception("Cannot leave domain")

    disable_services(connector)
    if uninstall:
        purge_samba(connector)


def main():
    parser = argparse.ArgumentParser(description="Package manager CLI with install and uninstall commands.")
    subparsers = parser.add_subparsers(title="commands", dest="command", help="Available commands")
    subparsers.required = True

    local_parser = subparsers.add_parser("local", help="Local operations")
    local_subparsers = local_parser.add_subparsers(dest='action', required=True)
    local_join_parser = local_subparsers.add_parser("join", help="Join locally")
    local_leave_parser = local_subparsers.add_parser("leave", help="Leave locally")

    local_join_parser.add_argument("passwd", type=str, help="Password of current user (must be sudo)")
    local_join_parser.add_argument("adAdminPassword", type=str, help="The Admin password of the Active Directory")
    local_join_parser.add_argument("realm", type=str, help="The realm that samba is going to join.")
    local_join_parser.add_argument("hostname", type=str, help="The hostname of the samba machine that going to join")
    local_join_parser.add_argument("--server", "-s", action="store_true", help="Join as member server/secondary domain")

    local_leave_parser.add_argument("passwd", type=str, help="Password of current user (must be sudo)")
    local_leave_parser.add_argument("adAdminPassword", type=str, help="The Admin password of the Active Directory")
    local_leave_parser.add_argument("--uninstall", "-u", action="store_true", default=False,
                                    help="Also uninstall packages installed by join")

    remote_parser = subparsers.add_parser("remote", help="Remote operations")
    remote_subparsers = remote_parser.add_subparsers(dest='action', required=True)
    remote_join_parser = remote_subparsers.add_parser("join", help="Join remotely")
    remote_leave_parser = remote_subparsers.add_parser("leave", help="Leave remotely")

    remote_join_parser.add_argument("address", type=str, help="Address of samba server")
    remote_join_parser.add_argument("port", type=int, help="Port of samba server")
    remote_join_parser.add_argument("user", type=str, help="Port of samba server")
    remote_join_parser.add_argument("passwd", type=str, help="Password of current user (must be sudo)")
    remote_join_parser.add_argument("adAdminPassword", type=str, help="The Admin password of the Active Directory")
    remote_join_parser.add_argument("realm", type=str, help="The realm that samba is going to join.")
    remote_join_parser.add_argument("hostname", type=str, help="The hostname of the samba machine that going to join")
    remote_join_parser.add_argument("--server", "-s", action="store_true",
                                    help="Join as member server/secondary domain")

    remote_leave_parser.add_argument("address", type=str, help="Address of samba server")
    remote_leave_parser.add_argument("port", type=int, help="Port of samba server")
    remote_leave_parser.add_argument("user", type=str, help="Port of samba server")
    remote_leave_parser.add_argument("passwd", type=str, help="Password of current user (must be sudo)")
    remote_leave_parser.add_argument("adAdminPassword", type=str, help="The Admin password of the Active Directory")
    remote_leave_parser.add_argument("--uninstall", "-u", action="store_true", default=False,
                                     help="Also uninstall packages installed by join")

    server_parser = subparsers.add_parser("serve", help="Run a server")
    server_parser.add_argument("--port", type=int, default=5000, help="A port for flask server")

    args = parser.parse_args()

    if args.command.lower() == "local":
        connector = LocalConnector(args.passwd)
    elif args.command.lower() == "remote":
        connector = SSHConnector(args.address, args.port, args.user, args.passwd)
    elif args.command.lower() == "serve":
        app.run(debug=True, port=args.port)
        return
    else:
        raise ValueError("Unknown host")

    if args.action.lower() == "join":
        join(connector, args.realm, args.hostname, args.adAdminPassword, args.server)
    elif args.action.lower() == "leave":
        leave(connector, args.adAdminPassword, args.uninstall)
    else:
        raise ValueError("Unknown Operation")


if __name__ == "__main__":
    main()
