DAX Processors
===========

-----
About
-----
DAX pipelines are defined by a creating a YAML text file. If you are not familiar with YAML, start here:
https://learnxinyminutes.com/docs/yaml/


----------------
Processor Repos
----------------
There are several existing processors that can be used without modification. The processors in these
repositories can also provide valuable examples.

https://github.com/bud42/dax-processors

https://github.com/MASILab/yaml_processors


----------------
Overview
----------------
The processor file defines how a script to run a pipeline should be created. DAX will use the processor to generate scripts to be submitted to your cluster as jobs. The script will contain the
commands to download the inputs from XNAT, run the pipeline, and prepare the results to be uploaded back to XNAT (the actual uploading is performed by DAX via "dax upload").

-------------------
Parts of the Processor YAML
-------------------
The primary components of a processor YAML file are:
    inputs
    outputs
    command
    attrs
    jobtemplate

Each of the components is required.


--------------------
inputs
--------------------
xnat

attrs

filters

--------------------
outputs
--------------------
outputs should be a list files or directories that should be uploaded to XNAT.


--------------------
command
--------------------
command should be a string template that is formatted using the values from inputs.


--------------------
attrs
--------------------


--------------------
jobtemplate
--------------------
