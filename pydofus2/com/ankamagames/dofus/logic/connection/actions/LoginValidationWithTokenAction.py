import sys
from pydofus2.com.ankamagames.dofus.logic.connection.actions.LoginValidationAction import (
    LoginValidationAction,
)


class LoginValidationWithTokenAction(LoginValidationAction):
    def __init__(self, params: list = None):
        super().__init__(params)

    @classmethod
    def create(
        cls, autoSelectServer: bool = False, serverId: int = 0, host: str = None
    ) -> "LoginValidationWithTokenAction":
        a: LoginValidationWithTokenAction = LoginValidationWithTokenAction(sys.argv[1:])
        a.password = ""
        a.username = ""
        a.autoSelectServer = autoSelectServer
        a.serverId = serverId
        a.host = host
        return a
