from com.ankamagames.dofus.network.messages.NetworkMessage import NetworkMessage


class ChallengeTargetsListMessage(NetworkMessage):
    protocolId = 7386
    targetIds:int
    targetCells:int
    
