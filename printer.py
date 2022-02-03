from __future__ import annotations
from win32com.client import Dispatch

import logging
import utilities
from errors import *
from label import Label

backend_logger = logging.getLogger("backend")


class DymoLabelPrinter:
    def __init__(self) -> object:
        self.printer_name = None
        self.label_file_path = None
        self.is_open = False

        try:
            self.printer_engine = Dispatch("Dymo.DymoAddIn")
            self.label_engine = Dispatch("Dymo.DymoLabels")
        except Exception as error:
            if error.strerror == "Invalid class string":
                raise MissingRequiredSoftwareError(
                    "Missing required software program. Please install DLS8Setup.8.7.exe."
                )

        printers = self.printer_engine.GetDymoPrinters()
        self.PRINTERS = [printer for printer in printers.split("|") if printer]
        backend_logger.info(f"Printers: {self.PRINTERS}")

    def __enter__(self):
        self.printer_engine.StartPrintJob()
        backend_logger.debug(
            f"Starting new print job. Selected printer: {self.printer_name}"
        )
        return self.printer_engine

    def __exit__(self, exc_type, exc_val, exc_tb):
        backend_logger.debug("Ending print job.")
        if exc_type is not None:
            backend_logger.exception(
                f"Exception occurred during print job. Exception: {exc_tb}"
            )
        self.printer_engine.EndPrintJob()

    def set_printer(self, printer_name: str):
        """Set the printer to use for printing."""
        if printer_name not in self.PRINTERS:
            backend_logger.error(f"Printer {printer_name} not found.")
            raise PrinterNotFoundError(f"Printer {printer_name} not found.")
        self.printer_engine.SelectPrinter(printer_name)
        backend_logger.info(f"Printer set to: {printer_name}")

    def print(self, label: Label, copies: int = 1):
        """Prints a label. This will set the file to what is defined in the label.
        Then it will set the fields to the values in the label."""
        self.register_label_file(label.file_path)

        for field, text in label.fields.items():
            self.set_field(field, text)

        with self as printer:
            backend_logger.debug(f"Printing {copies} copies.")
            printer.Print(copies, False)

    def set_field(self, field_name: str, field_value):
        """Set a field of the label."""
        backend_logger.debug(f"Setting field: {field_name} to: {field_value}")
        self.label_engine.SetField(field_name, field_value)

    def register_label_file(self, label_file_path: str) -> object:
        self.label_file_path = label_file_path
        self.is_open = self.printer_engine.Open(label_file_path)
        if not self.is_open:
            backend_logger.error(f"Could not open label file: {label_file_path}")
            raise InvalidLabelFileError(f"Could not open label file: {label_file_path}")
        backend_logger.debug(f"Label file set to: {label_file_path}")
