import json
from pydofus2.com.ankamagames.dofus.datacenter.jobs.Job import Job
from pydofus2.com.ankamagames.dofus.datacenter.jobs.Skill import Skill
res = {}
skills = Skill.getSkills()
for skill in skills:
    if skill.gatheredRessource:
        if skill.parentJobId not in res:
            res[skill.parentJobId] = { 
                "id" : skill.parentJobId,
                "name": skill.parentJob.name,
                "gatheredRessources": [] 
            }
        gr = {"name": skill.gatheredRessource.name, "id": skill.gatheredRessource.id, "levelMin": skill.levelMin}
        if gr not in res[skill.parentJobId]["gatheredRessources"]:
            res[skill.parentJobId]["gatheredRessources"].append(gr)

with open("Skills.json", "w") as f:
    json.dump(res, f, indent=4)
