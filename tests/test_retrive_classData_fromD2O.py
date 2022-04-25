from time import perf_counter
from com.ankamagames.dofus import Constants
from com.ankamagames.dofus.datacenter.jobs.Recipe import Recipe
from com.ankamagames.dofus.datacenter.notifications.Notification import Notification
from com.ankamagames.jerakine.data.I18nFileAccessor import I18nFileAccessor
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.data.GameDataFileAccessor import GameDataFileAccessor

logger = Logger(__name__)


I18nFileAccessor().init(Constants.LANG_FILE_PATH)
GameDataFileAccessor().initFromModuleName(Recipe.MODULE)


# r = Recipe.getRecipeByResultId(44)
# logger.info(r.resultName)
# for ingredient in r.ingredients:
#     logger.debug(ingredient.name)

notification = Notification.getNotificationById(37)
if notification.titleId == 756273:
    raise Exception(f"[{notification.title}] {notification.message}")
