import json
import os
import cv2
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from core import Region, Location
import math


dir_path = os.path.dirname(os.path.realpath(__file__))
patterns_dir = os.path.join(dir_path, "..", "patterns")

def loadPattern(name):
    return cv2.imread(os.path.join(patterns_dir, name))

RESIGN_POPUP_R = Region(698, 442, 533, 173)
DEFEAT_POPUP_R = Region(762, 696, 415, 141)
COMBAT_R = Region(325,23,1270,903)
MINIMAP_R = Region(62, 876, 190, 122)
PM_R = Region(793, 993, 27, 34)
PA_R = Region(729, 983, 55, 42)
COMBAT_ENDED_POPUP_R = Region(841, 701, 244, 66)
READY_R = Region(1312, 925, 145, 66)
COMBAT_ENDED_POPUP_CLOSE_R = Region(1231, 721, 22, 18)
MY_TURN_CHECK_R = Region(841, 1009, 17, 8)
OUT_OF_COMBAT_R = Region(104, 749, 37, 37)
CREATURE_MODE_R = Region(1339, 993, 27, 25)
MAP_COORDS_R = Region(0, 28, 298, 98)
CONNECT_R = Region(666, 88, 572, 531)
RECONNECT_BUTTON_R = Region(880, 381, 161, 57)
PLAY_GAME_BUTTON_R = Region(993, 652, 452, 260)
BANK_MAN_R = Region(935, 465, 121, 126)
BANK_MAN_TALK_R = Region(465, 601, 999, 236)
INV_OPEN_R = Region(1213, 76, 413, 138)
INV_FIRST_SLOT_R = Region(1249, 202, 67, 67)
LVL_UP_INFO_R = Region(0, 438, 486, 388)
SLOTS_R = Region(835, 920, 418, 86)
HAVRE_SAC_ZAAP_R = Region(525, 380, 79, 54)
ZAAP_CHOICES_R = Region(641, 268, 552, 461)
CHAT_R = Region(352, 972, 320, 31)
ZAAP_COORD_R = Region(1034, 295, 83, 394)
FARM_R = Region(384,63,1158,815)
ZAAP_SCROLL_BAR_END_L = Location(1269, 685)
ZAAP_END_SCROLL_C = QColor(190, 226, 0)

# Patterns
READY_BUTTON_P = loadPattern("READY_BUTTON_P.png")
COMBAT_ENDED_POPUP_P = loadPattern("END_COMBAT_P.png")
CREATURE_MODE_OFF_P = loadPattern("CREATURE_MODE_OFF_P.png")
SKIP_TURN_BUTTON_P = loadPattern("SKIP_TURN_BUTTON_P.png")
RESIGN_POPUP_P = loadPattern("RESIGN_POPUP_P.png")
DEFEAT_POPUP_P = loadPattern("DEFEAT_POPUP_P.png")
DISCONNECTED_BOX_P = loadPattern("DISCONNECTED_BOX_P.png")
RECONNECT_BUTTON_P = loadPattern("RECONNECT_BUTTON_P.png")
PLAY_GAME_BUTTON_P = loadPattern("PLAY_GAME_BUTTON_P.png")
CLOSE_POPUP_P = loadPattern("CLOSE_POPUP_P.png")
REDUCE_BOX_P = loadPattern("reduceBox.png")

# bank
BANK_MAN_P = loadPattern("BANK_MAN_P.png")
BANK_MAN_TALK_P = loadPattern("BANK_MAN_TALK_P.png")

# inventory
INVENTAIRE_P = loadPattern("INVENTAIRE.png")
EMPTY_SLOT_INV_P = loadPattern("EMPTY_SLOT_INV_P.png")

# ZAAP
ZAAP_OPEN_P = loadPattern("ZAAP_OPEN_P.png")

# Env Vars
HCELLS = 14.5
VCELLS = 20.5

UP = (0, -1)
LEFT = (-1, 0)
RIGHT = (1, 0)
DOWN = (0, 1)

mapChangeLoc = {
    UP: [
        Region(877, 29, 142, 12),
        Region(492, 29, 141, 11),
        Region(1318, 30, 165, 11)],
    LEFT: [
        Region(335, 349, 14, 126),
        Region(337, 112, 10, 116),
        Region(338, 719, 11, 116)],
    RIGHT: [
        Region(1576, 360, 7, 125),
        Region(1572, 53, 11, 98),
        Region(1572, 752, 12, 100)],
    DOWN: [
        Region(898, 901, 137, 12),
        Region(423, 905, 111, 6),
        Region(1334, 893, 111, 22)]
}

MY_TURN_CHECK_L = Location(1425, 963)
END_COMBAT_CLOSE_L = Location(1251, 737)
MY_TURN_C = QColor(0, 240, 206, 255)
RESIGN_BUTTON_LOC = Location(1443, 1006)
RESIGN_CONFIRM_L = Location(879, 567)
DEFEAT_POPUP_CLOSE_L = Location(1122, 730)
CLOSE_DISCONNECTED_BOX_L = Region(866, 549, 205, 42)
CLOSE_LVL_UP_POPUP_L = Region(336, 573, 46, 32)

# Shortcuts
RAPPEL_POTION_SHORTCUT = "e"
SKIP_TURN_SHORTCUT = 'space'
HAVRE_SAC_SHORTCUT = "h"

ENU_COLOR = [QColor(253, 242, 206), QColor(253, 190, 45), QColor(254, 249, 226), QColor(216, 138, 22)]
SRAM_COLOR = [QColor(61, 56, 150), QColor(251, 241, 191), QColor(33, 34, 88), QColor(227, 218, 173),
              QColor(34, 51, 153)]

FULL_POD_CHECK_L = Location(1266, 1019)
FULL_POD_COLOR = QColor(53, 190, 96)


class ObjColor:
    BOT = ENU_COLOR + SRAM_COLOR
    MOB = [QColor(46, 54, 61), QColor(41, 48, 55)]
    FREE = [QColor(150, 142, 103), QColor(142, 134, 94), QColor(186, 181, 155), QColor(128, 121, 85)]
    OBSTACLE = [QColor(255, 255, 255), QColor(88, 83, 58), QColor(79, 75, 52), QColor(228, 228, 226)]
    DARK = [QColor(0, 0, 0)]
    REACHABLE = [QColor(90, 125, 62), QColor(85, 121, 56), QColor(0, 102, 0), QColor(77, 109, 50)]
    INVOKE = [QColor(218, 57, 45), QColor(255, 244, 221)]
    MY_TURN_COLOR = QColor(252, 200, 0)


class ObjType:
    REACHABLE = QColor(Qt.darkGreen)
    OBSTACLE = QColor(88, 83, 58)
    DARK = Qt.black
    MOB = QColor(Qt.darkBlue)
    BOT = QColor(Qt.darkRed)
    FREE = QColor(142, 134, 94)
    INVOKE = QColor(Qt.yellow)
    UNKNOWN = QColor(Qt.gray)


def findObject(color):
    result = ObjType.UNKNOWN

    if color in ObjColor.OBSTACLE:
        result = ObjType.OBSTACLE

    elif color in ObjColor.FREE:
        result = ObjType.FREE

    elif color in ObjColor.REACHABLE:
        result = ObjType.REACHABLE

    elif color in ObjColor.INVOKE:
        result = ObjType.INVOKE

    elif color in ObjColor.MOB:
        result = ObjType.MOB

    elif color in ObjColor.BOT:
        result = ObjType.BOT

    elif color in ObjColor.DARK:
        result = ObjType.DARK

    return result

def getCellCoords(cell_id):
    Y = math.floor(cell_id / 14)
    if Y < 0:
        Y = 0
    if Y&1:
        X = (cell_id - Y * 14) * 2 + 1
    else:
        X = (cell_id - Y * 14) * 2
    return X, Y

def getCellPixelCenterCoords(x, y):
    map_px, map_py, map_pw, map_ph = COMBAT_R.getRect()
    cpx = map_px + int(map_pw / (2 * HCELLS)) * (x + 1) 
    cpy = map_py + int(map_ph / (2 * VCELLS)) * (y + 1)
    return cpx, cpy

with open(os.path.join(dir_path, "MapCoordinates.json")) as fp:
    map_coords = json.load(fp)

with open(os.path.join(dir_path, "MapScrollActions.json")) as fp:
    map_scrolls_json = json.load(fp)
    map_scrolls = {}
    for msc in map_scrolls_json:
        map_scrolls[msc["id"]] = msc

def getMapCoords(map_id):
    for map_data in map_coords:
        if map_id in map_data["mapIds"]:
            compressed_coords = map_data["compressedCoords"]
            break
    x = (compressed_coords >> 16)
    y = -(-compressed_coords & 65535)
    return x, y

def getMapDirections(mapId=None):
    if mapId:
        directions = []
        mapscrolls = map_scrolls[mapId]
        if mapscrolls["rightExists"]:
            directions.append((RIGHT, mapscrolls["rightMapId"]))
        if mapscrolls["bottomExists"]:
            directions.append((DOWN, mapscrolls["bottomMapId"]))
        if mapscrolls["leftExists"]:
            directions.append((LEFT, mapscrolls["leftMapId"]))
        if mapscrolls["topExists"]:
            directions.append((UP, mapscrolls["topMapId"]))
        return directions
    else:
        return [(RIGHT, None), (DOWN, None), (LEFT, None), (UP, None)]
