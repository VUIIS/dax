Writing a Settings File
=======================

Table of Contents
~~~~~~~~~~~~~~~~~

1.  `Definition of a ProjectSettings.py File <#definition-of-a-projectsettings.py-file>`__
2.  `Module and Processor <#module-and-processor>`__
3.  `What is a Module? <#what-is-a-module>`__
4.  `What is a Processor? <#what-is-a-processor>`__
5.  `How to Write a module.py <#how-to-write-a-module.py>`__
6.  `Scan Level Processor Template <#scan-level-processor-template>`__
7.  `Session Level Processor Template <#session-level-processor-template>`__
8.  `Spiders <#spiders>`__
9.  `What is a Spider? <#what-is-a-spider>`__
10. `How to Run a Spider? <#how-to-run-a-spider>`__
11. `How to Write a Spider? <#how-to-write-a-spider>`__
12. `Writing a ProjectSettings.py File <#writing-a-projectsettings.py-file>`__
13. `Imports and Variables <#imports-and-variables>`__
14. `Modules <#modules>`__
15. `Processors <#processors>`__
16. `Associate Modules/Processors to Project <#associate-modules/processors-to-project>`__
17. `Create a Launcher <#create-a-launcher>`__

---------------------------------------
Definition of a ProjectSettings.py file
---------------------------------------

ProjectSettings.py is a python script that describs each module/processor turned on by the user on a project or list of project (see below for the definition of a module or a processor). The ProjectSettings.py can be generated automatically by dax_manager if you are using REDCap to host your settings for your projects. For example, see the ProjectSettings.py file below for our test project on XNAT:

	.. image:: images/writing_settings_file/vustp_settings.png

--------------------
Module and Processor
--------------------

What is a Module?
~~~~~~~~~~~~~~~~~

A module is a python class script herited from the DAX module class. It's a processing that will generate raw data on a scan or a session such as converting dicom to NIFTI, generating preview, or syncing data between XNAT and REDCap. It has four functions that are required:

prerun() that will run at the beginning of an dax_update to generate the tmp folder to hold data and any processing that needs to happen before hand.
afterrun() that will run at the end of an dax_update to send report or set/check any variables after hand.
needs_run() that will check if the module needs to run on a session or scan.
run() representing the function that will be called for each session or scan to run.
You can check the existing modules in masimatlab under trunk/xnatspiders/modules/\* .

What is a Processor?
~~~~~~~~~~~~~~~~~~~~
A processor is a python class script herited from the DAX processor class. It can be on a session level or a scan level. It's defining a spider attributes to run as a job on the cluster. It's going to check if the inputs are present and generate the command line to add to the SLURM/PBS file to submit to the cluster. It has three functions that are required:

- should_run() that will check if an assessor need to exist for a scan or a session. It should return True or False. (Return always True for a session).
- has_inputs() that will check if all inputs are present on a scan/session to switch an assessor NEED_INPUTS status to NEED_TO_RUN.
- get_cmds() that will generate the command line to print in the SLURM/PBS file.

You can check the existing processors in masimatlab under trunk/xnatspiders/processors/\* .

The difference between Scan and Session processors is that a scan processor will operate on one single scan (one per scan found with the scantype given) and a session processor will operate on the full session (one per session).

How to Write a module.py
~~~~~~~~~~~~~~~~~~~~~~~~

You can use any example in Masimatlab on NITRC to write any modules. Keep in mind that each function needs to be there with the same input variables. We attached below the example of a simple module to set a unique series description for each scan in a session:

::

	from dax import XnatUtils,SessionModule
	import os,logging
	
	logger=logging.getLogger('dax')
	
	DEFAULT_TPM_PATH='/tmp/Unique_Series_Description_tmp/'
	DEFAULT_MODULE_NAME='Unique_Series_Description'
	DEFAULT_TEXT_REPORT='ERROR/WARNING for unique series description:\n'
	RESOURCE_FLAG_NAME='Module_Unique_Series_Description'
	
	class Module_Unique_Series_Description(SessionModule):
	   def __init__(self,module_name=DEFAULT_MODULE_NAME,
	         directory=DEFAULT_TPM_PATH,email=None,
	         Text_report=DEFAULT_TEXT_REPORT):
	               super(Module_Unique_Series_Description, self).__init__(module_name,directory,email,Text_report=DEFAULT_TEXT_REPORT)
	       
	   def prerun(self,settings_filename=):
	       pass
	   
	   def afterrun(self,xnat,project):
	       #send report
	       if self.send_an_email:
	           self.sendReport('**ERROR/WARNING for '+self.module_name+'**')
	           
	   def needs_run(self,sess_info,xnat):   
	       sess_res_list=XnatUtils.list_experiment_resources(xnat,sess_info['project_id'],sess_info['subject_id'], sess_info['session_id']);             
	       # Check for NIFTI resource
	       flagres_list = [r for r in sess_res_list if (r['label'] == RESOURCE_FLAG_NAME)]
	       if len(flagres_list) > 0:
	           logger.debug('Already run')
	           return False
	       
	       return True
	   
	   def run(self,session_info,session_obj):
	       Series_description=dict()
	       for scan in session_obj.scans().fetchall('obj'):
	           if scan.attrs.get('quality')!='unusable':
	               SD=scan.attrs.get('series_description')
	               if SD !=:
	                   if SD in Series_description:
	                       Series_description[SD] += 1
	                       scan.attrs.set('series_description',SD+str(Series_description[SD]))
	                       #if it's the second time add the number to the first one
	                       if Series_description[SD] == 2:
	                           ScanNumber1=session_obj.scan(Series_description['X'+SD+'X'])
	                           ScanNumber1.attrs.set('series_description',SD+'1')
	                   else:
	                       Series_description[SD] = 1
	                       Series_description['X'+SD+'X'] = scan.label()
	                        
	       #Create the flag resources on experiment level :
	       session_obj.resource(RESOURCE_FLAG_NAME).create()
	           
Each module if runnings only one time should create a resource on the session that you will be checking in the needs_run() function to know if the module needs to run.

You can follow the template below to write any processor. Keep in mind that each function needs to be there with the same input variables.

Scan Level Processor Template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the folder on masimatlab, you can find the template for a processor on the scan level. See below for the example_scan_processor.py:

::

	from dax import ScanProcessor
	from VUIIS_path_settings import MASIMATLAB_PATH
	import os,logging
	
	logger=logging.getLogger('dax')
	##Use logger to print statement like: logger.debug('comments')
	## if it's a warning: logger.warn('comments')
	## if it's an error: logger.error('comments')
	
	DEFAULT_SPIDER_PATH = MASIMATLAB_PATH+'/Spider_example_scan_vX.Y.Z.py'
	DEFAULT_WALLTIME = '40:00:00'
	DEFAULT_MEM = 6144
	DEFAULT_SCAN_TYPES=[]
	
	class example_scan_Processor (ScanProcessor):
	    def __init__(self, spider_path=DEFAULT_SPIDER_PATH, 
	          masimatlab=MASIMATLAB_PATH, version=None, 
	          walltime=DEFAULT_WALLTIME, mem_mb=DEFAULT_MEM, 
	          scan_types=DEFAULT_SCAN_TYPES):
	       #super initi
	       super(example_scan_Processor, self).__init__(scan_types,walltime,mem_mb,spider_path,version)
	       self.masimatlab=masimatlab
	
	   def should_run(self, scan_dict):
	       return (scan_dict['scan_type'] in self.scan_types)
	   
	   def has_inputs(self, assessor):
	       # Return two values, first value : 
	       #     for the job status: 0 for still NEED_INPUTS, -1 for NO_DATA, 1 for NEED_TO_RUN
	       #     for the qc status: for example missing inputs
	       # Always return 1,None for the qcstatus when NEED_TO_RUN
	       pass
	   
	   def get_cmds(self,assessor,jobdir):
	       proj = assessor.parent().parent().parent().label()
	       subj = assessor.parent().parent().label()
	       sess = assessor.parent().label()
	       assr = assessor.label()
	       scan = assr.split('-x-')[3]
	       spider_path = self.spider_path
	       masimatlab = self.masimatlab
	       software_path = self.software_path
	       
	       cmd = 'python '+spider_path+' -m '+masimatlab+' -p '+proj+' -d '+jobdir+' -s '+subj+' -e '+sess+' -c '+scan+' --Softwaredir '+software_path
	       return [cmd]

Follow this template to create your scan processor files.

Session Level Processor Template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the folder on masimatlab, you can find the template for a processor on the session (experiment) level. See below for the example_experiment_processor.py:

::

	from dax import SessionProcessor
	from VUIIS_path_settings import MASIMATLAB_PATH
	import os,logging
	
	logger=logging.getLogger('dax')
	##Use logger to print statement like: logger.debug('comments')
	## if it's a warning: logger.warn('comments')
	## if it's an error: logger.error('comments')
	
	DEFAULT_SPIDER_PATH = DEFAULT_MASIMATLAB_PATH+'/Spider_example_experiment_vX.Y.Z.py'
	DEFAULT_WALLTIME = '02:00:00'
	DEFAULT_MEM = 2048
	 
	class example_experiment_Processor (SessionProcessor):
	   def __init__(self, spider_path=DEFAULT_SPIDER_PATH, 
	         masimatlab=MASIMATLAB_PATH, version=None, walltime=DEFAULT_WALLTIME, mem_mb=DEFAULT_MEM):
	       #super initi
	       super(example_experiment_Processor, self).__init__(walltime,mem_mb,spider_path,version)
	       self.masimatlab=masimatlab
	
	   def should_run(self, sess_dict,intf):
	       return 1
	       
	   def has_inputs(self, assessor): 
	       # Return two values, first value : 
	       #     for the job status: 0 for still NEED_INPUTS, -1 for NO_DATA, 1 for NEED_TO_RUN
	       #     for the qc status: for example missing inputs
	       # Always return 1,None for the qcstatus when NEED_TO_RUN 
	       pass
   	
	   def get_cmds(self,assessor,jobdir):
	       proj = assessor.parent().parent().parent().label()
	       subj = assessor.parent().parent().label()
	       sess = assessor.parent().label()
	       spider_path = self.spider_path
	       masimatlab = self.masimatlab
	       spm_path = self.spm_path
	       fMRI_scantype = self.fMRI_scantype
	       T1_scantype = self.T1_scantype
	       
	       cmd = 'python '+spider_path+' -v -m '+masimatlab+' --spm '+spm_path+' -p '+proj+' -d '+jobdir+' -s '+subj+' -e '+sess+' -t '+fMRI_scantype+' -T '+T1_scantype
	       return [cmd]

Follow this template to create your session processor files.
	
-------
Spiders
-------

What is a Spider?
~~~~~~~~~~~~~~~~~

A spider is a python script that will execute a image processing task. For example, we have an fMRIQA spiders or a dtiQA spiders. A spider will require three functions:

- init_process() that takes care of downloading data from XNAT
- run_process() that performs the image processing
- finish_process() that copies the data in the upload queue folder.

Each function could be called independently from the script. A spider.py is associated to a processor.py. The inputs of a spider can be raw images from Scans or processed data from Assessors.

How to Run a Spider?
~~~~~~~~~~~~~~~~~~~~

A spider can be run manually by the user by calling the script and giving it the different arguments. For example, a user can run the spider to generate the fMRIQA report by the command:

- python Spider_fMRIQA.py -p VUSTP -s VUSTP7 -e VUSTP7a -c 701 -d /tmp/fmriqa_folder/ -m /home/test/masimatlab/

The spider will copy at the end the results in the upload queue folder.

If you want the spider to be turn on on a project, you will need to create a processor.py file associated to this spider and add it to your ProjectSettings.py file. It will then be used by dax executables to generate automatically the assessors and run the processes on the cluster.

How to Write a Spider?
~~~~~~~~~~~~~~~~~~~~~~

To learn how to write a spider, you can follow the tutorial Spider Template. You can also check the different spiders in the Masimatlab SVN folder from NITRC: http://www.nitrc.org/projects/masimatlab in the folder trunk/xnatspiders/spiders/\* .

---------------------------------
Writing a ProjectSettings.py File
---------------------------------

We already saw earlier what is a ProjectSettings.py file. You can check the previous paragraph about it and the example. We are gonna learn how to write those files below.

Imports and Variables
~~~~~~~~~~~~~~~~~~~~~

Your settings file should set those following imports:

::

	import os
	from dax import Launcher
	from Xnat_process_importer import *
	from Xnat_module_importer import *

The two last imports are coming from masimatlab folder. You can write this file yourself and give them to your PYTHONPATH in your configuration file. They need to import from your modules and processors each class. For example, Xnat_process_import looks like:

::

	#Import the processors from the folder in masimatlab/trunk/xnatspiders/processors
	from dtiqa_processor import DtiQa_Processor
	from dtiqa_multi_processor import dtiQA_Multi_Processor
	from fMRI_FirstLevel_CAP_processor import fMRI_FirstLevel_CAP_Processor
	from fMRI_FirstLevel_GONOGO_processor import fMRI_FirstLevel_GONOGO_Processor
	from fMRI_FirstLevel_MID_processor import fMRI_FirstLevel_MID_Processor
	from fMRI_Preprocess_processor import fMRI_Preprocess_Processor
	from fMRI_Preprocess_CAP_processor import fMRI_Preprocess_CAP_Processor
	from fMRI_Preprocess_GONOGO_processor import fMRI_Preprocess_GONOGO_Processor
	from fMRI_Preprocess_MID_processor import fMRI_Preprocess_MID_Processor
	from fmriqa_processor import FmriQa_Processor
	from freesurfer_processor import Freesurfer_Processor
	from intra_sess_reg_processor import intra_sess_reg_Processor
	from Multi_Atlas_processor import Multi_Atlas_Processor
	from nonrigid_reg_to_ATLAS_processor import nonrigid_reg_to_ATLAS_Processor
	from vbmqa_processor import VbmQa_Processor
	from White_Matter_Stamper_processor import White_Matter_Stamper_Processor
	from tbsspre_processor import TbssPre_Processor
	from FSL_First_processor import FSL_First_Processor
	from tracula_processor import Tracula_Processor
	from ON_CT_segmentation_processor import ON_CT_segmentation_Processor
	from ON_MR_segmentation_processor import ON_MR_segmentation_Processor
	from ON_MR_sheath_segmentation_processor import ON_MR_sheath_segmentation_Processor
	from swi_processor import SWI_processor
	from mra_processor import MRA_processor
	from asl_processor import ASL_processor
	from freesurfer_processor_sub1mm import Freesurfer_Processor_sub1mm
	from lst_processor import Lst_Processor
	from Bedpost_processor import Bedpost_Processor
	from aslqa_rest_processor import ASLQA_Rest_Processor
	from ashs_processor import ASHS_Processor
	from SCFusion_processor import SCFusion_Processor

After importing external files/packages, set all the variables you will need for your modules/processors.

Modules
~~~~~~~

After initiating the variables and importing the external files/packages, you will implemente an object for each module that you want to run on your project(s): For example:

::

	VUSTP_Module_dcm2nii_phillips=Module_dcm2nii_phillips(directory="/tmp/dcm2nii_phillips")
	VUSTP_Module_Preview_NIFTI=Module_Preview_NIFTI(directory="/tmp/preview_nifti",resourcename="NIFTI")
	VUSTP_Module_Sync_REDCap=Module_Sync_REDCap(directory="/tmp/sync_redcap",api_key="API_KEY_VUSTP")
 
We created for VUSTP three modules that we want to run:

- convertion of dicom to nifti for phillips data
- preview generation from NIFTI resource
- sync to REDCap the statistics for each spider that provides data to sync.

Processors
~~~~~~~~~~

After creating your modules for your project(s), you will implemente an object for each processor that you want to run on your project(s): For example:

::

	VUSTP_0_White_Matter_Stamper_Processor=White_Matter_Stamper_Processor() 
	VUSTP_0_Multi_Atlas_Processor=Multi_Atlas_Processor(walltime="65:00:00")
	VUSTP_0_FSL_First_Processor=FSL_First_Processor()
	VUSTP_0_FmriQa_Processor=FmriQa_Processor()
	VUSTP_1_FmriQa_Processor=FmriQa_Processor(mem_mb="4096",version="2.0.0")
	VUSTP_0_TbssPre_Processor=TbssPre_Processor()
	VUSTP_0_DtiQa_Processor=DtiQa_Processor(version="2.1.1",walltime="48:00:00")
	VUSTP_2_DtiQa_Processor=DtiQa_Processor(version="3.0.1",walltime="48:00:00")

We created for VUSTP eight processors that we want to run:

- White Matter Stamper using default parameters
- Multi Atlas using default parameters except the walltime that we set to 65 hours
- FSL First using default parameters
- fMRIQA for default version and also for version 2.0.0 with 4096mb memory per job.
- Tbss Preprocess using default parameters
- dtiQA for version 2.1.1 and version 3.0.1 for a walltime of 48 hours per job

Associate Modules/Processors to Project
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After creating one object per modules and processors we want to run, we create two dictionaries to link modules and processors to a project:

:: 

	#Set up modules for projects
	proj_mod = {"VUSTP":[VUSTP_Module_dcm2nii_phillips,VUSTP_Module_Preview_NIFTI,VUSTP_Module_Sync_REDCap]}
	#Set up processors for projects
	proj_proc = {"VUSTP": [VUSTP_0_White_Matter_Stamper_Processor,VUSTP_0_Multi_Atlas_Processor,VUSTP_0_FSL_First_Processor,VUSTP_0_FmriQa_Processor,VUSTP_1_FmriQa_Processor,VUSTP_0_Tracula_Processor, VUSTP_0_TbssPre_Processor,VUSTP_0_DtiQa_Processor,VUSTP_1_DtiQa_Processor]}

Create a Launcher
~~~~~~~~~~~~~~~~~

When everything is linked betwen project and modules/processors, we can create the launcher that will be used by DAX executables:

::

	#Launch jobs:
	myLauncher = Launcher(proj_proc,proj_mod,priority_project=p_order,job_email=email,job_email_options="FAIL",queue_limit=400)
