from com.ankamagames.dofus.network.enums.GameActionMarkTypeEnum import GameActionMarkTypeEnum
from com.ankamagames.dofus.types.entities.Projectile import Projectile
from com.ankamagames.dofus.types.enums.PortalAnimationEnum import PortalAnimationEnum
from com.ankamagames.jerakine.interfaces.IObstacle import IObstacle


class Glyph(Projectile, IObstacle):

    glyphType: int

    def __init__(
        self,
        nId: int,
        look,
        postInit: bool = False,
        startPlayingOnlyWhenDisplayed: bool = True,
        glyphType: int = 0,
    ):
        super().__init__(nId, look, postInit, startPlayingOnlyWhenDisplayed)
        self.glyphType = glyphType

    def canSeeThrough(self) -> bool:
        return True

    def canWalkThrough(self) -> bool:
        v: bool = True
        if (
            self.glyphType == GameActionMarkTypeEnum.TRAP
            or self.glyphType == GameActionMarkTypeEnum.PORTAL
            and self.getAnimation() != PortalAnimationEnum.STATE_DISABLED
        ):
            v = False
        return v

    def canWalkTo(self) -> bool:
        return True

    def addNumber(self, num: int, color: Color = None) -> None:
        pass

    def getIsTransparencyAllowed(self) -> bool:
        return True
