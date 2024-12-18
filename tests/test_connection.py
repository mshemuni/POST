import unittest

from post import SSHConnector


class TestConnection(unittest.TestCase):
    def setUp(self):
        self.CONNECTION = SSHConnector("172.16.102.16", 22, "pardus", "landofcanaan")

    def test_run(self):
        self.assertIn(
            self.CONNECTION.run("id -u").read().decode().strip(),
            "1000",
        )

    def test_sudo_run(self):
        self.assertIn(
            self.CONNECTION.sudo_run("id -u").read().decode().strip(),
            "0",
        )


if __name__ == "__main__":
    unittest.main()
