from post import Apt, SSHConnector, ConfigRaw, Service, LocalConnector


def create_gpo(connector: SSHConnector, name: str, password: str):
    connector.sudo_run(f"samba-tool gpo create {name} -U Administrator --password='{password}'")
