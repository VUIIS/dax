DAX Manager
===========

Table of Contents:
~~~~~~~~~~~~~~~~~~

1.  `About <#about>`__
2.  `How to set it up <#how-to-set-it-up>`__
3.  `How to add a Module <#how-to-add-a-module>`__
4.  `How to add a Process <#how-to-add-a-process>`__

--------------

-----
About
-----
DAX Manager is a non-required tool hosted in REDCap which allows you to quickly generate settings files that can be
launched with DAX. This alleviates the need to manual write settings files and makes updating scan types, walltimes, etc
a much quicker and streamlined process.

----------------
How to set it up
----------------
The main instrument should be called General and contains a lot of standard variables that are required for DAX to
interface with DAX Manager appropriately. For convenience, a copy of the latest data dictionary has been included
and can be downloaded here for reference. It is suggested to use this version even if you do not plan on running all of the
spiders because it is currently being used in production :file:`files/dax_manager/XNATProjectSettings_DataDictionary_2016-01-21.csv`.

-------------------
How to add a Module
-------------------
Variables used in a module must all start with the text immediately AFTER Module. For example, consider
"Module dcm2nii philips". All of the variables for this module must start with "dcm2nii_philips_". One required variable
is the "on" variable. This variable, again, in the case of "Module dcm2nii philips", would be called "dcm2nii_philips_on".
This is used to check to see if the module related to this record in REDCap should be run for your project or not. It must
also be of the yes/no REDCap type. If you do not have this variable included, you will get errors when you run dax_manager.
The second required variable is the "Module name" variable. In the case of "Module dcm2nii philips", this variable is called
"dcm2nii_philips_mod_name". This relates to the class name of the python module file. This information is stored in the
REDCap "Field Note" (See below).
    .. image:: images/dax_manager/dax_manager_module_field_note.png

This variable must be a REDCap Text Box type (as do all other variables at this point). This must be entered in the
following format: "Default: <Module_Class_Name>". All other variables that are used must also start with the "dcm2nii_philips_"
prefix and must match those of the module init.

Additionally, for the sake of user-friendliness, all variables should use REDCap's branching logic to only appear if the
module is "on". It is important to note that in all cases, the REDCap "Field Label" is not used in any automated fashion,
but should be something obvious to the users.

--------------------
How to add a Process
--------------------
Just like in the case of Modules, Processes follow a close formatting pattern. Similarly, all process variables should
start with the text immediately after "Process ". For this example, consider "Process Multi_Atlas". Just like in the case
of the modules, the first variable should be a REDCap yes/no and should be called "multi_atlas_on". The remainder of the
variables should all be of REDCap type "Text Box". The next required variable is the "Processor Name" variable which must
be labeled with the "<Process Name>_proc_name" suffix. In the case of "Process Multi_Atlas", this is called
"multi_atlas_proc_name". Just like in the case of the Module, the class name of the processor should be entered in the REDCap
Field Note after "Default: ".

There are several other required variables which will be enumerated below (suffix listed first):

#. _suffix_proc - Used to determine what the processor suffix (if any should be)
#. _version - The version of the spider (1.0.0, 2.0.1 etc)
#. _walltime - The amount of walltime to use for the spider when executed on the grid
#. _mem_mb - The amount of ram to request for the job to run. Note this should be in megabytes
#. _scan_types - If writing a ScanProcessor, this is required. If writing a SessionProcessor, this is not required. This, in the case of a ScanProcessor, is used to filter out the scan types that the processor will accept to run the spider on.

Just like in the case of a Module, all variables other than the "on" variable should use REDCap branching logic to only
be visible when the process is "on".


