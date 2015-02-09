#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" launcher.py

"""
__copyright__ = 'Copyright 2013 Vanderbilt University. All Rights Reserved'

import os
import sys
import logging
from datetime import datetime, timedelta

import processors
import modules
import XnatUtils
import task
import cluster
import bin
from task import Task
from dax_settings import RESULTS_DIR,DEFAULT_ROOT_JOB_DIR,DEFAULT_QUEUE_LIMIT

UPDATE_LOCK_FILE  = 'UPDATE_RUNNING.txt'
OPEN_TASKS_LOCK_FILE  = 'OPEN_TASKS_UPDATE_RUNNING.txt'
UPDATE_FORMAT = "%Y-%m-%d %H:%M:%S"
UPDATE_PREFIX = 'updated--'

#Logger to print logs
logger = logging.getLogger('dax')

class Launcher(object):
    def __init__(self,project_process_dict,project_modules_dict,priority_project=None,queue_limit=DEFAULT_QUEUE_LIMIT, root_job_dir=DEFAULT_ROOT_JOB_DIR, xnat_user=None, xnat_pass=None, xnat_host=None, upload_dir=None, job_email=None,job_email_options='bae'):
        self.queue_limit = queue_limit
        self.root_job_dir = root_job_dir
        self.project_process_dict = project_process_dict
        self.project_modules_dict = project_modules_dict
        self.priority_project = priority_project
        self.job_email=job_email
        self.job_email_options=job_email_options
        
        #Creating Folders for flagfile/pbs/outlog in RESULTS_DIR
        if not os.path.exists(RESULTS_DIR):
            os.mkdir(RESULTS_DIR)
        if not os.path.exists(os.path.join(RESULTS_DIR,'PBS')):
            os.mkdir(os.path.join(RESULTS_DIR,'PBS'))
        if not os.path.exists(os.path.join(RESULTS_DIR,'OUTLOG')):
            os.mkdir(os.path.join(RESULTS_DIR,'OUTLOG'))
        if not os.path.exists(os.path.join(RESULTS_DIR,'FlagFiles')):
            os.mkdir(os.path.join(RESULTS_DIR,'FlagFiles'))
        
        # Add empty lists for projects in one list but not the other
        for proj in self.project_process_dict.keys():
            if proj not in self.project_modules_dict:
                self.project_modules_dict[proj] = []
        
        for proj in self.project_modules_dict.keys():
            if proj not in self.project_process_dict:
                self.project_process_dict[proj] = []

        try:
            if xnat_user == None:
                self.xnat_user = os.environ['XNAT_USER']
            else:
                self.xnat_user = xnat_user
                
            if xnat_pass == None:
                self.xnat_pass = os.environ['XNAT_PASS']
            else:
                self.xnat_pass = xnat_pass
                
            if xnat_host == None:
                self.xnat_host = os.environ['XNAT_HOST']
            else:
                self.xnat_host = xnat_host

        except KeyError as e:
            logger.error("You must set the environment variable %s" % str(e))
            sys.exit(1)  
        
        #if project_process_dict == None:
            # TODO: get the default list of processors and get list of project 
            # this user has access to process here we could have the masispider 
            # user get all the projects it can access, so then users could just 
            # add masispider as a member of their project and it would process 
            # their data,good idea???

        # TODO: check the project process list
        # TODO: check that projects exist
    
    #If priority list given in parameters: 
    def get_project_list(self,list_of_all_projects):
        random_project=filter(lambda project: project not in self.priority_project, list_of_all_projects)
        return self.priority_project+random_project
        
    def update_open_tasks(self, lockfile_prefix,project_local,sessions_local):
        task_queue = []
        
        logger.info('-------------- Open Tasks Update --------------\n')
        
        if project_local:
            if ',' in project_local:
                logger.error('too much projects ID given to the option --project : '+project_local+'. Only for one project.')
                exit(1)
            elif project_local in self.project_process_dict.keys():
                #Updating session for a specific project
                project_list=[project_local]
            else:
                logger.error('failed to run locally on project '+project_local+'.The project is not part of the settings.')
                exit(1) 
        else:
            success = self.lock_open_tasks(lockfile_prefix)   
            if not success:
                logger.warn('failed to get lock on open tasks update. Already running.')
                exit(1)                              
            #Get default project list for XNAT out of the module and process dict
            project_list = sorted(set(self.project_process_dict.keys() + self.project_modules_dict.keys()))
            #Set the date on REDCAP for update starting
            bin.upload_update_date_redcap(project_list,type_update=2,start_end=1)
            
        try:
            logger.info('Connecting to XNAT at '+self.xnat_host)
            xnat = XnatUtils.get_interface(self.xnat_host,self.xnat_user,self.xnat_pass)
            
            logger.info('Getting task list...')
            task_list = self.get_open_tasks(xnat,project_list,sessions_local)
            
            logger.info(str(len(task_list))+' open jobs found')

            logger.info('Updating tasks...')
            for cur_task in task_list:
                logger.info('     Updating task:'+cur_task.assessor_label)
                task_status = cur_task.update_status()
                if task_status == task.NEED_TO_RUN:
                    logger.debug('     adding task to run '+cur_task.assessor_label)
                    task_queue.append(cur_task)
                    
            logger.info(str(len(task_queue))+' jobs ready to be launched')
        
            #===== Sort the task queue as desired - random? breadth-first? depth-first? 
            #task_queue.sort()
                        
            # Launch jobs
            self.launch_jobs(task_queue)
            
        finally:       
            self.unlock_open_tasks(lockfile_prefix)  
            #Set the date on REDCAP for update ending
            bin.upload_update_date_redcap(project_list,type_update=2,start_end=2)
            xnat.disconnect()
            logger.info('Connection to XNAT closed')
                           
    def module_prerun(self,projectID,settings_filename=''):  
        for mod in self.project_modules_dict[projectID]:
            #save the modules to redcap project vuiis xnat job before the prerun:
            data,record_id=bin.create_record_redcap(projectID, mod.getname())
            run=bin.save_job_redcap(data,record_id)
            if not run:
                logger.info(' ->ERROR: did not send the job to redcap for <'+mod.getname()+'> : '+record_id)
                
            mod.prerun(settings_filename)
        logger.debug('\n')
            
    def module_afterrun(self,xnat,projectID):    
        for mod in self.project_modules_dict[projectID]:
            mod.afterrun(xnat,projectID)
        logger.debug('\n')
    
    def get_open_tasks(self, xnat,project_list=None,sessions_local=None):
        task_list = []
        
        if project_list:
            pass
        else:
            #Priority:
            if self.priority_project:
                project_list=self.get_project_list(self.project_process_dict.keys())
            else:
                project_list = list(self.project_process_dict.keys())
        
        # iterate projects
        for project_id in project_list:
            logger.info('===== PROJECT:'+project_id+' =====')
            task_list.extend(self.get_project_open_tasks(xnat, project_id,sessions_local))
                                        
        return task_list
    
    def get_project_open_tasks(self, xnat, project_id,sessions_local=None):
        task_list = []
        
        # Get lists of processors for this project
        sess_proc_list, scan_proc_list = processors.processors_by_type(self.project_process_dict[project_id])
            
        # Get lists of assessors for this project
        assr_list  = XnatUtils.list_project_assessors(xnat, project_id)
        
        #filter the assessors to the sessions given as parameters if given
        if sessions_local and sessions_local.lower()!='all':
            #filter the list and keep the match between both list:
            assr_list=filter(lambda x: x['session_label'] in sessions_local.split(','), assr_list)
            if not assr_list:
                logger.warn('No processes from XNAT matched the sessions given in argument: '+sessions_local+' .')
                sys.exit(1)
            
        # Match each assessor to a processor, get a task, and add to list
        for assr_info in assr_list: 
            if assr_info['procstatus'] not in task.OPEN_STATUS_LIST and assr_info['qcstatus'] not in task.OPEN_QC_LIST:
                continue
                
            task_proc = self.match_proc(xnat, assr_info, sess_proc_list, scan_proc_list)
                             
            if task_proc == None:
                logger.warn('no matching processor found:'+assr_info['assessor_label'])
                continue
              
            # Get a new task with the matched processor
            assr = XnatUtils.get_full_object(xnat, assr_info)
            cur_task = Task(task_proc,assr,RESULTS_DIR)
            task_list.append(cur_task)      
                                        
        return task_list
    
    def match_proc(self, xnat, assr_info, sess_proc_list, scan_proc_list):         
        # Look for a match in sess processors
        for sess_proc in sess_proc_list:
            if sess_proc.xsitype == assr_info['xsiType'] and sess_proc.name == assr_info['proctype']:
                return sess_proc
                    
        # Look for a match in scan processors
        for scan_proc in scan_proc_list:
            if scan_proc.xsitype == assr_info['xsiType'] and scan_proc.name == assr_info['proctype']:
                return scan_proc
                    
        return None     
    
    def update(self, lockfile_prefix,project_local,sessions_local):        
        logger.info('-------------- Update --------------\n')
        
        if project_local:
            if ',' in project_local:
                logger.error('too much projects ID given to the option --project : '+project_local+'. Only for one project.')
                exit(1)
            elif project_local in self.project_process_dict.keys():
                #Updating session for a specific project
                project_list=[project_local]
            else:
                logger.error('failed to run locally on project '+project_local+'.The project is not part of the settings.')
                exit(1) 
        else:
            success = self.lock_update(lockfile_prefix)
            if not success:
                logger.warn('failed to get lock on open tasks update. Already running.')
                exit(1)   
        
            #Get default project list for XNAT out of the module and process dict
            project_list = sorted(set(self.project_process_dict.keys() + self.project_modules_dict.keys()))
            #Set the date on REDCAP for update starting
            bin.upload_update_date_redcap(project_list,type_update=1,start_end=1) 
            
        try:
            logger.info('Connecting to XNAT at '+self.xnat_host)
            xnat = XnatUtils.get_interface(self.xnat_host,self.xnat_user,self.xnat_pass)

            #Priority if set:
            if self.priority_project and not project_local:
                project_list=self.get_project_list(list(set(self.project_process_dict.keys() + self.project_modules_dict.keys())))
            
            # Update projects
            for project_id in project_list:  
                logger.info('===== PROJECT:'+project_id+' =====')         
                self.update_project(xnat, project_id, lockfile_prefix,sessions_local)
                
        finally:
            #If normal update (not local), remove flagfile at the end and set the date
            if not project_local: 
                self.unlock_update(lockfile_prefix)  
                #Set the date on REDCAP for update ending
                bin.upload_update_date_redcap(project_list,type_update=1,start_end=2)
            xnat.disconnect()
            logger.info('Connection to XNAT closed')
   
    def update_project(self, xnat, project_id, lockfile_prefix,sessions_local):
        #Modules prerun
        logger.info('  *Modules Prerun')
        if sessions_local:
            self.module_prerun(project_id, 'manual_update')
        else:
            self.module_prerun(project_id, lockfile_prefix)
        
        # Get lists of modules/processors per scan/exp for this project
        exp_mod_list, scan_mod_list = modules.modules_by_type(self.project_modules_dict[project_id])
        exp_proc_list, scan_proc_list = processors.processors_by_type(self.project_process_dict[project_id])
        
         # Check for new processors
        has_new = self.has_new_processors(xnat, project_id, exp_proc_list, scan_proc_list)

        # Get the list of sessions:
        list_sessions=XnatUtils.list_sessions(xnat, project_id)
        if sessions_local and sessions_local.lower()!='all':
            #filter the list and keep the match between both list:
            list_sessions=filter(lambda x: x['label'] in sessions_local.split(','), list_sessions)
            if not list_sessions:
                logger.warn('No session from XNAT matched the sessions given in argument: '+sessions_local+' .')
                
        # Update each session from the list:
        for sess_info in list_sessions:
            last_mod = datetime.strptime(sess_info['last_modified'][0:19], '%Y-%m-%d %H:%M:%S')
            last_up = self.get_lastupdated(sess_info)
            
            #If sessions_local is set, skip checking the date
            if (not has_new and last_up != None and last_mod < last_up and not sessions_local):
                logger.info('  +Session:'+sess_info['label']+': skipping, last_mod='+str(last_mod)+',last_up='+str(last_up))
            else: 
                logger.info('  +Session:'+sess_info['label']+': updating...')
                # NOTE: we set update time here, so if the sess is changed below it will be checked again    
                self.set_session_lastupdated(xnat, sess_info)
                self.update_session(xnat, sess_info, exp_proc_list, scan_proc_list, exp_mod_list, scan_mod_list)
        
        if not sessions_local or sessions_local.lower()=='all':
            # Modules after run
            logger.debug('*Modules Afterrun')
            self.module_afterrun(xnat,project_id)
     
    def update_session(self, xnat, sess_info, sess_proc_list, scan_proc_list, sess_mod_list, scan_mod_list):
        
        # Scans
        logger.debug('==Update for scans in session==')
        if scan_proc_list or scan_mod_list:
            scan_list = XnatUtils.list_scans(xnat, sess_info['project'], sess_info['subject_ID'], sess_info['ID'])
            for scan_info in scan_list:
                logger.debug('+SCAN: '+scan_info['scan_id'])
                self.update_scan(xnat, scan_info, scan_proc_list, scan_mod_list)
        logger.debug('==Update for session==')
        # Modules
        for sess_mod in sess_mod_list:
            logger.debug('* Module: '+sess_mod.getname())        
            sess_obj = None
            if (sess_mod.needs_run(sess_info, xnat)):
                if sess_obj == None:
                    sess_obj = XnatUtils.get_full_object(xnat, sess_info)
                        
                sess_mod.run(sess_info, sess_obj)

        # Processors
        for sess_proc in sess_proc_list:
            if sess_proc.should_run(sess_info, xnat):
                sess_task = sess_proc.get_task(xnat, sess_info, RESULTS_DIR)
                logger.debug('* Processor:'+sess_proc.name+': updating status: '+sess_task.assessor_label)
                sess_task.update_status()
        logger.debug('\n')
        
    def update_scan(self, xnat, scan_info, scan_proc_list, scan_mod_list):

        # Modules
        scan_obj = None
        for scan_mod in scan_mod_list:
            logger.debug('* Module: '+scan_mod.getname())
            if (scan_mod.needs_run(scan_info, xnat)):
                if scan_obj == None:
                    scan_obj = XnatUtils.get_full_object(xnat, scan_info)
                        
                scan_mod.run(scan_info, scan_obj)

        # Processors   
        for scan_proc in scan_proc_list:
            if scan_proc.should_run(scan_info):
                scan_task = scan_proc.get_task(xnat, scan_info, RESULTS_DIR)
                logger.debug('* Processor: '+scan_proc.name+': updating status: '+scan_task.assessor_label)
                scan_task.update_status()
     
    def launch_jobs(self, task_list):
        # Check cluster
        cur_job_count = cluster.count_jobs()
        if cur_job_count == -1:
            logger.error('cannot get count of jobs from cluster')
            return
        
        logger.info(str(cur_job_count)+' jobs currently in queue')
        
        # Launch until we reach cluster limit or no jobs left to launch
        while cur_job_count < self.queue_limit and len(task_list)>0:
            cur_task = task_list.pop()
            
            # Confirm task is still ready to run
            if cur_task.get_status() != task.NEED_TO_RUN:
                continue
            
            logger.info('  +Launching job:'+cur_task.assessor_label+', currently '+str(cur_job_count)+' jobs in cluster queue')
            success = cur_task.launch(self.root_job_dir,self.job_email,self.job_email_options)
            if(success != True):
                logger.error('ERROR:failed to launch job')

            cur_job_count = cluster.count_jobs()
            if cur_job_count == -1:
                logger.error('ERROR:cannot get count of jobs from cluster')
                return
                
    def lock_open_tasks(self, lockfile_prefix):
        lock_file = os.path.join(RESULTS_DIR,'FlagFiles',lockfile_prefix+'_'+OPEN_TASKS_LOCK_FILE)
        
        if os.path.exists(lock_file):
            return False
        else:
            open(lock_file, 'w').close()
            return True
        
    def lock_update(self,lockfile_prefix):
        lock_file = os.path.join(RESULTS_DIR,'FlagFiles',lockfile_prefix+'_'+UPDATE_LOCK_FILE)
        
        if os.path.exists(lock_file):
            return False
        else:
            open(lock_file, 'w').close()
            return True
                
    def unlock_open_tasks(self,lockfile_prefix):
        lock_file = os.path.join(RESULTS_DIR,'FlagFiles',lockfile_prefix+'_'+OPEN_TASKS_LOCK_FILE)
        
        if os.path.exists(lock_file):
            os.remove(lock_file)
               
    def unlock_update(self,lockfile_prefix):
        lock_file = os.path.join(RESULTS_DIR,'FlagFiles',lockfile_prefix+'_'+UPDATE_LOCK_FILE)
        
        if os.path.exists(lock_file):
            os.remove(lock_file)
        
    def get_lastupdated(self, info):
        update_time = info['last_updated'][len(UPDATE_PREFIX):]
        if update_time == '':
            return None
        else:
            return datetime.strptime(update_time, UPDATE_FORMAT)

    def set_session_lastupdated(self, xnat, sess_info):
        # We set update to one minute into the future since setting update field will change last modified time
        now = (datetime.now() + timedelta(minutes=1)).strftime(UPDATE_FORMAT)
        logger.debug('setting last_updated for:'+sess_info['label']+' to '+now)
        sess_obj = XnatUtils.get_full_object(xnat, sess_info)
        xsi_type = sess_info['xsiType']
        sess_obj.attrs.set(xsi_type+'/original', UPDATE_PREFIX+now)      
     
    # TODO: remove this after we are all projects have been updated to use the session field for last_updated               
    def lastupdated_subj2sess(self): 
        logger.debug('check for up to date subjects, apply timestamp to session last_updated')
        
        try:
            logger.info('Connecting to XNAT at '+self.xnat_host)
            xnat = XnatUtils.get_interface(self.xnat_host,self.xnat_user,self.xnat_pass)
            project_list = sorted(set(self.project_process_dict.keys() + self.project_modules_dict.keys()))
  
            # Update projects
            for project_id in project_list:
                logger.info('===== PROJECT:'+project_id+' =====')
                for subj_info in XnatUtils.list_subjects(xnat, project_id):
                    last_mod = datetime.strptime(subj_info['last_modified'][0:19], '%Y-%m-%d %H:%M:%S')
                    last_up = self.get_lastupdated(subj_info)
                    if (last_up != None and last_mod < last_up):
                        logger.info('  +Subject:'+subj_info['label']+', subject up to date:last_mod='+str(last_mod)+',last_up='+str(last_up))
                        for sess_info in XnatUtils.list_sessions(xnat, subj_info['project'], subj_info['ID']):
                            if sess_info['last_updated'] == '':
                                logger.info('  +Session:'+sess_info['label']+': subject up to date, setting update time to now')
                                self.set_session_lastupdated(xnat, sess_info)
                    else:
                        logger.info('  +Subject:'+subj_info['label']+', skipping:last_mod='+str(last_mod)+',last_up='+str(last_up))     
                                           
        finally:  
            xnat.disconnect()
            logger.info('Connection to XNAT closed')

    def has_new_processors(self, xnat, project_id, exp_proc_list, scan_proc_list):
        # Get unique list of assessors already in XNAT
        assr_list  = XnatUtils.list_project_assessors(xnat, project_id)
        assr_type_set = set([x['proctype'] for x in assr_list])
        
        # Get unique list of processors prescribed for project
        proc_name_set = set([x.name for x in (exp_proc_list+scan_proc_list)])
        
        # Get list of processors that don't have assessors in XNAT yet
        diff_list = list(proc_name_set.difference(assr_type_set))
        
        # Are there any?
        return (len(diff_list) > 0)
