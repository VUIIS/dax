import os
import shutil
import smtplib
import logging
from .dax_settings import SMTP_HOST,SMTP_FROM,SMTP_PASS
from email.mime.text import MIMEText
from datetime import datetime

#Logger for logs
logger=logging.getLogger('dax')

class Module(object):
    def __init__(self,module_name,directory,email,Text_report):
        self.module_name=module_name
        self.directory=directory
        if isinstance(email,list):
            self.email=email
        else:
            if email:
                self.email=[email]
            else:
                self.email=None
        self.Text_report=Text_report
        self.send_an_email=0
        
    def needs_run(self):
        raise NotImplementedError()
        
    def prerun(self):
        raise NotImplementedError()
    
    def afterrun(self):
        raise NotImplementedError()
    
    def report(self,string):
        self.Text_report+='  -'+string+'\n'  
        self.send_an_email=1
        
    def get_report(self):
        return self.Text_report
    
    def make_dir(self,suffix=''):
        #add the suffix if one to the directory:
        if suffix:
            if not suffix in self.directory:
                self.directory=self.directory.rstrip('/')+'_'+suffix
            
        #Check if the directory exists
        if not os.path.exists(self.directory):
            os.mkdir(self.directory)
        else:
            if suffix:
                self.clean_directory()
            else:
                today=datetime.now()
                self.directory=os.path.join(self.directory,self.module_name+'_tmp_'+str(today.year)+'_'+str(today.month)+'_'+str(today.day)+'_'+str(today.hour)+'_'+str(today.minute)+'_'+str(today.second))
    
                if not os.path.exists(self.directory):
                    os.mkdir(self.directory)
                else:
                    self.clean_directory()
    
    def getname(self):
        return self.module_name
 
    def clean_directory(self):
        files=os.listdir(self.directory)
        for f in files:
            if os.path.isdir(self.directory+'/'+f)==False:
                os.remove(self.directory+'/'+f)
            else:
                shutil.rmtree(self.directory+'/'+f)
                
    def sendReport(self,SUBJECT):
        if SMTP_HOST and SMTP_FROM and SMTP_PASS and self.email:
            # Create the container (outer) email message.
            msg = MIMEText(self.Text_report)
            msg['Subject'] = SUBJECT
            # me == the sender's email address
            # family = the list of all recipients' email addresses
            msg['From'] = SMTP_FROM
            msg['To'] = ",".join(self.email)
            
            # Send the email via our own SMTP server.
            s = smtplib.SMTP(SMTP_HOST)
            s.starttls()
            s.login(SMTP_FROM,SMTP_PASS)
            s.sendmail(SMTP_FROM, self.email, msg.as_string())
            s.quit()
        
class ScanModule(Module):
    def __init__(self,module_name,directory,email,Text_report):
        super(ScanModule, self).__init__(module_name,directory,email,Text_report)
        
    def run(self):
        raise NotImplementedError()

class SessionModule(Module):
    def __init__(self,module_name,directory,email,Text_report):
        super(SessionModule, self).__init__(module_name,directory,email,Text_report)
        
    def run(self):
        raise NotImplementedError()
    
def modules_by_type(mod_list):
    exp_mod_list = []
    scan_mod_list = []
            
    # Build list of processors by type
    for mod in mod_list:
        if issubclass(mod.__class__,ScanModule):
            scan_mod_list.append(mod)
        elif issubclass(mod.__class__,SessionModule):
            exp_mod_list.append(mod)
        else:
            logger.warn('unknown module type:'+mod)

    return exp_mod_list, scan_mod_list
