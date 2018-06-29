package org.nrg.xnat.archive;

import org.dcm4che2.data.Tag;
import org.dcm4che2.data.DicomObject;

public class VuiisDicomObjectFilter {
	final static String UNKNOWN_SUBJECT  = "UnknownSubject";
	final static String UNKNOWN_PROJECT  = "UnknownProject";

	/*
	 * filter: interprets the PatientName field to find the Project and Subject.
	 * These interepreted values are then written back to the DICOM header so 
     * that XNAT assigns the images to the correct project.
     */
	public static void filter(DicomObject dataset) {
		String project = null;
		String subject = null;
        String session = null;
        String comment = null;
        String vuiis_id = null;
        int uindex = -1;
        
        // Check that PatientComments has not already been set
        if (dataset.contains(Tag.PatientComments) && 
        		dataset.getString(Tag.PatientComments) != null && 
        		!dataset.getString(Tag.PatientComments).trim().equals("")) {
            return;
        }
        
        vuiis_id = dataset.getString(Tag.PatientName);
        uindex = vuiis_id.indexOf('_');
        if (uindex == -1) { // No underscore found
            project = UNKNOWN_PROJECT;
            subject = vuiis_id;
            session = subject;
        } else if(uindex == 0) { //Text only on right side of underscore, nothing on left
            project = UNKNOWN_PROJECT;
            subject = vuiis_id.substring(uindex+1);
            session = subject;
        } else if(uindex >= vuiis_id.length()-1) { //Text only on left side of underscore, nothing on right
            project = vuiis_id.substring(0, uindex).toUpperCase();
            subject = UNKNOWN_SUBJECT;
            session = subject;
        } else { //Text on both sides
            project = vuiis_id.substring(0, uindex).toUpperCase();
            subject = vuiis_id.substring(uindex+1);
            session = subject;
        }

		// Build comment and write to DICOM data
		comment = "Project:"+project+"; Subject:"+subject+"; Session:"+session;
		dataset.putString(Tag.PatientComments,
                          dataset.vrOf(Tag.PatientComments),
                          comment);
    }
};
