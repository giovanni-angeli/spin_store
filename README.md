
# spin_store

an example of django application using jsonschema on top of django models


## To build, install, test and run (for development):

```
    # READ and EDIT make.py, then::

    # 0. get hints:
    alfalib$ python make.py 
    available_actions:['build', 'create_venv', 'help', 'install', 'install_on_target', 'interact', 'test'].
    filtered actions:[].
    
    # 1. to create a virt env::
    alfalib$ python make.py create_venv

    # 2. build:
    alfalib$ python make.py build
    
    # 3. install the app into the virt env (all the required deps will be installed also),
    alfalib$ python make.py install
    
    # 4. run a test suite via "nose2" in the virt env:
    alfalib$ python make.py test
    
```

The make.py script is a home-made, specific tool to automate build/install/test cycle.
It is a wrapper instantiating the Maker class after setting some project-specific variables, letting the Maker be project-agnostic.

The Maker uses standard [python packaging tools](https://packaging.python.org) under the hood to build the distributable package (the python wheel) and 
    uses [nose2](http://nose2.readthedocs.io/en/latest/index.html) to run tests.

*make.py* and *maker.py* are, in the whole, less than 200 lines of code, you should **read**, **use** and **adapt** them.
