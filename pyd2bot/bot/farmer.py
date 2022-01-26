import logging
import random
from .fighter import Fighter
from . import Walker
logger = logging.getLogger("bot")

class Farmer(Walker):


    def canCollect(self, elem_id):
        logger.debug(f"Checking if elem {elem_id} can be collected")
        if elem_id in self.currMapStatedElems:
            ielem = self.currMapInteractiveElems[elem_id]
            selem = self.currMapStatedElems[elem_id]
            if ielem["onCurrentMap"] and selem["elementState"] == 0 and ielem["enabledSkills"]:
                return ielem["enabledSkills"][0]
        return None     


    def collectElement(self, elementId, skill):
        selem = self.currMapStatedElems[elementId]
        cellId = selem["elementCellId"]
        cellNode = self.cpf.getNodeFromId(cellId)
        neighbors = self.cpf.getAccessibleNeighbours(cellNode)
        for ncid in neighbors:
            if self.walkToCell(ncid):
                hash = bytes(random.getrandbits(8) for _ in range(48))
                self.farming.clear()
                self.farmingError.clear()
                self.inGame.wait()
                self.conn.send({
                    '__type__': 'InteractiveUseRequestMessage',
                    'elemId': elementId,
                    'hash_function': hash,
                    'skillInstanceUid': skill["skillInstanceUid"],
                })
                if self.farming.wait(5):
                    if self.farmingError.is_set():
                        logger.error("Farming error")
                    else:
                        logger.info(f"Collecting elem {elementId} ...")
                        if self.idle.wait(5):
                            logger.info(f"Element {elementId} collected")
                            return True
                if self._kill.is_set():
                    return
                logger.info(f"Failed to collect elem {elementId}")
                break


    def harvest(self):
        self.cpf.map = self.currMap
        logger.info("Looking for collectable resources")
        for id in self.currMapInteractiveElems.keys():
            enabledSkill = self.canCollect(id)         
            if enabledSkill is not None:
                self.collectElement(id, enabledSkill)
                if self._kill.is_set():
                    return

