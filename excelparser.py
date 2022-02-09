import pandas
from dataclasses import dataclass
from errors import *


@dataclass
class RequiredSheet:
    """A class to represent a required sheet."""

    name: str
    columns: list


from settings import *


def validate_dataframe(dataframe: pandas.DataFrame):
    """Validate the dataframe."""
    missing_sheets = []
    missing_columns = []
    for required_sheet in REQUIRED_SHEETS:
        if required_sheet.name not in dataframe:
            missing_sheets.append(required_sheet.name)

        if (
            not dataframe[required_sheet.name]
            .columns.isin(required_sheet.columns)
            .all()
        ):
            missing_columns.append(required_sheet.name)

    if missing_sheets:
        raise MissingRequiredSheetError(f"Missing required sheets: {missing_sheets}")
    elif missing_columns:
        raise MissingRequiredColumnError(f"Missing required columns: {missing_columns}")


def parse_excel(file_path: str) -> pandas.DataFrame:
    """Parse an excel file."""
    df = pandas.read_excel(file_path, sheet_name=None)
    validate_dataframe(df)
    return df
