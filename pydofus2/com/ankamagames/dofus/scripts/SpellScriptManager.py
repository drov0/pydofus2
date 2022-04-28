from com.ankamagames.dofus.logic.game.common.misc.ISpellCastProvider import ISpellCastProvider
from com.ankamagames.dofus.scripts.spells.SpellScript1 import SpellScript1
from com.ankamagames.dofus.scripts.spells.SpellScript2 import SpellScript2
from com.ankamagames.dofus.scripts.spells.SpellScript3 import SpellScript3
from com.ankamagames.dofus.scripts.spells.SpellScript5 import SpellScript5
from com.ankamagames.dofus.scripts.spells.SpellScript6 import SpellScript6
from com.ankamagames.dofus.scripts.spells.SpellScript7 import SpellScript7
from com.ankamagames.dofus.scripts.spells.SpellScript8 import SpellScript8
from com.ankamagames.jerakine.logger.Log import Log
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.script.ScriptErrorEnum import ScriptErrorEnum
from com.ankamagames.jerakine.types.Callback import Callback
from com.ankamagames.jerakine.utils.errors.SingletonError import SingletonError

logger = Logger(__name__)
class SpellScriptManager:

    SPELL_SCRIPT_1:SpellScript1

    SPELL_SCRIPT_2:SpellScript2

    SPELL_SCRIPT_3:SpellScript3

    SPELL_SCRIPT_5:SpellScript5

    SPELL_SCRIPT_6:SpellScript6

    SPELL_SCRIPT_7:SpellScript7

    SPELL_SCRIPT_8:SpellScript8

    

    _self:SpellScriptManager

    def __init__(self):
        super().__init__()
        if _self != null:
            raise SingletonError("SpellScriptManager is a singleton and should not be instanciated directly.")

    def getInstance(self) -> SpellScriptManager:
        if _self == null:
            _self = SpellScriptManager()
        return _self

    def runSpellScript(self, spellScriptId:int, spellCastProvider:ISpellCastProvider, successCallback:Callback = None, errorCallback:Callback = None) -> None:
        returnCode:int = 0
        scriptClass:Class = None
        scriptRunner:SpellFxRunner = None
        try:
            scriptClass = getDefinitionByName("com.ankamagames.dofus.scripts.spells.SpellScript" + spellScriptId)
        except Exception as e:
            logger.error("Can't find class SpellScript"(+, spellScriptId)):
        if scriptClass:
            scriptRunner = SpellFxRunner(spellCastProvider)
            returnCode = scriptRunner.run(scriptClass)
        else:
            returnCode = ScriptErrorEnum.SCRIPT_ERROR
        if returnCode:
            errorCallback.exec()
        else:
            successCallback.exec()


