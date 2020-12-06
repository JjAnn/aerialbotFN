# Aerial Loader
# Responsible for orchestrating updates, accounts, database management, etc.

import os
import subprocess
import asyncio
import logging
import sys
import logging
import sqlite3
import json
from webbrowser import open as openurl
from time import sleep


# Custom Logger
try:
    from logger import Logger
    logging.setLoggerClass(Logger)
except ImportError:
    print("Warning: cannot load file 'logger.py'. Logging will lack color.")
log = logging.getLogger("Aerial Main")


# Version-specific Python command, avoids situations where the default
# Python version is different from the one used to run the script.
python = "python" + str(sys.version_info[0]) + "." + str(sys.version_info[1])


# Installing & Upgrading Requirements
log.info("$CYANUpdating Packages... $RESET(This might take a minute)")
subprocess.check_call(
    [python, "-m", "ensurepip"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)
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
        "pyyaml",
        "aiohttp[speedups]"
    ],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)


import aiohttp
import prompt_toolkit
import fortnitepy
from fortnitepy.ext import commands


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

if not c.fetchone() or "--reset-database" in sys.argv:
    log.info("$GREENCreating Database...")
    c.execute("""DROP TABLE IF EXISTS `accounts`;""")
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
    c.close()
    if sys.stdin.isatty():
        log.info("Press CTRL+C when you have created all accounts.")
        while True:
            log.info("$GREENCreating Account...")

            with prompt_toolkit.patch_stdout.patch_stdout():
                try:
                    email = prompt_toolkit.prompt("Enter Email: ")
                    password = prompt_toolkit.prompt("Enter Password: ", is_password=True)
                except KeyboardInterrupt:
                    break

            log.info("Opening Browser...")
            log.info("Please sign in with the $CYAN$BOLDbot account $RESET$WHITEand $CYAN$BOLDcopy paste everything here$RESET$WHITE.")
            sleep(2)
            openurl("https://www.epicgames.com/id/login/epic?redirect_uri=https%3A%2F%2Fwww.epicgames.com%2Fid%2Fapi%2Fredirect%3FclientId%3D3446cd72694c4a4485d81b77adbb2141%26responseType%3Dcode")

            with prompt_toolkit.patch_stdout.patch_stdout():
                try:
                    return_url = prompt_toolkit.prompt("Paste Here & Press Enter: ")
                except KeyboardInterrupt:
                    break

            authorization_code = json.loads(return_url)["redirectUrl"].split("https://accounts.epicgames.com/fnauth?code=")
            log.info("Spinning Up Temporary Client...")
            client = fortnitepy.Client(auth=fortnitepy.AdvancedAuth(
                email=email,
                password=password,
                authorization_code=authorization_code
            ))

            @client.event
            async def event_device_auth_generate(details: dict, email: str):
                global password
                c = db.cursor()
                c.execute(
                    """INSERT INTO `accounts`
                    ('email', 'password', 'device_id', 'account_id', 'secret')
                    VALUES ('%s', '%s', '%s', '%s', '%s')"""
                    % (email, password, details["device_id"], details["account_id"], details["secret"])
                )
                c.close()
                log.info("$GREENSaved Device Details! Shutting Down...")

            @client.event
            async def event_ready():
                log.warning("Client is ready when it is not expected to be.")
                log.warning("Device details may or may not have been saved.")
                await client.close()

            client.run()


# Loading Clients
clients = []
c = db.cursor()
c.execute("""SELECT * FROM `accounts`;""")
for data in c.fetchall():
    clients.append(
        commands.Bot(
            command_prefix="/",
            auth=fortnitepy.AdvancedAuth(
                email=data[1],
                password=data[2],
                device_id=data[3],
                account_id=data[4],
                secret=data[5]
            )
        )
    )


# Loading Extensions
for ext in os.listdir("extensions"):
    if ext.endswith(".py") and os.path.isfile(f"extensions/{ext}.py"):
        try:
            for c in clients:
                c.load_extension(f"extensions.{ext[:-3]}")
            log.info(f"$GREENLoaded Extension $CYAN{ext[:-3]}$GREEN.")
        except:
            log.warning(f"Cannot Load Extension $CYAN{ext}$YELLOW.")

    elif os.path.isdir(f"extensions/{ext}") and os.path.isfile(f"extensions/{ext}/main.py"):
        if os.path.isfile(f"extensions/{ext}/requirements.txt"):
            subprocess.check_call(["pip3", "install", "-U", "-r", f"extensions/{ext}/requirements.txt"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            for c in clients:
                c.load_extension(f"extensions.{ext}.main")
            log.info(f"$GREENLoaded Extension $CYAN{ext}$GREEN.")
        except:
            log.warning(f"Cannot Load Extension $CYAN{ext}$YELLOW.")
