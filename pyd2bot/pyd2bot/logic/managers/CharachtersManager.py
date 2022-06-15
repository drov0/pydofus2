import json
import os
from pyd2bot.pyd2bot.BotConstants import BotConstants

BOTSDB = BotConstants.PERSISTENCE_DIR / "charachters.json"


class CharachtersManager:
    if not os.path.exists(BOTSDB):
        with open(BOTSDB, "w") as fp:
            json.dump({}, fp)
    with open(BOTSDB, "r") as fp:
        _db = json.load(fp)

    @classmethod
    def addEntry(cls, name, account, charId, serverId):
        cls._db.update(
            {
                name: {
                    "accountId": account,
                    "charachterId": int(charId),
                    "serverId": int(serverId),
                }
            }
        )
        with open(BOTSDB, "w") as fp:
            json.dump(cls._db, fp, indent=4)

    @classmethod
    def getEntry(cls, name):
        result = cls._db.get(name)
        if not result:
            raise Exception(f"Bot {name} not found")
        return result


if __name__ == "__main__":
    import sys

    botName = sys.argv[1]
    account = sys.argv[2]
    serverId = int(sys.argv[3])
    charachterId = int(sys.argv[4])
    CharachtersManager.addEntry(botName, account, charachterId, serverId)
