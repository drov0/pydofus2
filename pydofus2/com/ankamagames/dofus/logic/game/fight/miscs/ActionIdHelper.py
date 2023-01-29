import json
import os
from pathlib import Path

CURRDIR = Path(os.path.dirname(os.path.realpath(__file__)))


class ActionIdHelper:

    STAT_BUFF_ACTION_IDS: list = [
        1027,
        283,
        293,
        110,
        118,
        125,
        2844,
        123,
        119,
        126,
        124,
        422,
        424,
        426,
        428,
        430,
        138,
        112,
        165,
        1054,
        414,
        416,
        418,
        420,
        1171,
        2808,
        2812,
        2800,
        2804,
        2802,
        2806,
        2814,
        2810,
        178,
        2872,
        226,
        225,
        1166,
        1167,
        240,
        243,
        241,
        242,
        244,
        1076,
        111,
        128,
        1144,
        182,
        210,
        211,
        212,
        213,
        214,
        117,
        115,
        174,
        176,
        1039,
        1040,
        220,
        158,
        161,
        160,
        752,
        753,
        776,
        412,
        410,
        121,
        150,
        2846,
        2848,
        2852,
        2850,
        2854,
        2856,
        2858,
        2860,
        2836,
        2838,
        2840,
        2834,
        2842,
        2844,
    ]

    STAT_DEBUFF_ACTION_IDS: list = [
        157,
        153,
        2845,
        152,
        154,
        155,
        156,
        423,
        425,
        427,
        429,
        431,
        186,
        145,
        415,
        417,
        419,
        421,
        1172,
        2809,
        2813,
        2801,
        2805,
        2803,
        2807,
        2815,
        2811,
        179,
        245,
        248,
        246,
        247,
        249,
        1077,
        168,
        169,
        215,
        216,
        217,
        218,
        219,
        116,
        171,
        175,
        177,
        159,
        163,
        162,
        754,
        755,
        413,
        411,
        2857,
        2855,
        2861,
        2859,
        2853,
        2851,
        2849,
        2847,
        2843,
        2841,
        2839,
        2837,
        2835,
    ]

    with open(CURRDIR / "actionIdToStatNameMap.json", "r") as fs:
        actionIdToStatNameMap = json.load(fs)

    with open(CURRDIR / "percentStatBoostActionIdToStat.json", "r") as fs:
        percentStatBoostActionIdToStat = json.load(fs)

    with open(CURRDIR / "flatStatBoostActionIdToStat.json", "r") as fs:
        flatStatBoostActionIdToStat = json.load(fs)

    with open(CURRDIR / "shieldActionsIdToStatId.json", "r") as fs:
        shieldActionIdToStatId = json.load(fs)

    @classmethod
    def isBasedOnCasterLife(cls, param1: int) -> bool:
        if not (
            cls.isBasedOnCasterLifePercent(param1)
            or cls.isBasedOnCasterLifeMidlife(param1)
            or cls.isBasedOnCasterLifeMissing(param1)
        ):
            return bool(cls.isBasedOnCasterLifeMissingMaxLife(param1))
        return True

    @classmethod
    def isBasedOnCasterLifePercent(cls, param1: int) -> bool:
        _loc2_: int = param1
        if _loc2_ != 85:
            if _loc2_ != 86:
                if _loc2_ != 87:
                    if _loc2_ != 88:
                        if _loc2_ != 89:
                            if _loc2_ != 90:
                                if _loc2_ != 671:
                                    return False
        return True

    @classmethod
    def isBasedOnCasterLifeMissing(cls, param1: int) -> bool:
        if param1 == 279 or param1 == 275 or param1 == 276 or param1 == 277 or param1 == 278:
            return True
        return False

    @classmethod
    def isBasedOnCasterLifeMissingMaxLife(cls, param1: int) -> bool:
        if param1 == 1118 or param1 == 1121 or param1 == 1122 or param1 == 1119 or param1 == 1120:
            return True
        return False

    @classmethod
    def isBasedOnCasterLifeMidlife(cls, param1: int) -> bool:
        return param1 == 672

    @classmethod
    def isSplash(cls, param1: int) -> bool:
        if not cls.isSplashDamage(param1):
            return bool(cls.isSplashHeal(param1))
        return True

    @classmethod
    def isSplashDamage(cls, param1: int) -> bool:
        if not cls.isSplashFinalDamage(param1):
            return bool(cls.isSplashRawDamage(param1))
        return True

    @classmethod
    def isSplashFinalDamage(cls, param1: int) -> bool:
        _loc2_: int = param1
        if _loc2_ != 1223:
            if _loc2_ != 1224:
                if _loc2_ != 1225:
                    if _loc2_ != 1226:
                        if _loc2_ != 1227:
                            if _loc2_ != 1228:
                                return False
        return True

    @classmethod
    def isSplashRawDamage(cls, param1: int) -> bool:
        _loc2_: int = param1
        if _loc2_ != 1123:
            if _loc2_ != 1124:
                if _loc2_ != 1125:
                    if _loc2_ != 1126:
                        if _loc2_ != 1127:
                            if _loc2_ != 1128:
                                return False
        return True

    @classmethod
    def isSplashHeal(cls, param1: int) -> bool:
        if param1 == 2020:
            return True
        return False

    @classmethod
    def isBasedOnMovementPoints(cls, param1: int) -> bool:
        if param1 == 1012 or param1 == 1013 or param1 == 1016 or param1 == 1015 or param1 == 1014:
            return True
        return False

    @classmethod
    def isBasedOnTargetLifePercent(cls, param1: int) -> bool:
        if param1 == 1071 or param1 == 1068 or param1 == 1070 or param1 == 1067 or param1 == 1069 or param1 == 1048:
            return True
        return False

    @classmethod
    def isTargetMaxLifeAffected(cls, param1: int) -> bool:
        if not (
            param1 == 1037
            or param1 == 153
            or param1 == 1033
            or param1 == 125
            or param1 == 1078
            or param1 == 610
            or param1 == 267
            or param1 == 2844
        ):
            return param1 == 2845
        return True

    @classmethod
    def isBasedOnTargetLife(cls, param1: int) -> bool:
        if not (cls.isBasedOnTargetLifePercent(param1) or cls.isBasedOnTargetMaxLife(param1)):
            return bool(cls.isBasedOnTargetLifeMissingMaxLife(param1))
        return True

    @classmethod
    def isBasedOnTargetMaxLife(cls, param1: int) -> bool:
        return param1 == 1109

    @classmethod
    def isBasedOnTargetLifeMissingMaxLife(cls, param1: int) -> bool:
        if param1 == 1092 or param1 == 1095 or param1 == 1096 or param1 == 1093 or param1 == 1094:
            return True
        return False

    @classmethod
    def isBoostable(cls, param1: int) -> bool:
        _loc2_: bool = False
        _loc3_: int = param1
        if _loc3_ != 80:
            if _loc3_ != 82:
                if _loc3_ != 144:
                    if _loc3_ != 1063:
                        if _loc3_ != 1064:
                            if _loc3_ != 1065:
                                if _loc3_ != 1066:
                                    _loc2_ = (
                                        cls.isBasedOnCasterLife(param1)
                                        or cls.isBasedOnTargetLife(param1)
                                        or cls.isSplash(param1)
                                    )
                                    if _loc2_ == True:
                                        return False
                                    return True
        return False

    @classmethod
    def isLifeSteal(cls, param1: int) -> bool:
        if (
            param1 == 95
            or param1 == 2828
            or param1 == 82
            or param1 == 92
            or param1 == 94
            or param1 == 91
            or param1 == 93
        ):
            return True
        return False

    @classmethod
    def isHeal(cls, param1: int) -> bool:
        _loc2_: int = param1
        if _loc2_ != 81:
            if _loc2_ != 90:
                if _loc2_ != 108:
                    if _loc2_ != 143:
                        if _loc2_ != 407:
                            if _loc2_ != 786:
                                if _loc2_ != 1037:
                                    if _loc2_ != 1109:
                                        if _loc2_ != 2020:
                                            return False
        return True

    @classmethod
    def isShield(cls, param1: int) -> bool:
        _loc2_: int = param1
        if _loc2_ != 1020:
            if _loc2_ != 1039:
                if _loc2_ != 1040:
                    return False
        return True

    @classmethod
    def isTargetMarkDispell(cls, param1: int) -> bool:
        _loc2_: int = param1
        if _loc2_ != 2018:
            if _loc2_ != 2019:
                if _loc2_ != 2024:
                    return False
        return True

    @classmethod
    def isStatBoost(cls, param1: int) -> bool:
        if param1 in [266, 268, 269, 270, 271, 414]:
            return True
        else:
            return False

    @classmethod
    def statBoostToStatName(cls, param1: int) -> str:
        if param1 == 266:
            return "chance"
        elif param1 == 268:
            return "agility"
        elif param1 == 269:
            return "intelligence"
        elif param1 == 270:
            return "wisdom"
        elif param1 == 271:
            return "strength"
        else:
            return param1

    @classmethod
    def statBoostToBuffActionId(cls, param1: int) -> int:
        if param1 == 266:
            return 123
        elif param1 == 268:
            return 119
        elif param1 == 269:
            return 126
        elif param1 == 270:
            return 124
        elif param1 == 271:
            return 118
        else:
            return 0

    @classmethod
    def statBoostToDebuffActionId(cls, param1: int) -> int:
        if param1 == 266:
            return 152
        elif param1 == 268:
            return 154
        elif param1 == 269:
            return 155
        elif param1 == 270:
            return 156
        elif param1 == 271:
            return 157
        else:
            return -1

    @classmethod
    def isDamage(cls, param1: int, param2: int) -> bool:
        if param1 == 2 and param2 != 127 and param2 != 101:
            return True
        return False

    @classmethod
    def isPush(cls, param1: int) -> bool:
        _loc2_: int = param1
        if _loc2_ != 5:
            if _loc2_ != 1021:
                if _loc2_ != 1041:
                    if _loc2_ != 1103:
                        return False
        return True

    @classmethod
    def isPull(cls, param1: int) -> bool:
        _loc2_: int = param1
        if _loc2_ != 6:
            if _loc2_ != 1022:
                if _loc2_ != 1042:
                    return False
        return True

    @classmethod
    def isForcedDrag(cls, param1: int) -> bool:
        _loc2_: int = param1
        if _loc2_ != 1021:
            if _loc2_ != 1022:
                return False
        return True

    @classmethod
    def isDrag(cls, param1: int) -> bool:
        if not cls.isPush(param1):
            return cls.isPull(param1)
        return True

    @classmethod
    def allowCollisionDamage(cls, param1: int) -> bool:
        _loc2_: int = param1
        if _loc2_ != 5:
            if _loc2_ != 1041:
                return False
        return True

    @classmethod
    def isSummon(cls, param1: int) -> bool:
        _loc2_: bool = False
        _loc3_: int = param1
        if _loc3_ == 181:
            _loc2_ = cls.isSummonWithSlot(param1)
            if _loc2_ == True:
                return True
            return True
        if _loc3_ != 780:
            if _loc3_ != 1008:
                if _loc3_ != 1097:
                    if _loc3_ != 1189:
                        _loc2_ = cls.isSummonWithSlot(param1)
                        if _loc2_ == True:
                            return True
                        return False
        return True

    @classmethod
    def isSummonWithSlot(cls, param1: int) -> bool:
        _loc2_: int = param1
        if _loc2_ != 180:
            if _loc2_ != 405:
                if _loc2_ != 1011:
                    if _loc2_ != 1034:
                        if _loc2_ != 2796:
                            return False
        return True

    @classmethod
    def isSummonWithoutTarget(cls, param1: int) -> bool:
        _loc2_: int = param1
        if _loc2_ != 180:
            if _loc2_ != 181:
                if _loc2_ != 780:
                    if _loc2_ != 1008:
                        if _loc2_ != 1011:
                            if _loc2_ != 1034:
                                if _loc2_ != 1097:
                                    if _loc2_ != 1189:
                                        return False
        return True

    @classmethod
    def isKillAndSummon(cls, param1: int) -> bool:
        _loc2_: int = param1
        if _loc2_ != 405:
            if _loc2_ != 2796:
                return False
        return True

    @classmethod
    def isRevive(cls, param1: int) -> bool:
        _loc2_: int = param1
        if _loc2_ != 780:
            if _loc2_ != 1034:
                return False
        return True

    @classmethod
    def getSplashFinalTakenDamageElement(cls, param1: int) -> int:
        if param1 == 0:
            return 1224
        if param1 == 1:
            return 1228
        if param1 == 2:
            return 1226
        if param1 == 3:
            return 1227
        if param1 == 4:
            return 1225
        else:
            return 1223

    @classmethod
    def getSplashRawTakenDamageElement(cls, param1: int) -> int:
        if param1 == 0:
            return 1124
        if param1 == 1:
            return 1128
        if param1 == 2:
            return 1126
        if param1 == 3:
            return 1127
        if param1 == 4:
            return 1125
        else:
            return 1123

    @classmethod
    def isFakeDamage(cls, param1: int) -> bool:
        _loc2_: int = param1
        if _loc2_ != 90:
            if _loc2_ != 1047:
                if _loc2_ != 1048:
                    return False
        return True

    @classmethod
    def isSpellExecution(cls, param1: int) -> bool:
        if (
            param1 == 1160
            or param1 == 2160
            or param1 == 1019
            or param1 == 1018
            or param1 == 792
            or param1 == 2792
            or param1 == 2794
            or param1 == 2795
            or param1 == 1017
            or param1 == 2017
            or param1 == 793
            or param1 == 2793
        ):
            return True
        return False

    @classmethod
    def isTeleport(cls, param1: int) -> bool:
        _loc2_: bool = False
        _loc3_: int = param1
        if _loc3_ != 4:
            if _loc3_ != 1099:
                if _loc3_ != 1100:
                    if _loc3_ != 1101:
                        if _loc3_ != 1104:
                            if _loc3_ != 1105:
                                if _loc3_ != 1106:
                                    _loc2_ = cls.isExchange(param1)
                                    if _loc2_ == True:
                                        return True
                                    return False
        return True

    @classmethod
    def isExchange(cls, param1: int) -> bool:
        _loc2_: int = param1
        if _loc2_ != 8:
            if _loc2_ != 1023:
                return False
        return True

    @classmethod
    def canTeleportOverBreedSwitchPos(cls, param1: int) -> bool:
        _loc2_: int = param1
        if _loc2_ != 4:
            if _loc2_ != 1023:
                return False
        return True

    @classmethod
    def allowAOEMalus(cls, param1: int) -> bool:
        if cls.isSplash(param1) and False or cls.isShield(param1):
            return False
        return True

    @classmethod
    def canTriggerHealMultiplier(cls, param1: int) -> bool:
        if param1 == 90:
            return False
        return True

    @classmethod
    def canTriggerDamageMultiplier(cls, param1: int) -> bool:
        if param1 == 90:
            return False
        return True

    @classmethod
    def canTriggerOnHeal(cls, param1: int) -> bool:
        _loc2_: int = param1
        if _loc2_ != 90:
            if _loc2_ != 786:
                return True
        return False

    @classmethod
    def canTriggerOnDamage(cls, param1: int) -> bool:
        if param1 == 1048:
            return False
        return True

    @classmethod
    def StatToBuffPercentActionIds(cls, param1: int) -> int:
        if param1 == 1:
            return 2846
        if param1 == 10:
            return 2834
        if param1 == 11:
            return 2844
        if param1 == 12:
            return 2842
        if param1 == 13:
            return 2840
        if param1 == 14:
            return 2836
        if param1 == 15:
            return 2838
        if param1 == 23:
            return 2848
        else:
            return -1

    @classmethod
    def StatToDebuffPercentActionIds(cls, param1: int) -> int:
        if param1 == 1:
            return 2847
        if param1 == 10:
            return 2835
        if param1 == 11:
            return 2845
        if param1 == 12:
            return 2843
        if param1 == 13:
            return 2841
        if param1 == 14:
            return 2837
        if param1 == 15:
            return 2839
        if param1 == 23:
            return 2848
        else:
            return -1

    @classmethod
    def isLinearBuffActionIds(cls, param1: int) -> bool:
        if param1 == [
            31,
            33,
            34,
            35,
            36,
            37,
            59,
            60,
            61,
            62,
            63,
            69,
            101,
            121,
            124,
            141,
            142,
        ]:
            return False
        else:
            return True

    @classmethod
    def isStatModifier(cls, actionId: int) -> bool:
        if (actionId in cls.STAT_BUFF_ACTION_IDS or actionId in cls.STAT_DEBUFF_ACTION_IDS) and not cls.isShield(
            actionId
        ):
            return True
        return False

    @classmethod
    def isBuff(cls, actionId: int) -> bool:
        return actionId in cls.STAT_BUFF_ACTION_IDS

    @classmethod
    def isDebuff(cls, actionsId: int) -> bool:
        return actionsId in cls.STAT_DEBUFF_ACTION_IDS

    @classmethod
    def getActionIdStatName(cls, actionId: int) -> str:
        return cls.actionIdToStatNameMap.get(str(actionId), "undefined")

    @classmethod
    def isPercentStatBoostActionId(cls, actionId: int) -> bool:
        return str(actionId) in cls.percentStatBoostActionIdToStat

    @classmethod
    def isFlatStatBoostActionId(cls, actionId: int) -> bool:
        return str(actionId) in cls.flatStatBoostActionIdToStat

    @classmethod
    def getStatIdFromStatActionId(cls, statId: int) -> int:
        if cls.isFlatStatBoostActionId(statId):
            return cls.flatStatBoostActionIdToStat[str(statId)]
        if cls.isPercentStatBoostActionId(statId):
            return cls.percentStatBoostActionIdToStat[str(statId)]
        if str(statId) in cls.shieldActionIdToStatId:
            return cls.shieldActionIdToStatId[str(statId)]
        return -1

    @classmethod
    def isStatUpdated(cls, actionId: int) -> bool:
        if str(actionId) not in cls.flatStatBoostActionIdToStat:
            return str(actionId) in cls.flatStatBoostActionIdToStat
        return True

    @classmethod
    def isStatSteal(cls, param1: int) -> bool:
        if not (param1 == 266 or param1 == 267 or param1 == 268 or param1 == 269 or param1 == 270):
            return param1 == 271
        return True

    @classmethod
    def spellExecutionHasGlobalLimitation(cls, param1: int) -> bool:
        _loc2_: int = param1
        if _loc2_ != 2017:
            if _loc2_ != 2160:
                if _loc2_ != 2792:
                    if _loc2_ != 2793:
                        if _loc2_ != 2795:
                            return False
        return True

    @classmethod
    def isDamageInflicted(cls, param1: int) -> bool:
        if not (
            param1 == 100
            or param1 == 144
            or param1 == 89
            or param1 == 1071
            or param1 == 1092
            or param1 == 1118
            or param1 == 670
            or param1 == 671
            or param1 == 672
            or param1 == 279
            or param1 == 95
            or param1 == 82
            or param1 == 1012
            or param1 == 1223
            or param1 == 1123
            or param1 == 1224
            or param1 == 1124
            or param1 == 97
            or param1 == 1063
            or param1 == 86
            or param1 == 1070
            or param1 == 276
            or param1 == 1096
            or param1 == 1122
            or param1 == 92
            or param1 == 1016
            or param1 == 1228
            or param1 == 1128
            or param1 == 98
            or param1 == 1064
            or param1 == 87
            or param1 == 1067
            or param1 == 277
            or param1 == 1093
            or param1 == 1119
            or param1 == 93
            or param1 == 1013
            or param1 == 1225
            or param1 == 1125
            or param1 == 96
            or param1 == 1065
            or param1 == 85
            or param1 == 1068
            or param1 == 1095
            or param1 == 1121
            or param1 == 275
            or param1 == 91
            or param1 == 1014
            or param1 == 1227
            or param1 == 1127
            or param1 == 99
            or param1 == 1066
            or param1 == 88
            or param1 == 1069
            or param1 == 1094
            or param1 == 1120
            or param1 == 278
            or param1 == 94
            or param1 == 1015
            or param1 == 80
            or param1 == 1226
            or param1 == 1126
            or param1 == 2822
            or param1 == 2830
            or param1 == 2829
        ):
            return param1 == 2828
        return True
