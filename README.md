# POST

POST (Pardus Orchestration SysTem) is a python package used for orchestrate a low level system fleet.

It has almost no dependency on client side. The only needed thing is an `ssh` server and a sudo user to connect to the
client.

## Motivation
Why didn't we use ansible? There are 2 main reasons:

1. Ansible would be an overkill for such a simple needed.
2. Ansible is OS dependent. 

## Install
This project can be installed via `pip`.

Either clone or download the project. Change directory to the project and pip install it.

```bash
git clone THIS_URL

cd post

pip install .
```


## Example:

### Connection:

Creating an ssh connection.

```python
from post import SSHConnector

ssh_connection = SSHConnector("address", 22, "username", "password")

```

### Services:

Service object creation.

```python
from post import SSHConnector, Service

ssh_connection = SSHConnector("address", 22, "username", "password")
services = Service(ssh_connection)

# or
services_ = Service.from_ssh_connector("address", 22, "username", "password")

```

### Config:

Config object creation.

```python
from post import SSHConnector, Config

ssh_connection = SSHConnector("address", 22, "username", "password")
config = Config(ssh_connection, "/etc/samba/smb.conf")

# or
config_ = Config.from_ssh_connector("address", 22, "username", "password", "/etc/samba/smb.conf")

```

### Apt:

Apt object creation.

```python
from post import SSHConnector, Apt

ssh_connection = SSHConnector("address", 22, "username", "password")
apt = Apt(ssh_connection)

# or
apt_ = Apt.from_ssh_connector("address", 22, "username", "password")
```
