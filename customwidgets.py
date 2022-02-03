from __future__ import annotations
from PyQt5 import QtCore, QtGui, QtWidgets


class CustomQTableWidget(QtWidgets.QTableWidget):
    column_visibility_changed = QtCore.pyqtSignal(int, bool)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.header_context_menu = self.set_header_context_menu()

        self.mouse_over_column = -1  # -1 means no column is currently being hovered over

        self.setShowGrid(True)
        self.setAlternatingRowColors(True)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_row_context_menu)
        self.horizontalHeader().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.horizontalHeader().customContextMenuRequested.connect(
            self.show_header_context_menu)
        self.horizontalHeader().setDefaultSectionSize(75)
        self.horizontalHeader().setSortIndicatorShown(True)
        self.horizontalHeader().sortIndicatorChanged.connect(self.sort_table)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.verticalHeader().setStretchLastSection(False)
        self.setWordWrap(False)

        font = QtGui.QFont()
        font.setBold(True)
        self.horizontalHeader().setFont(font)

    def insert_row_data(self, data: list[str]):
        column_count = self.columnCount()
        assert len(data) == column_count

        row_count = self.rowCount()
        self.insertRow(row_count)
        for column, text in enumerate(data):
            item = QtWidgets.QTableWidgetItem(text)
            self.setItem(row_count, column, item)

    def set_table_headers(self, headers: list[str]):
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        self.header_context_menu = self.set_header_context_menu()

    def sort_table(self, column: int, order):
        self.sortItems(column, order)

    def toggle_column(self, checked):
        action = self.sender()
        header_text = action.text()

        for column in range(self.columnCount()):
            header = self.horizontalHeaderItem(column)
            if header.text() != header_text:
                continue

            self.setColumnHidden(column, not checked)
            # emit a signal on the column visibility change
            self.column_visibility_changed.emit(column, checked)

    def set_header_context_menu(self) -> QtWidgets.QMenu:
        menu = QtWidgets.QMenu()

        # menu.addAction("Hide This Column.", self.resize_all_columns)
        menu.addSeparator()

        headers = [self.horizontalHeaderItem(i)
                   for i in range(self.columnCount())]
        for header in headers:
            action = QtWidgets.QAction(header.text(), self)
            action.setCheckable(True)
            action.setChecked(True)
            action.toggled.connect(self.toggle_column)
            menu.addAction(action)

        menu.addSeparator()

        menu.addAction("Auto Resize This Column", self.resize_current_column)
        menu.addAction("Auto Resize All Columns", self.resize_all_columns)
        return menu

    def show_header_context_menu(self, pos):
        header = self.horizontalHeader()
        self.mouse_over_column = header.logicalIndexAt(pos)
        point = header.mapToGlobal(pos)
        self.header_context_menu.exec_(point)

    def resize_current_column(self):
        current_column = self.mouse_over_column
        self.resizeColumnToContents(current_column)

    def resize_all_columns(self):
        for column in range(self.columnCount()):
            self.resizeColumnToContents(column)

    def show_row_context_menu(self, pos):
        menu = QtWidgets.QMenu()
        menu.addAction("Copy", self.copy_selected_rows)
        menu.exec_(self.mapToGlobal(pos))

    def copy_selected_rows(self):
        rows = self.selectionModel().selectedRows()
        if not rows:
            return
        row_count = len(rows)
        column_count = self.columnCount()
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.clear()
        column_headers = [
            f'"{self.horizontalHeaderItem(i).text()}"' for i in range(column_count)]
        clipboard.setText(", ".join(column_headers) + "\n")
        for row in rows:
            row_data = []
            for column in range(column_count):
                item = self.item(row.row(), column)
                if item is None:
                    row_data.append("")
                else:
                    row_data.append(f"'{item.text()}'")
            clipboard.setText(clipboard.text() + ", ".join(row_data) + "\n")


class SearchWidget(QtWidgets.QWidget):
    def __init__(self, columns: list[str], database_class=None, parent=None):
        super().__init__(parent)

        self.database_class = database_class  # The associated database table
        self.search_results = []  # The list of search results
        self.columns = columns

        self.pagination_record_limit = 100
        """Number of records to show per page"""
        self.pagination_start_record = 1
        """Record number to start at"""
        self.pagination_records = []  # type: list[list[str]]
        """List of all records to show"""

        self.setContentsMargins(0, 0, 0, 0)
        self.setObjectName("SearchWidget")

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.setObjectName("main_layout")

        self.search_data_form = QtWidgets.QFormLayout()  # User specified data
        self.search_data_form.setContentsMargins(0, 0, 0, 5)
        self.search_data_form.setSpacing(5)
        self.search_data_form.setObjectName("search_data_form")
        self.main_layout.addLayout(self.search_data_form)

        self.search_data_vertical_layout = QtWidgets.QVBoxLayout()
        self.search_data_vertical_layout.setContentsMargins(0, 0, 0, 10)
        self.search_data_vertical_layout.setSpacing(0)
        self.search_data_vertical_layout.setObjectName(
            "search_data_vertical_layout")
        self.main_layout.addLayout(self.search_data_vertical_layout)

        self.search_button_layout = QtWidgets.QHBoxLayout()
        self.search_button_layout.setContentsMargins(0, 0, 0, 10)
        self.search_button_layout.setSpacing(5)
        self.search_button_layout.setObjectName("search_button_layout")

        self.search_button = QtWidgets.QPushButton("Search")
        self.search_button.setFixedSize(50, 25)
        self.search_button.setObjectName("search_button")
        self.advanced_search_button = QtWidgets.QPushButton("Advanced Search")
        self.advanced_search_button.setFixedSize(100, 25)
        self.advanced_search_button.setObjectName("advanced_search_button")
        self.search_button_layout.addStretch(1)
        self.search_button_layout.addWidget(self.search_button)
        self.search_button_layout.addWidget(self.advanced_search_button)
        self.main_layout.addLayout(self.search_button_layout)

        self.results_table = CustomQTableWidget()
        self.results_table.setObjectName("results_table")
        self.results_table.set_table_headers(self.columns)
        self.main_layout.addWidget(self.results_table)

        self.view_button_layout = QtWidgets.QHBoxLayout()
        self.view_button_layout.setContentsMargins(0, 10, 0, 0)
        self.view_button_layout.setSpacing(5)
        self.view_button_layout.setObjectName("view_button_layout")

        self.view_button = QtWidgets.QPushButton("View")
        self.view_button.setEnabled(False)
        self.results_table.itemSelectionChanged.connect(
            lambda: self.view_button.setEnabled(True))
        self.view_button.setFixedSize(50, 25)
        self.view_button.setObjectName("view_button")
        self.view_button_layout.addStretch(1)
        self.view_button_layout.addWidget(self.view_button)
        self.main_layout.addLayout(self.view_button_layout)

        self.pagination_layout = QtWidgets.QHBoxLayout()
        self.pagination_layout.setContentsMargins(0, 10, 0, 0)
        self.pagination_layout.setSpacing(5)
        self.pagination_layout.setObjectName("pagination_layout")

        self.previous_page_button = QtWidgets.QPushButton("Previous")
        self.previous_page_button.clicked.connect(self.previous_page)
        self.previous_page_button.setEnabled(False)
        self.previous_page_button.setFixedSize(75, 25)
        self.previous_page_button.setObjectName("previous_page_button")
        self.next_page_button = QtWidgets.QPushButton("Next")
        self.next_page_button.clicked.connect(self.next_page)
        self.next_page_button.setEnabled(False)
        self.next_page_button.setFixedSize(75, 25)
        self.next_page_button.setObjectName("next_page_button")
        self.pagination_label = QtWidgets.QLabel("")
        self.pagination_label.mouseDoubleClickEvent = self.pagination_label_double_click
        self.update_pagination_label()
        self.pagination_label.setObjectName("pagination_label")
        self.pagination_layout.addWidget(
            self.previous_page_button, alignment=QtCore.Qt.AlignLeft)
        self.pagination_layout.addWidget(
            self.pagination_label, alignment=QtCore.Qt.AlignCenter)
        self.pagination_layout.addWidget(
            self.next_page_button, alignment=QtCore.Qt.AlignRight)
        self.main_layout.addLayout(self.pagination_layout)

        self.setLayout(self.main_layout)

    @staticmethod
    def clean_line_edit_text(line_edit: QtWidgets.QLineEdit) -> None:
        line_edit.setText(line_edit.text().strip())

    def update_pagination(self) -> None:
        """Updates pagination"""
        self.previous_page_button.setEnabled(self.pagination_start_record > 1)
        self.next_page_button.setEnabled(
            self.pagination_start_record + self.pagination_record_limit < len(self.pagination_records))
        self.update_pagination_label()

        # Update table
        records = self.pagination_records[self.pagination_start_record -
                                          1:self.pagination_start_record + self.pagination_record_limit - 1]
        self.results_table.setRowCount(len(records))
        for row, record in enumerate(records):
            for col, value in enumerate(record):
                self.results_table.setItem(
                    row, col, QtWidgets.QTableWidgetItem(value))

    def next_page(self) -> None:
        """Moves to the next page"""
        self.pagination_start_record += self.pagination_record_limit
        self.update_pagination()

    def previous_page(self) -> None:
        """Moves to the previous page"""
        self.pagination_start_record -= self.pagination_record_limit
        self.update_pagination()

    def add_record(self, data: list[str]):
        self.results_table.insert_row_data(data)
        self.pagination_records.append(data)
        self.update_pagination()

    def set_record_data(self, data: list[list[str]]):
        self.pagination_records = []  # type: list[list[str]]
        for record in data:
            self.add_record(record)
        self.results_table.horizontalHeader().resizeSections(
            QtWidgets.QHeaderView.ResizeToContents)

    def update_pagination_label(self):
        self.pagination_label.setText(
            f"Records {self.pagination_start_record} - {self.pagination_start_record + self.pagination_record_limit - 1} of {len(self.pagination_records)}")

    def add_search_form_field(self, label: str, field: QtWidgets.QWidget):
        """Adds a search field to the search layout"""
        if isinstance(field, QtWidgets.QLineEdit):
            field.editingFinished.connect(
                lambda: self.clean_line_edit_text(field))
        self.search_data_form.addRow(QtWidgets.QLabel(label), field)

    def add_search_field(self, field: QtWidgets.QWidget, stretch: int = 0, alignment: QtCore.Qt.Alignment = QtCore.Qt.AlignLeft):
        """Adds a search field to the vertical layout below the search form."""
        if isinstance(field, QtWidgets.QLineEdit):
            field.editingFinished.connect(
                lambda: self.clean_line_edit_text(field))
        self.search_data_vertical_layout.addWidget(field, stretch, alignment)

    def change_pagination(self, value: int) -> None:
        self.pagination_record_limit = value
        self.update_pagination()

    def pagination_label_double_click(self, event):
        super().mouseDoubleClickEvent(event)

        # Open a dialog to change the number of records to show per page
        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle("Change Pagination")
        dialog.setFixedSize(250, 60)
        dialog.setWindowModality(QtCore.Qt.ApplicationModal)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        layout.setObjectName("layout")

        label = QtWidgets.QLabel("Records per page:")
        label.setObjectName("label")

        spinbox = QtWidgets.QSpinBox()
        spinbox.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        spinbox.setMinimum(1)
        spinbox.setMaximum(1000)
        spinbox.setValue(self.pagination_record_limit)
        spinbox.setObjectName("spinbox")
        spinbox.selectAll()

        form_layout = QtWidgets.QFormLayout()
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(5)
        form_layout.setObjectName("form_layout")
        form_layout.addRow(label, spinbox)
        layout.addLayout(form_layout)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(0)
        button_layout.setObjectName("button_layout")

        ok_button = QtWidgets.QPushButton("Ok")
        ok_button.setFixedSize(75, 25)
        ok_button.setObjectName("ok_button")
        button_layout.addWidget(ok_button)
        layout.addLayout(button_layout)

        dialog.setLayout(layout)

        ok_button.clicked.connect(
            lambda: self.change_pagination(spinbox.value()))
        ok_button.clicked.connect(dialog.close)
        dialog.exec()

    # def reload(self, search_criteria=None) -> None:
    #     """Reloads the search table."""
    #     self.search_results = []

    #     # TODO: Implement search criteria.
    #     if search_criteria:
    #         self.search_results = global_session.query(self.database_class).all()
    #     else:
    #         self.search_results = global_session.query(self.database_class).all()

    #     data = []
    #     for result in self.search_results:
    #         row = []
    #         for column in self.columns:
    #             row.append(getattr(result, column[1]))
    #         data.append(row)

    #     self.set_record_data(data)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout()

    def on_search_clicked():
        print(field_1.text())
        print(field_2.currentText())

    search_widget = SearchWidget()
    search_widget.search_button.clicked.connect(on_search_clicked)
    field_1 = QtWidgets.QLineEdit()
    field_2 = QtWidgets.QComboBox()
    field_2.addItems(["a", "b", "c"])
    search_widget.add_search_field(QtWidgets.QLabel("Field 1"), field_1)
    search_widget.add_search_field(QtWidgets.QLabel("Field 2"), field_2)

    data = []
    for i in range(1000):
        row = []
        for _ in range(3):
            row.append(f"Record {i}")
        data.append(row)

    search_widget.set_record_data(data)

    layout.addWidget(search_widget)
    widget.setLayout(layout)
    widget.show()
    sys.exit(app.exec_())
