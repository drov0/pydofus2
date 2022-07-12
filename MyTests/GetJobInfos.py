import json
from pydofus2.com.ankamagames.dofus.datacenter.jobs.Job import Job


Jobs = Job.getJobs()
res = {}
for Job in Jobs:
    res[Job.id] = {"name": Job.name}

with open("Jobs.json", "w") as f:
    json.dump(res, f, indent=4)
