from logging import Logger

from PyQt6 import QtWidgets, QtCore


class PleaseWaitDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Please Wait")
        self.setWindowModality(QtCore.Qt.WindowModality.ApplicationModal)
        self.setFixedSize(200, 100)
        self.setWindowFlags(
            self.windowFlags() & ~QtCore.Qt.WindowType.WindowContextHelpButtonHint
        )

        layout = QtWidgets.QVBoxLayout()
        message_label = QtWidgets.QLabel("Please wait ...")
        message_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(message_label)
        self.setLayout(layout)


class CustomQTreeWidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, connection, *args, **kwargs):
        self.connection = connection
        super().__init__(*args, **kwargs)


class GUIFunctions:
    def __init__(self, parent: QtWidgets.QMainWindow, logger: Logger):
        self.logger = logger
        self.parent = parent

    def ask(self, question):
        answer = QtWidgets.QMessageBox.question(
            self.parent,
            "POST",
            question,
            QtWidgets.QMessageBox.StandardButton.Yes
            | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No,
        )

        return answer == QtWidgets.QMessageBox.StandardButton.Yes

    def error(self, text):
        QtWidgets.QMessageBox.critical(self.parent, "POST", text)

    def warning(self, text):
        QtWidgets.QMessageBox.warning(self.parent, "POST", text)

    def inform(self, text):
        QtWidgets.QMessageBox.information(self.parent, "POST", text)

    def get_file(self):
        try:
            file, _ = QtWidgets.QFileDialog.getOpenFileName(
                self.parent,
                "POST get file",
                "",
            )
            return file
        except Exception as e:
            self.logger.error(e)
            return ""

    def clear_table(self, table_widget):
        while table_widget.rowCount() > 0:
            table_widget.removeRow(0)

    def remove_from_table(self, table_widget):
        selected_rows = list(
            set([index.row() for index in table_widget.selectedIndexes()])
        )
        selected_rows.sort(reverse=True)
        for row in selected_rows:
            table_widget.removeRow(row)

    def get_from_table(self, table_widget):
        number_of_rows = table_widget.rowCount()
        number_of_columns = table_widget.columnCount()
        ret = []
        if number_of_rows > 0 and number_of_columns > 0:
            for i in range(number_of_rows):
                row = []
                for j in range(number_of_columns):
                    row.append(table_widget.item(i, j).text())

                ret.append(row)

            return ret

        return []

    def get_from_table_selected(self, table_widget):
        ret = []
        for i in table_widget.selectionModel().selectedRows():
            row = []
            for j in range(table_widget.columnCount()):
                row.append(table_widget.item(i.row(), j).text())
            ret.append(row)

        return ret

    def add_to_table(self, table_widget, data):
        for line in data:
            row_position = table_widget.rowCount()
            table_widget.insertRow(row_position)
            for it, value in enumerate(line):
                table_widget.setItem(
                    row_position, it, QtWidgets.QTableWidgetItem(str(value))
                )

    def add_to_list(self, list_widget, data):
        it = list_widget.count() - 1
        for x in data:
            it = it + 1
            item = QtWidgets.QListWidgetItem()
            list_widget.addItem(item)
            item = list_widget.item(it)
            item.setText(x)

    def get_from_list(self, list_widget):
        return [list_widget.item(x).text() for x in range(list_widget.count())]

    def get_from_list_selected(self, list_widget):
        return [x.text() for x in list_widget.selectedItems()]

    def remove_from_list(self, list_widget):
        for x in list_widget.selectedItems():
            list_widget.takeItem(list_widget.row(x))

    def save_file(self):
        file, _ = QtWidgets.QFileDialog.getSaveFileName(
            self.parent, "POST", filter="csv (*.csv)"
        )
        return file

    def remove_selected_items_from_tree(self, tree_widget):
        selected_items = tree_widget.selectedItems()

        for item in selected_items:
            parent = item.parent()
            if parent is not None:
                parent.removeChild(item)
            else:
                index = tree_widget.indexOfTopLevelItem(item)
                tree_widget.takeTopLevelItem(index)

    def get_items_tree(self, tree_widget):
        return [
            tree_widget.topLevelItem(i) for i in range(tree_widget.topLevelItemCount())
        ]
