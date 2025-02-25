from pydofus2.com.ankamagames.dofus.network.messages.game.inventory.exchanges.ExchangeObjectMessage import ExchangeObjectMessage

class ExchangeObjectRemovedFromBagMessage(ExchangeObjectMessage):
    objectUID: int
    def init(self, objectUID_: int, remote_: bool):
        self.objectUID = objectUID_
        
        super().init(remote_)
    