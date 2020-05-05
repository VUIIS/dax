Containerized Image Processing Pipelines
========================================

Table of Contents:
~~~~~~~~~~~~~~~~~~

1.  `dtiQA <#dtiqa>`__
2.  `FMRIQA <#fmriqa>`__
3.  `temporal_lobe <#temporal-lobe>`__
4.  `bedpostx <#bedpostx>`__
5.  `multi_atlas <#multi_atlas>`__

We currently use Docker and Singularity to "containerize" our image processing pipelines. We typically create a docker image first, then create a singularity image with a pull from dockerhub.

-----
dtiQA
-----

- https://hub.docker.com/r/vuiiscci/dtiqa/
- https://singularity-hub.org/accounts/login/?next=/collections/822
- https://github.com/vuiiscci/dtiQA_app

Run Instructions
~~~~~~~~~~~~~~~~

For docker:

::

	sudo docker run --rm \
	--runtime=nvidia \
	-v $(pwd)/INPUTS/:/INPUTS/ \
	-v $(pwd)/OUTPUTS:/OUTPUTS/ \
	--user $(id -u):$(id -g) \
	vuiiscci/dtiqa

For singularity:

::

	singularity run -e \
	--nv \
	-B INPUTS/:/INPUTS \
	-B OUTPUTS/:/OUTPUTS \
	shub://vuiiscci/dtiQA_app

NOTE: You can omit --runtime=nvidia and --nv if you want to run without GPU.

------
FMRIQA
------

- https://hub.docker.com/r/vuiiscci/fmriqa/
- https://singularity-hub.org/accounts/login/?next=/collections/920
- https://github.com/vuiiscci/FMRIQA_app

Run Instructions
~~~~~~~~~~~~~~~~

For docker:

::

	sudo docker run --rm \
	-v $(pwd)/INPUTS/:/INPUTS/ \
	-v $(pwd)/OUTPUTS:/OUTPUTS/ \
	--user $(id -u):$(id -g) \
	vuiiscci/fmriqa

For singularity:

::

	singularity run -e \
	-B INPUTS/:/INPUTS \
	-B OUTPUTS/:/OUTPUTS \
	shub://vuiiscci/FMRIQA_app

-------------
temporal_lobe
-------------

- https://hub.docker.com/r/vuiiscci/temporal_lobe/
- https://singularity-hub.org/accounts/login/?next=/collections/828
- https://github.com/vuiiscci/Temporal_Lobe_app

Run Instructions
~~~~~~~~~~~~~~~~

For docker:

::

	sudo docker run --rm \
	-v $(pwd)/INPUTS/:/INPUTS/ \
	-v $(pwd)/OUTPUTS:/OUTPUTS/ \
	--user $(id -u):$(id -g) \
	vuiiscci/temporal_lobe

For singularity:

:: 

	singularity run -e \
	-B INPUTS/:/INPUTS \
	-B OUTPUTS/:/OUTPUTS \
	shub://vuiiscci/Temporal_Lobe_app

--------
bedpostx
--------

- https://hub.docker.com/r/vuiiscci/bedpostx/
- https://singularity-hub.org/accounts/login/?next=/collections/823
- https://github.com/vuiiscci/bedpostx_app

Run Instructions
~~~~~~~~~~~~~~~~

For docker:

::

	sudo docker run --rm \
	--runtime=nvidia \
	-v $(pwd)/INPUTS/:/INPUTS/ \
	-v $(pwd)/OUTPUTS:/OUTPUTS/ \
	--user $(id -u):$(id -g) \
	vuiiscci/bedpostx

For singularity:

::

	singularity run -e \
	--nv \
	-B INPUTS/:/INPUTS \
	-B OUTPUTS/:/OUTPUTS \
	shub://vuiiscci/bedpostx_app

NOTE: You can omit --runtime=nvidia and --nv if you want to run without GPU.

-----------
multi_atlas
-----------

- https://singularity-hub.org/accounts/login/?next=/collections/734
- https://github.com/vuiiscci/Multi_Atlas_app

Run Instructions
~~~~~~~~~~~~~~~~

For docker:

::

	sudo docker run --rm \
	-v $(pwd)/INPUTS/:/INPUTS/ \
	-v $(pwd)/OUTPUTS:/OUTPUTS/ \
	--user $(id -u):$(id -g) \
	vuiiscci/multi_atlas

For singularity:

	singularity run -e \
	-B INPUTS/:/INPUTS \
	-B OUTPUTS/:/OUTPUTS \
	shub://vuiiscci/Multi_Atlas_app

NOTE: Both dockerhub and singularity-hub are private due to atlases packaged in the containers. You will need to request permission to use this container.
