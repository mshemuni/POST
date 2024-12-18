from PyQt6 import QtWidgets, QtCore

from post.gui.cl import Ui_FormCL


class CLMainForm(QtWidgets.QWidget, Ui_FormCL):
    def __init__(self, parent):
        super(CLMainForm, self).__init__(parent)
        self.setupUi(self)

        self.the_parent = parent

        self.the_parent.logger.info("Command Line window loaded")

        self.lineEdit.returnPressed.connect(self.execute_command)
        self.comboBox.currentIndexChanged.connect(self.warn_sudo)

        self.lineEditSearch.textChanged.connect(self.search)

        self.lineEdit.setFocus()

    def search(self):
        self.the_parent.logger.info("Searching")

        to_search = self.lineEditSearch.text()
        for item in range(self.treeWidgetOutput.topLevelItemCount()):
            item = self.treeWidgetOutput.topLevelItem(item)
            if to_search.lower() not in item.text(0).lower():
                item.setHidden(True)
            else:
                item.setHidden(False)

    def warn_sudo(self):
        self.the_parent.logger.info("Sudo warning")

        if self.comboBox.currentIndex() == 1:
            self.the_parent.gui_functions.warning(
                "You are using sudo permissions!\n"
                "Actions performed with sudo can significantly impact your system. "
                "Proceed with caution to avoid unintended changes or damage. "
                "Ensure you fully understand the commands you execute."
            )

    def execute_command(self):
        self.the_parent.logger.info("Executing a command")

        command = self.lineEdit.text().strip()
        if not command:
            self.the_parent.logger.error("No command given")
            self.the_parent.gui_function.error("No command given")
            return

        outputs = {}
        items = self.the_parent.gui_functions.get_items_tree(self.the_parent.treeWidget)
        for it, item in enumerate(items, start=1):
            try:
                if self.comboBox.currentIndex() == 0:
                    stdout = item.connection.run(command)
                else:
                    stdout = item.connection.sudo_run(command)
            except Exception as e:
                self.the_parent.logger.warning(e)

            outputs[f"{item.connection.user}@{item.connection.address}"] = (
                stdout.read().decode().strip()
            )
            self.progressBar.setValue(int(100 * it / len(items)))
            QtCore.QCoreApplication.processEvents()

        if len(outputs) == 0:
            self.the_parent.logger.error("No outputs found")
            self.the_parent.gui_functions.error("No outputs found")

        group_layer = QtWidgets.QTreeWidgetItem(self.treeWidgetOutput, [command])
        group_layer.setFirstColumnSpanned(True)

        for address, output in outputs.items():
            QtWidgets.QTreeWidgetItem(group_layer, [address, output])

        self.lineEdit.clear()
