/*
 * GENERATED FILE
 * Created on Tue Oct 11 11:43:59 BST 2016
 *
 */
package org.nrg.xdat.model;

import java.util.List;

/**
 * @author XDAT
 *
 */
public interface ProcGenprocdataI extends XnatImageassessordataI {

	public String getXSIType();

	public void toXML(java.io.Writer writer) throws java.lang.Exception;

	/**
	 * scans/scan
	 * @return Returns an List of org.nrg.xdat.model.ProcGenprocdataScanI
	 */
	public <A extends org.nrg.xdat.model.ProcGenprocdataScanI> List<A> getScans_scan();

	/**
	 * scans/scan
	 * @return Returns an List of org.nrg.xdat.model.ProcGenprocdataScanI
	 */
	public <A extends org.nrg.xdat.model.ProcGenprocdataScanI> void addScans_scan(A item) throws Exception;

	/**
	 * @return Returns the procstatus.
	 */
	public String getProcstatus();

	/**
	 * Sets the value for procstatus.
	 * @param v Value to Set.
	 */
	public void setProcstatus(String v);

	/**
	 * @return Returns the proctype.
	 */
	public String getProctype();

	/**
	 * Sets the value for proctype.
	 * @param v Value to Set.
	 */
	public void setProctype(String v);

	/**
	 * @return Returns the procversion.
	 */
	public String getProcversion();

	/**
	 * Sets the value for procversion.
	 * @param v Value to Set.
	 */
	public void setProcversion(String v);

	/**
	 * @return Returns the jobid.
	 */
	public String getJobid();

	/**
	 * Sets the value for jobid.
	 * @param v Value to Set.
	 */
	public void setJobid(String v);

	/**
	 * @return Returns the walltimeused.
	 */
	public String getWalltimeused();

	/**
	 * Sets the value for walltimeused.
	 * @param v Value to Set.
	 */
	public void setWalltimeused(String v);

	/**
	 * @return Returns the memusedmb.
	 */
	public Integer getMemusedmb();

	/**
	 * Sets the value for proc:genProcData/memusedmb.
	 * @param v Value to Set.
	 */
	public void setMemusedmb(Integer v) ;

	/**
	 * @return Returns the jobstartdate.
	 */
	public Object getJobstartdate();

	/**
	 * Sets the value for jobstartdate.
	 * @param v Value to Set.
	 */
	public void setJobstartdate(Object v);

	/**
	 * @return Returns the memused.
	 */
	public String getMemused();

	/**
	 * Sets the value for memused.
	 * @param v Value to Set.
	 */
	public void setMemused(String v);

	/**
	 * @return Returns the jobnode.
	 */
	public String getJobnode();

	/**
	 * Sets the value for jobnode.
	 * @param v Value to Set.
	 */
	public void setJobnode(String v);
}
