from __future__ import annotations
import platform
import logging
import os
import ctypes
import sys
import math
import pandas
import datetime
import json
from logging.config import dictConfig
from PyQt5 import QtCore, QtGui, QtWidgets


from utilities import *
from errors import *
from mainwindow import Ui_MainWindow
from excelparser import parse_excel, REQUIRED_SHEETS, CUT_SHEET_NAME
from label import Label
from printer import DymoLabelPrinter
from settings import *
from update import check_for_updates


COLUMNS = ["Line", "Bundles"]
for required_sheet in REQUIRED_SHEETS:
    if required_sheet.name != CUT_SHEET_NAME:
        continue
    for column in required_sheet.columns:
        COLUMNS.append(column)


settings = QtCore.QSettings(COMPANY_NAME, PROGRAM_NAME)

# Default log settings

MAX_LOG_SIZE_MB = (
    DefaultSetting(
        settings=settings, group_name="Logging", name="max_log_size_mb", value=5
    )
    .initialize_setting()
    .value
)
MAX_LOG_COUNT = (
    DefaultSetting(
        settings=settings, group_name="Logging", name="max_log_count", value=3
    )
    .initialize_setting()
    .value
)
LOG_LEVEL = (
    DefaultSetting(
        settings=settings, group_name="Logging", name="log_level", value=logging.INFO
    )
    .initialize_setting()
    .value
)


# Default program settings
MAX_LABEL_COUNT = (
    DefaultSetting(
        settings=settings, group_name="Program", name="max_label_count", value=100
    )
    .initialize_setting()
    .value
)
REMOVE_PRINTED_LABELS = (
    DefaultSetting(
        settings=settings,
        group_name="Program",
        name="remove_printed_labels",
        value=True,
    )
    .initialize_setting()
    .value
)
DEBUG = (
    DefaultSetting(settings=settings, group_name="Program", name="debug", value=False)
    .initialize_setting()
    .value
)
if DEBUG == "true":
    DEBUG = True
else:
    DEBUG = False

DISSABLE_LABEL_PRINTING = (
    DefaultSetting(
        settings=settings,
        group_name="Program",
        name="disable_label_printing",
        value=False,
    )
    .initialize_setting()
    .value
)
if DISSABLE_LABEL_PRINTING == "true":
    DISSABLE_LABEL_PRINTING = True
else:
    DISSABLE_LABEL_PRINTING = False


if DEBUG:
    LOG_LEVEL = logging.DEBUG


dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "format": "%(asctime)s [%(levelname)s] in %(module)s: %(message)s",
            },
            "console": {
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "format": "[%(name)s] %(asctime)s [%(levelname)s] in %(module)s: %(message)s",
            },
        },
        "handlers": {
            "backend_log_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(LOG_FOLDER, BACK_END_LOG_FILE),
                "maxBytes": MAX_LOG_SIZE_MB * 1024 * 1024,
                "backupCount": MAX_LOG_COUNT,
                "formatter": "default",
            },
            "frontend_log_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": os.path.join(LOG_FOLDER, FRONT_END_LOG_FILE),
                "maxBytes": MAX_LOG_SIZE_MB * 1024 * 1024,
                "backupCount": MAX_LOG_COUNT,
                "formatter": "default",
            },
            "console": {"class": "logging.StreamHandler", "formatter": "console"},
        },
        "loggers": {
            "root": {
                "level": LOG_LEVEL,
                "handlers": ["backend_log_file", "frontend_log_file", "console"],
            },
            "backend": {
                "level": LOG_LEVEL,
                "handlers": ["backend_log_file", "console"],
            },
            "frontend": {
                "level": LOG_LEVEL,
                "handlers": ["frontend_log_file", "console"],
            },
        },
    }
)

# Create the loggers
root_logger = logging.getLogger("root")
backend_logger = logging.getLogger("backend")
frontend_logger = logging.getLogger("frontend")


class UserDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(UserDialog, self).__init__(parent)

        self.setWindowTitle("User")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.user = None  # type: User

        self.first_name_label = QtWidgets.QLabel("First Name:")
        self.first_name_input = QtWidgets.QLineEdit()
        self.last_name_label = QtWidgets.QLabel("Last Name:")
        self.last_name_input = QtWidgets.QLineEdit()

        self.ok_button = QtWidgets.QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)

        self.main_layout = QtWidgets.QVBoxLayout()
        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow(self.first_name_label, self.first_name_input)
        form_layout.addRow(self.last_name_label, self.last_name_input)

        self.main_layout.addWidget(
            QtWidgets.QLabel("Please enter your name to continue."), stretch=1
        )
        self.main_layout.addLayout(form_layout)
        self.main_layout.addWidget(self.ok_button)
        self.setLayout(self.main_layout)

        self.first_name_input.setFocus()
        self.first_name_input.setText(settings.value("User/first_name", ""))
        self.last_name_input.setText(settings.value("User/last_name", ""))

    def accept(self) -> None:
        first_name = self.first_name_input.text().strip()
        last_name = self.last_name_input.text().strip()
        if len(first_name) == 0 or len(last_name) == 0:
            frontend_logger.error("First and last name must be entered.")
            QtWidgets.QMessageBox.warning(
                self,
                "Missing Information",
                "Please enter your first and last name.",
            )
            return
        self.user = User(first_name, last_name)
        backend_logger.debug(f"Saving User: {self.user}")
        settings.setValue("User/first_name", first_name)
        settings.setValue("User/last_name", last_name)
        super().accept()


class CustomerNameDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(CustomerNameDialog, self).__init__(parent)

        self.setWindowTitle("Customer Name")
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint
        )
        self.setStyleSheet(
            """
            QDialog {
                background-color: #f0f0f0;
                border: 2px solid #d0d0d0;
                border-radius: 5px;
            }
            """
        )

        self.customer_name = ""

        self.name_label = QtWidgets.QLabel("Name:")
        self.name_input = QtWidgets.QLineEdit()

        self.ok_button = QtWidgets.QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)

        self.main_layout = QtWidgets.QVBoxLayout()
        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow(self.name_label, self.name_input)
        self.main_layout.addWidget(
            QtWidgets.QLabel("Please enter the customer's name.")
        )
        self.main_layout.addLayout(form_layout)
        self.main_layout.addWidget(self.ok_button)
        self.setLayout(self.main_layout)

        self.name_input.setFocus()

    def accept(self) -> None:
        self.customer_name = self.name_input.text().strip()
        if len(self.customer_name) == 0:
            frontend_logger.error("Customer name must be entered.")
            QtWidgets.QMessageBox.warning(
                self,
                "Missing Information",
                "Please enter the customer's name.",
            )
            return
        frontend_logger.info(f"Setting Customer Name: {self.customer_name}")
        super().accept()


class MainWindow(Ui_MainWindow, QtWidgets.QMainWindow):
    def __init__(self) -> object:
        super().__init__()

        self.dataframe = None  # type: pandas.DataFrame
        self.wire_bundle_label = Label("./templates/WireBundleLabel.label")
        self.user = None  # type: User
        self.previous_label = None  # type: Label
        self.customer_name = ""

        dialog = UserDialog()
        dialog.exec()
        if dialog.user is None:
            sys.exit(0)
        self.user = dialog.user
        root_logger.info(f"User: {self.user}")

        try:
            self.printer = DymoLabelPrinter()
        except MissingRequiredSoftwareError as error:
            root_logger.error(
                f"There is a missing software program required to run: {error}"
            )

            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setWindowTitle("Missing Required Software")
            msg.setText(str(error))
            msg.setInformativeText(
                "After clicking OK, the correct software will attempt to install. Note: This program will not work without this software."
            )
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msg.exec_()
            try:
                ctypes.windll.shell32.ShellExecuteW(
                    None,
                    "runas",
                    os.path.realpath(
                        os.path.join(
                            os.path.dirname(__file__),
                            "Dymo Software",
                            "DLS8Setup.8.7.exe",
                        )
                    ),
                )
            except Exception as error:
                root_logger.error("Could not find DLS8Setup.8.7.exe")
                root_logger.exception(error)
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Critical)
                msg.setWindowTitle("Missing Required Software")
                msg.setText(
                    "There was an issue running the software. Please try again."
                )
                msg.setDetailedText(str(error))
                msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
                msg.exec_()
            sys.exit(1)

        self.setupUi(self)
        self.tablewidget.set_table_headers(COLUMNS)
        # self.tablewidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.selected_printer_combobox.addItems(self.printer.PRINTERS)
        self.batch_size_spinbox.setMaximum(self.total_cut_qty_spinbox.value())

        self.setWindowTitle(f"{PROGRAM_NAME} v{VERSION}")
        if DEBUG:
            self.setWindowTitle(f"{PROGRAM_NAME} v{VERSION} - DEBUG MODE")
        self.connect_signals()

        # Restore program settings
        settings.beginGroup("MainWindow")
        try:
            self.restoreGeometry(settings.value("geometry"))
            self.selected_printer_combobox.setCurrentText(
                settings.value("selected_printer_name")
            )
        except Exception:
            pass
        settings.endGroup()

    def connect_signals(self):
        self.cut_sheet_browse_pushbutton.clicked.connect(self.cut_sheet_browse)
        self.reload_table_pushbutton.clicked.connect(self.reload_table)
        self.print_selected_pushbutton.clicked.connect(self.print_selected)
        self.print_previous_pushbutton.clicked.connect(self.print_previous)
        self.tablewidget.itemDoubleClicked.connect(self.print_selected)
        self.print_single_pushbutton.clicked.connect(self.print_single)
        self.total_cut_qty_spinbox.valueChanged.connect(
            self.on_total_cut_qty_spinbox_value_changed
        )

    def on_total_cut_qty_spinbox_value_changed(self):
        self.batch_size_spinbox.setMaximum(self.total_cut_qty_spinbox.value())

    def on_selected_printer_combobox_currentIndexChanged(self, index=None):
        self.printer.set_printer(self.selected_printer_combobox.currentText())

    def closeEvent(self, event=None):
        root_logger.info("Closing application.")

        backend_logger.debug("Saving window settings.")
        settings.beginGroup("MainWindow")
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue(
            "selected_printer_name", self.selected_printer_combobox.currentText()
        )
        settings.endGroup()

        self.close()

    def cut_sheet_browse(self):
        dir = settings.value("initial_cut_sheet_directory", "")
        file_path = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select Cut Sheet", dir, "Excel Files (*.xlsx)"
        )[0]

        frontend_logger.info(f"Selected cut sheet: {file_path}")

        if file_path == "":
            return
        try:
            self.customer_name = get_customer_name(file_path)
            frontend_logger.info(f"Customer Name: {self.customer_name}")
        except IndexError:
            frontend_logger.error("Could not find customer name. Prompting user.")
            dialog = CustomerNameDialog()
            dialog.exec()
            self.customer_name = dialog.customer_name

        self.cut_sheet_file_path_lineedit.setText(file_path)
        self.reload_table()
        self.print_selected_pushbutton.setEnabled(True)
        self.print_single_pushbutton.setEnabled(True)
        self.reload_table_pushbutton.setEnabled(True)

    def print_previous(self):
        frontend_logger.info("Printing previous label.")
        if self.previous_label is None:
            return

        timestamp = datetime.datetime.now().strftime(DATE_TIME_FORMAT)
        text = ", ".join(
            f"{key}: {value}" for key, value in self.previous_label.fields.items()
        )

        if DISSABLE_LABEL_PRINTING:
            frontend_logger.info(f"Printing label: {text}")
            return

        self.previous_label.set_field("timestamp", timestamp)
        self.printer.print(self.previous_label)

    def print_single(self):
        frontend_logger.info("Printing selected rows.")
        row_items = (
            self.tablewidget.selectedItems()
        )  # Flat list of all the selected items.
        column_count = self.tablewidget.columnCount()
        row_count = len(row_items) // column_count

        data = []
        to_remove = []
        for row in range(row_count):
            row_data = {}
            for column in range(column_count):
                column_heder = self.tablewidget.horizontalHeaderItem(column).text()
                row_data[column_heder] = row_items[row * column_count + column].text()
            to_remove.append(row_items[row * column_count + column].row())
            data.append(row_data)
            
        row["Bundles"] = 1
        self.print(data)

    def print(self, data: dict):
        part_number = get_part_number(self.cut_sheet_file_path_lineedit.text())
        for row in data:
            copies = int(row["Bundles"])
            timestamp = datetime.datetime.now().strftime(DATE_TIME_FORMAT)
            text = ""
            text += f"Cut By: {self.user.initials}\n"
            text += f"{self.customer_name} {part_number}\n"
            text += f'{row["Gauge"]}GA {row["Color"]} {row["Type"]}\n'
            text += f'{row["Length"]}\n'
            text += f'{row["Left Terminal"]}\n'
            text += f'{row["Right Terminal"]}'

            barcode = {
                "Timestamp": timestamp,
                "Cut By": self.user.json,
                "Customer": self.customer_name,
                "PN": part_number,
                "Wire": row["Gauge"] + "GA " + row["Color"] + " " + row["Type"],
                "Length": row["Length"].replace('"', ""),
                "Left Term": row["Left Terminal"],
                "Right Term": row["Right Terminal"],
            }

            self.wire_bundle_label.set_field("timestamp", timestamp)
            self.wire_bundle_label.set_field("left_text_box", text)
            self.wire_bundle_label.set_field("right_text_box", text)
            self.wire_bundle_label.set_field("barcode", json.dumps(barcode))

            self.previous_label = self.wire_bundle_label

            self.print_previous_pushbutton.setEnabled(True)

            if DISSABLE_LABEL_PRINTING:
                text = text = ", ".join(
                    f"{key}: {value}"
                    for key, value in self.wire_bundle_label.fields.items()
                )
                frontend_logger.info(f"Printing label: {text}")
            else:
                self.printer.print(self.wire_bundle_label, copies)

    def print_selected(self):
        frontend_logger.info("Printing selected rows.")
        row_items = (
            self.tablewidget.selectedItems()
        )  # Flat list of all the selected items.
        column_count = self.tablewidget.columnCount()
        row_count = len(row_items) // column_count

        data = []
        to_remove = []
        for row in range(row_count):
            row_data = {}
            for column in range(column_count):
                column_heder = self.tablewidget.horizontalHeaderItem(column).text()
                row_data[column_heder] = row_items[row * column_count + column].text()
            to_remove.append(row_items[row * column_count + column].row())
            data.append(row_data)

        self.print(data)

        if REMOVE_PRINTED_LABELS == "true":
            frontend_logger.info(f"Removing {len(to_remove)} label(s) from table.")
            for index in to_remove:
                frontend_logger.debug(f"Removing row: {index}")
                self.tablewidget.removeRow(index)

    def reload_table(self):
        frontend_logger.debug("Reloading table.")
        file_path = self.cut_sheet_file_path_lineedit.text()
        if file_path == "":
            return
        self.dataframe = parse_excel(file_path)

        cut_sheet = self.dataframe["Cut Sheet"]
        self.tablewidget.set_table_headers(COLUMNS)
        self.tablewidget.setRowCount(0)

        for row_index, row in cut_sheet.iterrows():
            if str(row["Qty"]) == "nan":
                frontend_logger.debug(
                    f"Skipping blank row {row_index + 2}."
                )  # +2 to make the number match the excel row number
                continue

            total_qty = self.total_cut_qty_spinbox.value()
            batch_size = self.batch_size_spinbox.value()
            bundles = math.ceil(total_qty / batch_size) * int(row["Qty"])

            self.tablewidget.insert_row_data(
                [
                    str(row_index + 1),
                    str(bundles),
                    str(int(row["Qty"])),
                    str(int(row["Gauge"])),
                    str(row["Type"]),
                    str(row["Color"]),
                    str(row["Length"]),
                    str(row["Left Strip"]),
                    str(row["Left Gap"]),
                    str(row["Right Strip"]),
                    str(row["Right Gap"]),
                    str(row["Left Terminal"]),
                    str(row["Right Terminal"]),
                ]
            )

        self.tablewidget.resizeColumnsToContents()
        self.print_previous_pushbutton.setEnabled(False)
        frontend_logger.debug(f"Inserted {len(cut_sheet)} rows.")


def main():
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    check_for_updates()
    app.exec_()


if __name__ == "__main__":
    root_logger.info("=" * 80)
    root_logger.info(f"Starting application... Version: {VERSION}")

    if DEBUG:
        root_logger.debug("Debug mode enabled.")

    if DISSABLE_LABEL_PRINTING:
        root_logger.warning(
            "Label printing is disabled. Labels will not be printed. However, each label will be logged."
        )

    # Log the os platform, version and architecture
    bits, linkage = platform.architecture()
    root_logger.info(
        f'{platform.system()} OS detected. Version: "{platform.version()}" Architecture: [Bits: "{bits}", Linkage: "{linkage}"]'
    )

    try:
        main()
    except Exception as error:
        root_logger.error("Application failed to start.")
        root_logger.exception(f"Exception: {error}")
        dialog = QtWidgets.QMessageBox()
        dialog.setWindowTitle("Fatal Error")
        dialog.setIcon(QtWidgets.QMessageBox.Critical)
        dialog.setText(f"Application failed to start.")
        dialog.setDetailedText(f"Exception: {error}")
        dialog.exec_()
        raise error
