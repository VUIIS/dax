Installation of fs:fsData and proc:genProcData
----------------------------------------------

Prerequisites:

-  install a XNAT instance. Follow
   https://wiki.xnat.org/display/XNAT16/XNAT+1.6+Installation+Guide to
   install XNAT

On XNAT VM:
^^^^^^^^^^^

1) Make a BACKUP of your $XNAT\_HOME, postgres db, and tomcat deployment

2) Stop tomcat

3) Remove default FreeSurfer files if installed:

::

    [root@xnat-server ~]#rm -r ${XNAT_HOME}/plugin-resources/project-skeletons/xnat/src/schemas/fs
    [root@xnat-server ~]#rm -r ${XNAT_HOME}/projects/xnat/src/schemas/fs
    [root@xnat-server ~]#rm -r ${XNAT_HOME}/deployments/xnat/src/schemas/fs

You also need to delete FS files from tomcat webapps directory if
already deployed.

4) Add modules

::

    [root@xnat-server ~]#cd ${XNAT_HOME}
    [root@xnat-server ~]#mkdir modules

Copy the files from dax/xnat\_modules/jar\_files: fs\_module.jar &
proc\_module.jar :sub:`:sub:`:sub:`~``` [root@xnat-server ~]#cp
fs\_module.jar
:math:`{XNAT_HOME}/modules/ [root@xnat-server ~]#cp proc_module.jar `\ {XNAT\_HOME}/modules/
:sub:`:sub:`:sub:`~```

The jar\_files folder is located in dax package at the path
dax/dax/xnat\_modules/jar\_files. You can download the files from github
repository: https://github.com/VUIIS/dax .

5) Run xnat update

::

    [root@xnat-server ~]#cd ${XNAT_HOME}
    [root@xnat-server ~]#bin/update.sh -Ddeploy=true

6) Run sql update

::

    [root@xnat-server ~]# cd ${XNAT_HOME}/deployments/[xnat.project.name]/
    [root@xnat-server ~]# psql -f sql/[xnat.project.name]-update.sql -U [db-user] [db-name]

7) Start tomcat

ON XNAT webapp:
^^^^^^^^^^^^^^^

1) Log onto XNAT as admin

2) click Administer > Data types

3) click Setup Additional Data Type

4) for fs:fsData

4.a) select fs:fsData and valid without adding anything at first.

4.b) Come back to the new types and edit the fields:

::

      enter "FreeSurfer" in both Singular Name and Plural Name field
      enter "FS" in Code field

4.c) Edit the "Available Report Actions" by adding delete if you want to
be able to delete assessor with the following values:

::

      Remove Name: delete
      Display Name: Delete
      Grouping: 
      Image: delete.gif
      Popup: 
      Secure Access: delete
      Feature:
      Additional Parameters:
      Sequence: 4

4.d) click submit and then accept defaults for subsequent screens

5) for proc:genProcData

5.a) select proc:genProcData and valid without adding anything at first.

5.b) Come back to the new types and edit the fields:

::

      enter "Processing" in both Singular Name and Plural Name field
      enter "Proc" in Code field

5.c) Edit the "Available Report Actions" by adding delete if you want to
be able to delete assessor with the following values:

::

      Remove Name: delete
      Display Name: Delete
      Grouping: 
      Image: delete.gif
      Popup: 
      Secure Access: delete
      Feature:
      Additional Parameters:
      Sequence: 4

5.d) click submit and then accept defaults for subsequent screens

You are now ready to use the two assessors fs:fsData and
proc:genProcData
