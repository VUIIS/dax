import os
import time
from datetime import date

import cluster
from cluster import PBS
import XnatUtils

from dax_settings import RESULTS_DIR

# Job Statuses
NEED_TO_RUN='NEED_TO_RUN' # assessor that is ready to be launch on the cluster (ACCRE). All the input data for the process to run are there.
NEED_INPUTS='NEED_INPUTS' # assessor where input data are missing from a scan, multiple scans or other assessor.
JOB_RUNNING='JOB_RUNNING' # the job has been submitted on the cluster and is running right now.
JOB_FAILED='JOB_FAILED' # the job failed on the cluster.
READY_TO_UPLOAD='READY_TO_UPLOAD' # Job done, waiting for the Spider to upload the results
UPLOADING='UPLOADING' # in the process of uploading the resources on XNAT.
COMPLETE='COMPLETE' # the assessors contains all the files. The upload and the job are done.  
READY_TO_COMPLETE='READY_TO_COMPLETE' # the job finished and upload is complete
DOES_NOT_EXIST='DOES_NOT_EXIST'
OPEN_STATUS_LIST = [NEED_TO_RUN, UPLOADING, JOB_RUNNING, READY_TO_COMPLETE, JOB_FAILED]

# QA Statuses
JOB_PENDING = 'Job Pending' # job is still running, not ready for QA yet
NEEDS_QA='Needs QA' # For FS, the complete status
PASSED_QA='Passed' # QA status set by the Image Analyst after looking at the results.
FAILED='Failed' # QA status set by the Image Analyst after looking at the results.
FAILED_NEEDS_REPROC='Failed-needs reprocessing'
PASSED_EDITED_QA='Passed with edits'
RERUN='Rerun' # will cause spider to delete results and rerun the processing
REPROC='Reproc' # will cause spider to zip the current results and put in OLD, and then processing
OPEN_QC_LIST = [RERUN, REPROC]

# Other Constants
DEFAULT_PBS_DIR=os.path.join(RESULTS_DIR,'PBS')
DEFAULT_OUT_DIR=os.path.join(RESULTS_DIR,'OUTLOG')
READY_TO_UPLOAD_FLAG_FILENAME = 'READY_TO_UPLOAD.txt'
OLD_RESOURCE = 'OLD'
EDITS_RESOURCE = 'EDITS'
REPROC_RES_SKIP_LIST = [OLD_RESOURCE, EDITS_RESOURCE]

class Task(object):
    def __init__(self, processor, assessor, upload_dir):
        self.processor = processor
        self.assessor = assessor
        self.upload_dir = upload_dir    
        self.atype = processor.xsitype.lower()

        # Create assessor if needed
        if not assessor.exists():
            assessor.create(assessors=self.atype)
            self.set_createdate_today()
            if self.atype == 'proc:genprocdata':
                assessor.attrs.set('proc:genprocdata/proctype', self.get_processor_name())
                assessor.attrs.set('proc:genprocdata/validation/status', JOB_PENDING)
                assessor.attrs.set('proc:genprocdata/procversion', self.get_processor_version())
            if processor.has_inputs(assessor):
                self.set_status(NEED_TO_RUN)
            else:
                self.set_status(NEED_INPUTS)
        
        # Cache for convenience
        self.assessor_id = assessor.id()
        self.assessor_label = assessor.label()
                 
    def get_processor_name(self):
        return self.processor.name
        
    def get_processor_version(self):
        return self.processor.version
    
    def is_open(self):
        astatus = self.get_status()
        return astatus in OPEN_STATUS_LIST
    
    def copy_memused(self):
        memusedmb = ''
        if self.atype == 'proc:genprocdata':
            memusedmb = self.assessor.attrs.get('proc:genprocdata/memusedmb')
        elif self.atype == 'fs:fsdata':
            #memusedmb = ''.join(self.assessor.xpath("//xnat:addParam[@name='memusedmb']/child::text()")).replace("\n","")
            memusedmb = self.assessor.attrs.get('fs:fsdata/memusedmb')
            
        if memusedmb.strip() != '':
            memused = memusedmb + 'mb'
            #print 'DEBUG:copy memused:'+self.assessor_label+':'+memused
            self.set_memused(memused)

    def check_job_usage(self):
        #self.copy_memused()
        
        memused = self.get_memused()
        walltime = self.get_walltime()
        
        if walltime != '':
            if memused == '':
                self.set_memused('NotFound')
            else:
                pass
                #print('DEBUG:memused and walltime already set, skipping')
            
            return
        
        jobstartdate = self.get_jobstartdate()
        
        # We can't get info from cluster if job too old
        if not cluster.is_traceable_date(jobstartdate):
            self.set_walltime('NotFound')
            self.set_memused('NotFound')
            return
        
        # Get usage with tracejob
        jobinfo = cluster.tracejob_info(self.get_jobid(), jobstartdate)
        if jobinfo['mem_used'] != '': 
            memused = str(int(jobinfo['mem_used'].split('kb')[0])/1024)+'mb'
            self.set_memused(memused)
        if jobinfo['walltime_used'] != '':
            self.set_walltime(jobinfo['walltime_used'])
            
    def get_memused(self):
        memused = ''
        if self.atype == 'proc:genprocdata':
            memused = self.assessor.attrs.get('proc:genprocdata/memused')
        elif self.atype == 'fs:fsdata':
            #memused = ''.join(self.assessor.xpath("//xnat:addParam[@name='memused']/child::text()")).replace("\n","")
            memused = self.assessor.attrs.get('fs:fsdata/memused')

        return memused.strip()
    
    def set_memused(self,memused):
        if self.atype == 'proc:genprocdata':
            self.assessor.attrs.set('proc:genprocdata/memused', memused)
        elif self.atype == 'fs:fsdata':
            #self.assessor.attrs.set("fs:fsdata/parameters/addParam[name=memused]/addField", memused)
            self.assessor.attrs.set('fs:fsdata/memused', memused)

    def get_walltime(self):
        walltime = ''
        if self.atype == 'proc:genprocdata':
            walltime = self.assessor.attrs.get('proc:genprocdata/walltimeused')
        elif self.atype == 'fs:fsdata':
            #walltime = ''.join(self.assessor.xpath("//xnat:addParam[@name='walltimeused']/child::text()")).replace("\n","")
            walltime = self.assessor.attrs.get('fs:fsdata/walltimeused')
        
        return walltime.strip()

    def set_walltime(self,walltime):
        if self.atype == 'proc:genprocdata':
            self.assessor.attrs.set('proc:genprocdata/walltimeused', walltime)
        elif self.atype == 'fs:fsdata':
            #self.assessor.attrs.set("fs:fsdata/parameters/addParam[name=walltimeused]/addField", walltime)
            self.assessor.attrs.set('fs:fsdata/walltimeused', walltime)
            
    def undo_processing(self):
        from pyxnat.core.errors import DatabaseError

        self.set_qcstatus(JOB_PENDING)
        self.set_jobid(' ')
        self.set_memused(' ')
        self.set_walltime(' ')
        
        out_resource_list = self.assessor.out_resources()
        for out_resource in out_resource_list:
            if out_resource.label() not in REPROC_RES_SKIP_LIST:
                print('\t  Removing '+out_resource.label())
                try:
                    out_resource.delete()
                except DatabaseError:
                    print('\t ERROR:deleting resource.')
                    pass
            
    def reproc_processing(self):
        curtime = time.strftime("%Y%m%d-%H%M%S")
        local_dir = self.assessor_label+'_'+curtime
        local_zip = local_dir+'.zip'
        xml_filename = self.upload_dir+'/'+local_dir+'/'+self.assessor_label+'.xml'
        
        # Make the temp dir
        os.makedirs(self.upload_dir+'/'+local_dir)
        
        # Download the current resources
        out_resource_list = self.assessor.out_resources()
        for out_resource in out_resource_list:
            olabel = out_resource.label()
            if olabel not in REPROC_RES_SKIP_LIST:
                print('\tDownloading:'+olabel)
                out_res = self.assessor.out_resource(olabel)
                out_res.get(self.upload_dir+'/'+local_dir, extract=True)
        
        # Download xml of assessor
        xml = self.assessor.get()
        f = open(xml_filename,'w')
        f.write(xml+'\n')
        f.close()
        
        # Zip it all up
        cmd = 'cd '+self.upload_dir + ' && zip -qr '+local_zip+' '+local_dir+'/'
        print('DEBUG:running cmd:'+cmd)
        os.system(cmd)    
            
        # Upload it to Archive
        self.assessor.out_resource(OLD_RESOURCE).file(local_zip).put(self.upload_dir+'/'+local_zip)
        
        # Run undo
        self.undo_processing()
        
        # TODO:
        # delete the local copies
        
    def update_status(self):                
        old_status = self.get_status()
        new_status = old_status
                
        if old_status == COMPLETE or old_status == JOB_FAILED:
            qcstatus = self.get_qcstatus()
            if qcstatus == REPROC:
                print('\t *INFO:qcstatus=REPROC, running reproc_processing...')
                self.reproc_processing()
                new_status = NEED_TO_RUN
            elif qcstatus == RERUN:
                print('\t *INFO:qcstatus=RERUN, running undo_processing...')
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
            self.set_qcstatus(NEEDS_QA)
            new_status = COMPLETE
        elif old_status == NEED_INPUTS:
            # Check it again in case available inputs changed
            if self.has_inputs():
                new_status = NEED_TO_RUN
        elif old_status == JOB_RUNNING:
            new_status = self.check_running()
        elif old_status == READY_TO_UPLOAD:
            # TODO: let upload spider handle it???
            #self.check_date()
            pass
        elif old_status == UPLOADING:
            # TODO: can we see if it's really uploading???
            pass
        else:
            print('\t *ERROR:unknown status:'+old_status)
            
        if (new_status != old_status):
            print('\t *INFO:changing status from '+old_status+' to '+new_status)
            self.set_status(new_status) 
        
            # Update QC Status        
            if new_status == COMPLETE:
                self.set_qcstatus(NEEDS_QA)
            
        return new_status
    
    def get_jobid(self):    
        jobid = ''    
        if self.atype == 'proc:genprocdata':
            jobid = self.assessor.attrs.get('proc:genprocdata/jobid')
        elif self.atype == 'fs:fsdata':
            #jobid = ''.join(self.assessor.xpath("//xnat:addParam[@name='jobid']/child::text()")).replace("\n","")
            jobid = self.assessor.attrs.get('fs:fsdata/jobid')
        return jobid
        
    def get_job_status(self):
        jobstatus = 'UNKNOWN'
        jobid = self.get_jobid()
        
        if jobid != '' and jobid != '0':
            jobstatus = cluster.job_status(jobid)
       
        return jobstatus
            
    def launch(self,jobdir,job_email=None,job_email_options='bae'):
        cmds = self.commands(jobdir)
        pbsfile = self.pbs_path()
        outlog = self.outlog_path()
        pbs = PBS(pbsfile,outlog,cmds,self.processor.walltime_str,self.processor.memreq_mb,self.processor.ppn,job_email,job_email_options)
        pbs.write()
        jobid = pbs.submit()
        
        if jobid == '' or jobid == '0':
            # TODO: raise exception
            print('ERROR:failed to launch job on cluster')
            return False
        else:
            self.set_status(JOB_RUNNING)
            self.set_jobid(jobid)
            self.set_jobstartdate_today()
            
            #save record on redcap for the job that has been launch
            project=self.assessor_label.split('-x-')[0]
            SM_name=self.get_processor_name()
            data,record_id=XnatUtils.create_record_redcap(project, SM_name)
            run=XnatUtils.save_job_redcap(data,record_id)
            if not run:
                print(' ->ERROR: did not send the job to redcap for jobID <'+str(jobid)+'>: '+record_id)
            
            return True
        
    def check_date(self):
        if self.get_createdate() != '':
            return
        
        jobstartdate = self.get_jobstartdate()
        if jobstartdate != '':
            self.set_createdate(jobstartdate)
            
    def get_jobstartdate(self):
        jobstartdate = ''
        if self.atype == 'proc:genprocdata':
            jobstartdate = self.assessor.attrs.get('proc:genProcData/jobstartdate')
        elif self.atype == 'fs:fsdata':
            #jobstartdate = ''.join(self.assessor.xpath("//xnat:addParam[@name='jobstartdate']/child::text()")).replace("\n","")
            jobstartdate = self.assessor.attrs.get('fs:fsdata/jobstartdate')
        return jobstartdate
    
    def set_jobstartdate_today(self):
        today_str = str(date.today())
        return self.set_jobstartdate(today_str)
        
    def set_jobstartdate(self,date_str):
        if self.atype == 'proc:genprocdata':
            self.assessor.attrs.set('proc:genProcData/jobstartdate', date_str)
        elif self.atype == 'fs:fsdata':
            #self.assessor.attrs.set("fs:fsdata/parameters/addParam[name=jobstartdate]/addField", date_str)
            self.assessor.attrs.set('fs:fsdata/jobstartdate', date_str)
    
    def get_createdate(self):
        createdate = ''
        if self.atype == 'proc:genprocdata':
            createdate = self.assessor.attrs.get('proc:genProcData/date')
        elif self.atype == 'fs:fsdata':
            createdate = self.assessor.attrs.get('fs:fsData/date')
            
        return createdate
    
    def set_createdate(self,date_str):
        if self.atype == 'proc:genprocdata':
            self.assessor.attrs.set('proc:genProcData/date', date_str)
        elif self.atype == 'fs:fsdata':
            self.assessor.attrs.set('fs:fsData/date', date_str)
        
        return date_str
    
    def set_createdate_today(self):
        today_str = str(date.today())
        self.set_createdate(today_str)
        return today_str
    
    def get_status(self):
        if not self.assessor.exists():
            xnat_status = DOES_NOT_EXIST
        elif self.atype == 'proc:genprocdata':
            xnat_status = self.assessor.attrs.get('proc:genProcData/procstatus')
        elif self.atype == 'fs:fsdata':
            xnat_status = self.assessor.attrs.get('fs:fsdata/procstatus')
        else:
            xnat_status = 'UNKNOWN_xsiType:'+self.atype
        return xnat_status
                    
    def set_status(self,status):        
        if self.atype == 'fs:fsdata':
            self.assessor.attrs.set('fs:fsdata/procstatus', status)
        else:
            self.assessor.attrs.set('proc:genprocdata/procstatus', status)
            
    def get_qcstatus(self):
        qcstatus = ''
        atype = self.atype
        
        if not self.assessor.exists():
            qcstatus = DOES_NOT_EXIST
        elif atype == 'proc:genprocdata' or atype == 'fs:fsdata':
            qcstatus = self.assessor.attrs.get(atype+'/validation/status')
        else:
            qcstatus = 'UNKNOWN_xsiType:'+atype

        return qcstatus
                    
    def set_qcstatus(self,qcstatus):    
        atype = self.atype
        self.assessor.attrs.set(atype+'/validation/status', qcstatus)
            
    def has_inputs(self):
        return self.processor.has_inputs(self.assessor)
    
    def set_jobid(self,jobid):
        if self.atype == 'proc:genprocdata':
            self.assessor.attrs.set('proc:genprocdata/jobid', jobid)
        elif self.atype == 'fs:fsdata':
            #self.assessor.attrs.set("fs:fsdata/parameters/addParam[name=jobid]/addField", jobid)
            self.assessor.attrs.set('fs:fsdata/jobid', jobid)

    def commands(self,jobdir):
        return self.processor.get_cmds(self.assessor,jobdir+"/"+self.assessor_label)
    
    def pbs_path(self):
        return DEFAULT_PBS_DIR+'/'+self.assessor_label+'.pbs'
    
    def outlog_path(self):
        return DEFAULT_OUT_DIR+'/'+self.assessor_label+'.output'
    
    def ready_flag_exists(self):
        flagfile = self.upload_dir+'/'+self.assessor_label+'/'+READY_TO_UPLOAD_FLAG_FILENAME
        return os.path.isfile(flagfile)

    def check_running(self):
        # Check status on cluster
        jobstatus = self.get_job_status()
        
        if jobstatus == 'R' or jobstatus == 'Q':
            # Still running
            return JOB_RUNNING
        elif not self.ready_flag_exists():
            # Check for a flag file created upon completion, if it's not there then the job failed
            return JOB_FAILED
        else:
            # Let Upload Spider handle the upload
            return JOB_RUNNING
