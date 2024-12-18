from pathlib import Path

from PyQt6 import QtWidgets, QtGui

from post.gui.about import Ui_FormAbout

LOGO = (Path(__file__).parent.parent.parent.parent / "post.png").absolute().__str__()


class AboutMainForm(QtWidgets.QWidget, Ui_FormAbout):
    def __init__(self, parent):
        super(AboutMainForm, self).__init__(parent)
        self.setupUi(self)

        self.the_parent = parent

        self.the_parent.logger.info("About window loaded")
        pixmap = QtGui.QPixmap(LOGO)

        resized_pixmap = pixmap.scaled(pixmap.width() // 4, pixmap.height() // 4)
        self.label_4.setPixmap(resized_pixmap)
