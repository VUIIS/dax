XnatUtils
=========

Table of Contents
~~~~~~~~~~~~~~~~~

1. `Conventions <#conventions>`__
 1. `XNAT Naming Convention <#xnat-naming-conventions>`__
 2. `How to name a resource on XNAT <#how-to-name-a-resource-on-xnat>`__
 3. `Assessor Label <#assessor-label>`__
 4. `Interface <#interface>`__
 5. `Pyxnat Objects <#pyxnat_objects>`__
2. `Classes <#classes>`__
 1. `InterfaceTemp <#interfacetemp>`__
 2. `AssessorHandler <#assessorhandler>`__
 3. `SpiderProcessHandler <#spiderprocesshandler>`__
 4. `Cached Classes <#cached-classes>`__
3. `Methods <#methods>`__
 1. `Looping through XNAT database <#looping-through-xnat-database>`__
 2. `Select Pyxnat Objects <#select-pyxnat-objects>`__
 3. `Download from XNAT <#download-from-xnat>`__
 4. `Upload to XNAT <#upload-to-xnat>`__
 5. `Methods for Processors using cached classes <#methods-for-processors-using-cached-classes>`__
 6. `Other Methods <#other-methods>`__

Conventions
~~~~~~~~~~~

----------------------
XNAT Naming Convention
----------------------

XNAT has four levels:

- project
- subject
- experiment
- scan/assessor

An experiment is identical to say a session. Most of the tutorial present on this wiki will use the word "session" for an experiment on XNAT. Each XNAT level can possess a "resource". It represents a folder on XNAT where it stores the data. Any data on XNAT will be stored in a resource. You can create resources on a project, on a subject, on a session, on a scan or on an assessor.

------------------------------
How to name a resource on XNAT
------------------------------

XNAT doesn't require the user to follow rules on naming the resources except the same rule than apply to any computer about naming folder.

A naming convention that dax tend to use/require is:

- For scan:
 - dicom files for a scan are stored in a resource called "DICOM"
 - nifty files for a scan are stored in a resource called "NIFTI"
 - bval and bvec for a diffusion scan are stored in two different resources called "BVAL" & "BVEC
 - snapshots of the scan are stored in a resource called "SNAPSHOTS"

- For assessor:
 - PDF for an assessor are stored in a resource called "PDF"
 - snapshots of the assessor's pdf are stored in a resource called "SNAPSHOTS"
 - pbs file submit to the cluster for an assessor are stored in a resource called "PBS"
 - outlogs of the assessor job are stored in a resource called "OUTLOG"

--------------
Assessor Label
--------------

An assessor is define in XNAT as an object representing the processed data for a session. dax is using a specific naming convention for the label associated to an assessor. It needs to follow the following pattern:

- assessor on a session: project-x-subject-x-session-x-proctype
 - ADNI-x-12931-x-MR_Session12-x-Tracula_v1
- assessor on a scan: project-x-subject-x-session-x-scan-x-proctype
 - DNI-x-12931-x-MR_Session12-x-301-x-fMRIQA_v2_test

---------
Interface
---------

Interface represents the connection between your python script and the XNAT database. You will open an interface every time you want to download or upload data to the database. To create this interface, you need to do:

:: 

	from dax import XnatUtils

	host = "xnat-server"
	user = "user"
	pwd = "XXXXX"
	xnat = XnatUtils.get_interface(host, user, pwd)

Typing your host, user, and password for every connection you open will be time consuming and can expose your login information. You can set the following environment variables to avoid giving those information:

- XNAT_HOST
- XNAT_USER
- XNAT_PASS

When this is set, you can call the method like this:

::

  xnat = XnatUtils.get_interface()
  
Warning: when you create an interface, don't forget to close it at the end using disconnect() (see below in methods). E.G:

::

  xnat.disconnect()

We will call intf or xnat the object returned by get_interface() .

--------------
Pyxnat Objects
--------------

Each level on XNAT corresponds to a pyxnat's object that are linked. You can access each object by selecting them using either the label or the ID in the right URI. For example, let's access the subject for ADNI project named "1234":

::

  from dax import XnatUtils
  
  xnat = XnatUtils.get_interface()
  project = "ADNI"
  subject = "1234"
  uri = "/project/"+project+"/subject/"+subject
  subject_obj = xnat.select(uri)
  if subject_obj.exists():
      print "Subject exists"

The uri needs to follow the pattern for each level:

- project: "/project/{project}"
- subject: "/project/{project}/subject/{subject}"
- session: "/project/{project}/subject/{subject}/experiment/{session}"
- scan: "/project/{project}/subject/{subject}/experiment/{session}/scan/{scan}"
- assessor: "/project/{project}/subject/{subject}/experiment/{session}/assessor/{assessor}"

Resource in XNAT language mean the folder in each object that holds data. You can have a resource at each level. To do so, you need to add the following path at the end of the previous uri:

- resource: /resource/{resource}
- for assessor: /out/resource/{resource}

You can also select object directly from a previous object. For example, in our previous example, if we select the session for the subject 1234 in ADNI from the subject_obj:

::

  session_label = "MR_session1"
  session_obj = subject_obj.select(session_label)
  if session_obj.exists():
       print "Session exists"

Classes
~~~~~~~

-------------
InterfaceTemp
-------------

InterfaceTemp is a class that extends the functionality of Interface from pyxnat to have a temporary cache that is removed when disconnect() is called.

You don't need to call this class. It's already integrated to the get_interface() method (see below).

---------------
AssessorHandler
---------------

AssessorHandler(label) is a class to handle assessor label string. You can create an object by giving the label of your assessor. E.G:

::

  from dax import XnatUtils
  
  label = "project-x-subject-x-session-x-(scan-x-)proctype
  ah = XnatUtils.AssessorHandler(label)

This class offers different methods such as getters for each object, is_valid method, and a select_assessor. All the examples below will be using those lines as a start.

See below for each of those methods:

- is_valid
 - is_valid(self) returns a boolean variable to define if the label given to the class is valid or not with dax conventions for assessor (see label variable above).

- getters
 - getters will allow you to access each element of your assessor label. The different variables available are listed below:

- project_id
- subject_label
- session_label
- scan_id (if assessor on a scan)
- proctype

To call the methods, you need to do get_ELEMENT() and replace ELEMENT with one of the variables above. E.G:

::

  session_label = ah.get_session_label()

- select_assessor
 - select_assessor(self, intf) will return the XNAT object representing your assessor. You can then use methods from XnatUtils or pyxnat to interact with the assessor. intf is the variable corresponding to the pyxnat interface. E.G:

::

  #use the lines above
  host = "xnat-server.XXXXX"
  user = "XXXXX"
  pwd = "XXXXX"
  xnat = XnatUtils.get_interface(host, user, pwd)
  
  assessor_obj = ah.select_assessor(xnat)

--------------------
SpiderProcessHandler
--------------------

SpiderProcessHandler(script_name, suffix, project, subject, experiment, scan=None) is a class to handle the results at the end of any spiders. Instead of having each user writing it's own code and fixing issues in each spider, we created a main class to handle the copy of outputs.

The class will create a folder named after the label of the assessor in the dax upload queue folder and can then add the different resources that need to be uploaded to XNAT.

The inputs for the class are:

- script_name: name of the script you are running. You can get that by using in python the command: sys.argv[0]
- suffix: suffix to add to the proctype for the assessor label. E.g: test for fMRIQA --> fMRIQA_v1_test
- project: project id on XNAT
- subject: subject label on XNAT (use the label and not the ID)
- experiment: session label on XNAT (use the label and not the ID)
- scan: scan ID on XNAT (need to be specify only if the spider is running on a scan)

To create a SpiderProcessHandler, here is an example:

::

  from dax import XnatUtils
  
  end_spider = XnatUtils.SpiderProcessHandler(sys.argv[0], "test", "Project1", "subject1", "session1")

See below for the methods useful for this class.

WARNING: if you use the spider class build in dax, you don't need to worry about this class.

- add_pdf
 - add_pdf(filepath) will copy the file define by filepath to the upload queue folder for dax.
  - end_spider.add_pdf("/Users/dax/Downloads/report.pdf")

- add_snapshots
 - add_snapshots(filepath) will copy the file define by filepath to the upload queue folder for dax.
  - end_spider.add_snapshots("/Users/dax/Downloads/snapshot.png")

- add_file
 - add_file(filepath, resource) will copy the file define by filepath to the upload queue folder for dax. resource defines the name of the folder/resource on XNAT where the filepath will be stored.
  - end_spider.add_file("/Users/dax/Downloads/stats.txt", "Metrics")

- add_folder
 - add_folder(folderpath, resource=None) will copy the folder define by folderpath to the upload queue folder for dax. resource defines the name of the folder/resource on XNAT where all the files in folderpath will be stored. If resource is not define, it will use the name of the folder.
  - end_spider.add_folder("/Users/dax/Downloads/STATS/")
  - end_spider.add_folder("/Users/dax/Downloads/OUTPUTS/", "OUT")

- done
 - done() will finish the process of copying the outputs by generating the flagfile and set the status of the assessor on XNAT to READY_TO_UPLOAD or JOB_FAILED.
  - end_spider.done()

- clean
 - clean(directory) will erase the temporary folder named directory that holds the data on the system.
  - end_spider.clean("/tmp/fMRIQA_test")

--------------
Cached Classes
--------------

The Cached classes (CachedImageSession() / CachedImageScan() / CachedImageAssessor() / CachedResource()) have been created for dax package exclusively. Those class caches the session XML information from XNAT in an object.

There are used to speed the access to pyxnat objects and interact with the database to generate the assessor, check the inputs, and run the tasks on the cluster. You don't need to create an object from those classes.

On the other hand, you might need to use them in your processor files. You can check the code on github in XnatUtils. Some methods have been created to used those classes.

You can find below for each classes the methods implemented.

**CachedImageSession**

- init(intf, proj, subj, sess)
 - To create the object cached session. intf is the interface for XNAT. proj, subj, and sess the information about XNAT object. E.G:

::

  cso = XnatUtils.CachedImageSession(xnat, "ADNI", "1234", "MR_Session1")

- label()
 - To return the label of the session. E.G:

::

  session_label = cso.label()

- get(name)
 - To get the value of a variable for the session. E.G:

::
  
  age = cso.get("age")

- scans()
 - To return the list of cached scans objects for the session. E.G:

::

  csco_list = cso.scans()
  for csco in csco_list:
      # do something

- assessors()
 - To return the list of cached assessors objects for the session. E.G:

::

  cao_list = cso.assessors()
  for cao in cao_list:
      # do something

- info()
 - To return the information listed below for the session as a python dictionaries (keys below, several keys for the same value separated by a slash).
  - ID: session id
  - label/session_label: session label
  - note: session note
  - session_type: session type (xnat type - e.g: mr:sessiondata)
  - project_id/project/project_label: project id
  - original/last_updated: last time the session was updated
  - modality/type: session type (e.g: MR)
  - UID
  - subject_id/subject_ID: subject id
  - subject_label: subject label
  - URI: URI used for this session
 - E.G: sess_info = cso.info()

- resources()
 - To return the list of cached resources objects for the session. E.G:

::

  cro_list = cro.assessors()
  for cro in cro_list:
     # do something

- get_resources()
 - To return the list of cached resources objects info() for the session (list of dictionaries). E.G:

::

  crdo_list = cso.get_resources()
  for crdo in crdo_list:
      # do something

**CachedImageScan**

CachedImageScan has the same methods than CachedImageSession. See below for the one that changed. No method scans() and assessors().

- init(scan_element, parent)
 - To create the object cached scan. scan_element is define in the XML. parent the cached session object that is the parent of the scan. E.G:

::

  csco = XnatUtils.CachedImageScan(scan_element, cso)

- parent()
 - To return the cached session associated to this scan. E.G:

::

  cso = csco.parent()

- info()
 - To return the information listed below for the scan as a python dictionaries (keys below, several keys for the same value separated by a slash).
  - ID/label/scan_label/scan_id: scan id
  - type/scan_type: scan type
  - series_description/scan_description: scan series description
  - quality/scan_quality: scan quality (usable/unusable/questionable)
  - frames/scan_frames: scan frames variable
  - note/scan_note: session note
  - project_id/project_label: project id
  - subject_id: subject id
  - subject_label: subject label
  - session_id: session id
  - session_label: session label
 - E.G: scan_info = csco.info()

**CachedImageAssessor**

CachedImageScan has the same methods than CachedImageSession. See below for the one that changed. get_resources() is now get_out_resources() . No method scans() and assessors().

- init(assr_element, parent)
 - To create the object cached assessor. assr_element is define in the XML. parent the cached session object that is the parent of the assessor. E.G:

::

  cao = XnatUtils.CachedImageAssessor(assr_element, cso)

- parent()
 - To return the cached session associated to this assessor. E.G:

::

  cso = cao.parent()

- info()
 - To return the information listed below for the assessor as a python dictionaries (keys below, several keys for the same value separated by a slash).
  - ID/assessor_id: assessor id
  - label/assessor_label: assessor label
  - xsiType: xsiType for the assessor (proc:genprocdata or fs:fsdata)
  - procstatus: proc status for the assessor
  - qcstatus: QA status for the assessor
  - version: version for the assessor
  - jobid: jobid on the cluster for the assessor
  - jobstartdate
  - memused: memory used in Mb
  - walltimeused
  - jobnode: node where the job is running
  - proctype: proctype for the assessor
  - project_id/project_label: project id
  - subject_id: subject id
  - subject_label: subject label
  - session_id: session id
  - session_label: session label
 - E.G: assessor_info = cao.info()

**CachedResource**

CachedResource has the same methods than CachedImageSession. See below for the one that changed. No method get_resources().

- init(assr_element, parent)
 - To create the object cached assessor. assr_element is define in the XML. parent the cached parent object (session/scan/assessor) that is the parent of the resource. E.G:

::

  cro = XnatUtils.CachedImageAssessor(element, parent)

- parent()
 - To return the cached parent associated to this resource. E.G:

::

  parent = cro.parent()

- info()
 - To return the information listed below for the resource as a python dictionaries (keys below, several keys for the same value separated by a slash).
  - URI: URI for the resource
  - label: resource label, name of the folder on XNAT (e.g: NIFTI)
  - file_size: size of the files
  - file_count: number of files for the resource
  - format: format of the file
  - content: information about the content
 - E.G: resource_info = cro.info()

Methods
~~~~~~~

-----------------------------
Looping through XNAT database
-----------------------------

Instead of looping directly through pyxnat objects (accessing the database for each call), you can use one of the methods below to get a python list of dictionary describing the pyxnat object that you wish (same output as info() in cached classes).

- list_XXX() methods - For each pyxnat object and Xnat level, you can get a list of objects.info(). See below for the list of all of the methods:
 - For project
  - list_projects(intf): get the list of all projects info
  - list_project_resources(intf, project_id): get the resources info for a project
 - For subject
  - list_subjects(intf, project_id=None): get the list of all subjects info (one project or all)
  - list_subject_resources(intf, project_id, subject_id): get the resources info for a specific subject
 - For session
  - list_experiments(intf, project_id=None, subject_id=None): get the list of all sessions info (one project, one subject or all)
  - list_experiment_resources(intf, project_id, subject_id, experiment_id): get the resources info for a specific session
  - list_sessions(intf, project_id=None, subject_id=None): get the list of all sessions info (one project or all). The difference with list_experiments is that this method add more variables to the dictionaries for each session (age/handedness/gender/yob/...)
 - For scan
  - list_scans(intf, project_id, subject_id, experiment_id): get the list of scans for a specific session.
  - list_project_scans(intf, project_id, include_shared=True): get the list of all scans in one project (set include_shared to false if you don't want the shared scans to show up)
  - list_scan_resources(intf, project_id, subject_id, experiment_id, scan_id): get the list of all resources for a specific scan
 - For assessor
  - list_assessors(intf, project_id, subject_id, experiment_id): get the list of assessors for a specific session.
  - list_project_assessors(intf, project_id): get the list of all assessors in one project.
  - list_assessor_out_resources(intf, project_id, subject_id, experiment_id, assessor_id): get the list of all resources for a specific assessor

**How to loop at a XNAT level?**

Now that you know about all the list methods, you can use them to extract a list of python dictionaries to loop through the database at different level and interact with XNAT.

For example, if we want to work on the scans that are "DTI" in our project "ADNI", you will do (those lines of code will be use in the rest of the method for this section):

::

  from dax import XnatUtils
  
  xnat = XnatUtils.get_interface()
  
  list_scans = XnatUtils.list_project_scans(xnat, "ADNI")
  
  # a nice way to filter this list and keep only the scan with the type __dti__:
  list_scans = filter(lambda x: "dti" in x['type'].lower(), list_scans)
  
  for scan_info in list_scans:
      # select the scan like we learned [here](#pyxnat-objects).
      # do something

---------------------
Select Pyxnat Objects
---------------------

Selecting a pyxnat objects like we saw in Pyxnat Objects requires the user to know the URI and remember how to call the select method in Interface.

From the object info dictionary , you can select directly the object by calling a method in dax (like scan_info above. We implemented several ways to select different objects easily.

- get_full_object(intf, obj_dict)
 - To select the object define by the obj_dict. E.G:

::

  scan_obj = XnatUtils.get_full_object(xnat, scan_info)
  
- select_obj(intf, project_id=None, subject_id=None, session_id=None, scan_id=None, assessor_id=None, resource=None)
 - To select the object describe by its arguments. E.G:

::

  project_obj = XnatUtils.select_obj(xnat, project_id="ADNI")
  subject_obj = XnatUtils.select_obj(xnat, project_id="ADNI", subject_id="1234")
  session_obj = XnatUtils.select_obj(xnat, project_id="ADNI", subject_id="1234", session_id="MR_Session1")
  scan_obj = XnatUtils.select_obj(xnat, project_id="ADNI", subject_id="1234", session_id="MR_Session1", scan_id="301")
  assessor = "ADNI-x-1234-x-MR_Session1-x-301-x-fMRIQA"
  assessor_obj = XnatUtils.select_obj(xnat, project_id="ADNI", subject_id="1234", session_id="MR_Session1", assessor_id=assessor)
  # on any level: e.g on the subject for the resource TestResource
  resource_obj = XnatUtils.select_obj(xnat, project_id="ADNI", subject_id="1234", resource="TestResource")

- select_assessor(intf, assessor_label)
 - To select the assessor object describe by the assessor label. Alternative to select_obj for the assessor. E.G:

::

  assessor = "ADNI-x-1234-x-MR_Session1-x-301-x-fMRIQA"
  assessor_obj = XnatUtils.select_assessor(xnat, assessor)

------------------
Download from XNAT
------------------

After selecting the pyxnat object from XNAT, how can we download the files present in the resources?

dax package introduced a range of methods to download those files. See below for each of them that you can use (as always, you can check the code on github to understand how it's working).

Line of code use for each method example:

::

  directory = "/tmp/data/"
  resource_obj = XnatUtils.select_obj(xnat, project_id="ADNI", subject_id="1234", session_id="MR_Session1", scan_id="301", resource="NIFTI")

- download_file_from_obj(directory, resource_obj, fname=None)
 - To download in the directory a file from a resource object. You can specify which file by giving the name of the file. If no name, it will download the biggest file in the resource. E.G:

::

  filepath = XnatUtils.download_file_from_obj(directory, resource_obj)
  
where filepath should be equal to "/tmp/data/biggest_file.nii.gz"

- download_file(directory, resource, project_id=None, subject_id=None, session_id=None, scan_id=None, assessor_id=None, fname=None)
 - To download in the directory a file from a resource by giving each XNAT level label or ID. You can specify which file by giving the name of the file. If no name, it will download the biggest file in the resource. E.G:

::

  filepath = XnatUtils.download_file(directory, "NIFTI", project_id="ADNI", subject_id="1234", session_id="MR_Session1", scan_id="301")
  
where filepath should be equal to "/tmp/data/biggest_file.nii.gz"

- download_files_from_obj(directory, resource_obj)
 - To download in the directory all files from a resource object. E.G:

::

  list_fpaths = XnatUtils.download_files_from_obj(directory, resource_obj)

where list_fpaths should be equal to ["/tmp/data/nifti1.nii.gz", "/tmp/data/nifti2.nii.gz", ...]

- download_files(directory, resource, project_id=None, subject_id=None, session_id=None, scan_id=None, assessor_id=None)
 - To download in the directory all files from a resource by giving each XNAT level label or ID. E.G:

::

  list_fpaths = XnatUtils.download_files(directory, "NIFTI", project_id="ADNI", subject_id="1234", session_id="MR_Session1", scan_id="301")

where list_fpaths should be equal to ["/tmp/data/nifti1.nii.gz", "/tmp/data/nifti2.nii.gz", ...]

- download_biggest_file_from_obj(directory, resource_obj)
 - To download in the directory the biggest file from a resource object. E.G:

::

  filepath = XnatUtils.download_biggest_file_from_obj(directory, resource_obj)

where filepath should be equal to "/tmp/data/nifti3.nii.gz"

- download_biggest_file(directory, resource, project_id=None, subject_id=None, session_id=None, scan_id=None, assessor_id=None)
 - To download in the directory the biggest file from a resource by giving each XNAT level label or ID. E.G:

::

  filepath = XnatUtils.download_biggest_file(directory, "NIFTI", project_id="ADNI", subject_id="1234", session_id="MR_Session1", scan_id="301")

where filepath should be equal to "/tmp/data/nifti3.nii.gz"

- download_from_obj(directory, xnat_obj, resources, all_files=False)
 - To download in the directory the biggest file or all files (all_files=true) from resources for a specific object. E.G:

::

  scan_obj = XnatUtils.select_obj(xnat, project_id="ADNI", subject_id="1234", session_id="MR_Session1", scan_id="301")
  list_filepaths = XnatUtils.download_from_obj(directory, scan_obj, ["NIFTI", "BVAL", "BVEC"])

where list_filepaths should be equal to ["/tmp/data/nifti3.nii.gz", "/tmp/data/nifti3.bval", "/tmp/data/nifti3.bvec"]

- download(directory, resources, project_id=None, subject_id=None, session_id=None, scan_id=None, assessor_id=None, all_files=False)
 - To download in the directory the biggest file or all files (all_files=true) by giving each XNAT level label or ID. E.G:

::
  
  list_filepaths = XnatUtils.download(directory, ["NIFTI", "BVAL", "BVEC"], project_id="ADNI", subject_id="1234", session_id="MR_Session1", scan_id="301")

where list_filepaths should be equal to ["/tmp/data/nifti3.nii.gz", "/tmp/data/nifti3.bval", "/tmp/data/nifti3.bvec"]

--------------
Upload to XNAT
--------------

After selecting the pyxnat object from XNAT, how can you now upload the files that you generated?

dax package introduced a range of methods to upload those files. See below for each of them that you can use (as always, you can check the code on github to understand how it's working).

Line of code use for each method example to upload to an assessor:

::

  assessor = "ADNI-x-1234-x-MR_Session1-x-301-x-fMRIQA"
  assessor_obj = XnatUtils.select_assessor(xnat, assessor)

All the methods have the boolean arguments :

- remove: to remove the same file if it already exists on XNAT for the resource
- removeall: to remove all the files on XNAT for the resource prior to upload the data

and return a boolean status, true if it uploaded successfully and false otherwise.

- upload_file_to_obj(filepath, resource_obj, remove=False, removeall=False, fname=None)
 - To upload the file to a resource object on XNAT. fname="name_you_want" to set a different name on the database for the file. E.G:

:: 

  resource_obj = assessor_obj.out_resource("PDF")
  filepath = "/tmp/data/report.pdf"
  status = XnatUtils.upload_file_to_obj(filepath, resource_obj, remove=True, fname="report_fMRIQA.pdf")

You will see on XNAT in PDF resource the file report_fMRIQA.pdf.

- upload_file(filepath, project_id=None, subject_id=None, session_id=None, scan_id=None, assessor_id=None, resource=None, remove=False, removeall=False, fname=None)
 - To upload the file to a resource by giving each XNAT level label or ID. fname="name_you_want" to set a different name on the database for the file. E.G:

::

  filepath = "/tmp/data/stats.txt"
  status = XnatUtils.upload_file(filepath, project_id="ADNI", subject_id="1234", session_id="MR_Session1", assessor_id=assessor, resource="STATS", remove=True, fname="metrics.txt")

You will see on XNAT in STATS resource the file metrics.txt.

- upload_files_to_obj(filepaths, resource_obj, remove=False, removeall=False)
 - To upload the files define in filepaths to a resource object on XNAT. E.G:

::

  resource_obj = assessor_obj.out_resource("Niftis")
  filepaths = ["/tmp/data/fa.nii.gz", "/tmp/data/md.nii.gz", "/tmp/data/ad.nii.gz", "/tmp/data/rd.nii.gz"]
  status = XnatUtils.upload_files_to_obj(filepaths, resource_obj)

- upload_files(filepaths, project_id=None, subject_id=None, session_id=None, scan_id=None, assessor_id=None, resource=None, remove=False, removeall=False)
 - To upload the files define in filepaths to a resource by giving each XNAT level label or ID. E.G:

::

  filepaths = ["/tmp/data/fa.nii.gz", "/tmp/data/md.nii.gz", "/tmp/data/ad.nii.gz", "/tmp/data/rd.nii.gz"]
  status = XnatUtils.upload_files(filepaths, project_id="ADNI", subject_id="1234", session_id="MR_Session1", assessor_id=assessor, resource="Niftis")

- upload_folder_to_obj(directory, resource_obj, remove=False, removeall=False)
 - To upload all files from a directory to a resource object on XNAT. E.G:

::

  resource_obj = assessor_obj.out_resource("out_images")
  directory = "/tmp/data/output_images/"
  status = XnatUtils.upload_folder_to_obj(directory, resource_obj)

- upload_folder(directory, project_id=None, subject_id=None, session_id=None, scan_id=None, assessor_id=None, resource=None, remove=False, removeall=False)
 - To upload all files from a directory to a resource by giving each XNAT level label or ID. E.G:

::

  directory = "/tmp/data/output_images/"
  status = XnatUtils.upload_folder(directory, project_id="ADNI", subject_id="1234", session_id="MR_Session1", assessor_id=assessor, resource="out_images")

- upload_assessor_snapshots(assessor_obj, original, thumbnail)
 - To upload the snapshots of a PDF to an assessor on XNAT. original is the snapshot original file path. thumbnail is the thumbnail file path for the snapshot. E.G:

::

  original = "/tmp/snapshots/original.png"
  thumbnail = "/tmp/snapshots/thumbnail.png"
  status = XnatUtils.upload_assessor_snapshots(assessor_obj, original, thumbnail)

-------------------------------------------
Methods for Processors using cached classes
-------------------------------------------

When you create your processor file, you will probably use those functions. The processor methods use the cached classes to interact with XNAT. We implemented as well a version using the object from pyxnat directly. See below for the method in XnatUtils.

- is_cscan_unusable(cscan)
 - To check if the cached scan is unusable. E.G:

::

  if not XnatUtils.is_cscan_unusable(cscan):
     # cscan usable, do something

- is_scan_unusable(scan)
 - To check if the scan object is unusable. E.G:

::

  status = XnatUtils.is_scan_unusable(scan_obj)

- is_cscan_good_type(cscan, types_list)
 - To check if the cached scan has a good type meaning if the cached scan type is in the list types_list. E.G:

::

  status = XnatUtils.is_cscan_good_type(cscan, ["T1", "MPRAGE", "t1", "mprage"])

- is_scan_good_type(scan, types_list)
 - To check if the scan object has a good type meaning if the scan type is in the list types_list. E.G:

::

  if XnatUtils.is_scan_good_type(scan_obj, ["T1", "MPRAGE", "t1", "mprage"]):
      #good T1 scan object, do something

- has_resource(cob, resource_label)
 - To check if the cached object possesses a resource called resource_label and if there is at least one file in the resource. E.G:

::

  boolean = XnatUtils.has_resource(scan_obj, "NIFTI)

- is_cassessor_usable(cassr)
 - To check if the cached assessor is usable meaning if it's qcstatus is good or bad or not ready. Returns -1 if failed, 0 if not ready, 1 if passed. E.G:

::

  assr_status = XnatUtils.is_cassessor_usable(cassr)
  if assr_status == 1:
     # assessor ready, let's do something
  elif assr_status == -1:
     # assessor qa failed, let's set the new assessor to no data
  else:
     # nothing

- is_assessor_usable(assessor_obj)
 - To check if the assessor object is usable meaning if it's qcstatus is good or bad or not ready. Returns -1 if failed, 0 if not ready, 1 if passed. E.G:

::

  assr_status = XnatUtils.is_cassessor_usable(assessor_obj)
  if assr_status == 1:
      # assessor ready, let's do something
  elif assr_status == -1:
      # assessor qa failed, let's set the new assessor to no data
  else:
     # nothing

- is_cassessor_good_type(cassr, types_list)
 - To check if the cached assessor has the good type meaning if it's proctype is in the list given in arguments. E.G:

::

  if XnatUtils.is_cassessor_good_type(cassr, ["fMRIQA_v2"]):
      # do something

- is_assessor_good_type(assessor_type, types_list)
 - To check if the assessor object has the good type meaning if it's proctype is in the list given in arguments. E.G:

::

  if XnatUtils.is_assessor_good_type(cassr, ["dtiQA_v2", "dtiQA_v3"]):
      # do something

- get_good_cscans(csess, scantypes)
 - To get the cached scans with a specific scan type from a cached session. E.G:

::

  list_cscans = XnatUtils.get_good_cscans(csess, ["DTI", "DWI"])

- get_good_scans(session_obj, scantypes)
 - To get the scans object with a specific scan type from a pyxnat session object. E.G:

:: 
 
  list_scans_object = XnatUtils.get_good_scans(session_object, ["DTI", "DWI"])

- get_good_cassr(csess, proctypes)
 - To get the cached assessor with a specific proctype from a cached session. E.G:

::

  list_cassr= XnatUtils.get_good_cassr(csess, ["fMRIQA_v2"])

- get_good_assr(session_obj, proctypes)
 - To get the assessor object with a specific proctype from a pyxnat session object. E.G:

::

  list_assessor_obj= XnatUtils.get_good_cassr(session_obj, ["fMRIQA_v2"])

-------------
Other Methods
-------------

Some methods have been implemented in XnatUtils without having any relation to XNAT and pyxnat. Some of the following methods are useful in general.

- clean_directory(directory)
 - To empty the directory, remove any files/folder from the directory. E.G:

::

  XnatUtils.clean_directory("/tmp/temporary_folder/")

- gzip_nii(directory)
 - To gzip all the nifty files that are not gzip in a directory (not in the subdirectories). E.G:

::

  XnatUtils.gzip_nii("/tmp/temporary_folder/")

- ungzip_nii(directory)
 - To unzip all the nifty files that are gzip in a directory (not in the subdirectories). E.G:

::

  XnatUtils.ungzip_nii("/tmp/temporary_folder/")

- makedir(directory, prefix='TempDir')
 - To make a directory. If the directory already exists, creates a new directory with the name: prefix_year_month_day at the date of creation. If the new name for the directory exists, clean the directory. E.G:

::

  XnatUtils.makedir("/tmp/temporary_folder/", prefix="test")

- get_files_in_folder(directory, label='')
 - To get all the files in a the directory (and subfolders as well). label is the path you want to add in front of each path. E.G: for all the files in /Users/Documents/test/data/outputs/

::

  list_files = XnatUtils.get_files_in_folder("data/outputs/", label="/Users/Documents/test/")
