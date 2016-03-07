""" Task object to generate / manage assessors and cluster """
import os
import time
import logging
from datetime import date

import cluster
from cluster import PBS

from dax_settings import DAX_Settings
DAX_SETTINGS = DAX_Settings()
RESULTS_DIR = DAX_SETTINGS.get_results_dir()
DEFAULT_EMAIL_OPTS = DAX_SETTINGS.get_email_opts()
JOB_EXTENSION_FILE = DAX_SETTINGS.get_job_extension_file()

#Logger to print logs
LOGGER = logging.getLogger('dax')

# Job Statuses
NO_DATA = 'NO_DATA'         # assessor that doesn't have data to run (for session assessor): E.G: dtiqa multi but no dti present.
NEED_TO_RUN = 'NEED_TO_RUN' # assessor that is ready to be launch on the cluster (ACCRE). All the input data for the process to run are there.
NEED_INPUTS = 'NEED_INPUTS' # assessor where input data are missing from a scan, multiple scans or other assessor.
JOB_RUNNING = 'JOB_RUNNING' # the job has been submitted on the cluster and is running right now.
JOB_FAILED = 'JOB_FAILED' # the job failed on the cluster.
READY_TO_UPLOAD = 'READY_TO_UPLOAD' # Job done, waiting for the Spider to upload the results
UPLOADING = 'UPLOADING' # in the process of uploading the resources on XNAT.
COMPLETE = 'COMPLETE' # the assessors contains all the files. The upload and the job are done.
READY_TO_COMPLETE = 'READY_TO_COMPLETE' # the job finished and upload is complete
DOES_NOT_EXIST = 'DOES_NOT_EXIST'
OPEN_STATUS_LIST = [NEED_TO_RUN, UPLOADING, JOB_RUNNING, READY_TO_COMPLETE, JOB_FAILED]


# QC Statuses
JOB_PENDING = 'Job Pending' # job is still running, not ready for QA yet
NEEDS_QA = 'Needs QA' # job ready to be QA
GOOD = 'Good'  # QC status set by the Image Analyst after looking at the results.
PASSED_QA = 'Passed' # QC status set by the Image Analyst after looking at the results.
FAILED = 'Failed' # QC status set by the Image Analyst after looking at the results.
BAD = 'Bad' # QC status set by the Image Analyst after looking at the results.
POOR = 'Poor' # QC status set by the Image Analyst after looking at the results.
RERUN = 'Rerun' # will cause spider to delete results and rerun the processing
REPROC = 'Reproc' # will cause spider to zip the current results and put in OLD, and then processing
DONOTRUN = 'Do Not Run' # Do not run this assessor anymore
FAILED_NEEDS_REPROC = 'Failed-needs reprocessing' # FS
PASSED_EDITED_QA = 'Passed with edits' # FS
OPEN_QA_LIST = [RERUN, REPROC]
BAD_QA_STATUS = [FAILED, BAD, POOR, DONOTRUN]

# Other Constants
DEFAULT_PBS_DIR = os.path.join(RESULTS_DIR, 'PBS')
DEFAULT_OUT_DIR = os.path.join(RESULTS_DIR, 'OUTLOG')
READY_TO_UPLOAD_FLAG_FILENAME = 'READY_TO_UPLOAD.txt'
OLD_RESOURCE = 'OLD'
EDITS_RESOURCE = 'EDITS'
REPROC_RES_SKIP_LIST = [OLD_RESOURCE, EDITS_RESOURCE]

class Task(object):
    """ Class Task to generate/manage the assessor with the cluster """
    def __init__(self, processor, assessor, upload_dir):
        """
        Init of class Task

        :param processor: processor used
        :param assessor: assessor dict ?
        :param upload_dir: upload directory to copy data to after the job finishes.
        :return: None

        """
        self.processor = processor
        self.assessor = assessor
        self.upload_dir = upload_dir
        self.atype = processor.xsitype.lower()

        # Create assessor if needed
        if not assessor.exists():
            assessor.create(assessors=self.atype)
            self.set_createdate_today()
            atype = self.atype.lower()
            if atype == 'proc:genprocdata':
                assessor.attrs.mset({atype +'/proctype':self.get_processor_name(),
                atype+'/procversion':self.get_processor_version()})

            self.set_proc_and_qc_status(NEED_INPUTS, JOB_PENDING)

        # Cache for convenience
        self.assessor_id = assessor.id()
        self.assessor_label = assessor.label()

    def get_processor_name(self):
        """
        Get the name of the Processor for the Task.

        :return: String of the Processor name.

        """
        return self.processor.name

    def get_processor_version(self):
        """
        Get the version of the Processor.

        :return: String of the Processor version.

        """
        return self.processor.version

    def is_open(self):
        """
        Check to see if a task is still in "Open" status as defined in
         OPEN_STATUS_LIST.

        :return: True if the Task is open. False if it is not open

        """
        astatus = self.get_status()
        return astatus in OPEN_STATUS_LIST

    def get_job_usage(self):
        """
        Get the amount of memory used, the amount of walltime used, the jobid
         of the process, the node the process ran on, and when it started
         from the scheduler.

        :return: List of strings. Memory used, walltime used, jobid, node used,
         and start date

        """
        atype = self.atype
        [memused, walltime, jobid, jobnode, jobstartdate] = self.assessor.attrs.mget(
            [atype+'/memused', atype+'/walltimeused', atype+'/jobid', atype+'/jobnode', atype+'/jobstartdate'])
        return [memused.strip(), walltime.strip(), jobid.strip(), jobnode.strip(), jobstartdate.strip()]

    def check_job_usage(self):
        """
        The task has now finished, get the amount of memory used, the amount of
         walltime used, the jobid of the process, the node the process ran on,
         and when it started from the scheduler. Set these values on XNAT

        :return: None

        """
        [memused, walltime, jobid, jobnode, jobstartdate] = self.get_job_usage()

        if walltime != '':
            if memused != '' and jobnode != '':
                LOGGER.debug('memused and walltime already set, skipping')
            else:
                if memused == '':
                    self.set_memused('NotFound')
                if jobnode == '':
                    self.set_jobnode('NotFound')
            return

        # We can't get info from cluster if job too old
        if not cluster.is_traceable_date(jobstartdate):
            self.set_walltime('NotFound')
            self.set_memused('NotFound')
            self.set_jobnode('NotFound')
            return

        # Get usage with tracejob
        jobinfo = cluster.tracejob_info(jobid, jobstartdate)
        if jobinfo['mem_used'].strip():
            self.set_memused(jobinfo['mem_used'])
        else:
            self.set_memused('NotFound')
        if jobinfo['walltime_used'].strip():
            self.set_walltime(jobinfo['walltime_used'])
        else:
            self.set_walltime('NotFound')
        if jobinfo['jobnode'].strip():
            self.set_jobnode(jobinfo['jobnode'])
        else:
            self.set_jobnode('NotFound')

    def get_memused(self):
        """
        Get the amount of memory used for a process

        :return: String of how much memory was used

        """
        memused = self.assessor.attrs.get(self.atype+'/memused')
        return memused.strip()

    def set_memused(self, memused):
        """
        Set the amount of memory used for a process

        :param memused: String denoting the amount of memory used
        :return: None

        """
        self.assessor.attrs.set(self.atype+'/memused', memused)

    def get_walltime(self):
        """
        Get the amount of walltime used for a process

        :return: String of how much walltime was used for a process

        """
        walltime = self.assessor.attrs.get(self.atype+'/walltimeused')
        return walltime.strip()

    def set_walltime(self, walltime):
        """
        Set the value of walltime used for an assessor on XNAT

        :param walltime: String denoting how much time was used running
         the process.
        :return: None

        """
        self.assessor.attrs.set(self.atype+'/walltimeused', walltime)

    def get_jobnode(self):
        """
        Gets the node that a process ran on

        :return: String identifying the node that a job ran on

        """
        jobnode = self.assessor.attrs.get(self.atype+'/jobnode')
        return jobnode.strip()

    def set_jobnode(self, jobnode):
        """
        Set the value of the the node that the process ran on on the grid

        :param jobnode: String identifying the node the job ran on
        :return: None

        """
        self.assessor.attrs.set(self.atype+'/jobnode', jobnode)

    def undo_processing(self):
        """
        Unset the job ID, memory used, walltime, and jobnode information
         for the assessor on XNAT

        :except: pyxnat.core.errors.DatabaseError when attempting to
         delete a resource
        :return: None

        """
        from pyxnat.core.errors import DatabaseError

        self.set_qcstatus(JOB_PENDING)
        self.set_jobid(' ')
        self.set_memused(' ')
        self.set_walltime(' ')
        self.set_jobnode(' ')

        out_resource_list = self.assessor.out_resources()
        for out_resource in out_resource_list:
            if out_resource.label() not in REPROC_RES_SKIP_LIST:
                LOGGER.info('   Removing '+out_resource.label())
                try:
                    out_resource.delete()
                except DatabaseError:
                    LOGGER.error('   ERROR:deleting resource.')

    def reproc_processing(self):
        """
        If the procstatus of an assessor is REPROC on XNAT, rerun the assessor.

        :return: None

        """
        curtime = time.strftime("%Y%m%d-%H%M%S")
        local_dir = self.assessor_label+'_'+curtime
        local_zip = local_dir+'.zip'
        xml_filename = os.path.join(self.upload_dir, local_dir, self.assessor_label+'.xml')

        # Make the temp dir
        os.makedirs(os.path.join(self.upload_dir, local_dir))

        # Download the current resources
        out_resource_list = self.assessor.out_resources()
        for out_resource in out_resource_list:
            olabel = out_resource.label()
            if olabel not in REPROC_RES_SKIP_LIST and len(out_resource.files().get()) > 0:
                LOGGER.info('   Downloading:'+olabel)
                out_res = self.assessor.out_resource(olabel)
                out_res.get(os.path.join(self.upload_dir, local_dir), extract=True)

        # Download xml of assessor
        xml = self.assessor.get()
        f = open(xml_filename, 'w')
        f.write(xml+'\n')
        f.close()

        # Zip it all up
        cmd = 'cd '+self.upload_dir + ' && zip -qr '+local_zip+' '+local_dir+'/'
        LOGGER.debug('running cmd:'+cmd)
        os.system(cmd)

        # Upload it to Archive
        self.assessor.out_resource(OLD_RESOURCE).file(local_zip).put(os.path.join(self.upload_dir, local_zip))

        # Run undo
        self.undo_processing()

        # TODO:
        # delete the local copies

    def update_status(self):
        """
        Update the satus of a Task object.

        :return: the "new" status (updated) of the Task.

        """
        old_status, qcstatus, jobid = self.get_statuses()
        new_status = old_status

        if old_status == COMPLETE or old_status == JOB_FAILED:
            if qcstatus == REPROC:
                LOGGER.info('   * qcstatus=REPROC, running reproc_processing...')
                self.reproc_processing()
                new_status = NEED_TO_RUN
            elif qcstatus == RERUN:
                LOGGER.info('   * qcstatus=RERUN, running undo_processing...')
                self.undo_processing()
                new_status = NEED_TO_RUN
            else:
                #self.check_date()
                pass
        elif old_status == NEED_TO_RUN:
            # TODO: anything, not yet???
            pass
        elif old_status == READY_TO_COMPLETE:
            self.check_job_usage()
            new_status = COMPLETE
        elif old_status == NEED_INPUTS:
            # This is now handled by dax_build
            pass
        elif old_status == JOB_RUNNING:
            new_status = self.check_running(jobid)
        elif old_status == READY_TO_UPLOAD:
            # TODO: let upload spider handle it???
            #self.check_date()
            pass
        elif old_status == UPLOADING:
            # TODO: can we see if it's really uploading???
            pass
        elif old_status == NO_DATA:
            pass
        else:
            LOGGER.warn('   * unknown status for '+self.assessor_label+': '+old_status)

        if new_status != old_status:
            LOGGER.info('   * changing status from '+old_status+' to '+new_status)

            # Update QC Status
            if new_status == COMPLETE:
                self.set_proc_and_qc_status(new_status, NEEDS_QA)
            else:
                self.set_status(new_status)

        return new_status

    def get_jobid(self):
        """
        Get the jobid of an assessor as stored on XNAT

        :return: string of the jobid

        """
        jobid = self.assessor.attrs.get(self.atype+'/jobid').strip()
        return jobid

    def get_job_status(self,jobid=None):
        """
        Get the status of a job given its jobid as assigned by the scheduler

        :param jobid: job id assigned by the scheduler
        :return: string from call to cluster.job_status or UNKNOWN.

        """
        jobstatus = 'UNKNOWN'
        if jobid == None:
            jobid = self.get_jobid()

        if jobid != '' and jobid != '0':
            jobstatus = cluster.job_status(jobid)

        return jobstatus

    def launch(self, jobdir, job_email=None, job_email_options=DEFAULT_EMAIL_OPTS, xnat_host=os.environ['XNAT_HOST']):
        """
        Method to launch a job on the grid

        :param jobdir: absolute path to where the data will be stored on the node
        :param job_email: who to email if the job fails
        :param job_email_options: grid-specific job email options (e.g.,
         fails, starts, exits etc)
        :raises: cluster.ClusterLaunchException if the jobid is 0 or empty
         as returned by pbs.submit() method
        :return: True if the job failed

        """
        cmds = self.commands(jobdir)
        pbsfile = self.pbs_path()
        outlog = self.outlog_path()
        pbs = PBS(pbsfile, outlog, cmds, self.processor.walltime_str, self.processor.memreq_mb,
                  self.processor.ppn, job_email, job_email_options, xnat_host)
        pbs.write()
        jobid = pbs.submit()

        if jobid == '' or jobid == '0':
            LOGGER.error('failed to launch job on cluster')
            raise cluster.ClusterLaunchException
        else:
            self.set_launch(jobid)
            return True

    def check_date(self):
        """
        Sets the job created date if the assessor was not made through
         dax_build

        :return: Returns if get_createdate() is != '', sets date otherwise

        """
        if self.get_createdate() != '':
            return

        jobstartdate = self.get_jobstartdate()
        if jobstartdate != '':
            self.set_createdate(jobstartdate)

    def get_jobstartdate(self):
        """
        Get the date that the job started

        :return: String of the date that the job started in "%Y-%m-%d" format

        """
        return self.assessor.attrs.get(self.atype+'/jobstartdate')

    def set_jobstartdate_today(self):
        """
        Set the date that the job started on the grid to today

        :return: call to set_jobstartdate with today's date

        """
        today_str = str(date.today())
        return self.set_jobstartdate(today_str)

    def set_jobstartdate(self, date_str):
        """
        Set the date that the job started on the grid based on user passed
         value

        :param date_str: Datestring in the format "%Y-%m-%d" to set the job
         starte date to
        :return: None

        """
        self.assessor.attrs.set(self.atype.lower()+'/jobstartdate', date_str)

    def get_createdate(self):
        """
        Get the date an assessor was created

        :return: String of the date the assessor was created in "%Y-%m-%d"
         format

        """
        return self.assessor.attrs.get(self.atype+'/date')

    def set_createdate(self, date_str):
        """
        Set the date of the assessor creation to user passed value

        :param date_str: String of the date in "%Y-%m-%d" format
        :return: String of today's date in "%Y-%m-%d" format

        """
        self.assessor.attrs.set(self.atype+'/date', date_str)
        return date_str

    def set_createdate_today(self):
        """
        Set the date of the assessor creation to today

        :return: String of todays date in "%Y-%m-%d" format

        """
        today_str = str(date.today())
        self.set_createdate(today_str)
        return today_str

    def get_status(self):
        """
        Get the procstatus of an assessor

        :return: The string of the procstatus of the assessor.
         DOES_NOT_EXIST if the assessor does not exist

        """
        if not self.assessor.exists():
            xnat_status = DOES_NOT_EXIST
        elif self.atype == 'proc:genprocdata':
            xnat_status = self.assessor.attrs.get('proc:genProcData/procstatus')
        elif self.atype == 'fs:fsdata':
            xnat_status = self.assessor.attrs.get('fs:fsdata/procstatus')
        else:
            xnat_status = 'UNKNOWN_xsiType:'+self.atype
        return xnat_status

    def get_statuses(self):
        """
        Get the procstatus, qcstatus, and job id of an assessor

        :return: Serially ordered strings of the assessor procstatus,
         qcstatus, then jobid.
        """
        atype = self.atype
        if not self.assessor.exists():
            xnat_status = DOES_NOT_EXIST
            qcstatus = DOES_NOT_EXIST
            jobid = ''
        elif atype == 'proc:genprocdata' or atype == 'fs:fsdata':
            xnat_status, qcstatus, jobid = self.assessor.attrs.mget(
                [atype+'/procstatus', atype+'/validation/status', atype+'/jobid'])
        else:
            xnat_status = 'UNKNOWN_xsiType:'+atype
            qcstatus = 'UNKNOWN_xsiType:'+atype
            jobid = ''

        return xnat_status, qcstatus, jobid

    def set_status(self, status):
        """
        Set the procstatus of an assessor on XNAT

        :param status: String to set the procstatus of the assessor to
        :return: None

        """
        self.assessor.attrs.set(self.atype+'/procstatus', status)

    def get_qcstatus(self):
        """
        Get the qcstatus of the assessor

        :return: A string of the qcstatus for the assessor if it exists.
         If it does not, it returns DOES_NOT_EXIST.
         The else case returns an UNKNOWN xsiType with the xsiType of the
         assessor as stored on XNAT.
        """
        qcstatus = ''
        atype = self.atype

        if not self.assessor.exists():
            qcstatus = DOES_NOT_EXIST
        elif atype == 'proc:genprocdata' or atype == 'fs:fsdata':
            qcstatus = self.assessor.attrs.get(atype+'/validation/status')
        else:
            qcstatus = 'UNKNOWN_xsiType:'+atype

        return qcstatus

    def set_qcstatus(self, qcstatus):
        """
        Set the qcstatus of the assessor

        :param qcstatus: String to set the qcstatus to
        :return: None

        """
        self.assessor.attrs.mset({self.atype+'/validation/status': qcstatus,
                                  self.atype+'/validation/validated_by':'NULL',
                                  self.atype+'/validation/date':'NULL',
                                  self.atype+'/validation/notes':'NULL',
                                  self.atype+'/validation/method':'NULL'})

    def set_proc_and_qc_status(self, procstatus, qcstatus):
        """
        Set the procstatus and qcstatus of the assessor

        :param procstatus: String to set the procstatus of the assessor to
        :param qcstatus: String to set the qcstatus of the assessor to
        :return: None

        """
        self.assessor.attrs.mset({self.atype+'/procstatus':procstatus,
                                  self.atype+'/validation/status':qcstatus})

    def set_jobid(self, jobid):
        """
        Set the job ID of the assessor on XNAT

        :param jobid: The ID of the process assigned by the grid scheduler
        :return: None

        """
        self.assessor.attrs.set(self.atype+'/jobid', jobid)

    def set_launch(self, jobid):
        """
        Set the date that the job started and its associated ID on XNAT.
        Additionally, set the procstatus to JOB_RUNNING

        :param jobid: The ID of the process assigned by the grid scheduler
        :return: None

        """
        today_str = str(date.today())
        atype = self.atype.lower()
        self.assessor.attrs.mset({
            atype+'/jobstartdate':today_str,
            atype+'/jobid':jobid,
            atype+'/procstatus':JOB_RUNNING})

    def commands(self, jobdir):
        """
        Call the get_cmds method of the class Processor.

        :param jobdir: Fully qualified path where the job will run on the node.
         Note that this is likely to start with /tmp on most grids.
        :return: A string that makes a command line call to a spider with all
         args.

        """
        return self.processor.get_cmds(self.assessor, os.path.join(jobdir, self.assessor_label))

    def pbs_path(self):
        """
        Method to return the path of the PBS file for the job

        :return: A string that is the absolute path to the PBS file that will
         be submitted to the scheduler for execution.

        """
        return os.path.join(DEFAULT_PBS_DIR, self.assessor_label+JOB_EXTENSION_FILE)

    def outlog_path(self):
        """
        Method to return the path of the PBS file for the job

        :return: A string that is the absolute path to the PBS file that will be submitted to the scheduler for execution.

        """
        return os.path.join(DEFAULT_OUT_DIR, self.assessor_label+'.output')

    def ready_flag_exists(self):
        """
        Method to see if the flag file
        <UPLOAD_DIR>/<ASSESSOR_LABEL>/READY_TO_UPLOAD.txt exists

        :return: True if the file exists. False if the file does not exist.

        """
        flagfile = os.path.join(self.upload_dir, self.assessor_label, READY_TO_UPLOAD_FLAG_FILENAME)
        return os.path.isfile(flagfile)

    def check_running(self, jobid=None):
        """
        Check to see if a job specified by the scheduler ID is still running

        :param jobid: The ID of the job in question assigned by the scheduler.
        :return: A String of JOB_RUNNING if the job is running or enqueued and
         JOB_FAILED if the ready flag (see read_flag_exists) does not exist
         in the assessor label folder in the upload directory.

        """
        # Check status on cluster
        jobstatus = self.get_job_status(jobid)

        if not jobstatus or jobstatus == 'R' or jobstatus == 'Q':
            # Still running
            return JOB_RUNNING
        elif not self.ready_flag_exists():
            # Check for a flag file created upon completion, if it's not there then the job failed
            return JOB_FAILED
        else:
            # Let Upload Spider handle the upload
            return JOB_RUNNING
