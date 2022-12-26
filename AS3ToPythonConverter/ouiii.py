
def checkClosed(self) -> bool:
if self._willClose:
    if len(self._asyncTrees) == 0:
        self._willClose = False
        self.dispatchEvent(Event(Event.CLOSE))
    return True
return False
