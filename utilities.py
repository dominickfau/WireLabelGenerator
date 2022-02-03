from __future__ import annotations
from typing import Any
from dataclasses import dataclass
from PyQt5.QtCore import QSettings


@dataclass
class DefaultSetting:
    """Default settings."""

    settings: QSettings
    group_name: str
    name: str
    value: Any

    def set(self, value) -> None:
        """Set the default setting."""
        self.value = value
        self.settings.beginGroup(self.group_name)
        self.settings.setValue(self.name, self.value)
        self.settings.endGroup()

    def initialize_setting(self) -> DefaultSetting:
        """Initialize the default setting or pulls the current setting value."""
        self.settings.beginGroup(self.group_name)
        if not self.settings.contains(self.name):
            self.settings.setValue(self.name, self.value)
        else:
            self.value = self.settings.value(self.name)
        self.settings.endGroup()
        return self


@dataclass
class User:
    first_name: str
    last_name: str

    def __str__(self) -> str:
        return self.full_name

    @property
    def json(self) -> dict:
        return {"first_name": self.first_name, "last_name": self.last_name}

    @property
    def full_name(self) -> str:
        """Get the full name of the user."""
        return f"{self.first_name}, {self.last_name}"

    @property
    def initials(self) -> str:
        """Get the initials of the user."""
        return f"{self.first_name[0]}{self.last_name[0]}".upper()


def get_file_name(file_path: str) -> str:
    """Get the file name."""
    return file_path.split("/")[-1].split(".")[0]


def get_part_number(file_path: str) -> str:
    """Get the part number."""
    return get_file_name(file_path).split(" ")[0]


def get_customer_name(file_path: str) -> str:
    """Get the customer name."""
    return get_file_name(file_path).split(" ")[1]
