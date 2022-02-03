from __future__ import annotations


class Label:
    """Represents a Dymo label."""

    def __init__(self, file_path: str):
        """Initialize the label."""
        self.file_path = file_path
        self.fields = {}  # type: dict[str, str] # field_name: value

    def set_field(self, field_name: str, value: str):
        """Set a field of the label."""
        self.fields[field_name] = value
