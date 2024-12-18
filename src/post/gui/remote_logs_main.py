from PyQt6 import QtWidgets

from post.gui.remote_logs import Ui_FormRemoteLogs


class RemoteLogsMainForm(QtWidgets.QWidget, Ui_FormRemoteLogs):
    def __init__(self, parent, data):
        super(RemoteLogsMainForm, self).__init__(parent)
        self.setupUi(self)

        self.the_parent = parent
        self.data = data

        self.the_parent.logger.info("Remote Logs window loaded")

        self.lineEditSearch.textChanged.connect(self.search)

        self.lists = []

        self.load()

    def search(self):
        self.the_parent.logger.info("Searching")

        for the_list in self.lists:
            to_search = self.lineEditSearch.text()
            for i in range(the_list.count()):
                item = the_list.item(i)
                if to_search.lower() not in item.text().lower():
                    item.setHidden(True)
                else:
                    item.setHidden(False)

    def load(self):
        self.the_parent.logger.info("Loading")

        try:
            for connection, logs in self.data.items():
                try:
                    new_tab = QtWidgets.QWidget()
                    layout = QtWidgets.QVBoxLayout()

                    the_list = QtWidgets.QListWidget()
                    layout.addWidget(the_list)
                    new_tab.setLayout(layout)
                    self.tabWidgetLogs.addTab(
                        new_tab, f"{connection.user}@{connection.address}"
                    )
                    self.the_parent.gui_functions.add_to_list(the_list, logs)
                    the_list.scrollToBottom()

                    self.lists.append(the_list)
                except Exception as e:
                    self.the_parent.logger.warning(e)

        except Exception as e:
            self.the_parent.logger.error(e)
            self.the_parent.gui_functions.error(str(e))
