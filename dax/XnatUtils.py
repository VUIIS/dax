import socket
import os
import sys
import shutil
import re
from datetime import datetime

from pyxnat import Interface
from lxml import etree

import redcap

from dax_settings import RESULTS_DIR

####################################################################################
#            Class JobHandler to copy file after the end of a Job                  #
####################################################################################   
class SpiderProcessHandler:
    def __init__(self,script_name,project,subject,experiment,scan=''):
        if len(script_name.split('/'))>1:
            script_name=os.path.basename(script_name)
        if script_name.endswith('.py'):
            script_name=script_name[:-3]
        if 'Spider' in script_name:
            script_name=script_name[7:]
            
        #ge the processname from spider
        if len(re.split("/*_v[0-9]/*", script_name))>1:
            self.version = script_name.split('_v')[-1]
            self.ProcessName=re.split("/*_v[0-9]/*", script_name)[0]+'_v'+self.version.split('.')[0]
        else:
            self.version = '1.0.0'
            self.ProcessName=script_name
        
        #make the assessor folder for upload
        if scan=='':
            self.assessor_label=project+'-x-'+subject+'-x-'+experiment+'-x-'+self.ProcessName
            self.dir=os.path.join(RESULTS_DIR,self.assessor_label)
        else:
            self.assessor_label=project+'-x-'+subject+'-x-'+experiment+'-x-'+scan+'-x-'+self.ProcessName
            self.dir=os.path.join(RESULTS_DIR,self.assessor_label)
        #if the folder already exists : remove it
        if not os.path.exists(self.dir):
            os.mkdir(self.dir)
        else:
            #Remove files in directories
            clean_directory(self.dir)

        print'INFO: Handling results ...'
        print'  -Creating folder '+self.dir+' for '+self.assessor_label
        self.project=project
        self.subject=subject
        self.experiment=experiment
        self.scan=scan
        self.finish=0
        self.error=0

    def set_error(self):
        self.error=1

    def add_pdf(self,filepath):
        #check if the file exists:
        if not os.path.exists(filepath.strip()):
            self.error=1
            print 'ERROR: file '+filepath+' does not exists.'
        else:
            #Check if it's a ps:
            if os.path.splitext(filepath)[1].lower()=='.ps':
                ps=os.path.basename(filepath)
                pdf_path=os.path.splitext(filepath)[0]+'.pdf'
                print '  -Converting '+ps+' file into a PDF '+pdf_path+' ...'
                #convertion in pdf
                os.system('ps2pdf '+filepath+' '+pdf_path)
            else:
                pdf_path=filepath
    
            #make the resource folder
            if not os.path.exists(self.dir+'/PDF'):
                os.mkdir(self.dir+'/PDF')
    
            #mv the pdf
            print'  -Copying PDF: '+pdf_path+' to '+self.dir
            os.system('cp '+pdf_path+' '+self.dir+'/PDF/')
            self.finish=1

    def add_snapshot(self,snapshot):
        #check if the file exists:
        if not os.path.exists(snapshot.strip()):
            self.error=1
            print 'ERROR: file '+snapshot+' does not exists.'
        else:
            #make the resource folder
            if not os.path.exists(self.dir+'/SNAPSHOTS'):
                os.mkdir(self.dir+'/SNAPSHOTS')
            #mv the snapshot
            print'  -Copying SNAPSHOTS: '+snapshot+' to '+self.dir
            os.system('cp '+snapshot+' '+self.dir+'/SNAPSHOTS/')

    def add_file(self,filePath,Resource):
        #check if the file exists:
        if not os.path.exists(filePath.strip()):
            self.error=1
            print 'ERROR: file '+filePath+' does not exists.'
        else:
            #make the resource folder
            if not os.path.exists(self.dir+'/'+Resource):
                os.mkdir(self.dir+'/'+Resource)
            #mv the file
            print'  -Copying '+Resource+': '+filePath+' to '+self.dir
            os.system('cp '+filePath+' '+self.dir+'/'+Resource+'/')
            #if it's a nii or a rec file, gzip it:
            if filePath.lower().endswith('.nii') or filePath.lower().endswith('.rec'):
                os.system('gzip '+os.path.join(self.dir,Resource,os.path.basename(filePath)))

    def add_folder(self,FolderPath,ResourceName=None):
        #check if the folder exists:
        if not os.path.exists(FolderPath.strip()):
            self.error=1
            print 'ERROR: folder '+FolderPath+' does not exists.'
        else:
            if ResourceName != None:
                #make the resource folder
                if not os.path.exists(self.dir+'/'+ResourceName):
                    os.mkdir(self.dir+'/'+ResourceName)
                #Get the initial directory:
                initDir=os.getcwd()
                #get the directory :
                Path,lastDir=os.path.split(FolderPath)
                if lastDir=='':
                    Path,lastDir=os.path.split(FolderPath[:-1])
                #mv the folder
                os.chdir(Path)
                os.system('zip -r '+ResourceName+'.zip '+lastDir)
                os.system('mv '+ResourceName+'.zip '+self.dir+'/'+ResourceName+'/')
                #return to the initial directory:
                os.chdir(initDir)
                print'  -Copying '+ResourceName+' after zipping the folder contents: '+FolderPath+' to '+self.dir
            else:
                #mv the folder
                print'  -Moving '+FolderPath+' to '+self.dir
                os.system('mv '+FolderPath+' '+self.dir)

    def setAssessorStatus(self, status):
        # Connection to Xnat
        try:
            xnat = get_interface()

            assessor=xnat.select('/project/'+self.project+'/subjects/'+self.subject+'/experiments/'+self.experiment+'/assessors/'+self.assessor_label)
            if assessor.exists():
                if 'FS' or 'FreeSurfer' in self.assessor_label.split('-x-')['-1']:
                    assessor.attrs.set('fs:fsdata/procstatus',status)
                else:
                    assessor.attrs.set('proc:genProcData/procstatus',status)
        finally:
            xnat.disconnect()

    def done(self):
        #creating the version file to give the spider version:
        f=open(os.path.join(self.dir,'version.txt'),'w')
        f.write(self.version)
        f.close()
        #Finish the folder
        if self.finish and not self.error:
            print'INFO: Job ready to be upload, error: '+ str(self.error)
            #make the flag folder
            open(os.path.join(self.dir,'READY_TO_UPLOAD.txt'), 'w').close()
            #set status to ReadyToUpload
            self.setAssessorStatus('READY_TO_UPLOAD')
        else:
            print'INFO: Job failed, check the outlogs, error: '+ str(self.error)
            #make the flag folder
            open(os.path.join(self.dir,'JOB_FAILED.txt'), 'w').close()
            #set status to JOB_FAILED
            self.setAssessorStatus('JOB_FAILED')

    def clean(self,directory):
        if self.finish and not self.error:
            #Remove the data
            shutil.rmtree(directory)
            
####################################################################################
#                       Access XNAT and list of XNAT Objs                          #
####################################################################################    
def get_interface():
    # Environs
    user = os.environ['XNAT_USER']
    pwd = os.environ['XNAT_PASS']
    host = os.environ['XNAT_HOST']
    # Don't sys.exit, let callers catch KeyErrors
    return Interface(host, user, pwd)

def list_subjects(intf, projectid=None):
    if projectid:
        post_uri = '/REST/projects/'+projectid+'/subjects'
    else:
        post_uri = '/REST/subjects'

    post_uri += '?columns=ID,project,label,URI,last_modified,src'

    subject_list = intf._get_json(post_uri)

    for s in subject_list:
        if (projectid != None):
            # Override the project returned to be the one we queried
            s['project'] = projectid

        s['project_id'] = s['project']
        s['project_label'] = s['project']
        s['last_updated'] = s['src']

    return subject_list

def list_experiments(intf, projectid=None, subjectid=None):
    if projectid and subjectid:
        post_uri = '/REST/projects/'+projectid+'/subjects/'+subjectid+'/experiments'
    elif projectid == None and subjectid == None:
        post_uri = '/REST/experiments'
    elif projectid and subjectid == None:
        post_uri = '/REST/projects/'+projectid+'/experiments'
    else:
        return None

    post_uri += '?columns=ID,URI,subject_label,subject_ID,modality,project,date,xsiType,label,xnat:subjectdata/meta/last_modified'
    experiment_list = intf._get_json(post_uri)

    for e in experiment_list:
        if (projectid != None):
            # Override the project returned to be the one we queried and add others for convenience
            e['project'] = projectid
            
        e['subject_id'] = e['subject_ID'] 
        e['session_id'] = e['ID']
        e['session_label'] = e['label']
        e['project_id'] = e['project']
        e['project_label'] = e['project']

    return sorted(experiment_list, key=lambda k: k['session_label'])

def list_sessions(intf, projectid=None, subjectid=None):
    type_list = []
    full_sess_list = []
    
    if projectid and subjectid:
        post_uri = '/REST/projects/'+projectid+'/subjects/'+subjectid+'/experiments'
    elif projectid == None and subjectid == None:
        post_uri = '/REST/experiments'
    elif projectid and subjectid == None:
        post_uri = '/REST/projects/'+projectid+'/experiments'
    else:
        return None
    
    # First get a list of all experiment types
    post_uri_types = post_uri+'?columns=xsiType'
    sess_list = intf._get_json(post_uri)
    for sess in sess_list:
        sess_type = sess['xsiType'].lower()
        if sess_type not in type_list:
            type_list.append(sess_type)
    
    # Get list of sessions for each type since we have to specific about last_modified field
    for sess_type in type_list:
        post_uri_type = post_uri + '?xsiType='+sess_type+'&columns=ID,URI,subject_label,subject_ID,modality,project,date,xsiType,label,'+sess_type+'/meta/last_modified,'+sess_type+'/original'
        sess_list = intf._get_json(post_uri_type)
        
        for sess in sess_list:
            # Override the project returned to be the one we queried
            if (projectid != None):
                sess['project'] = projectid
            
            sess['project_id'] = sess['project']
            sess['project_label'] = sess['project']
            sess['subject_id'] = sess['subject_ID'] 
            sess['session_id'] = sess['ID']
            sess['session_label'] = sess['label']
            sess['last_modified'] = sess[sess_type+'/meta/last_modified']
            sess['last_updated'] = sess[sess_type+'/original']
        
        # Add sessions of this type to full list    
        full_sess_list.extend(sess_list)
    
    # Return list sorted by label
    return sorted(full_sess_list, key=lambda k: k['session_label'])

def list_scans(intf, projectid, subjectid, experimentid):
    post_uri = '/REST/projects/'+projectid+'/subjects/'+subjectid+'/experiments'
    post_uri += '?columns=ID,URI,label,subject_label,project'
    post_uri += ',xnat:imagesessiondata/scans/scan/id'
    post_uri += ',xnat:imagesessiondata/scans/scan/type'
    post_uri += ',xnat:imagesessiondata/scans/scan/quality'
    post_uri += ',xnat:imagesessiondata/scans/scan/note'
    post_uri += ',xnat:imagesessiondata/scans/scan/frames'
    post_uri += ',xnat:imagesessiondata/scans/scan/series_description'
    post_uri += ',xnat:imagesessiondata/subject_id'
    scan_list = intf._get_json(post_uri)
    new_list = []

    for s in scan_list:
        if s['ID'] == experimentid or s['label'] == experimentid:
            snew = {}
            snew['scan_id'] = s['xnat:imagesessiondata/scans/scan/id']
            snew['scan_label'] = s['xnat:imagesessiondata/scans/scan/id']
            snew['scan_quality'] = s['xnat:imagesessiondata/scans/scan/quality']
            snew['scan_note'] = s['xnat:imagesessiondata/scans/scan/note']
            snew['scan_frames'] = s['xnat:imagesessiondata/scans/scan/frames']
            snew['scan_description'] = s['xnat:imagesessiondata/scans/scan/series_description']
            snew['scan_type'] = s['xnat:imagesessiondata/scans/scan/type']
            snew['ID'] = s['xnat:imagesessiondata/scans/scan/id']
            snew['label'] = s['xnat:imagesessiondata/scans/scan/id']
            snew['quality'] = s['xnat:imagesessiondata/scans/scan/quality']
            snew['note'] = s['xnat:imagesessiondata/scans/scan/note']
            snew['frames'] = s['xnat:imagesessiondata/scans/scan/frames']
            snew['series_description'] = s['xnat:imagesessiondata/scans/scan/series_description']
            snew['type'] = s['xnat:imagesessiondata/scans/scan/type']
            snew['project_id'] = projectid
            snew['project_label'] = projectid
            snew['subject_id'] = s['xnat:imagesessiondata/subject_id']
            snew['subject_label'] = s['subject_label']
            snew['session_id'] = s['ID']
            snew['session_label'] = s['label']
            snew['session_uri'] = s['URI']
            new_list.append(snew)

    return sorted(new_list, key=lambda k: k['label'])
    
def list_project_scans(intf, projectid, include_shared=True):
    new_list = []

    post_uri = '/REST/archive/experiments'
    post_uri += '?project='+projectid
    post_uri += '&xsiType=xnat:imageSessionData'
    post_uri += '&columns=ID,URI,label,subject_label,project'
    post_uri += ',xnat:imagesessiondata/subject_id'
    post_uri += ',xnat:imagescandata/id'
    post_uri += ',xnat:imagescandata/type'
    post_uri += ',xnat:imagescandata/quality'
    post_uri += ',xnat:imagescandata/note'
    post_uri += ',xnat:imagescandata/frames'
    post_uri += ',xnat:imagescandata/series_description'
    scan_list = intf._get_json(post_uri)

    for s in scan_list:
        snew = {}
        snew['scan_id']      = s['xnat:imagescandata/id']
        snew['scan_label']   = s['xnat:imagescandata/id']
        snew['scan_quality'] = s['xnat:imagescandata/quality']
        snew['scan_note']    = s['xnat:imagescandata/note']
        snew['scan_frames']  = s['xnat:imagescandata/frames']
        snew['scan_description'] = s['xnat:imagescandata/series_description']
        snew['scan_type']    = s['xnat:imagescandata/type']
        snew['ID']           = s['xnat:imagescandata/id']
        snew['label']        = s['xnat:imagescandata/id']
        snew['quality']      = s['xnat:imagescandata/quality']
        snew['note']         = s['xnat:imagescandata/note']
        snew['frames']       = s['xnat:imagescandata/frames']
        snew['series_description'] = s['xnat:imagescandata/series_description']
        snew['type']         = s['xnat:imagescandata/type']
        snew['project_id'] = projectid
        snew['project_label'] = projectid
        snew['subject_id'] = s['xnat:imagesessiondata/subject_id']
        snew['subject_label'] = s['subject_label']
        snew['session_id'] = s['ID']
        snew['session_label'] = s['label']
        snew['session_uri'] = s['URI']
        new_list.append(snew)
        
    if (include_shared):
        post_uri = '/REST/archive/experiments'
        post_uri += '?xnat:imagesessiondata/sharing/share/project='+projectid
        post_uri += '&xsiType=xnat:imageSessionData'
        post_uri += '&columns=ID,URI,label,subject_label,project'
        post_uri += ',xnat:imagesessiondata/subject_id'
        post_uri += ',xnat:imagescandata/id'
        post_uri += ',xnat:imagescandata/type'
        post_uri += ',xnat:imagescandata/quality'
        post_uri += ',xnat:imagescandata/note'
        post_uri += ',xnat:imagescandata/frames'
        post_uri += ',xnat:imagescandata/series_description'
        scan_list = intf._get_json(post_uri)
    
        for s in scan_list:
            snew = {}
            snew['scan_id']      = s['xnat:imagescandata/id']
            snew['scan_label']   = s['xnat:imagescandata/id']
            snew['scan_quality'] = s['xnat:imagescandata/quality']
            snew['scan_note']    = s['xnat:imagescandata/note']
            snew['scan_frames']  = s['xnat:imagescandata/frames']
            snew['scan_description'] = s['xnat:imagescandata/series_description']
            snew['scan_type']    = s['xnat:imagescandata/type']
            snew['ID']           = s['xnat:imagescandata/id']
            snew['label']        = s['xnat:imagescandata/id']
            snew['quality']      = s['xnat:imagescandata/quality']
            snew['note']         = s['xnat:imagescandata/note']
            snew['frames']       = s['xnat:imagescandata/frames']
            snew['series_description'] = s['xnat:imagescandata/series_description']
            snew['type']         = s['xnat:imagescandata/type']
            snew['project_id'] = projectid
            snew['project_label'] = projectid
            snew['subject_id'] = s['xnat:imagesessiondata/subject_id']
            snew['subject_label'] = s['subject_label']
            snew['session_id'] = s['ID']
            snew['session_label'] = s['label']
            snew['session_uri'] = s['URI']
            new_list.append(snew)
            
    return sorted(new_list, key=lambda k: k['scan_label'])

def list_scan_resources(intf, projectid, subjectid, experimentid, scanid):
    post_uri = '/REST/projects/'+projectid+'/subjects/'+subjectid+'/experiments/'+experimentid+'/scans/'+scanid+'/resources'
    resource_list = intf._get_json(post_uri)
    return resource_list
    
def list_experiment_resources(intf, projectid, subjectid, experimentid):
    post_uri = '/REST/projects/'+projectid+'/subjects/'+subjectid+'/experiments/'+experimentid+'/resources'
    resource_list = intf._get_json(post_uri)
    return resource_list

def list_assessors(intf, projectid, subjectid, experimentid):
    new_list = []

    # First get FreeSurfer
    post_uri = '/REST/projects/'+projectid+'/subjects/'+subjectid+'/experiments/'+experimentid+'/assessors'
    post_uri += '?columns=ID,label,URI,xsiType,project,xnat:imagesessiondata/subject_id,xnat:imagesessiondata/id,xnat:imagesessiondata/label,URI,fs:fsData/procstatus,fs:fsData/validation/status&xsiType=fs:fsData'
    assessor_list = intf._get_json(post_uri)

    for a in assessor_list:
        anew = {}
        anew['ID'] = a['ID']
        anew['label'] = a['label']
        anew['uri'] = a['URI']
        anew['assessor_id'] = a['ID']
        anew['assessor_label'] = a['label']
        anew['assessor_uri'] = a['URI']
        anew['project_id'] = projectid
        anew['project_label'] = projectid
        anew['subject_id'] = a['xnat:imagesessiondata/subject_id']
        anew['session_id'] = a['session_ID']
        anew['session_label'] = a['session_label']
        anew['procstatus'] = a['fs:fsdata/procstatus']
        anew['qcstatus'] = a['fs:fsdata/validation/status']
        anew['proctype'] = 'FreeSurfer'
        anew['xsiType'] = a['xsiType']
        new_list.append(anew)

    # Then add genProcData
    post_uri = '/REST/projects/'+projectid+'/subjects/'+subjectid+'/experiments/'+experimentid+'/assessors'
    post_uri += '?columns=ID,label,URI,xsiType,project,xnat:imagesessiondata/subject_id,xnat:imagesessiondata/id,xnat:imagesessiondata/label,proc:genprocdata/procstatus,proc:genprocdata/proctype,proc:genprocdata/validation/status&xsiType=proc:genprocdata'
    assessor_list = intf._get_json(post_uri)

    for a in assessor_list:
        anew = {}
        anew['ID'] = a['ID']
        anew['label'] = a['label']
        anew['uri'] = a['URI']
        anew['assessor_id'] = a['ID']
        anew['assessor_label'] = a['label']
        anew['assessor_uri'] = a['URI']
        anew['project_id'] = projectid
        anew['project_label'] = projectid
        anew['subject_id'] = a['xnat:imagesessiondata/subject_id']
        anew['session_id'] = a['session_ID']
        anew['session_label'] = a['session_label']
        anew['procstatus'] = a['proc:genprocdata/procstatus']
        anew['proctype'] = a['proc:genprocdata/proctype']
        anew['qcstatus'] = a['proc:genprocdata/validation/status']
        anew['xsiType'] = a['xsiType']
        new_list.append(anew)

    return sorted(new_list, key=lambda k: k['label'])

def list_project_assessors(intf, projectid):
    new_list = []
        
    # First get FreeSurfer
    post_uri = '/REST/archive/experiments'
    post_uri += '?project='+projectid
    post_uri += '&xsiType=fs:fsdata'
    post_uri += '&columns=ID,label,URI,xsiType,project'
    post_uri += ',xnat:imagesessiondata/subject_id,xnat:imagesessiondata/id'
    post_uri += ',xnat:imagesessiondata/label,URI,fs:fsData/procstatus'
    post_uri += ',fs:fsData/validation/status'
    assessor_list = intf._get_json(post_uri)

    for a in assessor_list:
        anew = {}
        anew['ID'] = a['ID']
        anew['label'] = a['label']
        anew['uri'] = a['URI']
        anew['assessor_id'] = a['ID']
        anew['assessor_label'] = a['label']
        anew['assessor_uri'] = a['URI']
        anew['project_id'] = projectid
        anew['project_label'] = projectid
        anew['subject_id'] = a['xnat:imagesessiondata/subject_id']
        anew['session_id'] = a['session_ID']
        anew['session_label'] = a['session_label']
        anew['procstatus'] = a['fs:fsdata/procstatus']
        anew['qcstatus'] = a['fs:fsdata/validation/status']
        anew['proctype'] = 'FreeSurfer'
        anew['xsiType'] = a['xsiType']
        new_list.append(anew)

    # Then add genProcData    
    post_uri = '/REST/archive/experiments'
    post_uri += '?project='+projectid
    post_uri += '&xsiType=proc:genprocdata'
    post_uri += '&columns=ID,label,URI,xsiType,project'
    post_uri += ',xnat:imagesessiondata/subject_id,xnat:imagesessiondata/id'
    post_uri += ',xnat:imagesessiondata/label,proc:genprocdata/procstatus'
    post_uri += ',proc:genprocdata/proctype,proc:genprocdata/validation/status'
    assessor_list = intf._get_json(post_uri)

    for a in assessor_list:
        anew = {}
        anew['ID'] = a['ID']
        anew['label'] = a['label']
        anew['uri'] = a['URI']
        anew['assessor_id'] = a['ID']
        anew['assessor_label'] = a['label']
        anew['assessor_uri'] = a['URI']
        anew['project_id'] = projectid
        anew['project_label'] = projectid
        anew['subject_id'] = a['xnat:imagesessiondata/subject_id']
        anew['session_id'] = a['session_ID']
        anew['session_label'] = a['session_label']
        anew['procstatus'] = a['proc:genprocdata/procstatus']
        anew['proctype'] = a['proc:genprocdata/proctype']
        anew['qcstatus'] = a['proc:genprocdata/validation/status']
        anew['xsiType'] = a['xsiType']
        new_list.append(anew)

    return sorted(new_list, key=lambda k: k['label'])

def list_assessor_out_resources(intf, projectid, subjectid, experimentid, assessorid):
    post_uri = '/REST/projects/'+projectid+'/subjects/'+subjectid+'/experiments/'+experimentid+'/assessors/'+assessorid+'/out/resources'
    resource_list = intf._get_json(post_uri)
    return resource_list
    
def select_assessor(intf,assessor_label):
    labels=assessor_label.split('-x-')
    return intf.select('/project/'+labels['0']+'/subject/'+labels['1']+'/experiment/'+labels['2']+'/assessor/'+assessor_label)

def get_full_object(intf,obj_dict):
    if 'scan_id' in obj_dict:
        proj = obj_dict['project_id']
        subj = obj_dict['subject_id']
        sess = obj_dict['session_id']
        scan = obj_dict['scan_id']
        return intf.select('/project/'+proj+'/subject/'+subj+'/experiment/'+sess+'/scan/'+scan)
    elif 'xsiType' in obj_dict and (obj_dict['xsiType'] == 'fs:fsData' or obj_dict['xsiType'] == 'proc:genProcData'):
        proj = obj_dict['project_id']
        subj = obj_dict['subject_id']
        sess = obj_dict['session_id']
        assr = obj_dict['assessor_id']
        return intf.select('/project/'+proj+'/subject/'+subj+'/experiment/'+sess+'/assessor/'+assr)
    elif 'experiments' in obj_dict['URI']:
        proj = obj_dict['project']
        subj = obj_dict['subject_ID']
        sess = obj_dict['ID']
        return intf.select('/project/'+proj+'/subject/'+subj+'/experiment/'+sess)
    elif 'subjects' in obj_dict['URI']:
        proj = obj_dict['project']
        subj = obj_dict['ID']
        return intf.select('/project/'+proj+'/subject/'+subj)
    else:
        return None

def get_assessor(xnat,projid,subjid,sessid,assrid):
    assessor = xnat.select('/projects/'+projid+'/subjects/'+subjid+'/experiments/'+sessid+'/assessors/'+assrid)
    return assessor
    
def get_resource_lastdate_modified(xnat,resource):
    # xpaths for times in resource xml
    CREATED_XPATH = "/cat:Catalog/cat:entries/cat:entry/@createdTime"
    MODIFIED_XPATH = "/cat:Catalog/cat:entries/cat:entry/@modifiedTime"
    
    # Get the resource object and its uri
    res_xml_uri = resource._uri+'?format=xml'
    
    # Get the XML for resource
    xmlstr = xnat._exec(res_xml_uri, 'GET')
    
    # Parse out the times
    root = etree.fromstring(xmlstr)
    create_times = root.xpath(CREATED_XPATH, namespaces=root.nsmap)
    mod_times = root.xpath(MODIFIED_XPATH, namespaces=root.nsmap)
    
    # Find the most recent time
    all_times = create_times + mod_times
    if all_times:
        max_time = max(all_times)
        date = max_time.split('.')[0]
        res_date=date.split('T')[0].replace('-','')+date.split('T')[1].replace(':','')
    else:
        res_date=('{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())).strip().replace('-','').replace(':','').replace(' ','')
    return res_date


####################################################################################
#                     Download resources XNAT (Scan/Assessor)                      #
#################################################################################### 
## from a scan given, download the resources
def download_Scan(Outputdirectory,projectName,subject,experiment,scan,resource_list,all_resources=0):
    """ Download resources from a specific project/subject/experiment/scan from Xnat into a folder.

    parameters :
        - Outputdirectory = directory where the files are going to be download
        - projectName = project name on Xnat
        - subject = subject label of the files you want to download from Xnat
        - experiment = experiment label of the files you want to download from Xnat
        - scan = scan label of the files you want to download from Xnat
        - resource_list = List of resources name
            E.G resource_list=['NIFTI','bval,'bvec']
        - all_resources : download all the resources. If 0, download the biggest one.

    """

    print'Download resources from '+ projectName + '/' + subject+ '/'+ experiment + '/'+ scan

    #Check input for subjects_exps_list :
    if isinstance(resource_list, list):
        pass
    elif isinstance(resource_list, str):
        resource_list=[resource_list]
    else:
        print "INPUTS ERROR: Check the format of the list of resources in the download_Scan function. Not a list.\n"
        sys.exit()

    try:
        xnat = get_interface()
        SCAN=xnat.select('/project/'+projectName+'/subjects/'+subject+'/experiments/'+experiment+'/scans/'+scan)
        if SCAN.exists():
            if SCAN.attrs.get('quality')!='unusable':
                dl_good_resources_scan(SCAN,resource_list,Outputdirectory,all_resources)
            else:
                print 'DOWNLOAD WARNING: Scan unusable!'
        else:
            print 'DOWNLOAD ERROR: '+ projectName + '/' + subject+ '/'+ experiment + '/'+scan+' does not correspond to a Project/Subject/experiment/scan on Xnat.'

    finally:
        xnat.disconnect()
    print '===================================================================\n'

## from a list of scantype given, Download the resources
def download_ScanType(Outputdirectory,projectName,subject,experiment,List_scantype,resource_list,all_resources=0):
    """ Same than download_Scan but you give a list of scan type instead of the scan ID
    """

    print'Download resources from '+ projectName + '/' + subject+ '/'+ experiment + ' and the scan types like ',
    print List_scantype

    #Check input for subjects_exps_list :
    if isinstance(resource_list, list):
        pass
    elif isinstance(resource_list, str):
        resource_list=[resource_list]
    else:
        print "INPUTS ERROR: Check the format of the list of resources in the download_ScanType function. Not a list.\n"
        sys.exit()

    #check list of SD:
    if isinstance(List_scantype, list):
        pass
    elif isinstance(List_scantype, str):
        List_scantype=[List_scantype]
    else:
        print "INPUTS ERROR: Check the format of the list of series_description in the download_ScanType function. Not a list.\n"
        sys.exit()

    try:
        xnat = get_interface()

        for scan in list_scans(xnat, projectName, subject, experiment):
            if scan['type'] in List_scantype:
                if scan['quality']!='unusable':
                    SCAN=xnat.select('/project/'+projectName+'/subjects/'+subject+'/experiments/'+experiment+'/scans/'+scan['ID'])
                    dl_good_resources_scan(SCAN,resource_list,Outputdirectory,all_resources)
                else:
                    print 'DOWNLOAD WARNING: Scan unusable!'

    finally:
        xnat.disconnect()
    print '===================================================================\n'

## from a list of scan series_description given, download the resources
def download_ScanSeriesDescription(Outputdirectory,projectName,subject,experiment,List_scanSD,resource_list,all_resources=0):
    """ Same than download_Scan but you give a list of series description instead of the scan ID
    """

    print'Download resources from '+ projectName + '/' + subject+ '/'+ experiment + ' and the list of series description ',
    print List_scanSD

    #Check input for subjects_exps_list :
    if isinstance(resource_list, list):
        pass
    elif isinstance(resource_list, str):
        resource_list=[resource_list]
    else:
        print "INPUTS ERROR: Check the format of the list of resources in the download_ScanSeriesDescription function. Not a list.\n"
        sys.exit()

    #check list of SD:
    if isinstance(List_scanSD, list):
        pass
    elif isinstance(List_scanSD, str):
        List_scanSD=[List_scanSD]
    else:
        print "INPUTS ERROR: Check the format of the list of series_description in the download_ScanSeriesDescription function. Not a list.\n"
        sys.exit()

    try:
        xnat = get_interface()

        for scan in list_scans(xnat, projectName, subject, experiment):
            SCAN=xnat.select('/project/'+projectName+'/subjects/'+subject+'/experiments/'+experiment+'/scans/'+scan['ID'])

            if SCAN.attrs.get('series_description') in List_scanSD:
                if scan['quality']!='unusable':
                    dl_good_resources_scan(SCAN,resource_list,Outputdirectory,all_resources)
                else:
                    print 'DOWNLOAD WARNING: Scan unusable!'

    finally:
        xnat.disconnect()
    print '===================================================================\n'

## from an assessor given, download the resources :
def download_Assessor(Outputdirectory,assessor_label,resource_list,all_resources=0):
    """ Download resources from a specific process from Xnat into a folder.

    parameters :
        - Outputdirectory = directory where the files are going to be download
        - assessor_label = assessor label on XNAT -> Project-x-subject-x-session(-x-scan)-x-process
        - resource_list = List of resources name
            E.G resource_list=['NIFTI','bval,'bvec']
        - all_resources : download all the resources. If 0, download the biggest one.

    """

    print'Download resources from process '+ assessor_label

    #Check input for subjects_exps_list :
    if isinstance(resource_list, list):
        pass
    elif isinstance(resource_list, str):
        resource_list=[resource_list]
    else:
        print "INPUTS ERROR: Check the format of the list of resources in the download_Assessor function. Not a list.\n"
        sys.exit()

    try:
        xnat = get_interface()
        labels=assessor_label.split('-x-')
        ASSESSOR=xnat.select('/project/'+labels[0]+'/subjects/'+labels[1]+'/experiments/'+labels[2]+'/assessors/'+assessor_label)
        dl_good_resources_assessor(ASSESSOR,resource_list,Outputdirectory,all_resources)

    finally:
        xnat.disconnect()
    print '===================================================================\n'

## from an assessor type, download the resources :
def download_AssessorType(Outputdirectory,projectName,subject,experiment,List_process_type,resource_list,all_resources=0):
    """ Same than download_Scan but you give a list of series description instead of the scan ID
    """

    print'Download resources from '+ projectName + '/' + subject+ '/'+ experiment + ' and the process ',
    print List_process_type

    #Check input for subjects_exps_list :
    if isinstance(resource_list, list):
        pass
    elif isinstance(resource_list, str):
        resource_list=[resource_list]
    else:
        print "INPUTS ERROR: Check the format of the list of resources in the download_AssessorType function. Not a list.\n"
        sys.exit()

    #Check input for subjects_exps_list :
    if isinstance(List_process_type, list):
        pass
    elif isinstance(List_process_type, str):
        List_process_type=[List_process_type]
    else:
        print "INPUTS ERROR: Check the format of the list of process type in the download_AssessorType function. Not a list.\n"
        sys.exit()

    #if FreeSurfer in the list, change it to FS
    List_process_type = [process_type.replace('FreeSurfer', 'FS') for process_type in List_process_type]

    try:
        xnat = get_interface()

        for assessor in list_assessors(xnat, projectName, subject, experiment):
            for proc_type in List_process_type:
                if proc_type==assessor['label'].split('-x-')[-1]:
                    ASSESSOR=xnat.select('/project/'+projectName+'/subjects/'+subject+'/experiments/'+experiment+'/assessors/'+assessor['label'])
                    dl_good_resources_assessor(ASSESSOR,resource_list,Outputdirectory,all_resources)

    finally:
        xnat.disconnect()
    print '===================================================================\n'


def dl_good_resources_scan(Scan,resource_list,Outputdirectory,all_resources):
    for Resource in resource_list:
        resourceOK=0
        if Scan.resource(Resource).exists():
            resourceOK=1
        elif Scan.resource(Resource.upper()).exists():
            Resource=Resource.upper()
            resourceOK=1
        elif Scan.resource(Resource.lower()).exists():
            Resource=Resource.lower()
            resourceOK=1

        if resourceOK and all_resources:
            download_all_resources(Scan.resource(Resource),Outputdirectory)
        elif resourceOK and not all_resources:
            dl,DLFileName=download_biggest_resources(Scan.resource(Resource),Outputdirectory)
            if not dl:
                print 'ERROR: Download failed, the size of file for the resource is zero.'

def dl_good_resources_assessor(Assessor,resource_list,Outputdirectory,all_resources):
    for Resource in resource_list:
        resourceOK=0
        if Assessor.out_resource(Resource).exists():
            resourceOK=1
        elif Assessor.out_resource(Resource.upper()).exists():
            Resource=Resource.upper()
            resourceOK=1
        elif Assessor.out_resource(Resource.lower()).exists():
            Resource=Resource.lower()
            resourceOK=1

        if resourceOK and all_resources:
            download_all_resources(Assessor.out_resource(Resource),Outputdirectory)
        elif resourceOK and not all_resources:
            dl,DLFileName=download_biggest_resources(Assessor.out_resource(Resource),Outputdirectory)
            if not dl:
                print 'ERROR: Download failed, the size of file for the resource is zero.'

def download_biggest_resources(Resource,directory,filename='0'):
    if os.path.exists(directory):
        number=0
        Bigger_file_size=0
        for index,fname in enumerate(Resource.files().get()[:]):
            size=int(Resource.file(fname).size())
            if Bigger_file_size<size:
                Bigger_file_size=size
                number=index

        if Bigger_file_size==0:
            return 0,'nan'
        else:
            Input_res_label_fname = Resource.files().get()[number]
            if filename=='0':
                DLFileName = os.path.join(directory,Input_res_label_fname)
            else:
                DLFileName = os.path.join(directory,filename)
            Resource.file(Input_res_label_fname).get(DLFileName)
            return 1,DLFileName
    else:
        print'ERROR download_biggest_resources in XnatUtils: Folder '+directory+' does not exist.'

def download_all_resources(Resource,directory):
    if os.path.exists(directory):
        #if more than one file:
        if len(Resource.files().get())>1:
            #create a dir with the resourcename:
            Outputdir=os.path.join(directory,Resource.label())
            if not os.path.exists(Outputdir):
                os.mkdir(Outputdir)
            print '   ->Downloading all resources for '+Resource.label()+' as a zip'
            Resource.get(Outputdir,extract=False) #not sure the extract True is working
            print '   ->Unzipping ...' 
            os.system('unzip -d '+Outputdir+' '+os.path.join(Outputdir,Resource.label()+'.zip'))
        #if only one, if using download all resources, download it and unzip it if it's a zip
        else:
            print '   ->Downloading resource for '+Resource.label()
            Input_res_label_fname = Resource.files().get()[0]
            Resource.file(Input_res_label_fname).get(os.path.join(directory,Input_res_label_fname))
            if os.path.join(directory,Input_res_label_fname)[-3:]=='zip':
                print '   -> Unzipping ...'
                os.system('unzip -d '+directory+' '+os.path.join(directory,Input_res_label_fname))
    else:
        print'ERROR download_all_resources in XnatUtils: Folder '+directory+' does not exist.'

def upload_all_resources(Resource,directory):
    if os.path.exists(directory):
        if not Resource.exists():
            Resource.create()
        #for each files in this folderl, Upload files in the resource :
        Resource_files_list=os.listdir(directory)
        #for each folder=resource in the assessor directory, more than 2 files, use the zip from XNAT
        if len(Resource_files_list)>2:
            upload_zip(directory,Resource)
        #One or two file, let just upload them:
        else:
            for filename in Resource_files_list:
                #if it's a folder, zip it and upload it
                if os.path.isdir(filename):
                    upload_zip(filename,directory+'/'+filename)
                elif filename.lower().endswith('.zip'):
                    Resource.put_zip(directory+'/'+filename, extract=True)
                else:
                    #upload the file
                    Resource.file(filename).put(directory+'/'+filename)
    else:
        print'ERROR upload_all_resources in XnatUtils: Folder '+directory+' does not exist.'

def upload_zip(Resource,directory):
    filenameZip=Resource.label()+'.zip'
    initDir=os.getcwd()
    #Zip all the files in the directory
    os.chdir(directory)
    os.system('zip '+filenameZip+' *')
    #upload
    Resource.put_zip(directory+'/'+filenameZip,extract=True)
    #return to the initial directory:
    os.chdir(initDir)
    
def download_resource_assessor(directory,xnat,project,subject,experiment,assessor_label,resources_list,quiet):
    """ Download the resources from the list for the assessor given in the argument (if resource_list[0]='all' -> download all)"""

    if not quiet:
        print '    +Process: '+assessor_label

    assessor=xnat.select('/project/'+project+'/subjects/'+subject+'/experiments/'+experiment+'/assessors/'+assessor_label)
    if not assessor.exists():
        print '      !!WARNING: No assessor with the ID selected.'
        return

    if 'fMRIQA' in assessor_label:
        labels=assessor_label.split('-x-')
        SCAN=xnat.select('/project/'+project+'/subjects/'+subject+'/experiments/'+experiment+'/scans/'+labels[3])
        SD=SCAN.attrs.get('series_description')
        SD=SD.replace('/','_')
        SD=SD.replace(" ", "")

        if SD!='':
            directory=directory+'-x-'+SD

    if not os.path.exists(directory):
        os.mkdir(directory)

    #all resources
    if resources_list[0]=='all':
        post_uri_resource = '/REST/projects/'+project+'/subjects/'+subject+'/experiments/'+experiment+'/assessors/'+assessor_label+'/out/resources'
        resources_list = xnat._get_json(post_uri_resource)
        for resource in resources_list:
            Resource=xnat.select('/project/'+project+'/subjects/'+subject+'/experiments/'+experiment+'/assessors/'+assessor_label+'/out/resources/'+resource['label'])
            if Resource.exists():
                if not quiet:
                    print '      *download resource '+resource['label']

                assessor_real_type=assessor_label.split('-x-')[-1]
                if 'FS' in assessor_real_type:
                    #make a directory for each of the resource
                    Res_path=directory+'/'+resource['label']
                    if not os.path.exists(Res_path):
                        os.mkdir(Res_path)
                    Resource.get(Res_path, extract=False)
                else:
                    if len(Resource.files().get()) > 0:
                        #make a directory for each of the resource
                        Res_path=directory+'/'+resource['label']
                        if not os.path.exists(Res_path):
                            os.mkdir(Res_path)

                        for fname in Resource.files().get()[:]:
                            Resfile = Resource.file(fname)
                            local_fname = os.path.join(Res_path, fname)
                            Resfile.get(local_fname)
                    else:
                        print "\t    *ERROR : The size of the resource is 0."

    #resources in the options
    else:
        for resource in resources_list:
            Resource=xnat.select('/project/'+project+'/subjects/'+subject+'/experiments/'+experiment+'/assessors/'+assessor_label+'/out/resources/'+resource)
            if Resource.exists():
                if not quiet:
                    print '      *download resource '+resource

                assessor_real_type=assessor_label.split('-x-')[-1]
                if 'FS' in assessor_real_type:
                    #make a directory for each of the resource
                    Res_path=directory+'/'+resource
                    if not os.path.exists(Res_path):
                        os.mkdir(Res_path)

                    Resource.get(Res_path, extract=False)
                else:
                    if len(Resource.files().get()) > 0:
                        #make a directory for each of the resource
                        Res_path=directory+'/'+resource
                        if not os.path.exists(Res_path):
                            os.mkdir(Res_path)

                        for fname in Resource.files().get()[:]:
                            Resfile = Resource.file(fname)
                            local_fname = os.path.join(Res_path, fname)
                            Resfile.get(local_fname)
                    else:
                        print "      !!ERROR : The size of the resource is 0."
            else:
                print '      !!WARNING : no resource '+resource+' for this assessor.'


    print'\n'

####################################################################################
#                                 Useful Functions                                 #
#################################################################################### 
def clean_directory(folder_name):
    files=os.listdir(folder_name)
    for f in files:
        if os.path.isdir(folder_name+'/'+f)==False:
            os.remove(folder_name+'/'+f)
        else:
            shutil.rmtree(folder_name+'/'+f)
    return 0

####################################################################################
#                           Save in REDCap jobs running                            #
#################################################################################### 
#function to send the data to the VUIIS XNAT Jobs redcap project about what is running
def save_job_redcap(data,record_id):
    try:
        # Environs
        redcap_api_url = os.environ['API_URL']
        redcap_api_key = os.environ['API_KEY_XNAT']
    except KeyError as e:
        print "You must set the environment variable %s to save the job on redcap." % str(e)
        return 0

    try:
        job_redcap_project = redcap.Project(redcap_api_url, redcap_api_key)
        response = job_redcap_project.import_records([data])
        assert 'count' in response
        print ' ->Record '+record_id+ ' uploaded for <'+data['spider_module_name']+'> : ' + str(response['count'])
        return 1
    except AssertionError as e:
        return 0

#create the data record for redcap
def create_record_redcap(project,SM_name):
    """ SM_name means the spider name or modules name: name_v# or name_vDEV#
    """
    #data for redcap
    data=dict()
    #create the record_ID
    date=str(datetime.now())
    record_id=project+'-'+date.strip().replace(':','_').replace('.','_').replace(' ','_')
    labels=SM_name.split('_v')
    #version in the name, if not it's 0
    if len(labels)>1:
        # _v ( equals to 2 characters) + number of characters in the last labels that is the version number
        nb_c=2+len(labels[-1])
        name=SM_name[:-nb_c]
        version='v'+labels[-1]
    else:
        name=SM_name
        version='v0'

    #create the data for redcap
    data['record_id']=record_id
    data['spider_module_name']=name
    data['spider_module_version']=version
    data['date']=date
    data['xnat_project']=project
    data['hostname'] = socket.gethostname()
    data['pi_lastname'] = pi_from_project(project)
    return data,record_id


def pi_from_project(project):
    pi = ''
    try:
        xnat = get_interface()
        proj = xnat.select.project(project)
        pi = proj.attrs.get('xnat:projectdata/pi/lastname')
    except:
        pass
    finally:
        xnat.disconnect()
        return pi
        
def print_args(options):
    print "--Arguments given to the spider--"
    for info,value in vars(options).items():
        if value:
            print info,": ", value
        else:
            print info,": Not set. The process might fail without this argument."
    print "---------------------------------"

def makedir(jobdir):
    if not os.path.exists(jobdir):
        os.mkdir(jobdir)
    else:
        today=datetime.now()
        jobdir=jobdir+'/TempDir_'+str(today.year)+'_'+str(today.month)+'_'+str(today.day)
        if not os.path.exists(jobdir):
            os.mkdir(jobdir)
        else:
            clean_directory(jobdir)
    return jobdir
 
# Upload a folder to a resource all files are zip and then unzip in Xnat   
def Upload_folder_to_resource(resourceObj,directory):
    filenameZip=resourceObj.label()+'.zip'
    initDir=os.getcwd()
    #Zip all the files in the directory
    os.chdir(directory)
    os.system('zip '+filenameZip+' *')
    #upload
    resourceObj.put_zip(directory+'/'+filenameZip,extract=True)
    #return to the initial directory:
    os.chdir(initDir)

# Download all resources in a folder. the folder will have the name Resource.label(),
# removes the previous folder if there is one.
def Download_resource_to_folder(Resource,directory):
    Res_path=os.path.join(directory,Resource.label())
    if os.path.exists(Res_path):
        os.remove(Res_path)
    Resource.get(directory,extract=True)

def copy_resource(intf, scan_dict,directory,old_res,new_res):
    SCAN = get_full_object(intf, scan_dict)
    #download
    Download_resource_to_folder(SCAN.resource(old_res),directory)
    #upload
    Upload_folder_to_resource(new_res,SCAN.resource(new_res),os.path.join(directory,old_res))
    #clean directory
    clean_directory(directory)
