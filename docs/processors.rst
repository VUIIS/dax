DAX Processors
===========

-----
About
-----
DAX pipelines are defined by creating YAML text files. If you are not familiar with YAML, start here:
https://learnxinyminutes.com/docs/yaml/.

A processor YAML file defines the Environment, Inputs, Commands, and Outputs of your pipeline.

----------------
Processor Repos
----------------
There are several existing processors that can be used without modification. The processors in these
repositories can also provide valuable examples.

https://github.com/VUIIS/dax_yaml_processor_examples

https://github.com/VUIIS/yaml_processors (private, internal use only)

----------------
Overview
----------------
The processor file defines how a script to run a pipeline should be created. DAX will use the processor to generate scripts to be submitted to your cluster as jobs. The script will contain the
commands to download the inputs from XNAT, run the pipeline, and prepare the results to be uploaded back to XNAT (the actual uploading is performed by DAX via *dax upload*).

----------------
A "Simple" Example
----------------
.. Let's start with a minimal example that we'll walk through first. Then we'll cover more advanced topics.

.. code-block:: yaml

  ---
  moreauto: true
  inputs:
    default:
      container_path: MRIQA_v1.0.0.simg
    xnat:
      scans:
        - name: scan_t1
          types: MPRAGE
          resources:
            - resource: NIFTI
              ftype: FILE
              varname: t1_nifti
  outputs:
    - path: stats.txt
      type: FILE
      resource: STATS
    - path: report.pdf
      type: FILE
      resource: PDF
    - path: DATA
      type: DIR
      resource: DATA
  command: >-
    singularity
    run
    --contain
    --cleanenv
    --home $INDIR
    --bind $INDIR:/dev/shm
    --bind $INDIR:/tmp
    --bind $INDIR:/INPUTS
    --bind $OUTDIR:/OUTPUTS
    {container_path}
    --t1_nifti /INPUTS/{t1_nifti}
  attrs:
    walltime: '36:00:00'
    memory: 8192


----------------
Parts of the Processor YAML
----------------

All processor YAML files should start with these two lines:

.. code-block:: yaml

  ---
  moreauto: true


The primary components of a processor YAML file are:

- inputs
- outputs
- command
- attrs

Each of these components is required.

--------------------
inputs
--------------------
The **inputs** section defines the files and parameters to be prepared for the pipeline. Currently, the only subsections of inputs supported are **defaults** and **xnat**.

The **defaults** subsection can contain paths to local resources such as singularity containers, local codebases, local data to be used by the pipeline. It can essentially contain any value 
that needs to be passed directly to the **command** template (see below). 

The **xnat** section defines the files, directories or values that are extracted from XNAT and passed to the command. Currently, the subsections of **xnat** that are supported are **scans**, **assessors**, **attrs**, and **filters**. Each of these subsections contains an array with a specific set of fields for each item in the array.


xnat scans
---------------
Each **xnat scans** item requires a **types** field. The **types** field is used to match against the scan type attribute on XNAT. The value can be a single string or a comma-separated list. Wildcards are also supported.

By default, any scan that matches will be included. You can exclude scans with a quality of *unusable* on XNAT by including the field **needs_qc** with value of *True*. The default is to run anything, i.e. a **needs_qc** value of *False*.
Note that *questionable* is treated the same as *usable*, so they'll always run.

The **resources** subsection of each xnat scan should contain a list of resources to download from the matched scan. Each resource requires fields for **ftype** and **var**. 

**ftype** specifies what type to downloaded from the resource, either *FILE*, *DIR*, or *DIRJ*. *FILE* will download individual files from the resource. *DIR* will download the whole directory from the resource with the hierarchy maintained. *DIRJ* will also download the directory but strips extraneous intermediate directories from the produced path as implemented by the *-j* flag of unzip.

The **var** field defines the tag to be replaced in the **command** string template (see below).

The optional **fmatch** field defines a regular expression to apply to filter the list of filenames in the resource.


xnat assessors
---------------
Each xnat assessor item requires a **proctype** field. The **proctype** field is used to match against the assessor proctype attribute on XNAT. The value can be a single string or a comma-separated list. Wildcards are also supported.

By default, any assessor that matches **proctype** will be included. However if **needs_qc** is set to *True*, assessors with a qcstatus of "Needs QA", "Bad", "Failed", "Poor", or "Do Not Run" will be excluded.

The **resources** subsection of each xnat assessor should contain a list of resources to download from the matched scan. Each resource requires fields for **ftype** and **var**. 

The **ftype** specifies what type to downloaded from the resource, either *FILE*, *DIR*, or *DIRJ*. *FILE* will download individual files from the resource. *DIR* will download the whole directory from the resource with the hierarchy maintained. *DIRJ* will also download the directory but strips extraneous intermediate directories from the produced path as impelemented by the "-j" flag of unzip.

The **var** field defines the tag to be replaced in the **command** string template (see below).

Optional fields for a resource are fmatch, fdest and fcount. fmatch defines a regular expression to apply to filter the list of filenames in the resource. fcount can be used to limit the number of files matched. By default, only 1 file is downloaded.  
The inputs for some containers are expected to be in specific locations with specific filenames. This is accomplished using the **fdest** field. The file or directory gets copied to /INPUTS and renamed to the name specified in **fdest**. 



xnat attrs
---------------
You can evaluate attributes at the subject, session, or scan level. Any fields that are accessible via the XNAT API can be queried. Each **attrs** item should contain a **varname**, **object**, and **attr**.
**varname** specifies the tag to be replaced in the **command** string template. **object** is the XNAT object type to query and can be either *subject*, *session*, or *scan*. **attr** is the XNAT field to query. If the object type is *scan*, then a scan name from the xnat scans section must be included with the **ref** field.

For example:

.. code-block:: yaml

  attrs:
      - varname: project
        object: session
        attr: project

This will extract the value of the project attribute from the session object and replace {project} in the command template.



xnat filters
------------------
**filters** allows you to filter a subset of the cartesian product of the matched scans and assessors. Currently, the only filter implemented is a match filter. It will only create the assessors where the specified list of inputs match. This is used when you want to link a set of assessors that all use the same initial scan as input.

For example:

.. code-block:: yaml

  filters:
      - type: match
        inputs: scan_t1,assr_freesurfer/scan_t1

This will tell DAX to only run this pipeline where the value for scan_t1 and assr_freesurfer/scan_t1 are the same scan.


outputs
--------------------
The **outputs** section defines a list files or directories to be uploaded to XNAT upon completion of the pipeline. Each output item must contain fields **path**, **type**, and **resource**. The **path** value contains the local relative path of the file or directory to be uploaded. The type of the path should either be *FILE* or *DIR*. The **resource** is the name of resource of the assessor created on XNAT where the output is to be uploaded.

For every processor, a *PDF* output with **resource** named PDF is required and must be of type *FILE*.

command
--------------------
The **command** field defines a string template that is formatted using the values from **inputs**.

Each tag specified inside curly braces ("{}"") corresponds to a field in the **defaults** input section, or to a **var** field from a resource on an input or to a **varname** in the xnat attrs section.

Not all **var** must be used.

attrs
--------------------
The **attrs** section defines miscellaneous other attributes including cluster parameters. These values replace tags in the jobtemplate. 


jobtemplate
--------------------
The **jobtemplate** is a text file that contains a template to create a batch job script. 

-------------------
Versioning
-------------------
By default, name and version are parsed from the container file name, based on the format:
<NAME>_v<major.minor.revision>.simg  where<NAME>_v<major> is the proctype.

The YAML file can override these by using any of the top level fields **procversion**, **procname**, and/or **proctype**. **procversion** specifies the major.minor.revision, e.g. *1.0.2*. **procname** specifies the name only without version, e.g. mprage. **proctype** is the name and major version, e.g. *mprage_v1*.
If only **procname** is specified, the version is parsed from the container name.
If only **procversion** is specified, the name is parsed from the container name.
If **proctype** is specified, it will override everything else to determine proctype.


-------------------
Notes on Singularity run options
-------------------
--cleanenv avoids env confusion, and --contain prevents accidentally using code from the host filesystem. However, with --contain, some spiders will need to have specific temp space on the host attached. E.g. for some versions of Freesurfer, --bind ${INDIR}:/dev/shm. For compiled Matlab spiders, we need to provide --home $INDIR to avoid .mcrCache collisions in temp space when multiple spiders are running. And, some cases may require ${INDIR}:/tmp or /tmp:/tmp.

