from pydofus2.com.ankamagames.dofus.network.messages.game.inventory.items.SymbioticObjectErrorMessage import SymbioticObjectErrorMessage

class MimicryObjectErrorMessage(SymbioticObjectErrorMessage):
    preview: bool
    def init(self, preview_: bool, errorCode_: int, reason_: int):
        self.preview = preview_
        
        super().init(errorCode_, reason_)
    