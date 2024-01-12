# Pyd2bot Dev Tools

This repo gathers different scripts and hacks used to :
    - generate code from dofus sources.
    - sniff exchanged traffic between dofus client and server.
    - make file regrouping some important build commands.
    - hacky as to python script converted that does some good work
    - protocol builder to parse dofus2 protocol specs from the source code
    - scripts to unpakc dofus2 maps, generate message classes from spec ...

## Install Cx_freeze windows

To be able to install Cx_freeze in windows you will need some extra dev stuff.
You will need the version 3.9 of python.
You need windows 10 SDK, download it and install it from here [link](https://www.microsoft.com/en-us/download/details.aspx?id=26999)

## Build and package

One  very usefull make rule is the bdist one, its used to generate an exe executable from the pyd2bot and pydofus2 sources.
That exe file is the executable used by kamator front end to launch pyd2bot sessions.
For that rule to work make sure to clone pyd2bot and pydofus2 in the parent directory of this repo (lets say we cloned it in devops dir).
| - devops\
\t| - MyTests\
\t..\
| - pyd2bot\
\t| - build.py\
\t..\
| - pydofus2\
\t..\
```make bdsit```

ou might need to setup log paths in windows:

```New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" `
-Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force```
## Sniffer App

The sniffer is based on wireshark you need to install it first
