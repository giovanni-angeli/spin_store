#!/usr/bin/env python
# coding: utf-8

import os
import sys

sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

from setup import SETUP_KW_ARGS

PY_VENV_PATH = "/opt/venvs/TMP_py_venv"  # where to create virtual env

TARGET_URL = "admin@192.168.0.100"
TARGET_USER_HOME = "/home/admin"

# ~ the path used to store temporarly built artifacts (the wheel), used as:
# ~     --dist-dir (-d)   directory to put final built distributions in
DIST_DIR = "/opt/DIST_DIR"

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

VERSION = SETUP_KW_ARGS["version"]
APP_NAME = SETUP_KW_ARGS["name"]

here = os.path.dirname(__file__)
sys.path.append(os.path.join('..', here)) 

from maker import main

main(root_path=ROOT_PATH,
    version=VERSION,
    app_name=APP_NAME,
    dist_dir=DIST_DIR,
    target_url=TARGET_URL,
    py_venv_path=PY_VENV_PATH, 
    target_user_home=TARGET_USER_HOME)
    

