# Form implementation generated from reading ui file 'about.ui'
#
# Created by: PyQt6 UI code generator 6.7.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_FormAbout(object):
    def setupUi(self, FormAbout):
        FormAbout.setObjectName("FormAbout")
        FormAbout.resize(450, 196)
        FormAbout.setMinimumSize(QtCore.QSize(450, 0))
        self.gridLayout_2 = QtWidgets.QGridLayout(FormAbout)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_4 = QtWidgets.QLabel(parent=FormAbout)
        self.label_4.setMinimumSize(QtCore.QSize(128, 128))
        self.label_4.setMaximumSize(QtCore.QSize(128, 128))
        self.label_4.setText("")
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 1)
        self.label = QtWidgets.QLabel(parent=FormAbout)
        font = QtGui.QFont()
        font.setPointSize(36)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 1, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(parent=FormAbout)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(parent=FormAbout)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 2, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 1, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding)
        self.gridLayout_2.addItem(spacerItem, 3, 0, 1, 1)

        self.retranslateUi(FormAbout)
        QtCore.QMetaObject.connectSlotsByName(FormAbout)

    def retranslateUi(self, FormAbout):
        _translate = QtCore.QCoreApplication.translate
        FormAbout.setWindowTitle(_translate("FormAbout", "About"))
        self.label.setText(_translate("FormAbout", "POST"))
        self.label_2.setText(_translate("FormAbout", "Pardus Orchestration SysTem"))
        self.label_3.setText(_translate("FormAbout", "Pardus Project"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    FormAbout = QtWidgets.QWidget()
    ui = Ui_FormAbout()
    ui.setupUi(FormAbout)
    FormAbout.show()
    sys.exit(app.exec())
