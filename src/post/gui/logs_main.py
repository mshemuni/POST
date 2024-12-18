from pathlib import Path

from PyQt6 import QtWidgets

from post.gui.logs import Ui_FormLogs

import os


def human_readable_size(file_path):
    size_bytes = os.path.getsize(file_path)
    if size_bytes == 0:
        return "0 B"

    size_units = ["B", "KB", "MB", "GB", "TB", "PB", "EB"]
    i = 0

    while size_bytes >= 1024 and i < len(size_units) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.2f} {size_units[i]}"


class LogsMainForm(QtWidgets.QWidget, Ui_FormLogs):
    def __init__(self, parent):
        super(LogsMainForm, self).__init__(parent)
        self.setupUi(self)

        self.the_parent = parent

        self.the_parent.logger.info("Logs window loaded")

        self.pushButtonReload.clicked.connect(self.reload)
        self.pushButtonClear.clicked.connect(self.clear)
        self.pushButtonExport.clicked.connect(self.export)
        self.lineEditSearch.textChanged.connect(self.search)

        self.reload()

    def search(self):
        self.the_parent.logger.info("Searching")

        to_search = self.lineEditSearch.text()
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            if to_search.lower() not in item.text().lower():
                item.setHidden(True)
            else:
                item.setHidden(False)

    def export(self):
        self.the_parent.logger.info("Exporting")

        file = self.the_parent.gui_functions.save_file()
        if file:
            try:
                source = Path(self.the_parent.log_file)
                destination = Path(file)
                destination.write_text(source.read_text())
            except Exception as e:
                self.the_parent.logger.error(e)
                self.the_parent.gui_functions.error(str(e))

    def size(self):
        self.the_parent.logger.info("Getting the size")

        size = human_readable_size(self.the_parent.log_file)
        self.label.setText(f"Log file size: {size}")

    def reload(self):
        self.the_parent.logger.info("Reloading")

        try:
            with open(self.the_parent.log_file, "r") as f:
                lines = list(map(str.strip, f.readlines()))
                self.listWidget.clear()
                self.the_parent.gui_functions.add_to_list(self.listWidget, lines)
                self.listWidget.scrollToBottom()

                self.size()
        except Exception as e:
            self.the_parent.logger.error(e)
            self.the_parent.gui_functions.error(str(e))

    def clear(self):
        self.the_parent.logger.info("Clearing")

        are_you_sure = self.the_parent.gui_functions.ask(
            "Are you sure you want to clear the log file?"
        )
        if are_you_sure:
            try:
                with open(self.the_parent.log_file, "w") as f:
                    f.write("")
            except Exception as e:
                self.the_parent.logger.error(e)
                self.the_parent.gui_functions.error(str(e))

            self.reload()
