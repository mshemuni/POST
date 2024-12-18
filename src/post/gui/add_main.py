import csv

from PyQt6 import QtWidgets, QtCore, QtGui

from post import SSHConnector
from post.gui.add import Ui_FormAdd


class AddMainForm(QtWidgets.QWidget, Ui_FormAdd):
    def __init__(self, parent):
        super(AddMainForm, self).__init__(parent)
        self.setupUi(self)

        self.the_parent = parent

        self.the_parent.logger.info("Add window loaded")

        self.checkBoxSinglePasswordShow.toggled.connect(self.toggle_password_visibility)
        self.pushButtonSingleTest.clicked.connect(self.test_single)
        self.pushButtonSingleAdd.clicked.connect(self.add_single)

        self.pushButtonImport.clicked.connect(self.import_connections)
        self.pushButtonBulkTest.clicked.connect(self.test_bulk)
        self.pushButtonBulkAdd.clicked.connect(self.add_bulk)

        self.tableWidgetBulkInformation.setContextMenuPolicy(
            QtCore.Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.tableWidgetBulkInformation.customContextMenuRequested.connect(
            self.show_context_menu
        )

        self.toggle_password_visibility()

        self.tableWidgetBulkInformation.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.Stretch
        )
        self.tableWidgetBulkInformation.setSortingEnabled(True)

    def add_bulk(self):
        self.the_parent.logger.info("add bulk executed")

        all_connections = self.the_parent.gui_functions.get_from_table(
            self.tableWidgetBulkInformation
        )

        if len(all_connections) == 0:
            self.the_parent.gui_functions.error("No connection is available")
            return

        for it, each_connection in enumerate(all_connections, start=1):
            try:
                connection = SSHConnector(*each_connection)
                self.the_parent.add_connection(connection)
            except Exception as e:
                self.the_parent.logger.warning(e)

            self.progressBar.setValue(int(100 * it / len(all_connections)))
            QtCore.QCoreApplication.processEvents()

        self.the_parent.menu_enabler()
        self.close()

    def show_context_menu(self, position):
        self.the_parent.logger.info("Right click menu loaded")

        menu = QtWidgets.QMenu()
        menu.addAction(
            "Insert",
            lambda: self.the_parent.gui_functions.add_to_table(
                self.tableWidgetBulkInformation, [["", "", "", ""]]
            ),
        )
        remove = menu.addAction(
            "Remove",
            lambda: self.the_parent.gui_functions.remove_from_table(
                self.tableWidgetBulkInformation
            ),
        )

        selected = self.tableWidgetBulkInformation.selectedItems()
        if len(selected) == 0:
            remove.setEnabled(False)

        clear = menu.addAction(
            "Clear",
            lambda: self.the_parent.gui_functions.clear_table(
                self.tableWidgetBulkInformation
            ),
        )
        available = self.tableWidgetBulkInformation.rowCount()
        if available == 0:
            clear.setEnabled(False)

        menu.exec(self.tableWidgetBulkInformation.mapToGlobal(position))

    def test_bulk(self):
        self.the_parent.logger.info("Test bulk executed")

        all_connections = self.the_parent.gui_functions.get_from_table(
            self.tableWidgetBulkInformation
        )
        if len(all_connections) == 0:
            self.the_parent.logger.warning("Nothing to test")
            self.the_parent.gui_functions.warning("Nothing to test")
            return

        for it, each_connection in enumerate(all_connections, start=1):
            try:
                _ = SSHConnector(*each_connection)
                color = "green"
            except Exception as e:
                color = "red"
                self.the_parent.logger.warning(e)

            for i in range(4):
                item = self.tableWidgetBulkInformation.item(it - 1, i)
                item.setForeground(QtGui.QColor(color))

            self.progressBar.setValue(int(100 * it / len(all_connections)))
            QtCore.QCoreApplication.processEvents()

    def import_connections(self):
        self.the_parent.logger.info("Importing connections")

        file = self.the_parent.gui_functions.get_file()
        if file:
            try:
                with open(file, "r", newline="", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    self.the_parent.gui_functions.add_to_table(
                        self.tableWidgetBulkInformation,
                        [list(map(str.strip, row)) for row in reader],
                    )
            except Exception as e:
                self.the_parent.logger.error(e)
                self.the_parent.gui_functions.error(str(e))

    def toggle_password_visibility(self):
        self.the_parent.logger.info("Password visibility toggled")

        if self.checkBoxSinglePasswordShow.isChecked():
            self.lineEditSinglePassword.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
        else:
            self.lineEditSinglePassword.setEchoMode(
                QtWidgets.QLineEdit.EchoMode.Password
            )

    def test_single(self):
        self.the_parent.logger.info("Single test executed")

        first_octet = self.spinBoxSingleFirstOctet.value()
        second_octet = self.spinBoxSingleSecondOctet.value()
        third_octet = self.spinBoxSingleThirdOctet.value()
        fourth_octet = self.spinBoxSingleFourthOctet.value()
        ip = f"{first_octet}.{second_octet}.{third_octet}.{fourth_octet}"
        port = self.spinBoxSinglePort.value()
        username = self.lineEditSingleUsername.text()
        password = self.lineEditSinglePassword.text()

        if not username:
            self.the_parent.logger.error("Please enter a username")
            self.the_parent.gui_functions.error("Please enter a username")
            return

        if not password:
            self.the_parent.logger.error("Please enter a password")
            self.the_parent.gui_functions.error("Please enter a password")
            return

        try:
            _ = SSHConnector(ip, port, username, password, logger=self.the_parent.logger)
            self.the_parent.gui_functions.inform("Connection Established")
        except Exception as e:
            self.the_parent.logger.error(e)
            self.the_parent.gui_functions.error(str(e))

    def add_single(self):
        self.the_parent.logger.info("Add single executed")

        first_octet = self.spinBoxSingleFirstOctet.value()
        second_octet = self.spinBoxSingleSecondOctet.value()
        third_octet = self.spinBoxSingleThirdOctet.value()
        fourth_octet = self.spinBoxSingleFourthOctet.value()
        ip = f"{first_octet}.{second_octet}.{third_octet}.{fourth_octet}"
        port = self.spinBoxSinglePort.value()
        username = self.lineEditSingleUsername.text()
        password = self.lineEditSinglePassword.text()

        if not username:
            self.the_parent.logger.error("Please enter a username")
            self.the_parent.gui_functions.error("Please enter a username")
            return

        if not password:
            self.the_parent.logger.error("Please enter a password")
            self.the_parent.gui_functions.error("Please enter a password")
            return

        try:
            connection = SSHConnector(
                ip, str(port), username, password, logger=self.the_parent.logger
            )
            self.the_parent.add_connection(connection)
            self.the_parent.menu_enabler()

            self.close()
        except Exception as e:
            self.the_parent.logger.error(e)
            self.the_parent.gui_functions.error(str(e))

    def closeEvent(self, event):
        self.parentWidget().close()
