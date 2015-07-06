""" Processor class define for Scan and Session """
import os
import re
import task
import logging
import XnatUtils

#Logger for logs
LOGGER = logging.getLogger('dax')

class Processor(object):
    """ Base class for processor """
    def __init__(self, walltime_str, memreq_mb, spider_path,
                 version=None, ppn=1, suffix_proc='',
                 xsitype='proc:genProcData'):
        """ init function """
        self.walltime_str = walltime_str # 00:00:00 format
        self.memreq_mb = memreq_mb  # memory required in megabytes
        #default values:
        self.version = "1.0.0"
        if not suffix_proc:
             self.suffix_proc=''
        else:
            if suffix_proc and suffix_proc[0] != '_':
                self.suffix_proc = '_'+suffix_proc
            else:
                self.suffix_proc = suffix_proc

        self.suffix_proc = self.suffix_proc.strip().replace(" ","")\
                               .replace('/','_').replace('*','_')\
                               .replace('.','_').replace(',','_')\
                               .replace('?','_').replace('!','_')\
                               .replace(';','_').replace(':','_')
        self.name = None
        self.spider_path = spider_path
        self.ppn = ppn
        self.xsitype = xsitype
        #getting name and version from spider_path
        self.set_spider_settings(spider_path, version)
        #if suffix_proc is empty, set it to "" for the spider call:
        if not suffix_proc:
            self.suffix_proc = ''

    #get the spider_path right with the version:
    def set_spider_settings(self, spider_path, version):
        """ function to set the spider version/path/name from the filepath """
        if version:
            #get the proc_name
            proc_name = os.path.basename(spider_path)[7:-3]
            #remove any version if there is one
            proc_name = re.split("/*_v[0-9]/*", proc_name)[0]
            #setting the version and name of the spider
            self.version = version
            self.name = '''{procname}_v{version}{suffix}'''.format(procname=proc_name,
                                                                   version=self.version.split('.')[0],
                                                                   suffix=self.suffix_proc)
            spider_name = '''Spider_{procname}_v{version}.py'''.format(procname=proc_name,
                                                                      version=version.replace('.', '_'))
            self.spider_path = os.path.join(os.path.dirname(spider_path), spider_name)
        else:
            self.default_settings_spider(spider_path)

    def default_settings_spider(self, spider_path):
        """ default function to get the spider version/name """
        #set spider path
        self.spider_path = spider_path
        #set the name and the version of the spider
        if len(re.split("/*_v[0-9]/*", spider_path)) > 1:
            self.version = os.path.basename(spider_path)[7:-3].split('_v')[-1].replace('_','.')
            spidername = os.path.basename(spider_path)[7:-3]
            self.name = '''{procname}_v{version}{suffix}'''.format(procname=re.split("/*_v[0-9]/*", spidername)[0],
                                                                   version=self.version.split('.')[0],
                                                                   suffix=self.suffix_proc)
        else:
            self.name = os.path.basename(spider_path)[7:-3]+self.suffix_proc

    # has_inputs - does this object have the required inputs?
    # e.g. NIFTI format of the required scan type and quality and are there no conflicting inputs.
    # i.e. only 1 required by 2 found?
    # other arguments here, could be Proj/Subj/Sess/Scan/Assessor depending on processor type?
    def has_inputs(self):
        """ has_inputs function to check if inputs present on XNAT to run the job """
        raise NotImplementedError()

    # should_run - is the object of the proper object type?
    # e.g. is it a scan? and is it the required scan type?
    # e.g. is it a T1?
    # other arguments here, could be Proj/Subj/Sess/Scan/Assessor depending on processor type?
    def should_run(self):
        """ return True if the assessor should exist/ False if not """
        raise NotImplementedError()

class ScanProcessor(Processor):
    """ Scan Processor class for processor on a scan on XNAT """
    def has_inputs(self):
        """ return status, qcstatus
            status = 0 if still NEED_INPUTS, -1 if NO_DATA, 1 if NEED_TO_RUN
            qcstatus = only when -1 or 0.
            You can set it to a short string that explain why it's no ready to run.
                e.g: No NIFTI
        """
        raise NotImplementedError()

    def __init__(self, scan_types, walltime_str, memreq_mb, spider_path, version=None, ppn=1, suffix_proc=''):
        """ init function overridden from base class """
        super(ScanProcessor, self).__init__(walltime_str, memreq_mb, spider_path, version, ppn, suffix_proc)
        if isinstance(scan_types, list):
            self.scan_types = scan_types
        elif isinstance(scan_types, str):
            if scan_types == 'all':
                self.scan_types = 'all'
            else:
                self.scan_types = scan_types.split(',')
        else:
            self.scan_types = []

    def get_assessor_name(self, cscan):
        """ return the assessor label """
        scan_dict = cscan.info()
        subj_label = scan_dict['subject_label']
        sess_label = scan_dict['session_label']
        proj_label = scan_dict['project_label']
        scan_label = scan_dict['scan_label']
        return proj_label+'-x-'+subj_label+'-x-'+sess_label+'-x-'+scan_label+'-x-'+self.name

    def get_task(self, intf, cscan, upload_dir):
        """ return the task object for this assessor """
        scan_dict = cscan.info()
        assessor_name = self.get_assessor_name(cscan)
        scan = XnatUtils.get_full_object(intf, scan_dict)
        assessor = scan.parent().assessor(assessor_name)
        return task.Task(self, assessor, upload_dir)

    def should_run(self, scan_dict):
        """ should_run function overwrited from base-class to check if it's a right scan"""
        if self.scan_types == 'all':
            return True
        else:
            return scan_dict['scan_type'] in self.scan_types

class SessionProcessor(Processor):
    """ Session Processor class for processor on a session on XNAT """
    def has_inputs(self):
        """ return status, qcstatus
            status = 0 if still NEED_INPUTS, -1 if NO_DATA, 1 if NEED_TO_RUN
            qcstatus = only when -1 or 0.
            You can set it to a short string that explain why it's no ready to run.
                e.g: No NIFTI
        """
        raise NotImplementedError()

    def __init__(self, walltime_str, memreq_mb, spider_path, version=None, ppn=1, suffix_proc=''):
        """ init function overridden from base class """
        super(SessionProcessor, self).__init__(walltime_str, memreq_mb, spider_path, version, ppn, suffix_proc)

    def should_run(self, session_dict):
        """ return if the assessor should exist. Always true on a session """
        return True

    def get_assessor_name(self, csess):
        """ return the assessor label """
        session_dict = csess.info()
        proj_label = session_dict['project']
        subj_label = session_dict['subject_label']
        sess_label = session_dict['label']
        return proj_label+'-x-'+subj_label+'-x-'+sess_label+'-x-'+self.name

    def get_task(self, intf, csess, upload_dir):
        """ return the task for this process """
        sess_info = csess.info()
        assessor_name = self.get_assessor_name(csess)
        session = XnatUtils.get_full_object(intf, sess_info)
        assessor = session.assessor(assessor_name)
        return task.Task(self, assessor, upload_dir)

def processors_by_type(proc_list):
    """ function to organize the assessor by type
        return two lists: one for scan, one for session
    """
    exp_proc_list = list()
    scan_proc_list = list()

    # Build list of processors by type
    for proc in proc_list:
        if issubclass(proc.__class__, ScanProcessor):
            scan_proc_list.append(proc)
        elif issubclass(proc.__class__, SessionProcessor):
            exp_proc_list.append(proc)
        else:
            LOGGER.warn('unknown processor type:'+proc)

    return exp_proc_list, scan_proc_list
