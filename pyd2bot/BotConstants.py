import os
from pathlib import Path


class BotConstants:
    PERSISTENCE_DIR = Path(os.getenv("APPDATA")) / "pyd2bot" / "persistence"
