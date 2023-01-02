# pydofus2

This is a pyton client for the mmorpg dofus2 all in python. It includes most of the game backend and no front end stuff.

## Getting Started

First and foremost install Python 3.9.12, Its the version used to develop the project.

> :warning: You may encounter compatibility issues with higher versions. [Link to python 3.9.12 download page](https://www.python.org/downloads/release/python-3912/)

One thing you should keep in mind is that this will setup a virtual env for you to work on. If you get the error `ModuleNotFoundError: No module named 'com'` its most likely because you opened a new terminal and you didn't activate the virtual env of the project.

### Install node js

Install node js. It is needed to run the simulated launcher.

### For windows users install make

For windows users I recommend configuring git bash as your default terminal for the project in vscode and use it to setup the env.
To install `make` under Windows, one way is throught the `chocolatey` package manager.
[Follow this link to install chocolatey](https://www.liquidweb.com/kb/how-to-install-chocolatey-on-windows/)

> :warning: If you don't run the make rules of this tuto on git bash you may encounter some annoying problems.

### Setup the dev environment

The command bellow will do it all for you. It will create a new Python venv and install all the dependencies.
After running it make sure to activate the virtual environment for the next steps.

```bash
make setup
```

After the setup is done, don't forget to activate the environment:

```bash
source .venv/Scripts/activate
```

### Fetch the data from Dofus Invoker(protocol, keys, version, msgClasses, maps)

Before exectuting the command bellow make sure to have an updated version of the game installed on your machine.
This will fetch important data from the sources of the game.

```bash
make update
```

> :warning: This process takes quite some time so be patient.
