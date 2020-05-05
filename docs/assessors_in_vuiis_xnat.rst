Assessors in VUIIS XNAT
=======================

An assessor is processed on XNAT. All files produced by a script using data from one scan / multiple scans / any other process data will be / need to be upload to an assessor.

The VUIIS XNAT is using two kind of assessors :

- proc:genProcData : the generic assessor type
- fs:fsData : the specific FreeSurfer assessor type that we created (deprecated)

We are using these statuses for the assessor: 

- NO_DATA : no data exists on the sessions to be able to run
- NEED_INPUTS : input data has not been created yet for a scan, multiple scans or other assessor; sometimes this means the inputs it needs aren't present, other times, this means everything is present but the assessor hasn't built yet
- NEED_TO_RUN : ready to be launched on the cluster (ACCRE). All input data for the process to run exist
- JOB_RUNNING : the assessor is built and the job is running on ACCRE or the job is completed and is waiting to be uploaded
- JOB_FAILED : the job failed on the cluster
- READY_TO_UPLOAD : Job done, waiting for the results to be uploaded
- UPLOADING : in the process of uploading the resources on XNAT
- READY_TO_COMPLETE : the assessors contains all the files but we still need finish up (this includes getting the walltime and memory used on ACCRE)
- COMPLETE : all finished

These status are used in the processes to launch / check jobs. To run a job, it will check the status NEED_TO_RUN for example.

We also have a QA status:

- Failed: QA status if failed set by the Image Analyst after looking at the results
- Passed: QA status if passed set by the Image Analyst after looking at the results
- Needs QA: QA status by default
- Rerun: to restart a process (e.g: FreeSurfer); this can be set by the user when a restart is desired

You can set a new status when you are checking the QA (E.G : Passed with Edits).
