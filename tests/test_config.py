import unittest
import secrets

from post import Config


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.address = "172.16.102.16"
        self.port = 22
        self.user = "pardus"
        self.password = "landofcanaan"
        self.path = f"/tmp/{secrets.token_hex(8)}.conf"

    def test_create(self):
        config = Config.from_ssh_connector(
            self.address, self.port, self.user, self.password, self.path, create=True
        )
        self.assertNotEqual(
            config.connector.sudo_run(f"ls {self.path}").read().decode().strip(), ""
        )
        config.connector.sudo_run(f"rm {self.path}")

    def test_create_does_not_exist(self):
        with self.assertRaises(FileNotFoundError):
            _ = Config.from_ssh_connector(
                self.address, self.port, self.user, self.password, self.path
            )

    def test_clear(self):
        config = Config.from_ssh_connector(
            self.address, self.port, self.user, self.password, self.path, create=True
        )
        config["test"] = {"test": "test"}
        config.clear()
        self.assertEqual(
            config.connector.sudo_run(f"cat {self.path}").read().decode().strip(), ""
        )

        config.connector.sudo_run(f"rm {self.path}")

    def test_update(self):
        config = Config.from_ssh_connector(
            self.address, self.port, self.user, self.password, self.path, create=True
        )

        config["test"] = {"test": "test"}
        old_content = (
            config.connector.sudo_run(f"cat {self.path}").read().decode().strip()
        )

        config["test2"] = {"test": "test"}
        new_content = (
            config.connector.sudo_run(f"cat {self.path}").read().decode().strip()
        )

        self.assertNotEqual(old_content, new_content)

        config.connector.sudo_run(f"rm {self.path}")

    def test_create_backup(self):
        config = Config.from_ssh_connector(
            self.address,
            self.port,
            self.user,
            self.password,
            self.path,
            create=True,
            backup=True,
        )
        files = (
            config.connector.sudo_run(f"ls {self.path}*")
            .read()
            .decode()
            .strip()
            .split("\n")
        )
        self.assertEqual(len(files), 2)
        config_ = Config.from_ssh_connector(
            self.address,
            self.port,
            self.user,
            self.password,
            self.path,
            create=True,
            backup=True,
        )
        files_ = (
            config_.connector.sudo_run(f"ls {self.path}*")
            .read()
            .decode()
            .strip()
            .split("\n")
        )
        self.assertEqual(len(files_), 3)
        config.connector.sudo_run(f"rm {self.path}*")

    def test___delitem__(self):
        config = Config.from_ssh_connector(
            self.address, self.port, self.user, self.password, self.path, create=True
        )

        config["test"] = {"test": "test"}
        old_content = (
            config.connector.sudo_run(f"cat {self.path}").read().decode().strip()
        )

        config["test2"] = {"test": "test"}
        new_content = (
            config.connector.sudo_run(f"cat {self.path}").read().decode().strip()
        )
        self.assertNotEqual(old_content, new_content)

        del config["test2"]
        deleted_content = (
            config.connector.sudo_run(f"cat {self.path}").read().decode().strip()
        )
        self.assertEqual(old_content, deleted_content)

        config.connector.sudo_run(f"rm {self.path}")


if __name__ == "__main__":
    unittest.main()
