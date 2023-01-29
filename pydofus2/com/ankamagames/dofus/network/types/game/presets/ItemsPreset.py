from pydofus2.com.ankamagames.dofus.network.types.game.presets.Preset import Preset
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.presets.ItemForPreset import ItemForPreset
    from pydofus2.com.ankamagames.dofus.network.types.game.look.EntityLook import EntityLook


class ItemsPreset(Preset):
    items: list["ItemForPreset"]
    mountEquipped: bool
    look: "EntityLook"

    def init(self, items_: list["ItemForPreset"], mountEquipped_: bool, look_: "EntityLook", id_: int):
        self.items = items_
        self.mountEquipped = mountEquipped_
        self.look = look_

        super().init(id_)
