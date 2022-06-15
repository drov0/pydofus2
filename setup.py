from pathlib import Path
import site
import os

ROOTDIR = CURR_DIR = Path(__file__).parent
SITEDIR = site.getsitepackages()[0]
with open(os.path.join(SITEDIR, "pydofus2.pth"), "w+") as fp:
    fp.write(str(ROOTDIR / "pydofus2"))
with open(os.path.join(SITEDIR, "pyd2bot.pth"), "w+") as fp:
    fp.write(str(ROOTDIR / "pyd2bot"))
