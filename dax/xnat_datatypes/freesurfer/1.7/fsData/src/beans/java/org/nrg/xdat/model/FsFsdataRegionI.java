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
public interface FsFsdataRegionI {

	public String getXSIType();

	public void toXML(java.io.Writer writer) throws java.lang.Exception;

	/**
	 * @return Returns the NVoxels.
	 */
	public Double getNvoxels();

	/**
	 * Sets the value for NVoxels.
	 * @param v Value to Set.
	 */
	public void setNvoxels(Double v);

	/**
	 * @return Returns the Volume.
	 */
	public Double getVolume();

	/**
	 * Sets the value for Volume.
	 * @param v Value to Set.
	 */
	public void setVolume(Double v);

	/**
	 * @return Returns the normMean.
	 */
	public Double getNormmean();

	/**
	 * Sets the value for normMean.
	 * @param v Value to Set.
	 */
	public void setNormmean(Double v);

	/**
	 * @return Returns the normStdDev.
	 */
	public Double getNormstddev();

	/**
	 * Sets the value for normStdDev.
	 * @param v Value to Set.
	 */
	public void setNormstddev(Double v);

	/**
	 * @return Returns the normMin.
	 */
	public Double getNormmin();

	/**
	 * Sets the value for normMin.
	 * @param v Value to Set.
	 */
	public void setNormmin(Double v);

	/**
	 * @return Returns the normMax.
	 */
	public Double getNormmax();

	/**
	 * Sets the value for normMax.
	 * @param v Value to Set.
	 */
	public void setNormmax(Double v);

	/**
	 * @return Returns the normRange.
	 */
	public Double getNormrange();

	/**
	 * Sets the value for normRange.
	 * @param v Value to Set.
	 */
	public void setNormrange(Double v);

	/**
	 * @return Returns the SegId.
	 */
	public String getSegid();

	/**
	 * Sets the value for SegId.
	 * @param v Value to Set.
	 */
	public void setSegid(String v);

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
	 * @return Returns the hemisphere.
	 */
	public String getHemisphere();

	/**
	 * Sets the value for hemisphere.
	 * @param v Value to Set.
	 */
	public void setHemisphere(String v);

	/**
	 * @return Returns the fs_fsData_vol_region_id.
	 */
	public Integer getFsFsdataVolRegionId();
}
