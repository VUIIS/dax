Configuring DAX on ACCRE
========================

Table of Contents:
~~~~~~~~~~~~~~~~~~

1.  `Setting up DAX executables <#setting-up-dax-executables>`__
2.  `dax_proxy <#dax-proxy>`__
3.  `dax_setup <#dax-setup>`__
4.  `DAX source <#dax-source>`__

Setting up DAX executables
--------------------------
 
Insert the following into your users bashrc:

::

	export XNAT_USER=<XNAT_USER>
	export XNAT_PASS=<XNAT_PASS>
	export XNAT_HOST=<XNAT_HOST>
	export PATH=/data/mcr/dax_proxy:$PATH

Remember to source your .bashrc. Afterwards, you should be able to call any DAX executables.	
	
dax_proxy
---------

All executables in dax_proxy are simply hard links to the same file:

::

	source /data/mcr/dax_setup/dax_setup.sh
	printf -v str '%q ' "${0##*/}" "$@"
	eval $str
	
This will source dax_setup.sh and then run the commands. This allows a "clean" environment to exist on the user's account.

dax_setup
---------

dax_setup.sh contains the following:

::

	[vuiisccidev@ginko dax_setup]$ cat dax_setup.sh
	ml Anaconda2/4.3.1
	source activate /data/mcr/anaconda/dax/dax
	export PATH=/data/mcr/dax/bin/dax_tools:/data/mcr/dax/bin/old_tools:/data/mcr/dax/bin/freesurfer_tools:/data/mcr/dax/bin/Xnat_tools:/data/mcr/masimatlab/trunk/xnatspiders/python/justinlib_v1_1_0/pythonlib/:/data/mcr/masimatlab/trunk/xnatspiders/python/justinlib_v1_1_0/xnatlib/:$PATH
	ml MATLAB/2017a
	
DAX itself is now contained in an anaconda environment. Since it's stored on /data/mcr, any user account can source it and should have the same version of dax running for consistency.

DAX source
----------

DAX is "installed" through a .pth file in the site-packages of the environment. The path is set to:

-  /data/mcr/dax

This allows us to make modifications to DAX's source code in the event of bug without having to reinstall it, and since its git clone'd, any changes which are made can be committed and pushed back to the dax github. The branch checked out on /data/mcr/dax is currently the "masispider" branch on the dax github.
