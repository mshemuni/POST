import time

from PyQt6 import QtWidgets, QtCore, QtGui

from post import Apt
from post.gui.apt import Ui_FormApt
from post.gui.package_info_main import ShowPackageMainForm


def package_arranger(ip_packages):
    result = {}
    try:
        for ip, packages in ip_packages.items():
            for package in packages:
                try:
                    package_name = package["package"]
                    package_details = {
                        key: value for key, value in package.items() if key != "package"
                    }

                    if package_name not in result:
                        result[package_name] = {}

                    result[package_name][ip] = package_details
                except Exception as e:
                    print(e)
    except Exception as e:
        print(e)

    return result


class AptMainForm(QtWidgets.QWidget, Ui_FormApt):
    def __init__(self, parent):
        super(AptMainForm, self).__init__(parent)
        self.setupUi(self)

        self.the_parent = parent

        self.the_parent.logger.info("Apt window loaded")

        self.pushButtonRefresh.clicked.connect(self.load)
        self.lineEditSearch.textChanged.connect(self.search)

        self.pushButtonPrevious.clicked.connect(self.previous_page)
        self.pushButtonNext.clicked.connect(self.next_page)

        self.treeWidgetPackages.setContextMenuPolicy(
            QtCore.Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.treeWidgetPackages.customContextMenuRequested.connect(
            self.tree_show_context_menu
        )

        self.items_per_page = 100
        self.current_page = 0
        self.data = {}
        self.keys = []
        self.filtered_keys = self.keys
        self.total_pages = (
            len(self.data) + self.items_per_page - 1
        ) // self.items_per_page

        self.load()
        self.search()

    def tree_show_context_menu(self, position):
        menu = QtWidgets.QMenu()

        selected = self.treeWidgetPackages.selectedItems()

        install = menu.addAction("Install", lambda: self.install())
        remove = menu.addAction("Remove", lambda: self.remove())
        reinstall = menu.addAction("Reinstall", lambda: self.reinstall())
        upgrade = menu.addAction("Upgrade", lambda: self.upgrade())
        purge = menu.addAction("Purge", lambda: self.purge())
        show_package = menu.addAction("Show Package ...", lambda: self.show_package())

        if len(selected) == 0:
            install.setEnabled(False)
            remove.setEnabled(False)
            reinstall.setEnabled(False)
            upgrade.setEnabled(False)
            purge.setEnabled(False)
            show_package.setEnabled(False)

        menu.addSeparator()
        menu_expand = menu.addAction(
            "Expand All", lambda: self.treeWidgetPackages.expandAll()
        )
        menu_collapse = menu.addAction(
            "Collapse All", lambda: self.treeWidgetPackages.collapseAll()
        )

        if self.treeWidgetPackages.topLevelItemCount() == 0:
            menu_expand.setEnabled(False)
            menu_collapse.setEnabled(False)

        menu.exec(self.treeWidgetPackages.mapToGlobal(position))

    def show_package(self):
        package = self.treeWidgetPackages.selectedItems()[0].text(0)
        if not package:
            self.the_parent.logger.warning("Nothing to do")
            self.the_parent.gui_functions.warning("Nothing to do")
            return

        data = {}

        items = self.the_parent.gui_functions.get_items_tree(self.the_parent.treeWidget)
        for it, item in enumerate(items, start=1):
            try:
                data[item.connection] = Apt(item.connection).show(package)
                self.progressBar.setValue(int(100 * it / len(items)))
                QtCore.QCoreApplication.processEvents()
            except Exception as e:
                self.the_parent.logger.warning(e)

        self.the_parent.show_window(ShowPackageMainForm(self.the_parent, data))

    def purge(self):
        package = self.treeWidgetPackages.selectedItems()[0].text(0)
        if not package:
            self.the_parent.logger.warning("Nothing to do")
            self.the_parent.gui_functions.warning("Nothing to do")
            return

        items = self.the_parent.gui_functions.get_items_tree(self.the_parent.treeWidget)
        for it, item in enumerate(items, start=1):
            try:
                Apt(item.connection).remove(package)
                self.progressBar.setValue(int(100 * it / len(items)) - 1)
                QtCore.QCoreApplication.processEvents()
            except Exception as e:
                self.the_parent.logger.warning(e)

        time.sleep(10)
        self.progressBar.setValue(100)
        self.load()
        self.search()

    def reinstall(self):
        package = self.treeWidgetPackages.selectedItems()[0].text(0)
        if not package:
            self.the_parent.logger.warning("Nothing to do")
            self.the_parent.gui_functions.warning("Nothing to do")
            return

        items = self.the_parent.gui_functions.get_items_tree(self.the_parent.treeWidget)
        for it, item in enumerate(items, start=1):
            try:
                Apt(item.connection).remove(package)
                self.progressBar.setValue(int(100 * it / len(items)) - 1)
                QtCore.QCoreApplication.processEvents()
            except Exception as e:
                self.the_parent.logger.warning(e)

        time.sleep(10)
        self.progressBar.setValue(100)
        self.load()
        self.search()

    def remove(self):
        package = self.treeWidgetPackages.selectedItems()[0].text(0)
        if not package:
            self.the_parent.logger.warning("Nothing to do")
            self.the_parent.gui_functions.warning("Nothing to do")
            return

        is_user_sure = self.the_parent.gui_functions.ask(
            f"Are you sure you want to remove {package} from all machines?"
        )
        if not is_user_sure:
            self.the_parent.logger.warning("User canceled")
            return

        items = self.the_parent.gui_functions.get_items_tree(self.the_parent.treeWidget)
        for it, item in enumerate(items, start=1):
            try:
                Apt(item.connection).remove(package)
                self.progressBar.setValue(int(100 * it / len(items)) - 1)
                QtCore.QCoreApplication.processEvents()
            except Exception as e:
                self.the_parent.logger.warning(e)

        time.sleep(10)
        self.progressBar.setValue(100)
        self.load()
        self.search()

    def install(self):
        package = self.treeWidgetPackages.selectedItems()[0].text(0)
        if not package:
            self.the_parent.logger.warning("Nothing to do")
            self.the_parent.gui_functions.warning("Nothing to do")
            return

        items = self.the_parent.gui_functions.get_items_tree(self.the_parent.treeWidget)
        for it, item in enumerate(items, start=1):
            try:
                Apt(item.connection).install(package)
                self.progressBar.setValue(int(100 * it / len(items)) - 1)
                QtCore.QCoreApplication.processEvents()
            except Exception as e:
                self.the_parent.logger.warning(e)

        time.sleep(10)
        self.progressBar.setValue(100)
        self.load()
        self.search()

    def upgrade(self):
        package = self.treeWidgetPackages.selectedItems()[0].text(0)
        if not package:
            self.the_parent.logger.warning("Nothing to do")
            self.the_parent.gui_functions.warning("Nothing to do")
            return

        items = self.the_parent.gui_functions.get_items_tree(self.the_parent.treeWidget)
        for it, item in enumerate(items, start=1):
            try:
                Apt(item.connection).upgrade(package)
                self.progressBar.setValue(int(100 * it / len(items)) - 1)
                QtCore.QCoreApplication.processEvents()
            except Exception as e:
                self.the_parent.logger.warning(e)

        time.sleep(10)
        self.progressBar.setValue(100)
        self.load()
        self.search()

    def load(self):
        machine_package = {}
        items = self.the_parent.gui_functions.get_items_tree(self.the_parent.treeWidget)
        for it, item in enumerate(items, start=1):
            the_list = Apt(item.connection).list()
            machine_package[f"{item.connection.user}@{item.connection.address}"] = (
                the_list
            )

        self.data = package_arranger(machine_package)
        self.keys = list(self.data.keys())
        self.total_pages = (
            len(self.data) + self.items_per_page - 1
        ) // self.items_per_page

    def update_page(self):
        self.treeWidgetPackages.clear()

        start_index = self.current_page * self.items_per_page
        end_index = start_index + self.items_per_page
        page_keys = self.filtered_keys[start_index:end_index]

        for package in page_keys:
            machine_and_properties = self.data[package]
            group_layer = QtWidgets.QTreeWidgetItem(self.treeWidgetPackages, [package])
            group_layer.setFirstColumnSpanned(True)
            for machine, properties in machine_and_properties.items():
                child = QtWidgets.QTreeWidgetItem(
                    group_layer,
                    [
                        machine,
                        properties["version"],
                        properties["tags"].__str__(),
                        properties["arch"],
                        properties["repo"],
                    ],
                )
                child.setFlags(child.flags() & ~QtCore.Qt.ItemFlag.ItemIsSelectable)
                if any(
                    item1 in item2
                    for item1 in ["installed", "upgradable"]
                    for item2 in properties["tags"]
                ):
                    for i in range(child.columnCount()):
                        child.setForeground(i, QtGui.QColor("#43A047"))
                        group_layer.setForeground(i, QtGui.QColor("#43A047"))
                    font = QtGui.QFont()
                    font.setBold(True)
                    group_layer.setFont(0, font)

        self.label.setText(f"{self.current_page + 1} of {self.total_pages}")

        self.pushButtonPrevious.setEnabled(self.current_page > 0)
        self.pushButtonNext.setEnabled(self.current_page < self.total_pages - 1)

    def previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_page()

    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.update_page()

    def search(self):
        query = self.lineEditSearch.text().strip().lower()

        if query:
            self.filtered_keys = [key for key in self.keys if query in key.lower()]
        else:
            self.filtered_keys = self.keys

        self.current_page = 0
        self.total_pages = (
            len(self.filtered_keys) + self.items_per_page - 1
        ) // self.items_per_page
        self.update_page()
