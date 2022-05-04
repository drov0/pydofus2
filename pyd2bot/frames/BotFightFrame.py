import collections
import math
import random
from threading import Timer
from time import sleep
from com.ankamagames.atouin.AtouinConstants import AtouinConstants
from com.ankamagames.atouin.utils.DataMapProvider import DataMapProvider
from com.ankamagames.dofus.datacenter.effects.EffectInstance import EffectInstance
from com.ankamagames.dofus.internalDatacenter.spells.SpellWrapper import SpellWrapper
from com.ankamagames.dofus.internalDatacenter.stats.EntityStats import EntityStats
from com.ankamagames.dofus.logic.game.fight.managers.CurrentPlayedFighterManager import CurrentPlayedFighterManager
from com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightSpellCastMessage import (
    GameActionFightSpellCastMessage,
)
from com.ankamagames.dofus.network.messages.game.actions.sequence.SequenceEndMessage import SequenceEndMessage
from com.ankamagames.dofus.network.messages.game.context.GameMapMovementMessage import GameMapMovementMessage
from com.ankamagames.dofus.network.messages.game.context.GameMapNoMovementMessage import GameMapNoMovementMessage
from com.ankamagames.dofus.network.types.game.context.GameContextActorInformations import GameContextActorInformations
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.atouin.managers.MapDisplayManager import MapDisplayManager
from com.ankamagames.atouin.messages.CellClickMessage import CellClickMessage
from com.ankamagames.atouin.messages.MapLoadedMessage import MapLoadedMessage
from com.ankamagames.dofus.datacenter.world.MapPosition import MapPosition
from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.dofus.kernel.net.ConnectionType import ConnectionType
from com.ankamagames.dofus.kernel.net.ConnectionsHandler import ConnectionsHandler
from com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import (
    PlayedCharacterManager,
)
from com.ankamagames.dofus.logic.game.common.misc.DofusEntities import DofusEntities
from com.ankamagames.dofus.logic.game.fight.frames.FightEntitiesFrame import (
    FightEntitiesFrame,
)
from com.ankamagames.dofus.logic.game.fight.miscs.FightReachableCellsMaker import (
    FightReachableCellsMaker,
)
from com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayEntitiesFrame import (
    RoleplayEntitiesFrame,
)
from com.ankamagames.dofus.network.messages.common.basic.BasicPingMessage import (
    BasicPingMessage,
)
from com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightCastRequestMessage import (
    GameActionFightCastRequestMessage,
)
from com.ankamagames.dofus.network.messages.game.context.fight.GameFightEndMessage import (
    GameFightEndMessage,
)
from com.ankamagames.dofus.network.messages.game.context.fight.GameFightJoinMessage import (
    GameFightJoinMessage,
)
from com.ankamagames.dofus.network.messages.game.context.fight.GameFightReadyMessage import (
    GameFightReadyMessage,
)
from com.ankamagames.dofus.network.messages.game.context.fight.GameFightTurnFinishMessage import (
    GameFightTurnFinishMessage,
)
from com.ankamagames.dofus.network.messages.game.context.fight.GameFightTurnStartMessage import (
    GameFightTurnStartMessage,
)
from com.ankamagames.dofus.network.messages.game.context.fight.character.GameFightShowFighterMessage import (
    GameFightShowFighterMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.MapComplementaryInformationsDataMessage import (
    MapComplementaryInformationsDataMessage,
)
from com.ankamagames.dofus.network.types.game.context.fight.GameFightMonsterInformations import (
    GameFightMonsterInformations,
)
from com.ankamagames.dofus.network.types.game.context.roleplay.GameRolePlayGroupMonsterInformations import (
    GameRolePlayGroupMonsterInformations,
)
from com.ankamagames.jerakine.entities.interfaces.IEntity import IEntity
from com.ankamagames.jerakine.entities.interfaces.IInteractive import IInteractive
from com.ankamagames.jerakine.map.LosDetector import LosDetector
from com.ankamagames.jerakine.messages.Frame import Frame
from com.ankamagames.jerakine.messages.Message import Message
from com.ankamagames.jerakine.metaclasses.Singleton import Singleton
from com.ankamagames.jerakine.types.enums.Priority import Priority
from com.ankamagames.jerakine.types.positions.MapPoint import MapPoint
from typing import TYPE_CHECKING, Tuple
from com.ankamagames.jerakine.types.zones.Cross import Cross
from com.ankamagames.jerakine.types.zones.IZone import IZone
from com.ankamagames.jerakine.types.zones.Lozenge import Lozenge
from com.ankamagames.jerakine.utils.display.spellZone.SpellShapeEnum import SpellShapeEnum

from damageCalculation.tools import StatIds


if TYPE_CHECKING:
    from com.ankamagames.dofus.logic.game.fight.frames.FightTurnFrame import (
        FightTurnFrame,
    )
    from com.ankamagames.dofus.logic.game.fight.frames.FightContextFrame import (
        FightContextFrame,
    )
    from com.ankamagames.dofus.logic.game.fight.frames.FightBattleFrame import FightBattleFrame
    from com.ankamagames.dofus.logic.game.fight.frames.FightSpellCastFrame import FightSpellCastFrame
    from pyd2bot.frames.BotFarmPathFrame import BotFarmPathFrame


logger = Logger(__name__)


class BotFightFrame(Frame, metaclass=Singleton):

    _frameFightListRequest: bool

    _fightCount: int = 0

    _mapPos: list

    _enabled: bool

    _inFight: bool

    _lastEntityOver: IInteractive

    _wait: bool

    _turnPlayed: int

    _myTurn: bool

    _turnAction: list

    _spellId = 13516  # Sadida ronce

    _lastTarget: int = None

    def __init__(self):
        self._turnAction = []
        super().__init__()

    def pushed(self) -> bool:
        self._enabled = True
        self.fakeActivity()
        self._myTurn = False
        self._mapPos = MapPosition.getMapPositions()
        self._wantcastSpell = None
        self._reachableCells = None
        return True

    @property
    def fightTurnFrame(self) -> "FightTurnFrame":
        return Kernel().getWorker().getFrame("FightTurnFrame")

    @property
    def fightContextFrame(self) -> "FightContextFrame":
        return Kernel().getWorker().getFrame("FightContextFrame")

    @property
    def entitiesFrame(self) -> "FightEntitiesFrame":
        return Kernel().getWorker().getFrame("FightEntitiesFrame")

    @property
    def spellFrame(self) -> "FightSpellCastFrame":
        return Kernel().getWorker().getFrame("FightSpellCastFrame")

    @property
    def battleFrame(self) -> "FightBattleFrame":
        return Kernel().getWorker().getFrame("FightBattleFrame")

    def pulled(self) -> bool:
        self._enabled = False
        return True

    @property
    def priority(self) -> int:
        return Priority.LOW

    @property
    def fightCount(self) -> int:
        return self._fightCount

    def findPathToTarget(self, spellw: SpellWrapper) -> Tuple[MapPoint, list[MapPoint]]:
        """
        Find path to the closest ldv to hit a mob.
        :param origin: position of the character
        :param po: max range of the spell
        :param targets: positions of the mobs
        :return: cell of the mob, path to the ldv if any else None
        """
        logger.debug("Searching for path to hit some mob")
        spellZone = self.getSpellZone(spellw)
        origin = self.fighterPos
        targets = self.mobPositions
        queue = collections.deque([[origin]])
        seen = {origin}
        while queue:
            path = queue.popleft()
            curr: MapPoint = path[-1]
            tested = {}
            currSpellZone = spellZone.getCells(curr.cellId)
            currReachableCells = self.getReachableCells(curr.cellId)
            for target in targets:
                if (
                    target["pos"].cellId in currSpellZone
                    and curr.los(LosDetector, DataMapProvider(), target["pos"], tested)
                    and self.canCastSpell(spellw, target["targetId"])
                ):
                    return target, path[1:]
            for cell in currReachableCells:
                mp = MapPoint.fromCellId(cell)
                pmove = curr.pointMov(DataMapProvider(), mp, False)
                if mp not in seen and pmove:
                    queue.append(path + [mp])
                    seen.add(mp)
        return None, None

    def getSpellWrapper(self, id: int) -> SpellWrapper:
        for spellw in PlayedCharacterManager().playerSpellList:
            if spellw.id == id:
                return spellw

    def getActualSpellRange(self, spellw: SpellWrapper) -> int:
        playerStats: EntityStats = CurrentPlayedFighterManager().getStats()
        range: int = spellw.maximalRangeWithBoosts
        minRange: int = spellw.minimalRange
        if spellw["rangeCanBeBoosted"]:
            range += playerStats.getStatTotalValue(StatIds.RANGE) - playerStats.getStatAdditionalValue(StatIds.RANGE)
        if range < minRange:
            range = minRange
        range = min(range, AtouinConstants.MAP_WIDTH * AtouinConstants.MAP_HEIGHT)
        if range < 0:
            range = 0
        return range

    def getSpellShape(self, spellw: SpellWrapper) -> int:
        spellShape: int = 0
        spellEffect: EffectInstance = None
        for spellEffect in spellw["effects"]:
            if spellEffect.zoneShape != 0 and (
                spellEffect.zoneSize > 0
                or spellEffect.zoneSize == 0
                and (spellEffect.zoneShape == SpellShapeEnum.P or spellEffect.zoneMinSize < 0)
            ):
                spellShape = spellEffect.zoneShape
        return spellShape

    def getSpellZone(self, spellw: SpellWrapper) -> IZone:
        range: int = self.getActualSpellRange(spellw)
        minRange: int = spellw.minimalRange
        spellShape: int = self.getSpellShape(spellw)
        castInLine: bool = spellw["castInLine"] or spellShape == SpellShapeEnum.l
        if castInLine and spellw["castInDiagonal"]:
            shapePlus = Cross(minRange, range, DataMapProvider())
            shapePlus.allDirections = True
            return shapePlus
        elif castInLine:
            return Cross(minRange, range, DataMapProvider())
        elif spellw["castInDiagonal"]:
            shapePlus = Cross(minRange, range, DataMapProvider())
            shapePlus.diagonal = True
            return shapePlus
        else:
            return Lozenge(minRange, range, DataMapProvider())

    def getLosCells(self, origin: MapPoint, spellId: int) -> list:
        rangeCells = self.getSpellRangeCells(self.getSpellWrapper(spellId), origin.cellId)
        losCells = LosDetector.getCell(DataMapProvider(), rangeCells, origin)
        return losCells

    def playTurn(self):
        self._reachableCells = self.getReachableCells()
        self._wantcastSpell = None
        spellw = self.getSpellWrapper(self._spellId)
        stats: EntityStats = CurrentPlayedFighterManager().getStats()
        movementPoints: int = stats.getStatTotalValue(StatIds.MOVEMENT_POINTS)
        actionPoints: int = stats.getStatTotalValue(StatIds.ACTION_POINTS)
        logger.debug(f"MP : {movementPoints}, AP : {actionPoints}")
        target, path = self.findPathToTarget(spellw)
        if path is not None:
            logger.debug(f"Found path of length {len(path)}")
            dest = None
            if len(path) == 0:
                self._wantcastSpell = {
                    "spellId": self._spellId,
                    "cellId": target["pos"].cellId,
                    "targetId": target["targetId"],
                }
                self.castSpell(self._spellId, target["pos"].cellId)
            elif path[-1].cellId in self._reachableCells:
                self._wantcastSpell = {
                    "spellId": self._spellId,
                    "cellId": target["pos"].cellId,
                    "targetId": target["targetId"],
                }
                self._lastTarget = target
                self.moveToCell(path[-1])
            else:
                for i, mp in enumerate(path):
                    if mp.cellId not in self._reachableCells:
                        if i == 0:
                            dest = None
                        else:
                            dest = path[i - 1]
                        break
                self.moveToCell(dest)
        else:
            self.turnEnd()

    def canCastSpell(self, spellw: SpellWrapper, targetId: int) -> bool:
        reason = [""]
        if CurrentPlayedFighterManager().canCastThisSpell(self._spellId, spellw.spellLevel, targetId, reason):
            return True
        else:
            # logger.error(f"Unable to cast spell for reason {reason[0]}")
            return False

    def process(self, msg: Message) -> bool:

        if isinstance(msg, GameFightJoinMessage):
            self._fightCount += 1
            self._inFight = True
            return True

        if isinstance(msg, GameFightEndMessage):
            self._inFight = False
            if Kernel().getWorker().contains("BotFarmPathFrame"):
                bfpf: "BotFarmPathFrame" = Kernel().getWorker().getFrame("BotFarmPathFrame")
            bfpf.doFarm()
            return True

        if isinstance(msg, MapComplementaryInformationsDataMessage):
            self._wait = False
            return False

        if isinstance(msg, MapLoadedMessage):
            self._wait = True
            return False

        if isinstance(msg, GameFightShowFighterMessage):
            self._turnPlayed = 0
            self._myTurn = False
            startFightMsg = GameFightReadyMessage()
            startFightMsg.init(True)
            ConnectionsHandler.getConnection().send(startFightMsg)
            return True

        if isinstance(msg, GameMapMovementMessage):
            if int(msg.actorId) == int(PlayedCharacterManager().id):
                if self._myTurn:
                    if self._wantcastSpell:
                        self.castSpell(self._wantcastSpell["spellId"], self._wantcastSpell["cellId"])
                    else:
                        self.turnEnd()
            return True

        if isinstance(msg, GameActionFightSpellCastMessage):
            if (
                self._myTurn
                and self._wantcastSpell
                and msg.spellId == self._wantcastSpell["spellId"]
                and msg.targetId == self._wantcastSpell["targetId"]
                and msg.sourceId == PlayedCharacterManager().id
                and msg.destinationCellId == self._wantcastSpell["cellId"]
            ):
                self.playTurn()

        if isinstance(msg, GameFightTurnStartMessage):
            turnStartMsg = msg
            if int(turnStartMsg.id) == int(PlayedCharacterManager().id):
                self._myTurn = True
                self._turnPlayed += 1
                self.playTurn()
            else:
                self._myTurn = False
            return True
        return False

    @property
    def actionPoints(self) -> int:
        stats = CurrentPlayedFighterManager().getStats()
        return stats.getStatTotalValue(StatIds.ACTION_POINTS)

    @property
    def movementPoints(self) -> int:
        stats = CurrentPlayedFighterManager().getStats()
        return stats.getStatTotalValue(StatIds.MOVEMENT_POINTS)

    def turnEnd(self) -> None:
        self.battleFrame.confirmTurnEnd()
        finDeTourMsg: GameFightTurnFinishMessage = GameFightTurnFinishMessage()
        finDeTourMsg.init(False)
        ConnectionsHandler.getConnection().send(finDeTourMsg)

    def fakeActivity(self) -> None:
        if not self._enabled:
            return
        Timer(60 * 5, self.fakeActivity).start()
        bpmgs: BasicPingMessage = BasicPingMessage()
        bpmgs.init(False)
        ConnectionsHandler.getConnection().send(bpmgs, ConnectionType.TO_ALL_SERVERS)

    def randomWalk(self) -> None:
        entity = None
        groupEntity: IEntity = None
        if self._inFight or self._wait:
            return
        rpEF: "RoleplayEntitiesFrame" = Kernel().getWorker().getFrame("RoleplayEntitiesFrame")
        if not rpEF:
            return
        avaibleCells: list = []
        for entity in rpEF.entities:
            if isinstance(entity, GameRolePlayGroupMonsterInformations):
                groupEntity = DofusEntities.getEntity(entity.contextualId)
                avaibleCells.append(MapPoint.fromCellId(groupEntity.position.cellId))
        if not avaibleCells or not len(avaibleCells):
            return
        ccmsg: CellClickMessage = CellClickMessage()
        ccmsg.cell = avaibleCells[math.floor(len(avaibleCells) * random.random())]
        ccmsg.cellId = ccmsg.cell.cellId
        ccmsg.id = MapDisplayManager().currentMapPoint.mapId
        Kernel().getWorker().process(ccmsg)

    @property
    def fighterInfos(self) -> "GameContextActorInformations":
        info = self.entitiesFrame.getEntityInfos(CurrentPlayedFighterManager().currentFighterId)
        return info

    @property
    def fighterPos(self) -> "MapPoint":
        return MapPoint.fromCellId(self.fighterInfos.disposition.cellId)

    def getReachableCells(self, cellId=None) -> list:
        infos = self.fighterInfos
        tmp = infos.disposition.cellId
        if cellId is None:
            cellId = tmp
        infos.disposition.cellId = cellId
        reachableCells: FightReachableCellsMaker = FightReachableCellsMaker(self.fighterInfos).reachableCells
        infos.disposition.cellId = tmp
        return reachableCells

    def fightRandomMove(self) -> None:
        if len(self.reachableCells) == 0:
            return
        randomCell: int = random.choice(self.reachableCells)
        self.moveToCell(MapPoint.fromCellId(randomCell))

    @property
    def mobPositions(self) -> list[MapPoint]:
        result = []
        for entity in FightEntitiesFrame.getCurrentInstance().entities.values():
            if entity.contextualId < 0 and isinstance(entity, GameFightMonsterInformations):
                monster = entity
                if (
                    monster.spawnInfo.teamId != self.fighterInfos.spawnInfo.teamId
                    and monster.spawnInfo.alive
                    and not monster.stats.summoned
                ):
                    result.append(
                        {"targetId": entity.contextualId, "pos": MapPoint.fromCellId(entity.disposition.cellId)}
                    )
        return result

    def castSpell(self, spellId: int, cellId: bool) -> None:
        gafcrmsg: GameActionFightCastRequestMessage = GameActionFightCastRequestMessage()
        gafcrmsg.init(spellId, cellId)
        ConnectionsHandler.getConnection().send(gafcrmsg)

    def moveToCell(self, cell: MapPoint) -> None:
        if not self._myTurn:
            logger.debug("Wants to move when it's not its turn yet")
            return False
        fightTurnFrame: "FightTurnFrame" = Kernel().getWorker().getFrame("FightTurnFrame")
        if not fightTurnFrame:
            logger.debug("Wants to move inside fight but 'FightTurnFrame' not found in kernel")
            return False
        logger.debug(f"Current cell {self.fighterInfos.disposition.cellId} moving to cell {cell.cellId}")
        fightTurnFrame.drawPath(cell)
        self._requestedMovement = cell
        fightTurnFrame.askMoveTo(cell)
        return True
