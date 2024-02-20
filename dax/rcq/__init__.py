""" rcq implements a job queue for DAX in REDCap. Launch/Update/Finish, no build or upload here."""
import logging


logger = logging.getLogger('dax.rcq')


# TODO: handle analysis job that only needs to be launched/updated but not
# uploaded. The job will upload it's own output. so when it's "completed" it's
# done. On finish we just need to update on redcap and delete from disk.
# Does Analysis job have a taskqueue entry or is job information stored in
# Analysis table?

# LAUNCH: requires TaskQueue from projects_redcap and slurm
# BUILD: requires Processors and TaskQueue from projects_redcap and xnat
# UPDATE: required projects_redcap and slurm
# SYNC: requires TaskQueue from projects_redcap and xnat


# TaskBuilder:
# instances_redcap
# projects_redcap
# xnat
# build()

# TaskQueue:
# projects_redcap
# get_open_tasks()
# add_task()
# apply_updates()
