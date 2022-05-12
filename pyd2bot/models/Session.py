from com.ankamagames.dofus.internalDatacenter.spells.SpellWrapper import SpellWrapper
from pyd2bot.logic.managers.BotCredsManager import BotCredsManager
from pyd2bot.logic.managers.PathManager import PathManager


class Session:
    def __init__(self, charachterId, spellId, pathId, statToUp):
        self.charachterId = charachterId
        self.spellId = spellId
        self.pathId = pathId
        self.path = PathManager.getPath(str(pathId))
        self.creds = BotCredsManager.getEntry(str(charachterId))
        self.spellId = int(spellId)
        self.statToUp = statToUp
