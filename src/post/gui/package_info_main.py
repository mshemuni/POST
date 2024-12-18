from PyQt6 import QtWidgets
import yaml

from post.gui.package_info import Ui_FormShowPackage


class ShowPackageMainForm(QtWidgets.QWidget, Ui_FormShowPackage):
    def __init__(self, parent, data):
        super(ShowPackageMainForm, self).__init__(parent)
        self.setupUi(self)

        self.the_parent = parent

        self.the_parent.logger.info("Show Package window loaded")

        self.data = data
        self.load()

    def load(self):
        self.the_parent.logger.info("Loading")
        try:
            for connection, data in self.data.items():
                try:
                    new_tab = QtWidgets.QWidget()
                    layout = QtWidgets.QVBoxLayout()

                    plain_text_edit = QtWidgets.QPlainTextEdit()

                    plain_text_edit.setPlainText(yaml.dump(data))

                    layout.addWidget(plain_text_edit)
                    new_tab.setLayout(layout)
                    self.tabWidget.addTab(
                        new_tab, f"{connection.user}@{connection.address}"
                    )
                except Exception as e:
                    self.the_parent.logger.warning(e)

        except Exception as e:
            self.the_parent.logger.error(e)
            self.the_parent.gui_fcuntions.error(e)
