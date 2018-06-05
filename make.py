#!/usr/bin/env python
# coding: utf-8

import os
import sys
import six

sys.dont_write_bytecode = True
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

from setup import SETUP_KW_ARGS

if six.PY3:
    PY_VENV_PATH = "/opt/venvs/py3venv"  # where to create/use virtual env
if six.PY2:
    PY_VENV_PATH = "/opt/venvs/py2venv"  # where to create/use virtual env

TARGET_URL = "admin@192.168.0.100"
TARGET_PY_VENV_PATH = "/home/admin/py27venv"

# ~ the path used to store temporarly built artifacts (the wheel), used as:
# ~     --dist-dir (-d)   directory to put final built distributions in
DIST_DIR = "/opt/DIST_DIR"

ROOT_PATH = os.path.abspath(os.path.dirname(__file__))

VERSION = SETUP_KW_ARGS["version"]
APP_NAME = SETUP_KW_ARGS["name"]

here = os.path.dirname(__file__)
sys.path.append(os.path.join('..', here, 'devices')) 

from maker import main

main(root_path=ROOT_PATH,
    version=VERSION,
    app_name=APP_NAME,
    dist_dir=DIST_DIR,
    target_url=TARGET_URL,
    py_venv_path=PY_VENV_PATH, 
    target_py_venv_path=TARGET_PY_VENV_PATH)
    
