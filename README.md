# pyd2bot

This is a full socket bot for the mmorpg dofus2 all in python. It also include most of the game backend that can be used for other purposes.

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

## Create bot data (account and creds)

The following steps will help you setup, in a secure way, a bot account for your tests. Make sure to have one ready to use.

### Create RSA key pair to encrypt your account credentials

* Create a folder outside the repository for example `/c/keys`.
  
* Add a new environment variable `PASS_ENC_KEYS` pointing to this folder. In my case, since I use git bash, I edited my bashrc
  
```bash
vim ~/.bashrc
```

and I added the line `export PASS_ENC_KEY=/c/keys`. This variable is used by the launcher to find the key to use to encrypt your passwords before saving them.

* Then run :

```bash
make genKeys
```

> :warning: You may have to restart your terminal for the new variable to be added to env.

### Create an entry for your bot credentials

Example:

```bash
make createAccount entryName='grinder' login='myAccountAwsomeLogin' password='keepThisOneSafe'
```

> :warning: Make sure to put the password inside single quotes to avoid having problems with special chars.

### Create an entry for the bot charachter infos

Example:

```bash
make createBot botName='grinder' account='grinder' charachterId='335911059666' serverId='210'
```

> Here the 'account' arg should correspond to the entryName you chose for your account creds.

> :warning: If you don't know how to get your server ID and character Id. Start the sniffer 'make startSniffer', go to page localhost:8888 and login manually. Then look for serverSelectionMessage.

### Develop your own bot or run the existing examples

Under the folder bot_test_examples, you will fin a bunch of bot examples that uses this framework.

You can run one of them by setting in the main file of the example the variable `botName` by the one you chose to create your bot account. 

Basically to develop you own bot you have to implement in one or multiple `Frame` classes the logic of your bot and then register them in them file with the function `registerFrame`.

## For developpers 

### Setup dependencies for the sniffer 

Trought the course of the developement you will heavily rely on the sniffer to watch messages exchanged between the client and the server.

This repo comes with its own sniffer capable to dissect dofus protocol messages.

Before you can run the sniffer you have to install Wireshark (for the tshark module). [Link to download Wireshark](https://www.wireshark.org/download.html).

To run the sinffer:

```bash
make startSniffer
```

This command will start a server on [link to access the sniffer webui after start](http://localhost:8888)

If you want the page to automatically open on your browser set the env variable `WEB_BROWSER` with the path to your browser. 

For Edge users (like me), to get the browser path, visite the page `edge:version` on the browser it self, the of the field `Command-line` will contain the browser path. It should look like this `"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --profile-directory=Default --flag-switches-begin --flag-switches-end`.

Set the variable `WEB BROWSER` to `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe --profile-directory=Default --flag-switches-begin --flag-switches-end`
