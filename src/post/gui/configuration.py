# Form implementation generated from reading ui file 'configuration.ui'
#
# Created by: PyQt6 UI code generator 6.7.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_FormConfigure(object):
    def setupUi(self, FormConfigure):
        FormConfigure.setObjectName("FormConfigure")
        FormConfigure.resize(450, 450)
        FormConfigure.setMinimumSize(QtCore.QSize(450, 450))
        self.gridLayout = QtWidgets.QGridLayout(FormConfigure)
        self.gridLayout.setObjectName("gridLayout")
        self.lineEditPath = QtWidgets.QLineEdit(parent=FormConfigure)
        self.lineEditPath.setObjectName("lineEditPath")
        self.gridLayout.addWidget(self.lineEditPath, 0, 0, 1, 1)
        self.checkBoxCreate = QtWidgets.QCheckBox(parent=FormConfigure)
        self.checkBoxCreate.setMinimumSize(QtCore.QSize(71, 22))
        self.checkBoxCreate.setMaximumSize(QtCore.QSize(71, 22))
        self.checkBoxCreate.setChecked(True)
        self.checkBoxCreate.setObjectName("checkBoxCreate")
        self.gridLayout.addWidget(self.checkBoxCreate, 0, 1, 1, 1)
        self.checkBoxBackup = QtWidgets.QCheckBox(parent=FormConfigure)
        self.checkBoxBackup.setMinimumSize(QtCore.QSize(71, 22))
        self.checkBoxBackup.setMaximumSize(QtCore.QSize(71, 22))
        self.checkBoxBackup.setChecked(True)
        self.checkBoxBackup.setObjectName("checkBoxBackup")
        self.gridLayout.addWidget(self.checkBoxBackup, 0, 2, 1, 1)
        self.pushButtonLoad = QtWidgets.QPushButton(parent=FormConfigure)
        self.pushButtonLoad.setObjectName("pushButtonLoad")
        self.gridLayout.addWidget(self.pushButtonLoad, 0, 3, 1, 1)
        self.plainTextEdit = QtWidgets.QPlainTextEdit(parent=FormConfigure)
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.gridLayout.addWidget(self.plainTextEdit, 1, 0, 1, 4)
        self.progressBar = QtWidgets.QProgressBar(parent=FormConfigure)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.gridLayout.addWidget(self.progressBar, 2, 0, 1, 3)
        self.pushButtonSave = QtWidgets.QPushButton(parent=FormConfigure)
        self.pushButtonSave.setObjectName("pushButtonSave")
        self.gridLayout.addWidget(self.pushButtonSave, 2, 3, 1, 1)

        self.retranslateUi(FormConfigure)
        QtCore.QMetaObject.connectSlotsByName(FormConfigure)

    def retranslateUi(self, FormConfigure):
        _translate = QtCore.QCoreApplication.translate
        FormConfigure.setWindowTitle(_translate("FormConfigure", "Form"))
        self.lineEditPath.setPlaceholderText(_translate("FormConfigure", "Path"))
        self.checkBoxCreate.setText(_translate("FormConfigure", "Force"))
        self.checkBoxBackup.setText(_translate("FormConfigure", "Backup"))
        self.pushButtonLoad.setText(_translate("FormConfigure", "Load"))
        self.pushButtonSave.setText(_translate("FormConfigure", "Save"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    FormConfigure = QtWidgets.QWidget()
    ui = Ui_FormConfigure()
    ui.setupUi(FormConfigure)
    FormConfigure.show()
    sys.exit(app.exec())
