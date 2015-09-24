Tutorial to install the data-types fs:fsData and proc:genProcData to your XNAT installation:
===

Prerequisites: install a XNAT instance.
  Follow https://wiki.xnat.org/display/XNAT16/XNAT+1.6+Installation+Guide to install XNAT

On XNAT VM:
  1) Make a BACKUP of your $XNAT_HOME, postgres db, and tomcat deployment
  2) Stop tomcat
  3) Remove default FreeSurfer files if installed:
    rm -r ${XNAT_HOME}/plugin-resources/project-skeletons/xnat/src/schemas/fs
    rm -r ${XNAT_HOME}/projects/xnat/src/schemas/fs
    rm -r ${XNAT_HOME}/deployments/xnat/src/schemas/fs
    # also need to delete FS files from tomcat webapps directory if already deployed
  
  4) Add modules
    cd ${XNAT_HOME}
    mkdir modules
    # file to copy: fs_module.jar & proc_module.jar
    cp jar_files/*.jar ${XNAT_HOME}/modules/  # copy the jar files to your "modules" folder
  
  5) Run xnat update
    cd ${XNAT_HOME}
    bin/update -Ddeploy=true

  6) Run sql update
    cd ${XNAT_HOME}/deployments/xnat/
    psql -d xnat -f sql/xnat-update.sql

  7) Start tomcat

ON XNAT webpage:
  1) Log onto XNAT as admin
  2) click Administer > Data types
  3) click Setup Additional Data Type
  4) for fs:fsData -- choose fs:fsData
    a) Add to the fields:
      enter "FreeSurfer" in both Singular Name and Plural Name field
      enter "FS" in Code field
    b) Add to "Available Report Actions" delete if you want to be able to delete assessor with the following values:
      Remove Name: delete
      Display Name: Delete
      Grouping: 
      Image: delete.gif
      Popup: 
      Secure Access: delete
      Feature:
      Additional Parameters:
      Sequence: 4
    c) click submit and then accept defaults for subsequent screens
  5) for proc:genProcData
    a) Add to the fields:
      enter "Processing" in both Singular Name and Plural Name field
      enter "Proc" in Code field
    b) Add to "Available Report Actions" delete if you want to be able to delete assessor with the following values:
      Remove Name: delete
      Display Name: Delete
      Grouping: 
      Image: delete.gif
      Popup: 
      Secure Access: delete
      Feature:
      Additional Parameters:
      Sequence: 4
    c) click submit and then accept defaults for subsequent screens

You are now ready to use the two assessors fs:fsData and proc:genProcData
