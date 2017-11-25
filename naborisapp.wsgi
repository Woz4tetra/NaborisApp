#!/usr/bin/python3
import sys
import logging
logging.basicConfig(stream=sys.stderr)

PROJECT_DIR = "/home/pi/NaborisApp/NaborisApp"
sys.path.insert(0, PROJECT_DIR)

from NaborisApp.NaborisApp import app as application
# application.secret_key = 's0mething'
application.debug = True
# application.threaded = True
