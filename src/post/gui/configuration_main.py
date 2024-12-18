from PyQt6 import QtWidgets, QtCore

from post import ConfigRaw
from post.gui.configuration import Ui_FormConfigure


class SelectConfigDialog(QtWidgets.QDialog):
    def __init__(self, parent, data):
        super().__init__(parent)
        self.setWindowTitle("Custom Dialog")

        self.the_parent = parent

        self.the_parent.parent.logger.info("Configuration window loaded")

        self.data = data

        self.dropdown = QtWidgets.QComboBox()

        self.plain_text_edit = QtWidgets.QPlainTextEdit()

        self.accept_button = QtWidgets.QPushButton("Accept")
        self.blank_button = QtWidgets.QPushButton("Blank")

        self.accept_button.clicked.connect(self.get_text)
        self.blank_button.clicked.connect(self.close)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.accept_button)
        button_layout.addWidget(self.blank_button)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(self.dropdown)
        main_layout.addWidget(self.plain_text_edit)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        self.dropdown.currentIndexChanged.connect(self.change)  # For index

        self.load()

    def get_text(self):
        self.the_parent.plainTextEdit.setPlainText(self.plain_text_edit.toPlainText())
        self.close()

    def change(self):
        self.plain_text_edit.setPlainText(self.data[self.dropdown.currentText()])

    def load(self):
        keys = list(self.data.keys())
        self.dropdown.addItems(keys)
        self.plain_text_edit.setPlainText(self.data[keys[0]])

    def closeEvent(self, event):
        self.parentWidget().close()


class ConfigurationMainForm(QtWidgets.QWidget, Ui_FormConfigure):
    def __init__(self, parent):
        super(ConfigurationMainForm, self).__init__(parent)
        self.setupUi(self)

        self.the_parent = parent

        self.the_parent.logger.info("Configuration window loaded")

        self.pushButtonLoad.clicked.connect(self.load)
        self.pushButtonSave.clicked.connect(self.save)

    def load(self):
        self.the_parent.logger.info("Loading")

        path = self.lineEditPath.text()

        if not path:
            self.the_parent.logger.error("Path must be provided")
            self.the_parent.gui_functions.error("Path must be provided")
            return

        items = self.the_parent.gui_functions.get_items_tree(self.the_parent.treeWidget)
        configs = {}
        for it, item in enumerate(items, start=1):
            try:
                config = ConfigRaw(
                    item.connection,
                    path,
                    create=self.checkBoxCreate.isChecked(),
                    backup=self.checkBoxBackup.isChecked(),
                    logger=self.the_parent.logger,
                )
                configs[f"{config.connector.user}@{config.connector.address}"] = (
                    config.read()
                )
            except Exception as e:
                self.the_parent.logger.warning(e)

            self.progressBar.setValue(int(100 * it / len(items)))
            QtCore.QCoreApplication.processEvents()

        if len(set(configs.values())) == 1:
            self.plainTextEdit.setPlainText(list(configs.values())[0])
        else:
            self.the_parent.show_window(SelectConfigDialog(self, configs))

    def save(self):
        self.the_parent.logger.info("Saving")

        text = self.plainTextEdit.toPlainText()

        path = self.lineEditPath.text()

        if not path:
            self.the_parent.logger.error("Path must be provided")
            self.the_parent.gui_functions.error("Path must be provided")
            return

        items = self.the_parent.gui_functions.get_items_tree(self.the_parent.treeWidget)
        for it, item in enumerate(items, start=1):
            try:
                config = ConfigRaw(
                    item.connection,
                    self.lineEditPath.text(),
                    create=self.checkBoxCreate.isChecked(),
                    backup=self.checkBoxBackup.isChecked(),
                    logger=self.the_parent.logger,
                )
                config.data = text

            except Exception as e:
                self.the_parent.logger.warning(e)

            self.progressBar.setValue(int(100 * it / len(items)))
            QtCore.QCoreApplication.processEvents()
