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
public interface FsLongfsdataHemisphereI {

	public String getXSIType();

	public void toXML(java.io.Writer writer) throws java.lang.Exception;

	/**
	 * @return Returns the NumVert.
	 */
	public Double getNumvert();

	/**
	 * Sets the value for NumVert.
	 * @param v Value to Set.
	 */
	public void setNumvert(Double v);

	/**
	 * @return Returns the SurfArea.
	 */
	public Double getSurfarea();

	/**
	 * Sets the value for SurfArea.
	 * @param v Value to Set.
	 */
	public void setSurfarea(Double v);

	/**
	 * regions/region
	 * @return Returns an List of org.nrg.xdat.model.FsLongfsdataHemisphereRegionI
	 */
	public <A extends org.nrg.xdat.model.FsLongfsdataHemisphereRegionI> List<A> getRegions_region();

	/**
	 * regions/region
	 * @return Returns an List of org.nrg.xdat.model.FsLongfsdataHemisphereRegionI
	 */
	public <A extends org.nrg.xdat.model.FsLongfsdataHemisphereRegionI> void addRegions_region(A item) throws Exception;

	/**
	 * @return Returns the name.
	 */
	public String getName();

	/**
	 * Sets the value for name.
	 * @param v Value to Set.
	 */
	public void setName(String v);

	/**
	 * @return Returns the fs_longFSData_hemisphere_id.
	 */
	public Integer getFsLongfsdataHemisphereId();
}
