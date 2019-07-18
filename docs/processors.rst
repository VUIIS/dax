DAX Processors
===========

-----
About
-----
DAX pipelines are defined by a creating a YAML text file. If you are not familiar with YAML, start here:
https://learnxinyminutes.com/docs/yaml/

The YAML defines the Environment, Inputs, Commands, and Outputs of your pipeline.

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

----------------
A "Simple" Example
----------------

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

All processor YAML files should start with this:

.. code-block:: yaml

  ---
  moreauto: true


The primary components of a processor YAML file are:

- inputs
- outputs
- command
- attrs

Each of these components is required.


inputs
--------------------
The inputs section defines the files and parameters to be prepared for the pipeline. Currently, the only the subsections of inputs supported are default and xnat.

xnat
  scans
       types
       resources 
          var - this should match up with a tag in the command template
          resources:
          - resource: 
            fmatch:
            fcount:
            fdest:
            ftype:

varname: fmri_nifti
   assessors
       proctype

fdest 
The file or directory gets copied to /INPUTS with the name specified in fdest. An ftype of DIRJ strips extraneous intermediate directories from the produced path.

needs_qc
The default is to run anything, False.

If you want to not run if a scan is "unusable", you set needs_qc to True. Note that questionable is treated the same as usable, so they'll always run.

If you want to only run if an assessor is "good", you set needs_qc to True, This will not run anything that's "NEEDS_QA". It will run on Passed, Good, etc.

(Optional) attrs
You can grab attributes at the subject, session, or scan level under inputs.xnat.attrs. Any fields that are accessible via the XNAT API can be queried.


(Optional) filters
This allows you to filter a subset of the cartesian product of the inputs. Currently, the only filter implemented is a match filter. It will only create the assessors where the specified list of inputs match.


outputs
--------------------
The output section defines a list files or directories to be uploaded to XNAT upon completion of the pipeline.

path: 
type:
resource:

A PDF output with resource named PDF is required and must be of type FILE.

command
--------------------
The command field defines a string template that is formatted using the values from inputs.

Each tag specified inside a curly braces {} corresponds to an input.resource.var 

Not all var must be used.

attrs
--------------------
The attrs section defines miscellanous other attributes including cluster parameters. 


jobtemplate
--------------------


-------------------
Versioning
-------------------
By default, name and version are parsed from the container file name, based on the format:
<NAME>_v<major.minor.revision>.simg  where<NAME>_v<major> is the proctype.

The YAML file can override these by using any of these fields: procversion, procname, proctype
procversion specifies the major.minor.revision, e.g. 1.0.2
procname specifies the name only without version, e.g. mprage
proctype is the name and major version, e.g. mprage_v1

If only procname is specified, the version is parsed from the container.
If only procversion is specified, the name is parsed from the container.
If proctype is specified, it will override everything else to determine proctype.


varname: tr
object: scan
attr: tr

-------------------
Notes on Singularity run options
-------------------
--cleanenv avoids env confusion. However we need to avoid --contain for the most part, because it removes access to temp space on the host that many spiders will need, e.g. Freesurfer and /dev/shm. For compiled Matlab spiders (at least), we need to provide --home $INDIR to avoid .mcrCache collisions in temp space when multiple spiders are running.

