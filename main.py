# Aerial Loader
# Responsible for orchestrating updates, accounts, database management, etc.

import os
import subprocess
import logging
import sys
import logging
import sqlite3
from webbrowser import open as openurl

# Custom Logger
try:
    from logger import Logger

    logging.setLoggerClass(Logger)
except ImportError:
    print("Warning: cannot load file 'logging.py'. Logging will lack color.")

log = logging.getLogger("Aerial Main")

# Version-specific Python command, avoids situations where the default
# Python version is different from the one used to run the script.
python = "python" + str(sys.version_info[0]) + "." + str(sys.version_info[1])

# Installing & Upgrading Requirements
log.info("$CYANUpdating Packages...")
subprocess.check_call(
    [
        python,
        "-m",
        "pip",
        "install",
        "-U",
        "pip",
        "fortnitepy",
        "websockets",
        "prompt_toolkit",
    ],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

import aiohttp
import fortnitepy
import prompt_toolkit

# Prompt Setup
async def prompt():
    session = prompt_toolkit.PromptSession()
    while True:
        with prompt_toolkit.patch_stdout():
            try:
                cmd = await session.prompt_async("> ")
            except KeyboardInterrupt:
                continue
            except EOFError:
                break


# Database
db = sqlite3.connect("data.sqlite")
c = db.cursor()
c.execute(
    """SELECT `name` FROM `sqlite_master` WHERE TYPE = 'table' AND NAME = 'accounts';"""
)
if not c.fetchone():
    c.execute(
        """CREATE TABLE "accounts" (
              "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
              "email" varchar(255) NOT NULL,
              "password" varchar(255) NOT NULL,
              "device_id" varchar(255) NOT NULL,
              "account_id" varchar(255) NOT NULL,
              "secret" varchar(255) NOT NULL
            );"""
    )
