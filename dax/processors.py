import os,re

import task
import XnatUtils

class Processor(object):
    def __init__(self,walltime_str,memreq_mb,spider_path,version=None,ppn=1,xsitype='proc:genProcData'):
        self.walltime_str=walltime_str # 00:00:00 format
        self.memreq_mb=memreq_mb  # memory required in megabytes      
        self.set_spider_settings(spider_path,version)
        self.ppn = ppn
        self.xsitype = xsitype

    #get the spider_path right with the version:
    def set_spider_settings(self,spider_path,version):
        if version:
            #get the proc_name
            proc_name=os.path.basename(spider_path)[7:-3]
            #remove any version if there is one
            proc_name=re.split("/*_v[0-9]/*", proc_name)[0]
            #setting the version and name of the spider
            self.version = version
            self.name = proc_name+'_v'+self.version.split('.')[0]
            self.spider_path = os.path.join(os.path.dirname(spider_path),'Spider_'+proc_name+'_v'+version+'.py')
        else:
            self.default_settings_spider(spider_path)
    
    def default_settings_spider(self,spider_path):
        #set spider path
        self.spider_path = spider_path
        #set the name and the version of the spider
        if len(re.split("/*_v[0-9]/*", spider_path))>1:
            self.version = os.path.basename(spider_path)[7:-3].split('_v')[-1]
            self.name = re.split("/*_v[0-9]/*", os.path.basename(spider_path)[7:-3])[0] +'_v'+ self.version.split('.')[0]
        else:
            self.version = '1.0.0'
            self.name = os.path.basename(spider_path)[7:-3]

    # has_inputs - does this object have the required inputs? e.g. NIFTI format of the required scan type and quality and are there no conflicting inputs, i.e. only 1 required by 2 found?
    def has_inputs(self): # what other arguments here, could be Project/Subject/Session/Scan/Assessor depending on type of processor?
        raise NotImplementedError()
     
    # should_run - is the object of the proper object type? e.g. is it a scan? and is it the required scan type? e.g. is it a T1?
    def should_run(self): # what other arguments here, could be Project/Subject/Session/Scan/Assessor depending on type of processor?
        raise NotImplementedError()
        
    def write_pbs(self,filename):
        raise NotImplementedError()

class ScanProcessor(Processor):
    def has_inputs(self):
        raise NotImplementedError()
     
    def should_run(self): 
        raise NotImplementedError()
    
    def __init__(self,scan_types,walltime_str,memreq_mb,spider_path,version=None, ppn=1):
        super(ScanProcessor, self).__init__(walltime_str, memreq_mb,spider_path,version,ppn)
        self.scan_types=scan_types
         
    def get_assessor_name(self,scan_dict):
        subj_label = scan_dict['subject_label']
        sess_label = scan_dict['session_label']
        proj_label = scan_dict['project_label']
        scan_label = scan_dict['scan_label']
        return (proj_label+'-x-'+subj_label+'-x-'+sess_label+'-x-'+scan_label+'-x-'+self.name)
        
    def get_task(self, intf, scan_dict, upload_dir):
        scan = XnatUtils.get_full_object(intf,scan_dict)
        assessor_name = self.get_assessor_name(scan_dict)
        assessor = scan.parent().assessor(assessor_name)
        return task.Task(self,assessor,upload_dir)
        
class SessionProcessor(Processor):
    def has_inputs(self):
        raise NotImplementedError()
     
    def should_run(self): 
        raise NotImplementedError()
    
    def __init__(self,walltime_str,memreq_mb,spider_path,version=None,ppn=1):
        super(SessionProcessor, self).__init__(walltime_str,memreq_mb,spider_path,version,ppn)
        
    def get_assessor_name(self,session_dict):  
        proj_label = session_dict['project']
        subj_label = session_dict['subject_label']
        sess_label = session_dict['label']  
        return (proj_label+'-x-'+subj_label+'-x-'+sess_label+'-x-'+self.name)
    
    def get_task(self, intf, session_dict, upload_dir):
        session = XnatUtils.get_full_object(intf,session_dict)
        assessor_name = self.get_assessor_name(session_dict)
        assessor = session.assessor(assessor_name)
        return task.Task(self,assessor,upload_dir)
    
def processors_by_type(proc_list):
    exp_proc_list = []
    scan_proc_list = []
            
    # Build list of processors by type
    for proc in proc_list:
        if issubclass(proc.__class__,ScanProcessor):
            scan_proc_list.append(proc)
        elif issubclass(proc.__class__,SessionProcessor):
            exp_proc_list.append(proc)
        else:
            print('ERROR:unknown processor type:'+proc)

    return exp_proc_list, scan_proc_list
