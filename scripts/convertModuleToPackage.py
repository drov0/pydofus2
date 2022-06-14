import os
from subprocess import PIPE, Popen

path ="../pydofus2/pydofus2"

for root, dirs, files in os.walk(path):
    for dir in dirs:
        if not os.path.exists(os.path.join(root, dir, "__init__.py")):
            with open(os.path.join(root, dir, "__init__.py"), "w") as f:
                f.write("")