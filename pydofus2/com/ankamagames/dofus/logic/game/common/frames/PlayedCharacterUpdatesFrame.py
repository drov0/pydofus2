from datetime import datetime
from time import perf_counter
from typing import TYPE_CHECKING

import pydofus2.com.ankamagames.dofus.internalDatacenter.spells.SpellWrapper as swmod
import pydofus2.com.ankamagames.dofus.kernel.Kernel as krnl
import pydofus2.com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager as pcm
from pydofus2.com.ankamagames.berilia.managers.KernelEvent import KernelEvent
from pydofus2.com.ankamagames.berilia.managers.KernelEventsManager import \
    KernelEventsManager
from pydofus2.com.ankamagames.dofus.datacenter.breeds.Breed import Breed
from pydofus2.com.ankamagames.dofus.datacenter.spells.SpellLevel import \
    SpellLevel
from pydofus2.com.ankamagames.dofus.logic.common.managers.PlayerManager import \
    PlayerManager
from pydofus2.com.ankamagames.dofus.logic.common.managers.StatsManager import \
    StatsManager
from pydofus2.com.ankamagames.dofus.logic.game.common.managers.InventoryManager import \
    InventoryManager
from pydofus2.com.ankamagames.dofus.logic.game.common.managers.TimeManager import \
    TimeManager
from pydofus2.com.ankamagames.dofus.logic.game.common.misc.DofusEntities import \
    DofusEntities
from pydofus2.com.ankamagames.dofus.logic.game.fight.managers.CurrentPlayedFighterManager import \
    CurrentPlayedFighterManager
from pydofus2.com.ankamagames.dofus.logic.game.fight.managers.SpellModifiersManager import \
    SpellModifiersManager
from pydofus2.com.ankamagames.dofus.network.enums.GameServerTypeEnum import \
    GameServerTypeEnum
from pydofus2.com.ankamagames.dofus.network.enums.PlayerLifeStatusEnum import \
    PlayerLifeStatusEnum
from pydofus2.com.ankamagames.dofus.network.enums.StatsUpgradeResultEnum import \
    StatsUpgradeResultEnum
from pydofus2.com.ankamagames.dofus.network.messages.game.almanach.AlmanachCalendarDateMessage import \
    AlmanachCalendarDateMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.atlas.compass.CompassResetMessage import \
    CompassResetMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.atlas.compass.CompassUpdatePartyMemberMessage import \
    CompassUpdatePartyMemberMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.atlas.compass.CompassUpdatePvpSeekMessage import \
    CompassUpdatePvpSeekMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.basic.BasicTimeMessage import \
    BasicTimeMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.character.debt.DebtsDeleteMessage import \
    DebtsDeleteMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.character.debt.DebtsUpdateMessage import \
    DebtsUpdateMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.character.spell.forgettable.ForgettableSpellDeleteMessage import \
    ForgettableSpellDeleteMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.character.spell.forgettable.ForgettableSpellEquipmentSlotsMessage import \
    ForgettableSpellEquipmentSlotsMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.character.spell.forgettable.ForgettableSpellListUpdateMessage import \
    ForgettableSpellListUpdateMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.character.stats.CharacterExperienceGainMessage import \
    CharacterExperienceGainMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.character.stats.CharacterLevelUpInformationMessage import \
    CharacterLevelUpInformationMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.character.stats.CharacterStatsListMessage import \
    CharacterStatsListMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.context.GameMapSpeedMovementMessage import \
    GameMapSpeedMovementMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.death.GameRolePlayGameOverMessage import \
    GameRolePlayGameOverMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.death.GameRolePlayPlayerLifeStatusMessage import \
    GameRolePlayPlayerLifeStatusMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.MapComplementaryInformationsDataMessage import \
    MapComplementaryInformationsDataMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.stats.StatsUpgradeResultMessage import \
    StatsUpgradeResultMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.initialization.CharacterCapabilitiesMessage import \
    CharacterCapabilitiesMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.initialization.ServerExperienceModificatorMessage import \
    ServerExperienceModificatorMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.initialization.SetCharacterRestrictionsMessage import \
    SetCharacterRestrictionsMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.interactive.zaap.KnownZaapListMessage import \
    KnownZaapListMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.inventory.exchanges.ExchangeMoneyMovementInformationMessage import \
    ExchangeMoneyMovementInformationMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.inventory.items.SetUpdateMessage import \
    SetUpdateMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.startup.StartupActionAddMessage import \
    StartupActionAddMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.startup.StartupActionFinishedMessage import \
    StartupActionFinishedMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.startup.StartupActionsListMessage import \
    StartupActionsListMessage
from pydofus2.com.ankamagames.dofus.network.types.game.character.characteristic.CharacterCharacteristicsInformations import \
    CharacterCharacteristicsInformations
from pydofus2.com.ankamagames.dofus.network.types.game.context.roleplay.HumanOptionAlliance import \
    HumanOptionAlliance
from pydofus2.com.ankamagames.dofus.network.types.game.context.roleplay.HumanOptionOrnament import \
    HumanOptionOrnament
from pydofus2.com.ankamagames.dofus.types.data.PlayerSetInfo import \
    PlayerSetInfo
from pydofus2.com.ankamagames.jerakine.data.I18n import I18n
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.messages.Frame import Frame
from pydofus2.com.ankamagames.jerakine.messages.Message import Message
from pydofus2.com.ankamagames.jerakine.types.enums.Priority import Priority

if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.logic.game.fight.frames.FightBattleFrame import \
        FightBattleFrame
    from pydofus2.com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayEntitiesFrame import \
        RoleplayEntitiesFrame
    from pydofus2.com.ankamagames.dofus.network.types.game.context.roleplay.GameRolePlayHumanoidInformations import \
        GameRolePlayHumanoidInformations


class PlayedCharacterUpdatesFrame(Frame):

    SPELL_TOOLTIP_CACHE_NUM: int = 0

    FORGETTABLE_SPELL_FIRST_NOTIF_NAME: str = "firstForgettableSpell"

    setList: dict = {}

    guildEmblemSymbolCategories: int

    _kamasLimit: float

    _giftListInitialized: bool

    def __init__(self):
        self._phenixMapId = None
        super().__init__()

    @property
    def priority(self) -> int:
        return Priority.HIGH

    @property
    def roleplayContextFrame(self):
        return krnl.Kernel().roleplayContextFrame

    @property
    def kamasLimit(self) -> float:
        return self._kamasLimit

    def pushed(self) -> bool:
        self.setList = dict()
        self._giftListInitialized = False
        return True

    def process(self, msg: Message) -> bool:

        if isinstance(msg, SetCharacterRestrictionsMessage):
            scrmsg = msg
            if scrmsg.actorId == pcm.PlayedCharacterManager().id:
                pcm.PlayedCharacterManager().restrictions = scrmsg.restrictions
            rpEntitiesFrame = krnl.Kernel().roleplayEntitiesFrame
            if rpEntitiesFrame:
                infos: "GameRolePlayHumanoidInformations" = rpEntitiesFrame.getEntityInfos(scrmsg.actorId)
                if infos and infos.humanoidInfo:
                    infos.humanoidInfo.restrictions = scrmsg.restrictions
            return True

        if isinstance(msg, ServerExperienceModificatorMessage):
            semsg = msg
            pcm.PlayedCharacterManager().experiencePercent = semsg.experiencePercent - 100
            return True

        if isinstance(msg, CharacterStatsListMessage):
            cslmsg = msg
            fightBattleFrame= krnl.Kernel().battleFrame
            if fightBattleFrame is not None and fightBattleFrame.executingSequence:
                fightBattleFrame.delayCharacterStatsList(cslmsg)
            else:
                self.updateCharacterStatsList(cslmsg.stats)
            if self.roleplayContextFrame and self.roleplayContextFrame.entitiesFrame:
                playerInfos = self.roleplayContextFrame.entitiesFrame.getEntityInfos(pcm.PlayedCharacterManager().id)
                if playerInfos:
                    playerInfos.alignmentInfos = cslmsg.stats.alignmentInfos
            if krnl.Kernel().questFrame:
                if krnl.Kernel().questFrame.achievmentsListProcessed == False:
                    krnl.Kernel().questFrame.processAchievements(True)
            KernelEventsManager().send(KernelEvent.CharacterStats)
            return True

        if isinstance(msg, MapComplementaryInformationsDataMessage):
            mcidmsg = msg
            for grai in mcidmsg.actors:
                grpci = grai
                if grpci and grpci.contextualId == pcm.PlayedCharacterManager().id:
                    pcm.PlayedCharacterManager().infos.entityLook = grpci.look
                    for opt in grpci.humanoidInfo.options:
                        if isinstance(opt, HumanOptionAlliance):
                            pcm.PlayedCharacterManager().characteristics.alignmentInfos.aggressable = opt.aggressable
            return False

        if isinstance(msg, CharacterCapabilitiesMessage):
            ccmsg = msg
            self.guildEmblemSymbolCategories = ccmsg.guildEmblemSymbolCategories
            return True

        # if isinstance(msg, ResetCharacterStatsRequestAction):
        #    rcsra = msg
        #    rcsrmsg = ResetCharacterStatsRequestMessage()
        #    rcsrmsg.initResetCharacterStatsRequestMessage()
        #    ConnectionsHandler().send(rcsrmsg)
        #    return True

        if isinstance(msg, StatsUpgradeResultMessage):
            surmsg = msg
            statUpgradeErrorText = None
            if surmsg.result == StatsUpgradeResultEnum.SUCCESS:
                Logger().info(f"Upgraded characteristics by {surmsg.nbCharacBoost} points")
            elif surmsg.result == StatsUpgradeResultEnum.NONE:
                statUpgradeErrorText = "ui.popup.statboostFailed.text"
            elif surmsg.result == StatsUpgradeResultEnum.GUEST:
                statUpgradeErrorText = "ui.fight.guestAccount"
            elif surmsg.result == StatsUpgradeResultEnum.RESTRICTED:
                statUpgradeErrorText = "ui.charSel.deletionErrorUnsecureMode"
            elif surmsg.result == StatsUpgradeResultEnum.IN_FIGHT:
                statUpgradeErrorText = "ui.error.cantDoInFight"
            elif surmsg.result == StatsUpgradeResultEnum.NOT_ENOUGH_POINT:
                statUpgradeErrorText = "ui.popup.statboostFailed.notEnoughPoint"
            if statUpgradeErrorText:
                Logger().info(I18n.getUiText(statUpgradeErrorText))
            KernelEventsManager().send(KernelEvent.StatsUpgradeResult, surmsg.result, surmsg.nbCharacBoost)
            return True

        if isinstance(msg, CharacterLevelUpInformationMessage):
            Logger().info(f"Player {msg.name} ({msg.id}) leveled up, new {msg.newLevel}")
            if msg.id == pcm.PlayedCharacterManager().id:
                clumsg = msg
                entityInfos = None
                newLevel = None
                previousLevel = pcm.PlayedCharacterManager().infos.level
                Logger().warning(f"Received a player new level {msg.newLevel}, previous level {pcm.PlayedCharacterManager().infos.level}.")
                newLevel = msg.newLevel
                pcm.PlayedCharacterManager().infos.level = newLevel
                Logger().info(f"Player {pcm.PlayedCharacterManager().id} leveled up, new level {newLevel}")
                if newLevel == 10 and PlayerManager().server.gameTypeId != GameServerTypeEnum.SERVER_TYPE_TEMPORIS:
                    newSpellWrappers = []
                    playerBreed = Breed.getBreedById(pcm.PlayedCharacterManager().infos.breed)
                    for spellVariant in playerBreed.breedSpellVariants:
                        for spellBreed in spellVariant.spells:
                            for spellLevelBreedId in spellBreed.spellLevels:
                                spellLevelBreed = SpellLevel.getLevelById(spellLevelBreedId)
                                if spellLevelBreed:
                                    obtentionLevel = spellLevelBreed.minPlayerLevel
                                    if obtentionLevel <= clumsg.newLevel and obtentionLevel > previousLevel:
                                        newSpellWrappers.append(
                                            swmod.SpellWrapper.create(spellBreed.id, spellLevelBreed.grade, False)
                                        )
                    for spellWrapper in pcm.PlayedCharacterManager().spellsInventory:
                        spellWrapper.updateSpellLevelAndEffectsAccordingToPlayerLevel()

                    if self.roleplayContextFrame:
                        entityInfos = self.roleplayContextFrame.entitiesFrame.getEntityInfos(
                            pcm.PlayedCharacterManager().id
                        )

                    if entityInfos:
                        for option in entityInfos.humanoidInfo.options:
                            if isinstance(option, HumanOptionOrnament):
                                option.level = newLevel
                KernelEventsManager().send(KernelEvent.PlayerLeveledUp, previousLevel, msg.newLevel)
            return True

        if isinstance(msg, CharacterExperienceGainMessage):
            return True

        if isinstance(msg, GameRolePlayPlayerLifeStatusMessage):
            state = PlayerLifeStatusEnum(msg.state)
            pcm.PlayedCharacterManager().state = state
            self._phenixMapId = msg.phenixMapId
            KernelEventsManager().send(KernelEvent.PlayerStateChanged, PlayerLifeStatusEnum(msg.state), msg.phenixMapId)
            return True

        if isinstance(msg, GameRolePlayGameOverMessage):
            pcm.PlayedCharacterManager().state = PlayerLifeStatusEnum.STATUS_TOMBSTONE
            return True

        if isinstance(msg, AlmanachCalendarDateMessage):
            # acdmsg = msg
            # AlmanaxManager().calendar = AlmanaxCalendar.getAlmanaxCalendarById(acdmsg.date)
            return True

        if isinstance(msg, SetUpdateMessage):
            sumsg = msg
            self.setList[sumsg.setId] = PlayerSetInfo(sumsg.setId, sumsg.setObjects, sumsg.setEffects)
            return True
        
        if isinstance(msg, KnownZaapListMessage):
            pcm.PlayedCharacterManager().updateKnownZaaps(msg.destinations);
            return True
    
        if isinstance(msg, CompassResetMessage):
            # crmsg = msg
            # name = "flag_srv" + crmsg.type

            # if crmsg.type  == CompassTypeEnum.COMPASS_TYPE_SPOUSE:
            #    socialFrame = krnl.Kernel().worker.getFrame("SocialFrame")
            #    socialFrame.spouse.followSpouse = False

            # if crmsg.type  == CompassTypeEnum.COMPASS_TYPE_PARTY:
            #    pcm.PlayedCharacterManager().followingPlayerIds = []
            #    return True
            return True

        if isinstance(msg, CompassUpdatePartyMemberMessage):
            pass

        if isinstance(msg, CompassUpdatePvpSeekMessage):
            pass

        if isinstance(msg, BasicTimeMessage):
            btmsg = msg
            receptionDelay = perf_counter() - btmsg.receptionTime
            TimeManager().serverTimeLag = (
                btmsg.timestamp + btmsg.timezoneOffset * 60 * 1000 - datetime.now().timestamp() + receptionDelay
            )
            TimeManager().serverUtcTimeLag = btmsg.timestamp - datetime.now().timestamp() + receptionDelay
            return True

        if isinstance(msg, StartupActionsListMessage):
            # salm = msg
            # giftList = []
            # initialGiftCount = 0
            # if pcm.PlayedCharacterManager().waitingGifts and pcm.PlayedCharacterManager().len(waitingGifts) != 0:
            #    initialGiftCount = pcm.PlayedCharacterManager().len(waitingGifts)
            # for gift in salm.actions:
            #        _items = []
            #    for item in gift.items:
            #       iw = ItemWrapper.create(0,0,item.objectGID,item.quantity,item.effects,False)
            #       _items.append(iw)
            #       obj = {
            #          "uid":gift.uid,
            #          "title":gift.title,
            #          "text":gift.text,
            #          "items":_items
            #       }
            #    giftList.append(obj)
            # pcm.PlayedCharacterManager().waitingGifts = giftList
            # if len(giftList) > 0:
            #    if self._giftListInitialized and len(giftList) != initialGiftCount and len(giftList) > initialGiftCount:
            #       pass
            # self._giftListInitialized = True
            return True

        if isinstance(msg, StartupActionAddMessage):
            # saam = msg
            # items = []
            # for itema in saam.newAction.items:
            #    iw = ItemWrapper.create(0,0,itema.objectGID,itema.quantity,itema.effects,False)
            #    items.append(iw)
            # obj = {
            #    "uid":saam.newAction.uid,
            #    "title":saam.newAction.title,
            #    "text":saam.newAction.text,
            #    "items":items
            # }
            # pcm.PlayedCharacterManager().waitingGifts.append(obj)
            return True

        # if isinstance(msg, GiftAssignRequestAction):
        #    gar = msg
        #    sao = StartupActionsObjetAttributionMessage()
        #    sao.initStartupActionsObjetAttributionMessage(gar.giftId,gar.characterId)
        #    ConnectionsHandler().send(sao)
        #    return True

        # if isinstance(msg, GiftAssignAllRequestAction):
        #    gaara = msg
        #    saaamsg = StartupActionsAllAttributionMessage()
        #    saaamsg.initStartupActionsAllAttributionMessage(gaara.characterId)
        #    ConnectionsHandler().send(saaamsg)
        #    return True

        if isinstance(msg, StartupActionFinishedMessage):
            # safm = msg
            # indexToDelete = -1
            # for giftAction in pcm.PlayedCharacterManager().waitingGifts:
            #    if giftAction.uid == safm.actionId:
            #       indexToDelete = pcm.PlayedCharacterManager().waitingGifts.find(giftAction)
            # if indexToDelete > -1:
            #    pcm.PlayedCharacterManager().waitingGifts.splice(indexToDelete,1)
            #    if len(pcm.PlayedCharacterManager().waitingGifts) == 0:
            #       pass
            return True

        if isinstance(msg, ExchangeMoneyMovementInformationMessage):
            emmim = msg
            self._kamasLimit = emmim.limit
            return True

        if isinstance(msg, DebtsUpdateMessage):
            pass
            # DebtManager().updateDebts(dum.debts)
            return True

        if isinstance(msg, DebtsDeleteMessage):
            pass
            # DebtManager().removeDebts(ddm.debts)
            return True

        if isinstance(msg, ForgettableSpellListUpdateMessage):
            # fslumsg = msg
            # if fslumsg.action == ForgettableSpellListActionEnum.FORGETTABLE_SPELL_LIST_DISPATCH:
            #    newSpellList = dict()
            #    for forgettableSpell in fslumsg.spells:
            #       newSpellList[forgettableSpell.spellId] = forgettableSpell
            #    pcm.PlayedCharacterManager().playerForgettableSpelldict = newSpellList
            # else:
            #    ds = DataStoreType("AccountModule_",True,DataStoreEnum.LOCATION_LOCAL,DataStoreEnum.BIND_ACCOUNT)
            #    if not StoreDataManager().getData(ds,FORGETTABLE_SPELL_FIRST_NOTIF_NAME):
            #       StoreDataManager().setData(ds,FORGETTABLE_SPELL_FIRST_NOTIF_NAME,True)
            #       nid = NotificationManager().prepareNotification(I18n.getUiText("ui.temporis.popupFirstSpellAddedTitle"),I18n.getUiText("ui.temporis.popupFirstSpellAddedContent"),NotificationTypeEnum.TUTORIAL,"FirstForgettableSpellNotif")
            #       NotificationManager().addButtonToNotification(nid,I18n.getUiText("ui.temporis.popupFirstSpellAddedButton"),"OpenForgettableSpellsUiAction")
            #       NotificationManager().sendNotification(nid)
            #    playerForgettableSpellsDict = pcm.PlayedCharacterManager().playerForgettableSpelldict
            #    for forgettableSpell in fslumsg.spells:
            #       playerForgettableSpellsDict[forgettableSpell.spellId] = forgettableSpell
            # KernelEventsManager().processCallback(HookList.ForgettableSpellListUpdate)
            # StorageOptionManager().updateStorageView()
            # InventoryManager().inventory.releaseHooks()
            return True

        if isinstance(msg, ForgettableSpellDeleteMessage):
            # fsdmsg = msg
            # playerForgettableSpellsDict = pcm.PlayedCharacterManager().playerForgettableSpelldict
            # for forgettableSpellId in fsdmsg.spells:
            #    del playerForgettableSpellsDict[forgettableSpellId]
            # StorageOptionManager().updateStorageView()
            # InventoryManager().inventory.releaseHooks()
            return True

        if isinstance(msg, ForgettableSpellEquipmentSlotsMessage):
            # fsesmsg = msg
            # pcm.PlayedCharacterManager().playerMaxForgettableSpellsfloat = fsesmsg.quantity
            return True

        if isinstance(msg, KnownZaapListMessage):
            kzlmsg = msg
            pcm.PlayedCharacterManager().updateKnownZaaps(kzlmsg.destinations)
            return True

        # if isinstance(msg, UpdateSpellModifierAction):
        #    usmaction = msg
        #    self.updateSpellModifier(usmaction.entityId,usmaction.spellId,usmaction.statId)
        #    return True

        if isinstance(msg, GameMapSpeedMovementMessage):
            gmsmm = msg
            newSpeedAjust = 10 * (gmsmm.speedMultiplier - 1)
            pcm.PlayedCharacterManager().speedAjust = newSpeedAjust
            if (
                DofusEntities().getEntity(pcm.PlayedCharacterManager().id) is not None
                and self.roleplayContextFrame is not None
            ):
                DofusEntities().getEntity(pcm.PlayedCharacterManager().id).speedAdjust = newSpeedAjust
            return True

        return False

    @classmethod
    def updateCharacterStatsList(cls, stats: CharacterCharacteristicsInformations, isInFight=False) -> None:
        if isInFight:
            player = CurrentPlayedFighterManager().playerManager
        else:
            player = pcm.PlayedCharacterManager()
        playerInventory = InventoryManager.getInstance(player.instanceId)
        playerId = player.id
        StatsManager().addRawStats(playerId, stats.characteristics)
        SpellModifiersManager().setRawSpellsModifiers(playerId, stats.spellModifiers)
        if playerInventory and stats.kamas != playerInventory.inventory.kamas:
            playerInventory.inventory.kamas = stats.kamas
            KernelEventsManager().send(KernelEvent.KamasUpdate, stats.kamas)
        player.characteristics = stats
        if player.isFighting:
            swmod.SpellWrapper.refreshAllPlayerSpellHolder(playerId)
        Logger().info(f"Updated stats of player {playerId}")

    def updateSpellModifier(self, targetId: float, spellId: float, statId: float) -> None:
        playerId: float = pcm.PlayedCharacterManager().id
        if playerId is not targetId:
            return
        spell = swmod.SpellWrapper.getSpellWrapperById(spellId, playerId)
        if spell is not None:
            spell = spell.clone()
            ++spell.versionNum

    def pulled(self) -> bool:
        return True
