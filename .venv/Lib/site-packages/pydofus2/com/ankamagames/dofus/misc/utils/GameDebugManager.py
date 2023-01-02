from pydofus2.com.ankamagames.jerakine.metaclasses.Singleton import Singleton


class GameDebugManager(metaclass=Singleton):

    buffsDebugActivated: bool = False

    haxeGenerateTestFromNextSpellCast: bool = False

    haxeGenerateTestFromNextSpellCast_stats: bool = False

    haxeGenerateTestFromNextSpellCast_infos: bool = False

    detailedFightLog_unGroupEffects: bool = False

    detailedFightLog_showIds: bool = False

    detailedFightLog_showEverything: bool = False

    detailedFightLog_showBuffsInUi: bool = False
