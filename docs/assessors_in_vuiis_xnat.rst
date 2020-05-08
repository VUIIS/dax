Assessors in VUIIS XNAT
=======================

An assessor is processed on XNAT. All files produced by a script using data from one scan / multiple scans / any other process data will be / need to be upload to an assessor.

The VUIIS XNAT is using two kind of assessors :

- proc:genProcData : the generic assessor type
- fs:fsData : the specific FreeSurfer assessor type that we created (deprecated)

We are using these statuses for the assessor: 

- NO_DATA : no data exists on the sessions to be able to run
- NEED_INPUTS : input data has not been created yet for a scan, multiple scans or other assessor; sometimes this means the inputs it needs aren't present, other times, this means everything is present but the assessor hasn't built yet
- NEED_TO_RUN : ready to be launched on the cluster (ACCRE). All input data for the process to run exists
- JOB_RUNNING : the assessor is built and the job is running on ACCRE or the job is completed and is waiting to be uploaded
- JOB_FAILED : the job failed on the cluster
- READY_TO_UPLOAD : Job done, waiting for the results to be uploaded to XNAT from the cluster
- UPLOADING : in the process of uploading the resources on XNAT
- READY_TO_COMPLETE : the assessors contains all the files but we still need finish up (this includes getting the walltime and memory used on ACCRE)
- COMPLETE : all finished

There is a QA status that is managed by the project owner. This field defaults to "Needs QA". Other values can be set as desired. If set to "Rerun", the assessor will automatically be deleted and rerun.

