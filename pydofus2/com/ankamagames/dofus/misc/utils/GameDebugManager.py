from com.ankamagames.jerakine.metaclasses.Singleton import Singleton


class GameDebugManager(metaclass=Singleton):

    buffsDebugActivated: bool = True

    haxeGenerateTestFromNextSpellCast: bool = True

    haxeGenerateTestFromNextSpellCast_stats: bool = True

    haxeGenerateTestFromNextSpellCast_infos: bool = True

    detailedFightLog_unGroupEffects: bool = True

    detailedFightLog_showIds: bool = True

    detailedFightLog_showEverything: bool = True

    detailedFightLog_showBuffsInUi: bool = True
