from PyQt6 import QtWidgets, QtCore, QtGui

from post import SSHConnector
from post.gui.scanner import Ui_FormScanner
from post.utils.common import check_ssh


class ScannerMainForm(QtWidgets.QWidget, Ui_FormScanner):
    def __init__(self, parent):
        super(ScannerMainForm, self).__init__(parent)
        self.setupUi(self)

        self.the_parent = parent

        self.the_parent.logger.info("Scanner window loaded")

        self.checkBoxSharedPasswordShow.toggled.connect(self.toggle_password_visibility)
        self.pushButtonScan.clicked.connect(self.scan)
        self.pushButtonTest.clicked.connect(self.test)
        self.pushButtonAdd.clicked.connect(self.add)

        self.tableWidgetConnection.setContextMenuPolicy(
            QtCore.Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.tableWidgetConnection.customContextMenuRequested.connect(
            self.show_context_menu
        )

        self.toggle_password_visibility()

    def show_context_menu(self, position):
        self.the_parent.logger.info("Right click menu loaded")

        menu = QtWidgets.QMenu()
        menu.addAction(
            "Remove",
            lambda: self.the_parent.gui_functions.remove_from_table(
                self.tableWidgetConnection
            ),
        )
        menu.addAction(
            "Clear",
            lambda: self.the_parent.gui_functions.clear_table(self.tableWidgetConnection),
        )
        menu.exec(self.tableWidgetConnection.mapToGlobal(position))

    def toggle_password_visibility(self):
        self.the_parent.logger.info("Password visibility toggled")

        if self.checkBoxSharedPasswordShow.isChecked():
            self.lineEditSharedPassword.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
        else:
            self.lineEditSharedPassword.setEchoMode(
                QtWidgets.QLineEdit.EchoMode.Password
            )

    def scan(self):
        self.the_parent.logger.info("Scanning")

        first_octet = self.spinBoxFirstOctet.value()
        second_octet = self.spinBoxSecondOctet.value()
        third_octet = self.spinBoxThirdOctet.value()

        upper_range = self.spinBoxLastOctetUpper.value()
        lower_range = self.spinBoxLastOctetLower.value()

        port = self.spinBoxPort.value()
        the_range = range(lower_range, upper_range + 1)
        connections = []
        for it, last_octet in enumerate(the_range, start=1):
            try:
                ip = f"{first_octet}.{second_octet}.{third_octet}.{last_octet}"
                check = check_ssh(ip, port=port)

                if check:
                    connections.append([ip, port, "", ""])
            except Exception as e:
                self.the_parent.logger.warning(e)

            self.progressBar.setValue(int(100 * it / len(the_range)))
            QtCore.QCoreApplication.processEvents()

        self.the_parent.gui_functions.add_to_table(self.tableWidgetConnection, connections)

        self.stackedWidget.setCurrentIndex(1)

    def test(self):
        self.the_parent.logger.info("Testing")

        all_connections = self.the_parent.gui_functions.get_from_table(
            self.tableWidgetConnection
        )

        if self.groupBoxShared.isChecked():
            username = self.lineEditSharedUsername.text()
            password = self.lineEditSharedPassword.text()

            for each in all_connections:
                each[2:4] = [username, password]

        if len(all_connections) == 0:
            self.the_parent.gui_functions.warning("Nothing to add")
            return

        for it, each_connection in enumerate(all_connections, start=1):
            try:
                if not each_connection[2]:
                    raise ValueError("Username cannot be blank")

                if not each_connection[3]:
                    raise ValueError("Password cannot be blank")

                _ = SSHConnector(*each_connection)
                color = "green"
            except Exception as e:
                self.the_parent.logger.warning(e)
                color = "red"

            for i in range(4):
                item = self.tableWidgetConnection.item(it - 1, i)
                item.setForeground(QtGui.QColor(color))

            self.progressBar_2.setValue(int(100 * it / len(all_connections)))
            QtCore.QCoreApplication.processEvents()

    def add(self):
        self.the_parent.logger.info("Adding")

        all_connections = self.the_parent.gui_functions.get_from_table(
            self.tableWidgetConnection
        )

        if self.groupBoxShared.isChecked():
            username = self.lineEditSharedUsername.text()
            password = self.lineEditSharedPassword.text()

            for each in all_connections:
                each[2:4] = [username, password]

        if len(all_connections) == 0:
            self.the_parent.gui_functions.warning("Nothing to add")
            return

        for it, each_connection in enumerate(all_connections, start=1):
            try:
                connection = SSHConnector(*each_connection)
                self.the_parent.add_connection(connection)
            except Exception as e:
                self.the_parent.logger.warning(e)

            self.progressBar_2.setValue(int(100 * it / len(all_connections)))
            QtCore.QCoreApplication.processEvents()

        self.the_parent.menu_enabler()

        self.close()

    def closeEvent(self, event):
        self.parentWidget().close()
