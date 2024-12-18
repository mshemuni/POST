from pathlib import Path

from PyQt6 import QtWidgets

from post.gui.license import Ui_FormLicense


class LicenseMainForm(QtWidgets.QWidget, Ui_FormLicense):
    def __init__(self, parent):
        super(LicenseMainForm, self).__init__(parent)
        self.setupUi(self)

        self.the_parent = parent

        self.the_parent.logger.info("License window loaded")

        with open(f"{Path(__file__).parent}/../../../LICENSE") as f:
            self.plainTextEdit.setPlainText(f.read())
