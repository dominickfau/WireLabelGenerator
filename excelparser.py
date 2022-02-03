import pandas

from errors import *
from utilities import get_part_number

FILE_PATH = "./templates/5001753.xlsx"

REQUIRED_SHEETS = {
    "Cut Sheet": [
        "Qty",
        "Gauge",
        "Type",
        "Color",
        "Length",
        "Left Strip",
        "Left Gap",
        "Right Strip",
        "Right Gap",
        "Left Terminal",
        "Right Terminal",
    ]
}


def validate_dataframe(dataframe: pandas.DataFrame):
    """Validate the dataframe."""
    missing_sheets = []
    missing_columns = []
    for required_sheet_name, required_columns in REQUIRED_SHEETS.items():
        if required_sheet_name not in dataframe:
            missing_sheets.append(required_sheet_name)

        if not dataframe[required_sheet_name].columns.isin(required_columns).all():
            missing_columns.append(required_sheet_name)

    if missing_sheets:
        raise MissingRequiredSheetError(f"Missing required sheets: {missing_sheets}")
    elif missing_columns:
        raise MissingRequiredColumnError(f"Missing required columns: {missing_columns}")


def parse_excel(file_path: str) -> pandas.DataFrame:
    """Parse an excel file."""
    df = pandas.read_excel(file_path, sheet_name=None)
    validate_dataframe(df)
    return df


if __name__ == "__main__":
    part_number = get_part_number(FILE_PATH)
    print(f"Part number: {part_number}")
    df = parse_excel(FILE_PATH)
    print(df)
