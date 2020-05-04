Sending DICOM to Vanderbilt XNAT
================================

1.  `How to Send DICOMs to XNAT <#how-to-send-dicoms-to-xnat>`__
2.  `XNAT and DICOM <#xnat-and-dicom>`__
3.  `Using DicomBrowser <#using-dicombrowser>`__
4.  `Using dcm4che <#using-dcm4che>`__
5.  `Send the DICOMs to XNAT <#send-the-dicoms-to-xnat>`__

--------------------------
How to Send DICOMs to XNAT
--------------------------

XNAT and DICOM
~~~~~~~~~~~~~~

XNAT has a DICOM server and can read DICOM. All the scans from the VUIIS are processed automatically and send to the Pre-Archive with the PI name as a project. You can also send DICOM from your computer to the Pre-Archive.

XNAT will read some of the tags to be able to locate where you want the DICOM to be, meaning which project / subject / experiment. XNAT is looking for specific tags in your dicom header ( http://mindhive.mit.edu/node/1352 ). We will use only the first pass.

Using DicomBrowser
~~~~~~~~~~~~~~~~~~

(See ppt on course 2 about how to send DICOM to XNAT using DicomBrowser)

This method will be useful if you want to send one Session at a time or one scan/DICOM at a time. You can download DicomBrowser for any OS here : http://nrg.wustl.edu/software/dicom-browser/ .

- First step :

Open a DICOM and edit the (0010,4000) tag called "Patient Comments". You need to keep the same syntax (do not include quotes): 

"Project:ProjectIDonXnat;Subject:SubjectIDonXnat;Session:SessionIDonXnat"

with the ProjectIDonXnat, SubjectIDonXnat, and SessionIDonXnat the project / subject / session you want on XNAT.

- Second Step:

Click on File->send and fill the blank in the pop up window with :

::

	Host: xnat.vanderbilt.edu
	Port: 8104
	Remote AE title: VandyXNAT
	Local AE Title: VandyXNAT

and then press "send".

You should see in the next couples of secondes/minutes the session in the Pre-Archive.

Using dcm4che
~~~~~~~~~~~~~

Everything you need is almost in the svn reporsitory (masimatlab/trunk/xnatspiders/dcm4che_tools/).

- Java and Eclipse : getting started

The way to send dicoms to Xnat need a little of hack from your side (not too much), meaning by that that you know how to program in java. If you don't know how to program in general, ask help from people in this project.

Eclipse is a great way to program in java and will compile your file for you. Everything is already in it.

- Create a new project

After downloading and installing it, open eclipse, select a workspace and create a new java project with the name you want ( E.G : dcmTool).

Import the file from masimatlab called SNARLdcmEdit.java with the option import or just open the file and do a copy/paste on a new file .java in your project.

- Configure the java build path

Right mouse click on the file, select Build Path -> Configure Build Path.

Select the tab Libraries.

Select "Add External JARs..." and add all the .jar files in the folder masimatlab/trunk/xnatspiders/dcm4che_tools/dcm4che-2.0.27/lib and masimatlab/trunk/xnatspiders/dcm4che_tools/dcm4che-2.0.27/extlib .

Select "Add External Class Folder..." and add the folder masimatlab/trunk/xnatspiders/dcm4che_tools/dcm4che-2.0.27/etc .

There should be no more errors in your file.

- Change the SNARLdcmEdit.java

You will have to change the file SNARLdcmEdit.java to do what you need.

You need to set the tag (0010,4000) to "Project:"ProjectIDonXnat";Subject:"SubjectIDonXnat";Session:"SessionIDonXnat. Usually you can find the Subject ID or the Session ID or both in the dicom header and you will just need to copy it.

In the file SNARLdcmEdit.jave in your Eclipse java project, find the comments "// Step 2 - edit dicom".

Change the code to write the good sentence for the (0010,4000) tag called "Patient Comments". For example, the following tag will have the value CTONS as a project name, the subject and session name comes from the session name ( The tag PatientID gives the session and from it we have the subjectID in this case : E.G : 003a -> 003 is the subject ID and 003a the session ID).

Now that you have changed the SNARLdcmEdit.java to set the dicom tag (0010,4000), Eclipse will automatically compile the file. You will see a SNARLdcmEdit.class in your bin folder on Eclipse. This SNARLdcmEdit.class will need to be copy everytime you change it to the dcm4che-2.0.27/etc/ .

WARNING : Please, to do so, copy first the dcm4che-2.0.27 from the svn repository on your local home and make change on this copy and not directly in the svn masimatlab. Add the path of this dcm4che copy to your environment variable PATH in your bashrc :

::

	#In your bashrc :
	export PATH=/PathToTheDcm4che-2.0.27Copy:$PATH

- What does this file?

The SNARLdcmEdit.java will open your dicom and edit the (0010,4000) tag to the value you have set. Xnat will do the rest when you send the dicoms.

- How to call this function?

Edit the masimatlab/trunk/xnatspiders/dcm4che_tools/Edit_dcm_new_folder.sh and change the folder "/tmp/ben" to a temporatory folder of your choice where the dicoms will be copied.

With the masimatlab/trunk/xnatspiders/dcm4che_tools/Edit_dcm_new_folder.sh file and after setting your PATH env. variable, use the command line with the full path to the main folder where all your dicoms are :

::

	find /FullPathToTheDicomFolder -name '*.dcm' -exec /FullPath/Edit_dcm_new_folder.sh {}\;

An easy way to check that the script is doing what you need, use DicomBrowser ( http://nrg.wustl.edu/software/dicom-browser/ ) to open a dicom header and check the value of the tag (0010,4000).

Send the DICOMs to XNAT
~~~~~~~~~~~~~~~~~~~~~~~

Create the project on Xnat with the same project ID that the one you have set in the SNARLdcmEdit.java (here "CTONS"). When the previous command is done and all the dicoms header have been changed, call the command line:

::

	dcmsnd XNAT@10.140.10.212:8104 /FullPathTemporatoryFolder/* 

If you look at the prearchive, you will see all your dicom with the subject and session arriving there with the status RECEIVING. When all the status change to READY, you can archive them.
