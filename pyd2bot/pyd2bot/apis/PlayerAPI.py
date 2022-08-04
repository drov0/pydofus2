
from pydofus2.com.ankamagames.dofus.kernel.Kernel import Kernel
from pydofus2.com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import PlayedCharacterManager
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayEntitiesFrame import RoleplayEntitiesFrame
    from pydofus2.com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayInteractivesFrame import RoleplayInteractivesFrame
    from pydofus2.com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayMovementFrame import RoleplayMovementFrame
    from pyd2bot.logic.roleplay.frames.BotFarmPathFrame import BotFarmPathFrame
    from pyd2bot.logic.roleplay.frames.BotPartyFrame import BotPartyFrame
    from pyd2bot.logic.roleplay.frames.BotUnloadInBankFrame import BotUnloadInBankFrame
    from pyd2bot.logic.roleplay.frames.BotUnloadInSellerFrame import BotUnloadInSellerFrame
    
class PlayerAPI:
    
    @staticmethod
    def status() -> str:
        from pydofus2.com.ankamagames.atouin.managers.MapDisplayManager import MapDisplayManager
        from pyd2bot.logic.roleplay.frames.BotSellerCollectFrame import BotSellerCollectFrame


        bpframe : 'BotPartyFrame' = Kernel().getWorker().getFrame("BotPartyFrame")
        mvframe : 'RoleplayMovementFrame' = Kernel().getWorker().getFrame("RoleplayMovementFrame")
        iframe  : 'RoleplayInteractivesFrame' = Kernel().getWorker().getFrame("RoleplayInteractivesFrame")
        rpeframe : 'RoleplayEntitiesFrame' = Kernel().getWorker().getFrame("RoleplayEntitiesFrame")
        bfpf : 'BotFarmPathFrame' = Kernel().getWorker().getFrame("BotFarmPathFrame")
        
        if MapDisplayManager().currentDataMap is None:
            return "loadingMap"
        elif rpeframe and not rpeframe.mcidm_processessed:
            return "processingMapComplementaryData"
        elif PlayedCharacterManager().isInFight:
            return "fighting"
        elif bpframe and bpframe.followingLeaderTransition:
            return f"inTransition:{bpframe.followingLeaderTransition}"
        elif bpframe and bpframe.joiningLeaderVertex is not None:
            return f"joiningLeaderVertex:{bpframe.joiningLeaderVertex}"
        elif Kernel().getWorker().getFrame("BotSellerCollectFrame"):
            f : "BotSellerCollectFrame" = Kernel().getWorker().getFrame("BotSellerCollectFrame")
            return "collectingSellerItems:" + f.state.name
        elif Kernel().getWorker().getFrame("BotUnloadInBankFrame"):
            f : "BotUnloadInBankFrame" = Kernel().getWorker().getFrame("BotUnloadInBankFrame")
            return "inBankAutoUnload:" + f.state.name
        elif Kernel().getWorker().getFrame("BotUnloadInSellerFrame"):
            f : "BotUnloadInSellerFrame" = Kernel().getWorker().getFrame("BotUnloadInSellerFrame")
            return "inSellerAutoUnload:" + f.state.name
        elif Kernel().getWorker().getFrame("BotPhenixAutoRevive"):
            return "inPhenixAutoRevive"
        elif Kernel().getWorker().getFrame("BotAutoTripFrame"):
            return "inAutoTrip"
        elif bfpf and bfpf._followinMonsterGroup:
            return "followingMonsterGroup"
        elif bfpf and bfpf._followingIe:
            return "followingIe"
        elif iframe and iframe._usingInteractive:
            return "interacting"
        elif mvframe and mvframe._isMoving:
            return "moving"
        else:
            return "idle"