import collections
import math
import random
from threading import Timer
from time import sleep
from types import FunctionType
from com.ankamagames.atouin.AtouinConstants import AtouinConstants
from com.ankamagames.atouin.utils.DataMapProvider import DataMapProvider
from com.ankamagames.dofus.datacenter.effects.EffectInstance import EffectInstance
from com.ankamagames.dofus.internalDatacenter.spells.SpellWrapper import SpellWrapper
from com.ankamagames.dofus.internalDatacenter.stats.EntityStats import EntityStats
from com.ankamagames.dofus.logic.game.fight.managers.CurrentPlayedFighterManager import CurrentPlayedFighterManager
from com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightNoSpellCastMessage import (
    GameActionFightNoSpellCastMessage,
)
from com.ankamagames.dofus.network.messages.game.actions.sequence.SequenceEndMessage import SequenceEndMessage
from com.ankamagames.dofus.network.messages.game.actions.sequence.SequenceStartMessage import SequenceStartMessage
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
    from com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayMovementFrame import RoleplayMovementFrame


logger = Logger("Dofus2")


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
        self._turnAction = []
        self._seqQueue = []
        self._waitingSeqEnd = False
        self._turnPlayed = 0
        return True

    @property
    def turnFrame(self) -> "FightTurnFrame":
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

    def findPathToTarget(self, spellw: SpellWrapper, targetSum=False) -> Tuple[MapPoint, list[MapPoint]]:
        """
        Find path to the closest ldv to hit a mob.
        :param origin: position of the character
        :param po: max range of the spell
        :param targets: positions of the mobs
        :return: cell of the mob, path to the ldv if any else None
        """
        spellZone = self.getSpellZone(spellw)
        origin = self.fighterPos
        logger.debug(f"Searching for path to hit some target, origin = {origin.cellId}")
        targets = self.getMobPositions(targetSum)
        if not targets:
            return None, None
        queue = collections.deque([[origin]])
        seen = {origin}
        while queue:
            path = queue.popleft()
            curr: MapPoint = path[-1]
            currSpellZone = spellZone.getCells(curr.cellId)
            ldv = LosDetector.getCell(DataMapProvider(), currSpellZone, curr)
            for target in targets:
                if target["pos"] in ldv and self.canCastSpell(spellw, target["targetId"]):
                    logger.debug(
                        f"Found path {[mp.cellId for mp in path]} to hit a target {target['targetId']} at pos {target['pos'].cellId}"
                    )
                    return target, path[1:]
            currReachableCells = FightReachableCellsMaker(self.fighterInfos, curr.cellId, 1).reachableCells
            for cellId in currReachableCells:
                mp = MapPoint.fromCellId(cellId)
                if mp not in seen:
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

    def addTurnAction(self, fct: FunctionType, args: list) -> None:
        self._turnAction.append({"fct": fct, "args": args})

    def nextTurnAction(self) -> None:
        # logger.debug(f"Next turn action, {self._turnAction}")
        if len(self._turnAction) > 0:
            action = self._turnAction.pop(0)
            action["fct"](*action["args"])
            self._waitingSeqEnd = True
        else:
            self.playTurn()

    def playTurn(self):
        self._reachableCells = FightReachableCellsMaker(self.fighterInfos).reachableCells
        # logger.debug(f"reachable cells {self._reachableCells}")
        self._wantcastSpell = None
        spellw = self.getSpellWrapper(self._spellId)
        logger.debug(f"MP : {self.movementPoints}, AP : {self.actionPoints}")
        target, path = self.findPathToTarget(spellw, targetSum=False)
        if path is not None:
            target, path = self.findPathToTarget(spellw, targetSum=True)
        if path is not None:
            if len(path) == 0:
                self.addTurnAction(self.castSpell, [self._spellId, target["pos"].cellId])
            elif path[-1].cellId in self._reachableCells:
                self.addTurnAction(self.askMove, [path])
                self.addTurnAction(self.castSpell, [self._spellId, target["pos"].cellId])
            else:
                for i, mp in enumerate(path):
                    if mp.cellId not in self._reachableCells:
                        if i != 0:
                            self.addTurnAction(self.askMove, [path[:i]])
                        break
                self.addTurnAction(self.turnEnd, [])
        else:
            logger.debug("No path to any target found")
            self.addTurnAction(self.turnEnd, [])
        self.nextTurnAction()

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

        elif isinstance(msg, GameFightEndMessage):
            self._inFight = False
            return True

        elif isinstance(msg, GameActionFightNoSpellCastMessage):
            # logger.debug(f"failed to cast spell {msg.to_json()}")
            self.turnEnd()
            return True

        elif isinstance(msg, MapComplementaryInformationsDataMessage):
            self._wait = False
            return False

        elif isinstance(msg, MapLoadedMessage):
            self._wait = True
            return False

        elif isinstance(msg, GameFightShowFighterMessage):
            self._turnPlayed = 0
            self._myTurn = False
            startFightMsg = GameFightReadyMessage()
            startFightMsg.init(True)
            ConnectionsHandler.getConnection().send(startFightMsg)
            return True

        elif isinstance(msg, SequenceEndMessage):
            if self._myTurn:
                if self._seqQueue:
                    self._seqQueue.pop()
                    if not self._seqQueue:
                        if self._waitingSeqEnd:
                            self._waitingSeqEnd = False
                            self.nextTurnAction()
            return True

        elif isinstance(msg, SequenceStartMessage):
            if self._myTurn:
                self._seqQueue.append(msg)
            return True

        elif isinstance(msg, GameFightTurnStartMessage):
            turnStartMsg = msg
            self._myTurn = int(turnStartMsg.id) == int(PlayedCharacterManager().id)
            if self._myTurn:
                logger.debug("my turn to play")
                self._seqQueue.clear()
                self._myTurn = True
                self._turnAction.clear()
                self._turnPlayed += 1
                self.nextTurnAction()

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
        self._myTurn = False
        self._seqQueue.clear()
        self._turnAction.clear()
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

    def fightRandomMove(self) -> None:
        if len(self.reachableCells) == 0:
            return
        randomCell: int = random.choice(self.reachableCells)
        self.askMove(MapPoint.fromCellId(randomCell))

    def getMobPositions(self, targetSum) -> list[MapPoint]:
        result = []
        logger.debug(f"Deads list : {self.battleFrame._deadTurnsList}")
        for entity in FightEntitiesFrame.getCurrentInstance().entities.values():
            if entity.contextualId < 0 and isinstance(entity, GameFightMonsterInformations):
                monster = entity
                if (
                    monster.spawnInfo.teamId != self.fighterInfos.spawnInfo.teamId
                    and float(entity.contextualId) not in self.battleFrame._deadTurnsList
                    and (targetSum or not monster.stats.summoned)
                ):
                    result.append(
                        {"targetId": entity.contextualId, "pos": MapPoint.fromCellId(entity.disposition.cellId)}
                    )
        logger.debug(f"Found targets : {[(tgt['targetId'], tgt['pos'].cellId) for tgt in result]}")
        return result

    def castSpell(self, spellId: int, cellId: bool) -> None:
        gafcrmsg: GameActionFightCastRequestMessage = GameActionFightCastRequestMessage()
        gafcrmsg.init(spellId, cellId)
        ConnectionsHandler.getConnection().send(gafcrmsg)

    def askMove(self, mpcells: list[MapPoint], mpcellsTackled: list[MapPoint] = []) -> None:
        logger.debug(f"ask move follwing path {[mp.cellId for mp in mpcells]}")
        if not self._myTurn:
            logger.debug("Wants to move when it's not its turn yet")
            return False
        fightTurnFrame: "FightTurnFrame" = Kernel().getWorker().getFrame("FightTurnFrame")
        if not fightTurnFrame:
            logger.debug("Wants to move inside fight but 'FightTurnFrame' not found in kernel")
            return False
        cells = [mp.cellId for mp in mpcells]
        cellsTackled = [mp.cellId for mp in mpcellsTackled]
        fightTurnFrame.askMoveTo(cells, cellsTackled)
        return True
