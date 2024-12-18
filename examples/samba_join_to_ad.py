from post import Apt, SSHConnector, ConfigRaw, Service, LocalConnector
from post.utils.error import NotFound

import argparse

def purge_samba(connector: SSHConnector):
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

def disable_services(connector: SSHConnector):
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
    connector.logger.info(f"Ensuring Realm: {realm} exists")

    output = connector.sudo_run(f"realm discover {realm} &>/dev/null && echo 1 || echo 0")
    if output.read().decode().strip() == "0":
        connector.logger.error(f"Realm {realm} is not reachable. Check the file /etc/resolv.conf")
        raise ValueError(f"Realm {realm} is not reachable. Check the file /etc/resolv.conf")


def set_hostname(connector: SSHConnector, hostname: str, force:bool=False) -> str:
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

def synchronize_time(connector: SSHConnector, realm:str):
    connector.logger.info(f"synchronizing the time with the server")

    command = f"ntpdate -u {realm.lower()} &>/dev/null && echo 1 || echo 0"
    print(command)
    output = connector.sudo_run(command)
    _ = output.read().decode().strip()
    if output.read().decode().strip() == "0":
        connector.logger.error(f"Cannot update the time to {realm}")
        raise ValueError(f"Cannot update the time to {realm}")


def kerberos_configuration(connector: SSHConnector, realm: str) -> None:
    connector.logger.info(f"Setting kerberos configuration")

    connector.sudo_run("cp /etc/krb5.conf /etc/krb5.conf.bak")

    server_s_name_command = connector.sudo_run(f"samba-tool domain info {realm}|grep 'DC name'|cut -d':' -f2")
    server_s_name = server_s_name_command.read().decode().strip().lower()

    config = ConfigRaw(connector, "/etc/krb5.conf", create=True, backup=True)
    config.data = f"""[libdefaults]
    default_realm = {realm.upper()}
    default_tkt_enctypes = des3-hmac-sha1 des-cbc-crc
    default_tgs_enctypes = des3-hmac-sha1 des-cbc-crc
    dns_lookup_kdc = true
    dns_lookup_realm = false

[realms]
    NIAEI.PRD = {{
        kdc = {server_s_name.lower()}
        admin_server = {server_s_name.lower()}
        master_kdc = {server_s_name.lower()}
        default_domain = {realm.lower()}
    }}

[domain_realm]
    .mit.edu = {realm.upper()}
    mit.edu = {realm.upper()}

[logging]
    kdc = SYSLOG:DEBUG
    admin_server = FILE=/var/log/kadm5.log
"""

#     config = ConfigRaw(connector, "/etc/krb5.conf", create=True, backup=True)
#     config.data = f"""[libdefaults]
# 	default_realm = {realm.upper()}
# 	dns_lookup_realm = false
# 	dns_lookup_kdc = true
#
# [plugins]
#        localauth = {{
#              module = winbind:/usr/lib64/samba/krb5/winbind_krb5_localauth.so
#              enable_only = winbind
#        }}
#
# [global]
#       krb5_auth = yes
#       krb5_ccache_type = FILE
#     """


def samba_configuration(connector: SSHConnector, realm: str) -> None:
    connector.logger.info(f"Setting samba configuration")
    connector.sudo_run("mv /etc/samba/smb.conf /etc/samba/smb.conf.bak")

def join_ad(connector: SSHConnector, realm: str, password: str, secondary:bool=False) -> None:
    connector.logger.info(f"Joining Active Directory")

    membership = "MEMBER"
    if secondary:
        membership = "DC"

    command = (f"samba-tool domain join {realm} {membership} -U Administrator --password='{password}' &>/dev/null && echo 1 || echo 0")
    output = connector.sudo_run(command)
    if output.read().decode().strip() == "0":
        raise Exception("Cannot join AD")

def restart_services(connector: SSHConnector):
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
    connector.logger.info(f"Testing the join as a member")

    command = "wbinfo --ping-dc"
    output = connector.sudo_run(command)
    connector.logger.info(output.read().decode())

def test_join_as_server(connector: SSHConnector, realm:str, ad_admin_password: str):
    connector.logger.info(f"Testing the join as a secondary")

    command = "samba-tool user list"
    output = connector.sudo_run(command)
    connector.logger.info(output.read().decode())

    dash_b = ",".join([f"dc={each}" for each in realm.split(".")])
    command2 = f"ldapsearch -H ldap://{realm.lower()} -D 'administrator@{realm.lower()}' -w {ad_admin_password} -b '{dash_b}' '(objectClass=user)'"
    output2 = connector.sudo_run(command2)
    connector.logger.info(output2.read().decode())

def remove_secrets(connector: SSHConnector):
    connector.logger.info("Removing secrets")
    connector.sudo_run("rm -f /var/lib/samba/private/secrets.ldb")
    connector.sudo_run("rm -f /var/lib/samba/private/secrets.tdb")


def join(connector: SSHConnector, realm: str, hostname: str, ad_admin_password: str, secondary: bool = False) -> None:
    install_samba(connector)
    ensure_realm(connector, realm)
    _ = set_hostname(connector, hostname, force=True)
    synchronize_time(connector, realm)
    kerberos_configuration(connector, realm)
    samba_configuration(connector, realm)

    if secondary:
        remove_secrets(connector)

    join_ad(connector, realm, ad_admin_password, secondary=secondary)
    restart_services(connector)

    if secondary:
        test_join_as_server(connector, realm, ad_admin_password)

    else:
        test_join_as_member(connector)

def leave(connector: SSHConnector, password: str, uninstall: bool):
    command = f"samba-tool domain demote -UAdministrator --password='{password} &>/dev/null && echo 1 || echo 0"
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
    remote_join_parser.add_argument("--server", "-s", action="store_true", help="Join as member server/secondary domain")

    remote_leave_parser.add_argument("address", type=str, help="Address of samba server")
    remote_leave_parser.add_argument("port", type=int, help="Port of samba server")
    remote_leave_parser.add_argument("user", type=str, help="Port of samba server")
    remote_leave_parser.add_argument("passwd", type=str, help="Password of current user (must be sudo)")
    remote_leave_parser.add_argument("adAdminPassword", type=str, help="The Admin password of the Active Directory")
    remote_leave_parser.add_argument("--uninstall", "-u", action="store_true", default=False,
                                     help="Also uninstall packages installed by join")

    args = parser.parse_args()

    if args.command.lower() == "local":
        connector = LocalConnector(args.passwd)
    elif args.command.lower() == "remote":
        connector = SSHConnector(args.address, args.port, args.user, args.passwd)
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
