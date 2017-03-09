/*
 * GENERATED FILE
 * Created on Tue Oct 11 11:22:11 BST 2016
 *
 */
package org.nrg.xdat.turbine.modules.screens;
import org.apache.turbine.util.RunData;
import org.apache.velocity.context.Context;
import org.nrg.xdat.turbine.modules.screens.SecureReport;

/**
 * @author XDAT
 *
 */
public class XDATScreen_report_fs_automaticSegmentationData extends SecureReport {
	public static org.apache.log4j.Logger logger = org.apache.log4j.Logger.getLogger(XDATScreen_report_fs_automaticSegmentationData.class);
	/* (non-Javadoc)
	 * @see org.nrg.xdat.turbine.modules.screens.SecureReport#finalProcessing(org.apache.turbine.util.RunData, org.apache.velocity.context.Context)
	 */
	public void finalProcessing(RunData data, Context context) {
		try{
			org.nrg.xdat.om.FsAutomaticsegmentationdata om = new org.nrg.xdat.om.FsAutomaticsegmentationdata(item);
			org.nrg.xdat.om.XnatMrsessiondata mr = om.getMrSessionData();
			context.put("om",om);
			System.out.println("Loaded om object (org.nrg.xdat.om.FsAutomaticsegmentationdata) as context parameter 'om'.");
			context.put("mr",mr);
			System.out.println("Loaded mr session object (org.nrg.xdat.om.XnatMrsessiondata) as context parameter 'mr'.");
			context.put("subject",mr.getSubjectData());
			System.out.println("Loaded subject object (org.nrg.xdat.om.XnatSubjectdata) as context parameter 'subject'.");
		} catch(Exception e){}
	}}
