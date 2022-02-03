class Error(Exception):
    """Base class for other exceptions"""

    pass


class PrinterNotFoundError(Error):
    """Raised when the printer is not found"""

    pass


class InvalidLabelFileError(Error):
    """Raised when the label file is invalid"""

    pass


class MissingRequiredSoftwareError(Error):
    """Raised when a missing software package is missing or not found."""

    pass


class MissingRequiredSheetError(Error):
    """Raised when a required sheet is missing."""

    pass


class MissingRequiredColumnError(Error):
    """Raised when a required column is missing."""

    pass
