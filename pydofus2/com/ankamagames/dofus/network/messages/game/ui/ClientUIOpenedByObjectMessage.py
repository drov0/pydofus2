from pydofus2.com.ankamagames.dofus.network.messages.game.ui.ClientUIOpenedMessage import ClientUIOpenedMessage

class ClientUIOpenedByObjectMessage(ClientUIOpenedMessage):
    uid: int
    def init(self, uid_: int, type_: int):
        self.uid = uid_
        
        super().init(type_)
    