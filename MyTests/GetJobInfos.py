from pydofus2.com.ankamagames.dofus.datacenter.jobs.Job import Job


Jobs = Job.getJobs()
for Job in Jobs:
    print(f"Jobname = {Job.name}, Jobid = {Job.id}")
