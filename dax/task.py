""" Task object to generate / manage assessors and cluster """
import os
import time
import logging
from datetime import date

import cluster
from cluster import PBS
import XnatUtils, bin

from dax_settings import RESULTS_DIR, DEFAULT_EMAIL_OPTS, JOB_EXTENSION_FILE

#Logger to print logs
LOGGER = logging.getLogger('dax')

# Job Statuses
NO_DATA = 'NO_DATA'         # assessor that doesn't have data to run (for session assessor): E.G: dtiqa multi but no dti present.
NEED_TO_RUN = 'NEED_TO_RUN' # assessor that is ready to be launch on the cluster (ACCRE). All the input data for the process to run are there.
NEED_INPUTS = 'NEED_INPUTS' # assessor where input data are missing from a scan, multiple scans or other assessor.
JOB_RUNNING = XnatUtils.JOB_RUNNING # the job has been submitted on the cluster and is running right now.
JOB_FAILED = XnatUtils.JOB_FAILED # the job failed on the cluster.
READY_TO_UPLOAD = XnatUtils.READY_TO_UPLOAD # Job done, waiting for the Spider to upload the results
UPLOADING = 'UPLOADING' # in the process of uploading the resources on XNAT.
COMPLETE = 'COMPLETE' # the assessors contains all the files. The upload and the job are done.
READY_TO_COMPLETE = 'READY_TO_COMPLETE' # the job finished and upload is complete
DOES_NOT_EXIST = 'DOES_NOT_EXIST'
OPEN_STATUS_LIST = [NEED_TO_RUN, UPLOADING, JOB_RUNNING, READY_TO_COMPLETE, JOB_FAILED]

# QA Statuses
BAD_QA_STATUS = XnatUtils.BAD_QA_STATUS
JOB_PENDING = XnatUtils.JOB_PENDING
NEEDS_QA = XnatUtils.NEEDS_QA
PASSED_QA = 'Passed' # QA status set by the Image Analyst after looking at the results.
FAILED = 'Failed' # QA status set by the Image Analyst after looking at the results.
FAILED_NEEDS_REPROC = 'Failed-needs reprocessing'
PASSED_EDITED_QA = 'Passed with edits'
RERUN = 'Rerun' # will cause spider to delete results and rerun the processing
REPROC = XnatUtils.REPROC
OPEN_QC_LIST = [RERUN, REPROC]

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
        """ init function """
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

            self.set_statuses(NEED_INPUTS, JOB_PENDING)

        # Cache for convenience
        self.assessor_id = assessor.id()
        self.assessor_label = assessor.label()

    def get_processor_name(self):
        """ return name of the processor """
        return self.processor.name

    def get_processor_version(self):
        """ return the version of the processor """
        return self.processor.version

    def is_open(self):
        """ return true if the task status is open """
        astatus = self.get_status()
        return astatus in OPEN_STATUS_LIST
        
    def get_job_usage(self):
        """ return assessor job usage values from XNAT """
        atype = self.atype
        [memused, walltime, jobid, jobnode, jobstartdate] = self.assessor.attrs.mget(
            [atype+'/memused', atype+'/walltimeused', atype+'/jobid', atype+'/jobnode', atype+'/jobstartdate'])
        return [memused.strip(), walltime.strip(), jobid.strip(), jobnode.strip(), jobstartdate.strip()]

    def check_job_usage(self):
        """ check the job information on the cluster for the task """
        [memused, walltime, jobid, jobnode, jobstartdate] = self.get_job_usage()

        if walltime != '':
            if memused != '' and jobnode != '':
                LOGGER.debug('memused and walltime already set, skipping')
                pass
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
        """ return memused of the assessor """
        memused = self.assessor.attrs.get(self.atype+'/memused')
        return memused.strip()

    def set_memused(self, memused):
        """ set memused on the assessor """
        self.assessor.attrs.set(self.atype+'/memused', memused)

    def get_walltime(self):
        """ return walltime of the assessor """
        walltime = self.assessor.attrs.get(self.atype+'/walltimeused')
        return walltime.strip()

    def set_walltime(self, walltime):
        """ set walltime on the assessor """
        self.assessor.attrs.set(self.atype+'/walltimeused', walltime)

    def get_jobnode(self):
        """ return jobnode of the assessor"""
        jobnode = self.assessor.attrs.get(self.atype+'/jobnode')
        return jobnode.strip()

    def set_jobnode(self, jobnode):
        """ set jobnode on the assessor """
        self.assessor.attrs.set(self.atype+'/jobnode', jobnode)

    def undo_processing(self):
        """ undo a processing on XNAT """
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
                    pass

    def reproc_processing(self):
        """ rerun a processing from XNAT """
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
        """ update the status of a task """
        old_status, qcstatus, jobid = self.get_statuses()
        new_status = old_status

        if old_status == COMPLETE or old_status == JOB_FAILED:
            if qcstatus == REPROC:
                LOGGER.info('   *qcstatus=REPROC, running reproc_processing...')
                self.reproc_processing()
                new_status = NEED_TO_RUN
            elif qcstatus == RERUN:
                LOGGER.info('   *qcstatus=RERUN, running undo_processing...')
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
            LOGGER.warn('   *unknown status for '+self.assessor_label+': '+old_status)

        if new_status != old_status:
            LOGGER.info('   *changing status from '+old_status+' to '+new_status)

            # Update QC Status
            if new_status == COMPLETE:
                self.set_statuses(new_status, NEEDS_QA)
            else:
                self.set_status(new_status)

        return new_status

    def get_jobid(self):
        """ return jobid for the task """
        jobid = self.assessor.attrs.get(self.atype+'/jobid').strip()
        return jobid

    def get_job_status(self,jobid=None):
        """ return job status for the task """
        jobstatus = 'UNKNOWN'
        if jobid == None:
            jobid = self.get_jobid()

        if jobid != '' and jobid != '0':
            jobstatus = cluster.job_status(jobid)

        return jobstatus

    def launch(self, jobdir, job_email=None, job_email_options=DEFAULT_EMAIL_OPTS):
        """ launch the task on the cluster """
        cmds = self.commands(jobdir)
        pbsfile = self.pbs_path()
        outlog = self.outlog_path()
        pbs = PBS(pbsfile, outlog, cmds, self.processor.walltime_str, self.processor.memreq_mb,
                  self.processor.ppn, job_email, job_email_options)
        pbs.write()
        jobid = pbs.submit()

        if jobid == '' or jobid == '0':
            # TODO: raise exception
            LOGGER.error('failed to launch job on cluster')
            return False
        else:
            self.set_launch(jobid)
            return True

    def check_date(self):
        """ check the date of the job start """
        if self.get_createdate() != '':
            return

        jobstartdate = self.get_jobstartdate()
        if jobstartdate != '':
            self.set_createdate(jobstartdate)

    def get_jobstartdate(self):
        """ return the starting date of the job """
        return self.assessor.attrs.get(self.atype+'/jobstartdate')

    def set_jobstartdate_today(self):
        """ set the starting date for the assessor as the day of today"""
        today_str = str(date.today())
        return self.set_jobstartdate(today_str)

    def set_jobstartdate(self, date_str):
        """ set the starting date of the assessor """
        self.assessor.attrs.set(self.atype.lower()+'/jobstartdate', date_str)

    def get_createdate(self):
        """ return create date of assessor """
        return self.assessor.attrs.get(self.atype+'/date')

    def set_createdate(self, date_str):
        """ set create date for assessor and return it """
        self.assessor.attrs.set(self.atype+'/date', date_str)
        return date_str

    def set_createdate_today(self):
        """ set create date to today """
        today_str = str(date.today())
        self.set_createdate(today_str)
        return today_str

    def get_status(self):
        """ return procstatus for assessor """
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
        """ return procstatus and qcstatus for assessor """
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
        """ set the procstatus """
        self.assessor.attrs.set(self.atype+'/procstatus', status)

    def get_qcstatus(self):
        """ return qcstatus """
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
        """ set the qcstatus """
        self.assessor.attrs.set(self.atype+'/validation/status', qcstatus)
        
    def set_statuses(self, procstatus, qcstatus):
        atype = self.atype
        """ set the procstatus """
        self.assessor.attrs.mset({atype+'/procstatus':procstatus, atype+'/validation/status':qcstatus})

    def set_jobid(self, jobid):
        """ set the jobid """
        self.assessor.attrs.set(self.atype+'/jobid', jobid)

    def set_launch(self, jobid):
        """ set the launch params  of the assessor """
        today_str = str(date.today())
        atype = self.atype.lower()
        self.assessor.attrs.mset({
            atype+'/jobstartdate':today_str,
            atype+'/jobid':jobid,
            atype+'/procstatus':JOB_RUNNING})

    def commands(self, jobdir):
        """ get the commands from the processor """
        return self.processor.get_cmds(self.assessor, os.path.join(jobdir, self.assessor_label))

    def pbs_path(self):
        """ return the pbs path for the task """
        return os.path.join(DEFAULT_PBS_DIR, self.assessor_label+JOB_EXTENSION_FILE)

    def outlog_path(self):
        """ return the outlog path for the task """
        return os.path.join(DEFAULT_OUT_DIR, self.assessor_label+'.output')

    def ready_flag_exists(self):
        """ return the flag path """
        flagfile = os.path.join(self.upload_dir, self.assessor_label, READY_TO_UPLOAD_FLAG_FILENAME)
        return os.path.isfile(flagfile)

    def check_running(self,jobid=None):
        """ check if the job is still running """
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
