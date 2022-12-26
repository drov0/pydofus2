#!/bin/bash
cd C:/Users/majdoub/botdev/dofusBotDev
source .venv/Scripts/activate
python pyd2bot/pyd2bot.py --host $1 --port $2 --id $3
