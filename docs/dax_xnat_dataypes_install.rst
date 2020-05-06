Installation of fs:fsData and proc:genProcData
----------------------------------------------

Prerequisites:

-  install an XNAT instance
   https://wiki.xnat.org/documentation/getting-started-with-xnat

On XNAT VM:
^^^^^^^^^^^

1) Make a BACKUP of your $XNAT\_HOME, postgres db, and tomcat deployment

2) Stop tomcat

3) Copy plugins to XNAT

Copy the files dax-plugin-fsData-X.Y.Z.jar and dax-plugin-genProcData-X.Y.Z.jar to ${XNAT_HOME}/plugins

The plugins folder is located in the dax package at the path
dax/misc/xnat-plugins/files. You can download the files from github
repository: https://github.com/VUIIS/dax .

4) Start tomcat and confirm that plugins are installed

ON XNAT webapp:
^^^^^^^^^^^^^^^

1) Log onto XNAT as admin

2) click Administer > Data types

3) click Setup Additional Data Type

4) for fs:fsData (NOTE: the fs:fsData datatype is deprecated. Install only if the need is known to exist)

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

You are now ready to use the two assessor types fs:fsData and
proc:genProcData
