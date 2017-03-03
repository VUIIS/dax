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
public interface FsLongfsdataI extends XnatSubjectassessordataI {

	public String getXSIType();

	public void toXML(java.io.Writer writer) throws java.lang.Exception;

	/**
	 * @return Returns the fsversion.
	 */
	public String getFsversion();

	/**
	 * Sets the value for fsversion.
	 * @param v Value to Set.
	 */
	public void setFsversion(String v);

	/**
	 * @return Returns the measures/volumetric/ICV.
	 */
	public Double getMeasures_volumetric_icv();

	/**
	 * Sets the value for measures/volumetric/ICV.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_icv(Double v);

	/**
	 * @return Returns the measures/volumetric/lhCortexVol.
	 */
	public Double getMeasures_volumetric_lhcortexvol();

	/**
	 * Sets the value for measures/volumetric/lhCortexVol.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_lhcortexvol(Double v);

	/**
	 * @return Returns the measures/volumetric/rhCortexVol.
	 */
	public Double getMeasures_volumetric_rhcortexvol();

	/**
	 * Sets the value for measures/volumetric/rhCortexVol.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_rhcortexvol(Double v);

	/**
	 * @return Returns the measures/volumetric/CortexVol.
	 */
	public Double getMeasures_volumetric_cortexvol();

	/**
	 * Sets the value for measures/volumetric/CortexVol.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_cortexvol(Double v);

	/**
	 * @return Returns the measures/volumetric/SubCortGrayVol.
	 */
	public Double getMeasures_volumetric_subcortgrayvol();

	/**
	 * Sets the value for measures/volumetric/SubCortGrayVol.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_subcortgrayvol(Double v);

	/**
	 * @return Returns the measures/volumetric/TotalGrayVol.
	 */
	public Double getMeasures_volumetric_totalgrayvol();

	/**
	 * Sets the value for measures/volumetric/TotalGrayVol.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_totalgrayvol(Double v);

	/**
	 * @return Returns the measures/volumetric/SupraTentorialVol.
	 */
	public Double getMeasures_volumetric_supratentorialvol();

	/**
	 * Sets the value for measures/volumetric/SupraTentorialVol.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_supratentorialvol(Double v);

	/**
	 * @return Returns the measures/volumetric/lhCorticalWhiteMatterVol.
	 */
	public Double getMeasures_volumetric_lhcorticalwhitemattervol();

	/**
	 * Sets the value for measures/volumetric/lhCorticalWhiteMatterVol.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_lhcorticalwhitemattervol(Double v);

	/**
	 * @return Returns the measures/volumetric/rhCorticalWhiteMatterVol.
	 */
	public Double getMeasures_volumetric_rhcorticalwhitemattervol();

	/**
	 * Sets the value for measures/volumetric/rhCorticalWhiteMatterVol.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_rhcorticalwhitemattervol(Double v);

	/**
	 * @return Returns the measures/volumetric/CorticalWhiteMatterVol.
	 */
	public Double getMeasures_volumetric_corticalwhitemattervol();

	/**
	 * Sets the value for measures/volumetric/CorticalWhiteMatterVol.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_corticalwhitemattervol(Double v);

	/**
	 * measures/volumetric/regions/region
	 * @return Returns an List of org.nrg.xdat.model.FsLongfsdataRegionI
	 */
	public <A extends org.nrg.xdat.model.FsLongfsdataRegionI> List<A> getMeasures_volumetric_regions_region();

	/**
	 * measures/volumetric/regions/region
	 * @return Returns an List of org.nrg.xdat.model.FsLongfsdataRegionI
	 */
	public <A extends org.nrg.xdat.model.FsLongfsdataRegionI> void addMeasures_volumetric_regions_region(A item) throws Exception;

	/**
	 * measures/surface/hemisphere
	 * @return Returns an List of org.nrg.xdat.model.FsLongfsdataHemisphereI
	 */
	public <A extends org.nrg.xdat.model.FsLongfsdataHemisphereI> List<A> getMeasures_surface_hemisphere();

	/**
	 * measures/surface/hemisphere
	 * @return Returns an List of org.nrg.xdat.model.FsLongfsdataHemisphereI
	 */
	public <A extends org.nrg.xdat.model.FsLongfsdataHemisphereI> void addMeasures_surface_hemisphere(A item) throws Exception;

	/**
	 * timepoints/timepoint
	 * @return Returns an List of org.nrg.xdat.model.FsLongfsdataTimepointI
	 */
	public <A extends org.nrg.xdat.model.FsLongfsdataTimepointI> List<A> getTimepoints_timepoint();

	/**
	 * timepoints/timepoint
	 * @return Returns an List of org.nrg.xdat.model.FsLongfsdataTimepointI
	 */
	public <A extends org.nrg.xdat.model.FsLongfsdataTimepointI> void addTimepoints_timepoint(A item) throws Exception;
}
