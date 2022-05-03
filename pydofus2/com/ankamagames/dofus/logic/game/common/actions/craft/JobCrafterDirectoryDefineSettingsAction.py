import sys
from com.ankamagames.dofus.internalDatacenter.jobs.KnownJobWrapper import KnownJobWrapper
from com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import PlayedCharacterManager
from com.ankamagames.dofus.misc.utils.AbstractAction import AbstractAction
from com.ankamagames.dofus.network.types.game.context.roleplay.job.JobCrafterDirectorySettings import (
    JobCrafterDirectorySettings,
)
from com.ankamagames.jerakine.handlers.messages.Action import Action


class JobCrafterDirectoryDefineSettingsAction(AbstractAction, Action):

    jobId: int

    minLevel: int

    free: bool

    settings: JobCrafterDirectorySettings

    def __init__(self, params: list = None):
        super().__init__(params)

    @classmethod
    def create(cls, jobId: int, minLevel: int, free: bool) -> "JobCrafterDirectoryDefineSettingsAction":
        job: KnownJobWrapper = None
        act: JobCrafterDirectoryDefineSettingsAction = cls(sys.argv[1:])
        act.jobId = jobId
        act.minLevel = minLevel
        act.free = free
        act.settings = JobCrafterDirectorySettings()
        jobs: list = PlayedCharacterManager().jobs
        for i in range(len(jobs)):
            job = jobs[i]
            if job and job.id == jobId:
                act.settings.init(i, minLevel, free)
        return act
