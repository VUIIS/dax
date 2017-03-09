/*
 * GENERATED FILE
 * Created on Wed Oct 12 11:10:43 BST 2016
 *
 */
package org.nrg.xdat.model;

import java.util.List;

/**
 * @author XDAT
 *
 */
public interface ProcSubjgenprocdataStudyI {

	public String getXSIType();

	public void toXML(java.io.Writer writer) throws java.lang.Exception;

	/**
	 * @return Returns the id.
	 */
	public String getId();

	/**
	 * Sets the value for id.
	 * @param v Value to Set.
	 */
	public void setId(String v);

	/**
	 * @return Returns the studyUID.
	 */
	public String getStudyuid();

	/**
	 * Sets the value for studyUID.
	 * @param v Value to Set.
	 */
	public void setStudyuid(String v);

	/**
	 * @return Returns the studyDate.
	 */
	public String getStudydate();

	/**
	 * Sets the value for studyDate.
	 * @param v Value to Set.
	 */
	public void setStudydate(String v);

	/**
	 * @return Returns the seriesNumber.
	 */
	public String getSeriesnumber();

	/**
	 * Sets the value for seriesNumber.
	 * @param v Value to Set.
	 */
	public void setSeriesnumber(String v);

	/**
	 * @return Returns the seriesUID.
	 */
	public String getSeriesuid();

	/**
	 * Sets the value for seriesUID.
	 * @param v Value to Set.
	 */
	public void setSeriesuid(String v);

	/**
	 * @return Returns the proc_subjGenProcData_Study_id.
	 */
	public Integer getProcSubjgenprocdataStudyId();
}
