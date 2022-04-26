import sys
from com.ankamagames.dofus.misc.utils.AbstractAction import AbstractAction
from com.ankamagames.jerakine.handlers.messages.Action import Action
from com.ankamagames.jerakine.messages.IDontLogThisMessage import IDontLogThisMessage


class LoginValidationAction(AbstractAction, Action, IDontLogThisMessage):

    username: str

    password: str

    autoSelectServer: bool

    serverId: int

    host: str

    def __init__(self, params: list = None):
        super().__init__(params)

    def create(
        self,
        username: str,
        password: str,
        autoSelectServer: bool,
        serverId: int = 0,
        host: str = None,
    ) -> "LoginValidationAction":
        a: LoginValidationAction = LoginValidationAction(self._parameters)
        a.password = password
        a.username = username
        a.autoSelectServer = autoSelectServer
        a.serverId = serverId
        a.host = host
        return a
