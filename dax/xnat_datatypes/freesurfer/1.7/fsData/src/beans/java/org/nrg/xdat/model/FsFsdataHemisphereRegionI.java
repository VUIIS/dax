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
public interface FsFsdataHemisphereRegionI {

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
	 * @return Returns the GrayVol.
	 */
	public Double getGrayvol();

	/**
	 * Sets the value for GrayVol.
	 * @param v Value to Set.
	 */
	public void setGrayvol(Double v);

	/**
	 * @return Returns the ThickAvg.
	 */
	public Double getThickavg();

	/**
	 * Sets the value for ThickAvg.
	 * @param v Value to Set.
	 */
	public void setThickavg(Double v);

	/**
	 * @return Returns the ThickStd.
	 */
	public Double getThickstd();

	/**
	 * Sets the value for ThickStd.
	 * @param v Value to Set.
	 */
	public void setThickstd(Double v);

	/**
	 * @return Returns the MeanCurv.
	 */
	public Double getMeancurv();

	/**
	 * Sets the value for MeanCurv.
	 * @param v Value to Set.
	 */
	public void setMeancurv(Double v);

	/**
	 * @return Returns the GausCurv.
	 */
	public Double getGauscurv();

	/**
	 * Sets the value for GausCurv.
	 * @param v Value to Set.
	 */
	public void setGauscurv(Double v);

	/**
	 * @return Returns the FoldInd.
	 */
	public Double getFoldind();

	/**
	 * Sets the value for FoldInd.
	 * @param v Value to Set.
	 */
	public void setFoldind(Double v);

	/**
	 * @return Returns the CurvInd.
	 */
	public Double getCurvind();

	/**
	 * Sets the value for CurvInd.
	 * @param v Value to Set.
	 */
	public void setCurvind(Double v);

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
	 * @return Returns the fs_fsData_surf_region_id.
	 */
	public Integer getFsFsdataSurfRegionId();
}
