import time
import unittest
from unittest import skip

from post import Apt
from post.utils.error import NotFound


class TestApt(unittest.TestCase):

    def setUp(self):
        self.APT = Apt.from_ssh_connector("172.16.102.16", 22, "pardus", "landofcanaan")

    def test_repositories(self):
        self.assertIn(
            {
                "kind": "deb",
                "options": None,
                "url": "http://depo.pardus.org.tr/pardus",
                "distribution": "yirmiuc",
                "components": "main contrib non-free non-free-firmware",
            },
            self.APT.repositories(),
        )

    @skip("Cannot add a repository without key etc. we have to solve that first.")
    def test_add_repository(self):
        self.APT.add_repository(
            "deb https://dl.winehq.org/wine-builds/debian bookworm main"
        )

    def test_update(self):
        self.APT.update()

    def test_upgrade(self):
        self.assertTrue(True)

    def test_list(self):
        self.assertIn(
            {
                "package": "apt",
                "repo": "yirmiuc-deb,now",
                "version": "2.6.1",
                "arch": "amd64",
                "tags": ["installed"],
            },
            self.APT.list(),
        )

    def test_install(self):
        self.APT.install("dstat")
        time.sleep(10)
        self.assertIn(
            {
                "package": "dstat",
                "repo": "yirmiuc-deb,now",
                "version": "0.7.4-6.1",
                "arch": "all",
                "tags": ["installed"],
            },
            self.APT.list(),
        )

        self.APT.purge("dstat")
        time.sleep(10)

        self.assertNotIn(
            {
                "package": "dstat",
                "repo": "yirmiuc-deb,now",
                "version": "0.7.4-6.1",
                "arch": "all",
                "tags": ["installed"],
            },
            self.APT.list(),
        )

    def test_install_wrong_name(self):
        with self.assertRaises(NotFound):
            self.APT.install("MOHAMMAD")

    def test_reinstall(self):
        self.APT.install("dstat")
        time.sleep(10)
        self.assertIn(
            {
                "package": "dstat",
                "repo": "yirmiuc-deb,now",
                "version": "0.7.4-6.1",
                "arch": "all",
                "tags": ["installed"],
            },
            self.APT.list(),
        )

        self.APT.reinstall("dstat")
        time.sleep(10)
        self.assertIn(
            {
                "package": "dstat",
                "repo": "yirmiuc-deb,now",
                "version": "0.7.4-6.1",
                "arch": "all",
                "tags": ["installed"],
            },
            self.APT.list(),
        )

        self.APT.purge("dstat")
        time.sleep(10)

        self.assertNotIn(
            {
                "package": "dstat",
                "repo": "yirmiuc-deb,now",
                "version": "0.7.4-6.1",
                "arch": "all",
                "tags": ["installed"],
            },
            self.APT.list(),
        )

    def test_reinstall_wrong_name(self):
        with self.assertRaises(NotFound):
            self.APT.reinstall("MOHAMMAD")

    def test_remove(self):
        self.APT.install("dstat")
        time.sleep(10)
        self.assertIn(
            {
                "package": "dstat",
                "repo": "yirmiuc-deb,now",
                "version": "0.7.4-6.1",
                "arch": "all",
                "tags": ["installed"],
            },
            self.APT.list(),
        )

        self.APT.remove("dstat")
        time.sleep(10)

        self.assertNotIn(
            {
                "package": "dstat",
                "repo": "yirmiuc-deb,now",
                "version": "0.7.4-6.1",
                "arch": "all",
                "tags": ["installed"],
            },
            self.APT.list(),
        )

    def test_remove_wrong_name(self):
        with self.assertRaises(NotFound):
            self.APT.remove("MOHAMMAD")

    def test_purge(self):
        self.APT.install("dstat")
        time.sleep(10)
        self.assertIn(
            {
                "package": "dstat",
                "repo": "yirmiuc-deb,now",
                "version": "0.7.4-6.1",
                "arch": "all",
                "tags": ["installed"],
            },
            self.APT.list(),
        )

        self.APT.purge("dstat")
        time.sleep(10)

        self.assertNotIn(
            {
                "package": "dstat",
                "repo": "yirmiuc-deb,now",
                "version": "0.7.4-6.1",
                "arch": "all",
                "tags": ["installed"],
            },
            self.APT.list(),
        )

    def test_purge_wrong_name(self):
        with self.assertRaises(NotFound):
            self.APT.purge("MOHAMMAD")

    def test_search(self):
        self.assertIn(
            {
                "name": "apt",
                "repo": "yirmiuc-deb,now",
                "version": "2.6.1",
                "architecture": "amd64",
                "description": "commandline package manager",
            },
            self.APT.search("apt"),
        )

    def test_search_wrong_name(self):
        self.assertEqual(len(self.APT.search("MOHAMMAD")), 0)

    def test_show(self):
        self.assertIsInstance(self.APT.show("dstat"), dict)

    def test_show_wrong_name(self):
        with self.assertRaises(NotFound):
            self.APT.show("MOHAMMAD")


if __name__ == "__main__":
    unittest.main()
