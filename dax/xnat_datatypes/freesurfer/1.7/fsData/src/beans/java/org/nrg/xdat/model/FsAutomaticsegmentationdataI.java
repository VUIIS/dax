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
public interface FsAutomaticsegmentationdataI extends XnatMrassessordataI {

	public String getXSIType();

	public void toXML(java.io.Writer writer) throws java.lang.Exception;

	/**
	 * @return Returns the ICV.
	 */
	public Integer getIcv();

	/**
	 * Sets the value for fs:automaticSegmentationData/ICV.
	 * @param v Value to Set.
	 */
	public void setIcv(Integer v) ;

	/**
	 * regions/region
	 * @return Returns an List of org.nrg.xdat.model.XnatVolumetricregionI
	 */
	public <A extends org.nrg.xdat.model.XnatVolumetricregionI> List<A> getRegions_region();

	/**
	 * regions/region
	 * @return Returns an List of org.nrg.xdat.model.XnatVolumetricregionI
	 */
	public <A extends org.nrg.xdat.model.XnatVolumetricregionI> void addRegions_region(A item) throws Exception;
}
