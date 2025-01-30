from pathlib import Path

from PyQt6 import QtWidgets, QtGui, QtCore

from post.gui.user import Ui_FormUser

LOGO = (Path(__file__).parent.parent.parent.parent / "post.png").absolute().__str__()


class UserGroupsDialog(QtWidgets.QDialog):
    def __init__(self, user, username, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Groups")
        self.user = user
        self.username = username

        main_layout = QtWidgets.QVBoxLayout(self)

        self.list_widget = QtWidgets.QListWidget(self)
        self.list_widget.setSelectionMode(QtWidgets.QListWidget.SelectionMode.ExtendedSelection)

        main_layout.addWidget(self.list_widget)

        button_layout = QtWidgets.QHBoxLayout()

        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        button_layout.addItem(spacer)

        self.cancel_button = QtWidgets.QPushButton("Cancel")
        button_layout.addWidget(self.cancel_button)

        self.ok_button = QtWidgets.QPushButton("OK", self)
        button_layout.addWidget(self.ok_button)

        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        self.load()

    def load(self):
        self.the_parent.logger.infor("Loading")

        groups = self.user.list_groups()
        user_groups = self.user.groups(self.username)
        for user_group in user_groups:
            groups.remove(user_group)

        self.list_widget.addItems(user_groups)
        self.list_widget.selectAll()
        self.list_widget.addItems(groups)

    def accept(self):
        groups = []
        for item in self.list_widget.selectedItems():
            groups.append(item.text())

        self.user.group_set(self.username, groups)

        super().accept()


class PasswordChangeDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Set New Password")
        self.setLayout(QtWidgets.QVBoxLayout())

        # Password 1
        self.label1 = QtWidgets.QLabel("Enter Password:")
        self.layout().addWidget(self.label1)

        self.password = QtWidgets.QLineEdit()
        self.password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.layout().addWidget(self.password)

        self.label2 = QtWidgets.QLabel("Confirm Password:")
        self.layout().addWidget(self.label2)

        self.password_repeat = QtWidgets.QLineEdit()
        self.password_repeat.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.layout().addWidget(self.password_repeat)

        vertical_spacer = QtWidgets.QSpacerItem(
            20,
            40,
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        self.layout().addItem(vertical_spacer)

        self.show_password_cb = QtWidgets.QCheckBox("Show Password")
        self.layout().addWidget(self.show_password_cb)

        self.ok_button = QtWidgets.QPushButton("OK")
        self.layout().addWidget(self.ok_button)

        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.layout().addWidget(self.cancel_button)

        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        self.show_password_cb.stateChanged.connect(self.toggle_password_visibility)

    def accept(self):
        if len(self.password.text()) == 0:
            QtWidgets.QMessageBox.warning(
                self, "Validation Error", "Password must not be empty"
            )
            return

        if not self.show_password_cb.isChecked():
            if self.password.text() != self.password_repeat.text():
                QtWidgets.QMessageBox.warning(
                    self, "Validation Error", "Passwords should match"
                )
                return
        super().accept()

    def toggle_password_visibility(self):
        if self.show_password_cb.isChecked():
            self.password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
            self.password_repeat.hide()
            self.label2.hide()
        else:
            self.password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
            self.password_repeat.show()
            self.label2.show()

    def get_results(self):
        return self.password.text()


class UserDeleteAskBox(QtWidgets.QDialog):
    def __init__(self, question, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Delete User")
        layout = QtWidgets.QVBoxLayout(self)

        self.message_box = QtWidgets.QMessageBox(self)
        self.message_box.setText(question)
        self.message_box.setIcon(QtWidgets.QMessageBox.Icon.Question)
        layout.addWidget(self.message_box)

        self.checkbox_delete_home_dir = QtWidgets.QCheckBox("Delete Home Directory")
        self.checkbox_delete_all_files = QtWidgets.QCheckBox("Delete All Files")
        layout.addWidget(self.checkbox_delete_home_dir)
        layout.addWidget(self.checkbox_delete_all_files)

        self.checkbox_delete_home_dir.setChecked(True)
        self.checkbox_delete_all_files.setChecked(True)

        self.ok_button = QtWidgets.QPushButton("OK")
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        layout.addWidget(self.ok_button)
        layout.addWidget(self.cancel_button)

    def get_results(self):
        """Returns the state of checkboxes as a tuple."""
        return (
            self.checkbox_delete_home_dir.isChecked(),
            self.checkbox_delete_all_files.isChecked(),
        )


class UserAddDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Add User")

        layout = QtWidgets.QVBoxLayout()

        self.lineEdit_user = QtWidgets.QLineEdit(self)
        label = QtWidgets.QLabel("Username:")
        layout.addWidget(label)
        layout.addWidget(self.lineEdit_user)

        self.lineEdit_home_directory = QtWidgets.QLineEdit(self)
        label = QtWidgets.QLabel("Home Directory:")
        layout.addWidget(label)
        layout.addWidget(self.lineEdit_home_directory)

        self.lineEdit_shell = QtWidgets.QLineEdit(self)
        label = QtWidgets.QLabel("Shell:")
        layout.addWidget(label)
        layout.addWidget(self.lineEdit_shell)

        self.lineEdit_full_name = QtWidgets.QLineEdit(self)
        label = QtWidgets.QLabel("Full Name:")
        layout.addWidget(label)
        layout.addWidget(self.lineEdit_full_name)

        vertical_spacer = QtWidgets.QSpacerItem(
            20,
            40,
            QtWidgets.QSizePolicy.Policy.Minimum,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        layout.addItem(vertical_spacer)

        self.button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

    def accept(self):
        if not self.lineEdit_user.text().strip():
            QtWidgets.QMessageBox.warning(
                self, "Validation Error", "Username cannot be empty"
            )
            return
        super().accept()

    def get_values(self):
        username = self.lineEdit_user.text()
        home_directory = self.lineEdit_home_directory.text()
        shell = self.lineEdit_shell.text()
        full_name = self.lineEdit_full_name.text()

        if home_directory:
            home_directory_to_use = home_directory
        else:
            home_directory_to_use = None

        if shell:
            shell_to_use = shell
        else:
            shell_to_use = None

        if full_name:
            full_name_to_use = full_name
        else:
            full_name_to_use = None

        return username, home_directory_to_use, shell_to_use, full_name_to_use


class UserMainForm(QtWidgets.QWidget, Ui_FormUser):
    def __init__(self, parent, users):
        super(UserMainForm, self).__init__(parent)
        self.setupUi(self)

        self.the_parent = parent
        self.users = users

        self.the_parent.logger.info("User window loaded")
        pixmap = QtGui.QPixmap(LOGO)

        self.lineEdit.textChanged.connect(self.search)
        self.tree_widgets = []

        self.load()

    def load(self):
        self.the_parent.logger.infor("Loading user list")

        self.tree_widgets.clear()
        for user in self.users:
            new_tab = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout()

            tree_widget = QtWidgets.QTreeWidget()
            tree_widget.setColumnCount(4)
            tree_widget.setHeaderLabels(
                ["User ID", "Group ID", "Home Dir", "Enabled", "Gecos"]
            )
            tree_widget.setContextMenuPolicy(
                QtCore.Qt.ContextMenuPolicy.CustomContextMenu
            )
            tree_widget.customContextMenuRequested.connect(
                lambda pos, tw=tree_widget, usr=user: self.show_context_menu(
                    pos, tw, usr
                )
            )

            for each_user in user.__list():
                info = user.info(each_user)
                group_layer = QtWidgets.QTreeWidgetItem(tree_widget, [each_user])
                group_layer.setFirstColumnSpanned(True)

                _ = QtWidgets.QTreeWidgetItem(
                    group_layer,
                    [str(info[2]), str(info[3]), info[5], str(info[1]), info[4]],
                )

                font = QtGui.QFont()

                if not info[1]:
                    color = QtGui.QColor("#E53935")
                    font.setBold(False)
                else:
                    color = QtGui.QColor("#43A047")
                    font.setBold(True)

                group_layer.setForeground(0, color)
                group_layer.setFont(0, font)

            layout.addWidget(tree_widget)
            self.tree_widgets.append(tree_widget)

            new_tab.setLayout(layout)
            self.tabWidget.addTab(
                new_tab, f"{user.connector.user}@{user.connector.address}"
            )

    def show_context_menu(self, pos, tree_widget, user):
        menu = QtWidgets.QMenu(self)
        try:

            selected = tree_widget.selectedItems()

            menu.addAction("Add ...", lambda: self.add_user(user, tree_widget))
            rm = menu.addAction("Remove", lambda: self.del_user(user, tree_widget))
            groups = menu.addAction(
                "Groups ...", lambda: self.groups_show(user, tree_widget)
            )
            menu.addSeparator()
            enable = menu.addAction(
                "Enable", lambda: self.enable_user(user, tree_widget)
            )
            disable = menu.addAction(
                "Disable", lambda: self.disable_user(user, tree_widget)
            )
            menu.addSeparator()
            password = menu.addAction(
                "Password ...", lambda: self.change_password(user, tree_widget)
            )

            if len(selected) == 0:
                rm.setEnabled(False)
                password.setEnabled(False)
                enable.setEnabled(False)
                disable.setEnabled(False)
                groups.setEnabled(False)
            else:
                is_enabled = user.is_enabled(selected[0].text(0))
                if is_enabled:
                    enable.setEnabled(False)
                else:
                    disable.setEnabled(False)

        except Exception as e:
            self.the_parent.logger.error(e)
            self.the_parent.gui_functions.error(str(e))
            return

        menu.exec(tree_widget.mapToGlobal(pos))

    def groups_show(self, user, tree_widget):
        self.the_parent.logger.infor("Showing groups")

        selected = tree_widget.selectedItems()
        username = selected[0].text(0)
        dialog = UserGroupsDialog(user, username, self)
        dialog.setMinimumSize(225, 225)
        dialog.show()

    def change_password(self, user, tree_widget):
        self.the_parent.logger.infor("Showing change password")

        selected = tree_widget.selectedItems()
        username = selected[0].text(0)
        dialog = PasswordChangeDialog(self)
        if dialog.exec():
            try:
                user.set_password(username, dialog.get_results())
            except Exception as e:
                self.the_parent.logger.error(e)
                self.the_parent.gui_functions.error(str(e))

    def enable_user(self, user, tree_widget):
        self.the_parent.logger.infor("Enabling the user")

        selected = tree_widget.selectedItems()
        username = selected[0].text(0)
        if self.the_parent.gui_function.ask(f"Are you sure you want to enable `{username}`?"):
            try:
                user.enable(username)
                self.reload(user, tree_widget)
            except Exception as e:
                self.the_parent.logger.error(e)
                self.the_parent.gui_functions.error(str(e))

    def disable_user(self, user, tree_widget):
        self.the_parent.logger.infor("Disabling the user")

        selected = tree_widget.selectedItems()
        username = selected[0].text(0)
        if self.the_parent.gui_function.ask(f"Are you sure you want to disable `{username}`?"):
            try:
                user.disable(username)
                self.reload(user, tree_widget)
            except Exception as e:
                self.the_parent.logger.error(e)
                self.the_parent.gui_functions.error(str(e))

    def del_user(self, user, tree_widget):
        self.the_parent.logger.infor("Deleting the user")

        selected = tree_widget.selectedItems()
        username = selected[0].text(0)
        dialog = UserDeleteAskBox(f"Are you sure you want to delete `{username}`?", self)
        if dialog.exec():
            try:
                del_home, del_files = dialog.get_results()
                user.rm(username, del_home, del_files)
                self.reload(user, tree_widget)
            except Exception as e:
                self.the_parent.logger.error(e)
                self.the_parent.gui_functions.error(str(e))

    def add_user(self, user, tree_widget):
        self.the_parent.logger.infor("Adding a user")

        dialog = UserAddDialog(self)
        if dialog.exec():
            try:
                user.add(*dialog.get_values())
                self.reload(user, tree_widget)
            except Exception as e:
                self.the_parent.logger.error(e)
                self.the_parent.gui_functions.error(str(e))

    def reload(self, user, tree_widget):
        self.the_parent.logger.infor("Reloading user list")

        tree_widget.clear()
        for each_user in user.__list():
            info = user.info(each_user)
            group_layer = QtWidgets.QTreeWidgetItem(tree_widget, [each_user])
            group_layer.setFirstColumnSpanned(True)

            _ = QtWidgets.QTreeWidgetItem(
                group_layer,
                [str(info[2]), str(info[3]), info[5], str(info[1]), info[4]],
            )

            font = QtGui.QFont()

            if not info[1]:
                color = QtGui.QColor("#E53935")
                font.setBold(False)
            else:
                color = QtGui.QColor("#43A047")
                font.setBold(True)

            group_layer.setForeground(0, color)
            group_layer.setFont(0, font)

    def search(self):
        text = self.lineEdit.text().strip()
        for tree_widget in self.tree_widgets:
            for i in range(tree_widget.topLevelItemCount()):
                item = tree_widget.topLevelItem(i)
                to_search_in = [item.text(0)]
                for row in range(item.childCount()):
                    child_item = item.child(row)
                    to_search_in.append(child_item.text(0))
                    to_search_in.append(child_item.text(1))
                    to_search_in.append(child_item.text(2))
                    to_search_in.append(child_item.text(4))

                if text.lower() not in " ".join(to_search_in).lower():
                    item.setHidden(True)
                else:
                    item.setHidden(False)
