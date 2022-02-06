import os


COMPANY_NAME = "DF-Software"
PROGRAM_NAME = "Wire Cutting Label Generator"
PROGRAM_VERSION = "1.0.2"
USER_HOME_FOLDER = os.path.expanduser("~")
COMPANY_FOLDER = os.path.join(USER_HOME_FOLDER, "Documents", COMPANY_NAME)
PROGRAM_FOLDER = os.path.join(COMPANY_FOLDER, PROGRAM_NAME)

LOG_FOLDER = os.path.join(PROGRAM_FOLDER, "Logs")
FRONT_END_LOG_FILE = "frontend.log"
BACK_END_LOG_FILE = "backend.log"

DATABASE_FILE = os.path.join(PROGRAM_FOLDER, "database.db")

DATE_TIME_FORMAT = "%m-%d-%Y %H:%M"


if not os.path.exists(COMPANY_FOLDER):
    os.makedirs(COMPANY_FOLDER)

if not os.path.exists(PROGRAM_FOLDER):
    os.makedirs(PROGRAM_FOLDER)

if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)
