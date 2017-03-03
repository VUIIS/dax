/*
 * GENERATED FILE
 * Created on Tue Oct 11 11:22:11 BST 2016
 *
 */
package org.nrg.xdat.model;

import java.util.List;

/**
 * @author XDAT
 *
 */
public interface FsLongfsdataTimepointI {

	public String getXSIType();

	public void toXML(java.io.Writer writer) throws java.lang.Exception;

	/**
	 * @return Returns the imageSessionID.
	 */
	public String getImagesessionid();

	/**
	 * Sets the value for imageSessionID.
	 * @param v Value to Set.
	 */
	public void setImagesessionid(String v);

	/**
	 * @return Returns the label.
	 */
	public String getLabel();

	/**
	 * Sets the value for label.
	 * @param v Value to Set.
	 */
	public void setLabel(String v);

	/**
	 * @return Returns the visit_id.
	 */
	public String getVisitId();

	/**
	 * Sets the value for visit_id.
	 * @param v Value to Set.
	 */
	public void setVisitId(String v);

	/**
	 * @return Returns the project.
	 */
	public String getProject();

	/**
	 * Sets the value for project.
	 * @param v Value to Set.
	 */
	public void setProject(String v);

	/**
	 * @return Returns the fs_longFSData_timepoint_id.
	 */
	public Integer getFsLongfsdataTimepointId();
}
