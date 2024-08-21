DAX Processors, version 3
===========

-----
About
-----
DAX pipelines are defined by creating YAML text files. If you are not familiar with YAML, start here:
https://learnxinyminutes.com/docs/yaml/.

A processor YAML file defines the Environment, Inputs, Commands, and Outputs of your pipeline.

Version 3 processors have a number of new options and conveniences.

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
A Basic Example
----------------

.. code-block:: yaml
    
    ---
    procyamlversion: 3.0.0-dev.0                 # Indicates to run as a v3 processor
    
    containers:                                  # Containers we will ref in the command section
      - name: EXAMP                                  # Reference by this name in command section
        path: example_v2.0.0.sif                     # Name/path that is replaced in command section
        source: docker://vuiiscci/example:v2.0.0     # Not used, but good practice to set it
    
    requirements:  # Requirements for the cluster node, substituted into SBATCH section of job template
      walltime: 0-2  # Time to request - SLURM supports the format DAYS-HOURS
      memory: 16G
    
    inputs:
      vars:   # Keyvalues to substitute in the command, for passing static settings
          - param1: param1value
      xnat:
        attrs:  # Values to extract from xnat at the specified level of the current instance
          - varname:  scanID     # Name to be used to dereference later
            object:   scan       # Source, of: project, subject, session, scan, assessor
            attr:     ID         # Name of the field in xnat
            ref:      scan_fmri  # From which object in inputs, referred to by name
        scans:
          - name: scan_fmri       # the name of this scan to dereference later
            types: fMRI_run*      # the scan types to match on the session in XNAT
            nifti: fmri.nii.gz    # Shortcut to download file in NIFTI resource as fmri.nii.gz
            resources:            # To get files in other resources
              - resource: EDAT        # Name of the resource
                fdest: edat.txt       # Download the file as edat.txt
                varname: edat_txt     # Reference for command string substitution
        assessors:
          - name: assr_preproc
            proctypes: preproc-fmri_v2
            resources:
              - {resource: FILTERED_DATA, fdest: filtered_data.nii.gz}
    
    outputs:
      - pdf: report*.pdf        # Matching file uploaded to PDF resource
      - stats: stats.txt        # Matching file uploaded to STATS resource
      - dir: PREPROC            # Matching directory (PREPROC) uploaded to PREPROC resource
      - path: inputpathname     # General purpose for other outputs
        type: DIR                   # Type is FILE or DIR
        resource: RESOURCENAME      # Store it in resource RESOURCENAME
    
    # Available commands are 'singularity_run' and 'singularity_exec'. These include default
    # flags --contain --cleanenv, and mount points for temp space plus INPUTS and OUTPUTS
    command:
      type: singularity_run
      extraopts: []       # Appends to default options for the run command
      container: EXAMP    # Name of the container in the list above
      args: >-
        --fmri_file /INPUTS/fmri.nii.gz
        --filtered_file /INPUTS/filtered_data.nii.gz
        --param1 {param1value}
        --scan_id {scanID}
        --edat_txt /INPUTS/{edat_txt}
    
    description: |
      Example description that gets printed to every PDF created by this processor
      1. step 1 does something cool
      2. step 2 does this other thing
    
    # Specify the job template to use (examples: https://github.com/VUIIS/dax_templates/)
    job_template: job_template_v3.txt


----------------
Parts of the Processor YAML
----------------

--------------------
inputs (required)
--------------------
The **inputs** section defines the files and parameters to be prepared for the pipeline. Currently, the only subsections of inputs supported are **vars** and **xnat**.

The **vars** subsection can store parameters to be passed as pipeline options, such as smoothing kernel size, etc that may be more conveniently coded here to substitute into the command arguments.

The **xnat** section defines the files, directories or values that are extracted from XNAT and passed to the command. Currently, the subsections of **xnat** that are supported are **scans**, **assessors**, **attrs**, and **filters**. Each of these subsections contains an array with a specific set of fields for each item in the array.


xnat scans
---------------
Each **xnat scans** item requires a **types** field. The **types** field is used to match against the scan type attribute on XNAT. The value can be a single string or a comma-separated list. Wildcards are also supported.

The **resources** subsection of each xnat scan should contain a list of resources to download from the matched scan.

**ftype** specifies what type to downloaded from the resource, either *FILE*, *DIR*, or *DIRJ*. *FILE* will download individual files from the resource. *DIR* will download the whole directory from the resource with the hierarchy maintained. *DIRJ* will also download the directory but strips extraneous intermediate directories from the produced path as implemented by the *-j* flag of unzip.

The **varname** field defines tags to be replaced in the **command** string template (see below).

The optional **fmatch** field defines a regular expression to apply to filter the list of filenames in the resource. **fmulti** affects how inputs are handled when there are multiple matching files in a resource. By default, this situation causes an exception, but if **fmulti** is set to *any1*, a single (arbitrary) file is selected from the matching files instead.

By default, any scan that matches will be included as an available input. Several optional settings affect this:

- If **needs_qc** is *True* and **require_usable** is *False* or not specified, assessors that would have a scan as an input will be created, but will not run if the scan is marked *unusable*.

- If **needs_qc** is *True* and **require_usable** is also *True*, assessors that would have a scan as an input will be created, but will not run unless the scan is marked *usable*.

- If **skip_unusable** is *True*, assessors that would have an *unusable* scan as an input will not even be created.

- **keep_multis** may be *all* (the default); *first*; *last*; or an index 1,2,3,... This applies when there are multiple scans in the session that match as possible inputs. Normally all matching scans are used as inputs, multiplying assessors as needed. When *first* is specified, only the first matching scan will be used as an input, reducing the number of assessors built by a factor of the number of matching scans. "First" is defined as alphabetical order by scan ID, cast to lowercase. The exact scan type is not considered; only whether there is a match with the **types** specified.


xnat assessors
---------------
Each xnat assessor item requires a **proctype** field. The **proctype** field is used to match against the assessor proctype attribute on XNAT. The value can be a single string or a comma-separated list. Wildcards are also supported.

Any assessor that matches **proctype** will be included as a possible input. However if **needs_qc** is set to *True*, input assessors with a qcstatus of "Needs QA", "Bad", "Failed", "Poor", or "Do Not Run" will cause the new assessor not to run.

The **resources** subsection of each xnat assessor should contain a list of resources to download from the matched scan.

The **ftype** specifies what type to downloaded from the resource, either *FILE*, *DIR*, or *DIRJ*. *FILE* will download individual files from the resource. *DIR* will download the whole directory from the resource with the hierarchy maintained. *DIRJ* will also download the directory but strips extraneous intermediate directories from the produced path as impelemented by the "-j" flag of unzip.

The **varname** field defines the tag to be replaced in the **command** string template (see below).

Optional fields for a resource are **fmatch** and **fdest**. fmatch defines a regular expression to apply to filter the list of filenames in the resource. The inputs for some containers are expected to be in specific locations with specific filenames. This is accomplished using the **fdest** field. The file or directory gets copied to /INPUTS and renamed to the name specified in **fdest**. 


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

  # Or equivalently
  attrs:
      - {varname: project, object: assessor, attr: project}
        
This will extract the value of the project attribute from the assessor object and replace {project} in the command template.


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

*PDF* and *STATS* outputs, as well as *DIR* type outputs, have shortcuts as shown in the example.


command
--------------------
The **command** field defines a string template that is formatted using the values from **inputs**.

Each tag specified inside curly braces ("{}"") corresponds to a field in the **defaults** input section, or to a **var** field from a resource on an input or to a **varname** in the xnat attrs section.

See the example for explanations of the other fields.


jobtemplate
--------------------
The **jobtemplate** is a text file that contains a template to create a batch job script. 

-------------------
Versioning
-------------------
Processor name and version are parsed from the processor file name, based on the format
<NAME>_v<major.minor.revision>.yaml. <NAME>_v<major> will be used as the proctype.


-------------------
Notes on singularity options
-------------------
The default options are *SINGULARITY_BASEOPTS* in dax/dax/processors_v3.py::

    --contain --cleanenv
    --home $JOBDIR
    --bind $INDIR:/INPUTS
    --bind $OUTDIR:/OUTPUTS
    --bind $JOBDIR:/tmp
    --bind $JOBDIR:/dev/shm

$JOBDIR, $INDIR, $OUTDIR are available at run time, and refer to locations on the filesystem of the node where the job is running.

Singularity has default binds that differ between installations. --contain disables these to prevent cross-talk with the host filesystem. And --cleanenv prevents cross-talk with the host environment. However, with --contain, some spiders will need to have specific temp space on the host attached. E.g. for some versions of Freesurfer, --bind ${INDIR}:/dev/shm. For compiled Matlab spiders, we need to provide --home $INDIR to avoid .mcrCache collisions in temp space when multiple spiders are running. And, some cases may require ${INDIR}:/tmp or /tmp:/tmp. Thus the defaults above.

The *opts* option is available to replace the binds if needed (--cleanenv and --contain are appended regardless)

The entire singularity command is built as::

    singularity <run|exec> <SINGULARITY_BASEOPTS> <extraopts> <container> <args>

or if opts is provided::

    singularity <run|exec> --cleanenv --contain <opts> <extraopts> <container> <args>



---------------------------
Subject-Level Processors
---------------------------

As of version 2.7, dax supports subject-level processors, in addition to session-level. The subject-level
processors can include inputs across multiple sessions within the same subject. In the processor yaml, a subject-level processor is
implied by including the "sessions" level between inputs.xnat and scans/assessors. Each session requires the attribute types.
The types are matched against the XNAT field xnat:imageSessionData/session_type. Currently the match must be exact.

To set the session type of a session, you can use dax/pyxnat:

.. code-block:: python

    xnat.select_session(PROJ, SUBJ, SESS).attrs.set('session_type', SESSTYPE)



Below is an example of a subject-level processor that will include an assessor from two different sessions of session types Baseline and Week12.

.. code-block:: yaml

    ---
    procyamlversion: 3.0.0-dev.0
    containers:
      - name: EMOSTROOP
        path: fmri_emostroop_v2.0.0.sif
        source: docker://bud42/fmri_emostroop:v2
    requirements:
      walltime: 0-2
      memory: 16G
    inputs:
      xnat:
        sessions:
          - types: Baseline 
            assessors:
              - name: assr_emostroop_a
                types: fmri_emostroop_v1
                resources:
                  - resource: PREPROC
                    fmatch: swauFMRI.nii.gz
                    fdest:  swauFMRIa.nii.gz
          - types: Week12
            assessors:
              - name: assr_emostroop_c
                types: fmri_emostroop_v1
                resources:
                  - resource: PREPROC
                    fmatch: swauFMRI.nii.gz
                    fdest:  swauFMRIc.nii.gz
    outputs:
      - dir: PREPROC
      - dir: 1stLEVEL
    command:
      type: singularity_run
      container: EMOSTROOP
      args: BLvsWK12


The assessor will be created under the subject on XNAT, at the same level as a session. The proctype of the assessor will be derived from the filename just like
session-level processors. The XNAT data type of the assessor, or xsiType, will be proc:subjGenProcData (for session-level assessors the type is proc:genprocData).
