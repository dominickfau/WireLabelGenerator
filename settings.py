import os
from utilities import Version


COMPANY_NAME = "DF-Software"
PROGRAM_NAME = "Wire Cutting Label Generator"
VERSION = Version(major=1, minor=0, patch=3)
USER_HOME_FOLDER = os.path.expanduser("~")
COMPANY_FOLDER = os.path.join(USER_HOME_FOLDER, "Documents", COMPANY_NAME)
PROGRAM_FOLDER = os.path.join(COMPANY_FOLDER, PROGRAM_NAME)

# Logging
LOG_FOLDER = os.path.join(PROGRAM_FOLDER, "Logs")
FRONT_END_LOG_FILE = "frontend.log"
BACK_END_LOG_FILE = "backend.log"

# Program Settings
DATE_TIME_FORMAT = "%m-%d-%Y %H:%M"


# Github
GITHUB_USERNAME = "dominickfau"
GITHUB_REPO_NAME = "WireLabelGenerator"

GITHUB_LATEST_RELEASE_ENDPOINT = (
    f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO_NAME}/releases/latest"
)


if not os.path.exists(COMPANY_FOLDER):
    os.makedirs(COMPANY_FOLDER)

if not os.path.exists(PROGRAM_FOLDER):
    os.makedirs(PROGRAM_FOLDER)

if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)
