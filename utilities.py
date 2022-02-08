from __future__ import annotations
from asyncio import protocols
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
class Version:
    """Class to hold the version information."""

    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    @property
    def total(self) -> int:
        return self.major + self.minor + self.patch

    def __eq__(self, __o: Version) -> bool:
        return self.total == __o.total

    def __lt__(self, __o: Version) -> bool:
        return self.total < __o.total

    def __gt__(self, __o: Version) -> bool:
        return self.total > __o.total

    def __le__(self, __o: Version) -> bool:
        return self.total <= __o.total

    def __ge__(self, __o: Version) -> bool:
        return self.total >= __o.total

    @staticmethod
    def from_string(version: str) -> Version:
        """Method to create a version object from a string."""
        major, minor, patch = parse_version(version)
        return Version(int(major), int(minor), int(patch))


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


def parse_version(version: str) -> tuple[int, int, int]:
    """Parse the version string.

    Args:
        version (str): The version string to parse.

    Returns:
        tuple[int, int, int]: Returns the major, minor, patch for the version.
    """
    version = version.replace("v", "")
    major, minor, patch = version.split(".")
    return major, minor, patch
