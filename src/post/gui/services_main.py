from collections import defaultdict

from PyQt6 import QtWidgets, QtCore, QtGui

from post import Service
from post.gui.remote_logs_main import RemoteLogsMainForm
from post.gui.services import Ui_FormServices


def service_arranger(services):
    result = defaultdict(lambda: defaultdict(dict))

    for service, items in services.items():
        try:
            for item in items:
                name = item["unit"]
                for key, value in item.items():
                    if key != "unit":
                        result[name][service][key] = value
        except Exception as e:
            print(e)

    all_services = services.keys()
    all_keys = {
        k
        for items in services.values()
        for item in items
        for k in item.keys()
        if k != "unit"
    }

    for name, services in result.items():
        for service in all_services:
            if service not in services:
                result[name][service] = {key: "---" for key in all_keys}

    return {k: dict(v) for k, v in result.items()}


class ServicesMainForm(QtWidgets.QWidget, Ui_FormServices):
    def __init__(self, parent):
        super(ServicesMainForm, self).__init__(parent)
        self.setupUi(self)

        self.the_parent = parent

        self.the_parent.logger.info("Services window loaded")

        self.pushButtonRefresh.clicked.connect(self.refresh)
        self.lineEditSearch.textChanged.connect(self.search)

        self.treeWidgetServices.setContextMenuPolicy(
            QtCore.Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.treeWidgetServices.customContextMenuRequested.connect(
            self.tree_show_context_menu
        )

        self.refresh()

    def search(self):
        self.the_parent.logger.info("Searching")

        to_search = self.lineEditSearch.text()
        for item in range(self.treeWidgetServices.topLevelItemCount()):
            item = self.treeWidgetServices.topLevelItem(item)
            if to_search.lower() not in item.text(0).lower():
                item.setHidden(True)
            else:
                item.setHidden(False)

    def tree_show_context_menu(self, position):
        menu = QtWidgets.QMenu()

        selected = self.treeWidgetServices.selectedItems()

        start = menu.addAction("Start", lambda: self.service_start())
        stop = menu.addAction("Stop", lambda: self.service_stop())
        restart = menu.addAction("Restart", lambda: self.service_restart())
        enable = menu.addAction("Enable", lambda: self.service_enable())
        disable = menu.addAction("Disable", lambda: self.service_disable())
        logs = menu.addAction("Logs ...", lambda: self.service_logs())
        menu.addSeparator()
        menu_expand = menu.addAction(
            "Expand All", lambda: self.treeWidgetServices.expandAll()
        )
        menu_collapse = menu.addAction(
            "Collapse All", lambda: self.treeWidgetServices.collapseAll()
        )

        if self.treeWidgetServices.topLevelItemCount() == 0:
            menu_expand.setEnabled(False)
            menu_collapse.setEnabled(False)

        if len(selected) == 0:
            start.setEnabled(False)
            stop.setEnabled(False)
            restart.setEnabled(False)
            enable.setEnabled(False)
            disable.setEnabled(False)
            logs.setEnabled(False)

        menu.exec(self.treeWidgetServices.mapToGlobal(position))

    def service_logs(self):
        self.the_parent.logger.info("Showing logs")

        selected_items = self.treeWidgetServices.selectedItems()
        the_service = selected_items[0].text(0)
        the_logs = {}
        items = self.the_parent.gui_functions.get_items_tree(self.the_parent.treeWidget)
        for it, item in enumerate(items, start=1):
            try:
                logs = Service(item.connection).logs(the_service)
                the_logs[item.connection] = logs
                self.progressBar.setValue(int(100 * it / len(items)))
                QtCore.QCoreApplication.processEvents()
            except Exception as e:
                self.the_parent.logger.warning(e)

        if len(the_logs) == 0:
            self.the_parent.logger.error("No logs found")
            self.the_parent.gui_functions.error("No logs found")
            return

        self.the_parent.show_window(RemoteLogsMainForm(self.the_parent, the_logs))

    def service_start(self):
        self.the_parent.logger.info("Starting a service")

        selected_items = self.treeWidgetServices.selectedItems()
        the_service = selected_items[0].text(0)
        items = self.the_parent.gui_functions.get_items_tree(self.the_parent.treeWidget)
        for it, item in enumerate(items, start=1):
            try:
                Service(item.connection).start(the_service)
                self.progressBar.setValue(int(100 * it / len(items)))
                QtCore.QCoreApplication.processEvents()
            except Exception as e:
                self.the_parent.logger.warning(e)

        self.refresh()

    def service_stop(self):
        self.the_parent.logger.info("Stopping a service")

        selected_items = self.treeWidgetServices.selectedItems()
        the_service = selected_items[0].text(0)
        items = self.the_parent.gui_functions.get_items_tree(self.the_parent.treeWidget)
        for it, item in enumerate(items, start=1):
            try:
                Service(item.connection).stop(the_service)
                self.progressBar.setValue(int(100 * it / len(items)))
                QtCore.QCoreApplication.processEvents()
            except Exception as e:
                self.the_parent.logger.warning(e)

        self.refresh()

    def service_restart(self):
        self.the_parent.logger.info("Restarting a service")

        selected_items = self.treeWidgetServices.selectedItems()
        the_service = selected_items[0].text(0)
        items = self.the_parent.gui_functions.get_items_tree(self.the_parent.treeWidget)
        for it, item in enumerate(items, start=1):
            try:
                Service(item.connection).resstart(the_service)
                self.progressBar.setValue(int(100 * it / len(items)))
                QtCore.QCoreApplication.processEvents()
            except Exception as e:
                self.the_parent.logger.warning(e)

        self.refresh()

    def service_enable(self):
        self.the_parent.logger.info("Enabling a service.")

        selected_items = self.treeWidgetServices.selectedItems()
        the_service = selected_items[0].text(0)
        items = self.the_parent.gui_functions.get_items_tree(self.the_parent.treeWidget)
        for it, item in enumerate(items, start=1):
            try:
                Service(item.connection).enable(the_service)
                self.progressBar.setValue(int(100 * it / len(items)))
                QtCore.QCoreApplication.processEvents()
            except Exception as e:
                self.the_parent.logger.warning(e)

        self.refresh()

    def service_disable(self):
        self.the_parent.logger.info("Disabling a service")

        selected_items = self.treeWidgetServices.selectedItems()
        the_service = selected_items[0].text(0)
        items = self.the_parent.gui_functions.get_items_tree(self.the_parent.treeWidget)
        for it, item in enumerate(items, start=1):
            try:
                Service(item.connection).disable(the_service)
                self.progressBar.setValue(int(100 * it / len(items)))
                QtCore.QCoreApplication.processEvents()
            except Exception as e:
                self.the_parent.logger.warning(e)

        self.refresh()

    def refresh(self):
        self.the_parent.logger.info("Refreshing")

        self.treeWidgetServices.clear()
        services = {}
        for item in self.the_parent.gui_functions.get_items_tree(self.the_parent.treeWidget):
            try:
                srvcs = Service(item.connection)
                services[srvcs] = srvcs.list()
            except Exception as e:
                self.the_parent.logger.warning(e)

        if len(services) == 0:
            self.the_parent.logger.warning("No services found")
            self.the_parent.gui_functions.warning("No services found")
            return

        load_status = []

        for service, data in service_arranger(services).items():
            group_layer = QtWidgets.QTreeWidgetItem(self.treeWidgetServices, [service])
            group_layer.setFirstColumnSpanned(True)
            good_counter = {"active": 0, "inactive": 0, "failed": 0}
            for machine, information in data.items():
                load_status.append(information["active"])
                child = QtWidgets.QTreeWidgetItem(
                    group_layer,
                    [
                        f"{machine.connector.user}@{machine.connector.address}",
                        information["load"],
                        information["active"],
                        information["substate"],
                        information["description"],
                    ],
                )
                if information["active"] == "active":
                    for i in range(child.columnCount()):
                        child.setForeground(i, QtGui.QColor("#43A047"))
                    good_counter["active"] += 1
                elif information["active"] == "failed":
                    for i in range(child.columnCount()):
                        child.setForeground(i, QtGui.QColor("#E53935"))
                    good_counter["failed"] += 1
                else:
                    good_counter["inactive"] += 1

                child.setFlags(child.flags() & ~QtCore.Qt.ItemFlag.ItemIsSelectable)

            if good_counter["active"] == len(data):
                group_layer.setForeground(0, QtGui.QColor("#43A047"))
            elif good_counter["failed"] == len(data):
                group_layer.setForeground(0, QtGui.QColor("#E53935"))
            elif good_counter["inactive"] != len(data):
                if good_counter["active"] > 0 or good_counter["failed"] > 0:
                    group_layer.setForeground(0, QtGui.QColor("#C0CA33"))

            if good_counter["active"] != 0 or good_counter["failed"] != 0:
                font = QtGui.QFont()
                font.setBold(True)
                group_layer.setFont(0, font)
