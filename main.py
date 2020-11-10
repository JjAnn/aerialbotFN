# Aerial Loader
# Responsible for orchestrating updates, accounts, database management, etc.

import os
import subprocess
import logging
import sys
import logging

try: from logger import Logger
except ImportError:
    sys.exit(
        "Cannot locate one or more necessary files.\n" + 
        "Make sure that you are running the script from the right folder."
    )

# Version-specific Python command, avoids situations where the default
# Python version is different from the one used to run the script.
python = "python" + str(sys.version_info[0]) + "." + str(sys.version_info[1])

# Installing & Upgrading Requirements
subprocess.check_call(
    [python, "-m", "pip", "install", "-U", "pip", "fortnitepy", "websockets"],
    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
)

# TBD: literally everything else, im watching the apple event rn lol
