#!/usr/bin/env python
# coding: utf-8

import os
import sys
import logging
import time
import pprint

import six

""" Custom (hand-made) tool intended to be useful for:
    
    - setting up virtualenv,
    - build the pip-installable python-wheel of the package,
    - install the built python-wheel into the created virtualenv (eventually on a remote target),
    - test (using nose2) the built python-wheel into the created virtualenv.

    this gives the developer a tool to modify, build and test the project in closed form 
    and that can be directly inserted in a continuous integration framework.
    
    It is to be used via a wrapper script (see, e.g.: alfalib/make.py)
    and it uses std setup.py file (see, e.g.: alfalib/setup.py)
    
"""

class Maker(object):
    
    """ Here, each non private method (not o.startswith("_")) is an 'action', 
    i.e. something to be specified as input option when calling make.py (the wrapper).
    """

    def __init__(self, root_path,
                 version,
                 app_name,
                 dist_dir,
                 py_venv_path, # where creating virtual env
                 target_url="admin@192.168.0.100",
                 target_py_venv_path="/home/admin/python",
                 interactive_info_message=""):

        self.root_path = root_path
        self.version   = version  
        self.app_name  = app_name 
        self.dist_dir  = dist_dir
        self.py_venv_path = py_venv_path
        self.target_url = target_url
        self.target_py_venv_path = target_py_venv_path
        self.interactive_info_message = interactive_info_message

        self.activate = ". {}/bin/activate".format(self.py_venv_path)
        
        os.chdir(self.root_path)

        if six.PY3:
            self.wheel_fullname = '{}-{}-py3-none-any.whl'.format(self.app_name, self.version)
        elif six.PY2:
            self.wheel_fullname = '{}-{}-py2-none-any.whl'.format(self.app_name, self.version)
        
        self.available_actions = [o for o in dir(self) if not o.startswith("_") and callable(getattr(self, o))]

    def help(self):
        
        "Print help."

        action_list_ = [ "{}:   {}".format(a, getattr(self, a).__doc__) for a in self.available_actions]
        print("usage:\n\t{} [action1, [action2, [...]],]\n\navailable actions:\n{}\n\n".format(sys.argv[0], pprint.pformat(action_list_)))
        sys.exit(0)

    def create_venv(self):
        
        "re-build and setup the python virtual env"
        
        cmd_ = """(rm -fr {py_venv_path}/*; 
        virtualenv -p {python_executable} {py_venv_path}; 
        . {py_venv_path}/bin/activate ; 
        pip install --upgrade pip ; 
        pip install wheel)
        """.format(python_executable=sys.executable, py_venv_path=self.py_venv_path)
        
        os.system(cmd_)

    def build(self):

        "Build the wheel using 'setup.py bdist_wheel'."
        
        os.system("rm -f {}/{}*".format(self.dist_dir, self.wheel_fullname))

        setup_cmd = "{} setup.py bdist_wheel --dist-dir {}".format(sys.executable, self.dist_dir)
        if ("--quiet" in sys.argv):
            setup_cmd += " > /dev/null"
        os.system(setup_cmd)
        
        os.system("rm -fr build".format(self.version))
        os.system("rm -fr {}.egg-info".format(self.app_name, self.version))

    def install(self):

        "Install the wheel in virt env."

        uninstall_cmd = "{};pip uninstall -y {}".format(self.activate, self.app_name)
        install_cmd = "{};pip install {}/{}".format(self.activate, self.dist_dir, self.wheel_fullname)

        if ("--quiet" in sys.argv):
            uninstall_cmd += " > /dev/null"
            install_cmd += " > /dev/null"

        os.system(uninstall_cmd)
        os.system(install_cmd)

    def test(self):

        "Run tests with nose2."
        
        print("checking for nose2 to be available...")
        os.system("{};pip install nose2 > /dev/null".format(self.activate))

        # ~ let's pass this to the environ, in case tests use it.
        os.environ["PY_VENV_PATH"] = self.py_venv_path
        
        print("running tests with nose2 from:{} ...".format(os.getcwd()))
        os.system("{};nose2 --verbose".format(self.activate))

    def install_on_target(self):

        "Install the wheel to target. this is for development; for deploy, it should be (e.g.) translated to an ansible role."

        activate_on_target = ". {}/bin/activate".format(self.target_py_venv_path)

        cmds_ = [
            "scp {}/{} {}:{}/{}".format(self.dist_dir, self.wheel_fullname, self.target_url, self.target_py_venv_path, self.wheel_fullname),
            'ssh {} "{}; pip uninstall -y {}"'.format(self.target_url, activate_on_target, self.app_name),
            'ssh {} "{}; pip install {}/{}"'.format(self.target_url, activate_on_target, self.target_py_venv_path, self.wheel_fullname),
        ]
        
        for cmd_ in cmds_:
            print("executing cmd_:{}".format(cmd_))
            os.system(cmd_)

        
        # ~ os.system('ssh {} "{}; {} --post_install supervisor"'.format(
            # ~ self.target_url, activate_on_target, self.app_name))

        # ~ time.sleep(2)

        # ~ os.system('ssh {} "{}; sudo supervisorctl status {}"'.format(
            # ~ self.target_url, activate_on_target, self.app_name))

    def interact(self):
        
        "Run a ptipython session in the virt env where the package is installed: you can import, inspect and play with it. "
        
        print("starting ptipython in virtual env:{}.".format(self.py_venv_path))
        print(self.interactive_info_message)
        os.system("{};pip install ptipython --quiet".format(self.activate))
        os.system("{};ptipython".format(self.activate))



def main(*args, **kwargs):
    
    logging.debug("running Maker kwargs:{}".format(kwargs))

    m_ = Maker(**kwargs)

    print("available_actions:{}.".format(m_.available_actions))
    
    # ~ filter input options, searching for omonimous Maker's method
    actions_ = [a_ for a_ in sys.argv[1:] if a_ in m_.available_actions]
    
    print("filtered actions:{}.".format(actions_))

    # ~ execute actions
    for a_ in actions_:
        getattr(m_, a_)()
    
