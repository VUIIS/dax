/*
 * GENERATED FILE
 * Created on Tue Oct 11 11:22:11 BST 2016
 *
 */
package org.nrg.xdat.om.base.auto;
import org.apache.log4j.Logger;
import org.nrg.xft.*;
import org.nrg.xft.security.UserI;
import org.nrg.xdat.om.*;
import org.nrg.xft.utils.ResourceFile;
import org.nrg.xft.exception.*;

import java.util.*;

/**
 * @author XDAT
 *
 *//*
 ******************************** 
 * DO NOT MODIFY THIS FILE
 *
 ********************************/
@SuppressWarnings({"unchecked","rawtypes"})
public abstract class AutoFsLongfsdata extends XnatSubjectassessordata implements org.nrg.xdat.model.FsLongfsdataI {
	public static final Logger logger = Logger.getLogger(AutoFsLongfsdata.class);
	public static final String SCHEMA_ELEMENT_NAME="fs:longFSData";

	public AutoFsLongfsdata(ItemI item)
	{
		super(item);
	}

	public AutoFsLongfsdata(UserI user)
	{
		super(user);
	}

	/*
	 * @deprecated Use AutoFsLongfsdata(UserI user)
	 **/
	public AutoFsLongfsdata(){}

	public AutoFsLongfsdata(Hashtable properties,UserI user)
	{
		super(properties,user);
	}

	public String getSchemaElementName(){
		return "fs:longFSData";
	}
	 private org.nrg.xdat.om.XnatSubjectassessordata _Subjectassessordata =null;

	/**
	 * subjectAssessorData
	 * @return org.nrg.xdat.om.XnatSubjectassessordata
	 */
	public org.nrg.xdat.om.XnatSubjectassessordata getSubjectassessordata() {
		try{
			if (_Subjectassessordata==null){
				_Subjectassessordata=((XnatSubjectassessordata)org.nrg.xdat.base.BaseElement.GetGeneratedItem((XFTItem)getProperty("subjectAssessorData")));
				return _Subjectassessordata;
			}else {
				return _Subjectassessordata;
			}
		} catch (Exception e1) {return null;}
	}

	/**
	 * Sets the value for subjectAssessorData.
	 * @param v Value to Set.
	 */
	public void setSubjectassessordata(ItemI v) throws Exception{
		_Subjectassessordata =null;
		try{
			if (v instanceof XFTItem)
			{
				getItem().setChild(SCHEMA_ELEMENT_NAME + "/subjectAssessorData",v,true);
			}else{
				getItem().setChild(SCHEMA_ELEMENT_NAME + "/subjectAssessorData",v.getItem(),true);
			}
		} catch (Exception e1) {logger.error(e1);throw e1;}
	}

	/**
	 * subjectAssessorData
	 * set org.nrg.xdat.model.XnatSubjectassessordataI
	 */
	public <A extends org.nrg.xdat.model.XnatSubjectassessordataI> void setSubjectassessordata(A item) throws Exception{
	setSubjectassessordata((ItemI)item);
	}

	/**
	 * Removes the subjectAssessorData.
	 * */
	public void removeSubjectassessordata() {
		_Subjectassessordata =null;
		try{
			getItem().removeChild(SCHEMA_ELEMENT_NAME + "/subjectAssessorData",0);
		} catch (FieldNotFoundException e1) {logger.error(e1);}
		catch (java.lang.IndexOutOfBoundsException e1) {logger.error(e1);}
	}

	//FIELD

	private String _Fsversion=null;

	/**
	 * @return Returns the fsversion.
	 */
	public String getFsversion(){
		try{
			if (_Fsversion==null){
				_Fsversion=getStringProperty("fsversion");
				return _Fsversion;
			}else {
				return _Fsversion;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for fsversion.
	 * @param v Value to Set.
	 */
	public void setFsversion(String v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/fsversion",v);
		_Fsversion=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private Double _Measures_volumetric_icv=null;

	/**
	 * @return Returns the measures/volumetric/ICV.
	 */
	public Double getMeasures_volumetric_icv() {
		try{
			if (_Measures_volumetric_icv==null){
				_Measures_volumetric_icv=getDoubleProperty("measures/volumetric/ICV");
				return _Measures_volumetric_icv;
			}else {
				return _Measures_volumetric_icv;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for measures/volumetric/ICV.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_icv(Double v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/measures/volumetric/ICV",v);
		_Measures_volumetric_icv=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private Double _Measures_volumetric_lhcortexvol=null;

	/**
	 * @return Returns the measures/volumetric/lhCortexVol.
	 */
	public Double getMeasures_volumetric_lhcortexvol() {
		try{
			if (_Measures_volumetric_lhcortexvol==null){
				_Measures_volumetric_lhcortexvol=getDoubleProperty("measures/volumetric/lhCortexVol");
				return _Measures_volumetric_lhcortexvol;
			}else {
				return _Measures_volumetric_lhcortexvol;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for measures/volumetric/lhCortexVol.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_lhcortexvol(Double v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/measures/volumetric/lhCortexVol",v);
		_Measures_volumetric_lhcortexvol=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private Double _Measures_volumetric_rhcortexvol=null;

	/**
	 * @return Returns the measures/volumetric/rhCortexVol.
	 */
	public Double getMeasures_volumetric_rhcortexvol() {
		try{
			if (_Measures_volumetric_rhcortexvol==null){
				_Measures_volumetric_rhcortexvol=getDoubleProperty("measures/volumetric/rhCortexVol");
				return _Measures_volumetric_rhcortexvol;
			}else {
				return _Measures_volumetric_rhcortexvol;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for measures/volumetric/rhCortexVol.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_rhcortexvol(Double v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/measures/volumetric/rhCortexVol",v);
		_Measures_volumetric_rhcortexvol=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private Double _Measures_volumetric_cortexvol=null;

	/**
	 * @return Returns the measures/volumetric/CortexVol.
	 */
	public Double getMeasures_volumetric_cortexvol() {
		try{
			if (_Measures_volumetric_cortexvol==null){
				_Measures_volumetric_cortexvol=getDoubleProperty("measures/volumetric/CortexVol");
				return _Measures_volumetric_cortexvol;
			}else {
				return _Measures_volumetric_cortexvol;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for measures/volumetric/CortexVol.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_cortexvol(Double v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/measures/volumetric/CortexVol",v);
		_Measures_volumetric_cortexvol=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private Double _Measures_volumetric_subcortgrayvol=null;

	/**
	 * @return Returns the measures/volumetric/SubCortGrayVol.
	 */
	public Double getMeasures_volumetric_subcortgrayvol() {
		try{
			if (_Measures_volumetric_subcortgrayvol==null){
				_Measures_volumetric_subcortgrayvol=getDoubleProperty("measures/volumetric/SubCortGrayVol");
				return _Measures_volumetric_subcortgrayvol;
			}else {
				return _Measures_volumetric_subcortgrayvol;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for measures/volumetric/SubCortGrayVol.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_subcortgrayvol(Double v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/measures/volumetric/SubCortGrayVol",v);
		_Measures_volumetric_subcortgrayvol=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private Double _Measures_volumetric_totalgrayvol=null;

	/**
	 * @return Returns the measures/volumetric/TotalGrayVol.
	 */
	public Double getMeasures_volumetric_totalgrayvol() {
		try{
			if (_Measures_volumetric_totalgrayvol==null){
				_Measures_volumetric_totalgrayvol=getDoubleProperty("measures/volumetric/TotalGrayVol");
				return _Measures_volumetric_totalgrayvol;
			}else {
				return _Measures_volumetric_totalgrayvol;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for measures/volumetric/TotalGrayVol.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_totalgrayvol(Double v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/measures/volumetric/TotalGrayVol",v);
		_Measures_volumetric_totalgrayvol=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private Double _Measures_volumetric_supratentorialvol=null;

	/**
	 * @return Returns the measures/volumetric/SupraTentorialVol.
	 */
	public Double getMeasures_volumetric_supratentorialvol() {
		try{
			if (_Measures_volumetric_supratentorialvol==null){
				_Measures_volumetric_supratentorialvol=getDoubleProperty("measures/volumetric/SupraTentorialVol");
				return _Measures_volumetric_supratentorialvol;
			}else {
				return _Measures_volumetric_supratentorialvol;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for measures/volumetric/SupraTentorialVol.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_supratentorialvol(Double v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/measures/volumetric/SupraTentorialVol",v);
		_Measures_volumetric_supratentorialvol=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private Double _Measures_volumetric_lhcorticalwhitemattervol=null;

	/**
	 * @return Returns the measures/volumetric/lhCorticalWhiteMatterVol.
	 */
	public Double getMeasures_volumetric_lhcorticalwhitemattervol() {
		try{
			if (_Measures_volumetric_lhcorticalwhitemattervol==null){
				_Measures_volumetric_lhcorticalwhitemattervol=getDoubleProperty("measures/volumetric/lhCorticalWhiteMatterVol");
				return _Measures_volumetric_lhcorticalwhitemattervol;
			}else {
				return _Measures_volumetric_lhcorticalwhitemattervol;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for measures/volumetric/lhCorticalWhiteMatterVol.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_lhcorticalwhitemattervol(Double v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/measures/volumetric/lhCorticalWhiteMatterVol",v);
		_Measures_volumetric_lhcorticalwhitemattervol=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private Double _Measures_volumetric_rhcorticalwhitemattervol=null;

	/**
	 * @return Returns the measures/volumetric/rhCorticalWhiteMatterVol.
	 */
	public Double getMeasures_volumetric_rhcorticalwhitemattervol() {
		try{
			if (_Measures_volumetric_rhcorticalwhitemattervol==null){
				_Measures_volumetric_rhcorticalwhitemattervol=getDoubleProperty("measures/volumetric/rhCorticalWhiteMatterVol");
				return _Measures_volumetric_rhcorticalwhitemattervol;
			}else {
				return _Measures_volumetric_rhcorticalwhitemattervol;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for measures/volumetric/rhCorticalWhiteMatterVol.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_rhcorticalwhitemattervol(Double v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/measures/volumetric/rhCorticalWhiteMatterVol",v);
		_Measures_volumetric_rhcorticalwhitemattervol=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private Double _Measures_volumetric_corticalwhitemattervol=null;

	/**
	 * @return Returns the measures/volumetric/CorticalWhiteMatterVol.
	 */
	public Double getMeasures_volumetric_corticalwhitemattervol() {
		try{
			if (_Measures_volumetric_corticalwhitemattervol==null){
				_Measures_volumetric_corticalwhitemattervol=getDoubleProperty("measures/volumetric/CorticalWhiteMatterVol");
				return _Measures_volumetric_corticalwhitemattervol;
			}else {
				return _Measures_volumetric_corticalwhitemattervol;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for measures/volumetric/CorticalWhiteMatterVol.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_corticalwhitemattervol(Double v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/measures/volumetric/CorticalWhiteMatterVol",v);
		_Measures_volumetric_corticalwhitemattervol=null;
		} catch (Exception e1) {logger.error(e1);}
	}
	 private ArrayList<org.nrg.xdat.om.FsLongfsdataRegion> _Measures_volumetric_regions_region =null;

	/**
	 * measures/volumetric/regions/region
	 * @return Returns an List of org.nrg.xdat.om.FsLongfsdataRegion
	 */
	public <A extends org.nrg.xdat.model.FsLongfsdataRegionI> List<A> getMeasures_volumetric_regions_region() {
		try{
			if (_Measures_volumetric_regions_region==null){
				_Measures_volumetric_regions_region=org.nrg.xdat.base.BaseElement.WrapItems(getChildItems("measures/volumetric/regions/region"));
			}
			return (List<A>) _Measures_volumetric_regions_region;
		} catch (Exception e1) {return (List<A>) new ArrayList<org.nrg.xdat.om.FsLongfsdataRegion>();}
	}

	/**
	 * Sets the value for measures/volumetric/regions/region.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_regions_region(ItemI v) throws Exception{
		_Measures_volumetric_regions_region =null;
		try{
			if (v instanceof XFTItem)
			{
				getItem().setChild(SCHEMA_ELEMENT_NAME + "/measures/volumetric/regions/region",v,true);
			}else{
				getItem().setChild(SCHEMA_ELEMENT_NAME + "/measures/volumetric/regions/region",v.getItem(),true);
			}
		} catch (Exception e1) {logger.error(e1);throw e1;}
	}

	/**
	 * measures/volumetric/regions/region
	 * Adds org.nrg.xdat.model.FsLongfsdataRegionI
	 */
	public <A extends org.nrg.xdat.model.FsLongfsdataRegionI> void addMeasures_volumetric_regions_region(A item) throws Exception{
	setMeasures_volumetric_regions_region((ItemI)item);
	}

	/**
	 * Removes the measures/volumetric/regions/region of the given index.
	 * @param index Index of child to remove.
	 */
	public void removeMeasures_volumetric_regions_region(int index) throws java.lang.IndexOutOfBoundsException {
		_Measures_volumetric_regions_region =null;
		try{
			getItem().removeChild(SCHEMA_ELEMENT_NAME + "/measures/volumetric/regions/region",index);
		} catch (FieldNotFoundException e1) {logger.error(e1);}
	}
	 private ArrayList<org.nrg.xdat.om.FsLongfsdataHemisphere> _Measures_surface_hemisphere =null;

	/**
	 * measures/surface/hemisphere
	 * @return Returns an List of org.nrg.xdat.om.FsLongfsdataHemisphere
	 */
	public <A extends org.nrg.xdat.model.FsLongfsdataHemisphereI> List<A> getMeasures_surface_hemisphere() {
		try{
			if (_Measures_surface_hemisphere==null){
				_Measures_surface_hemisphere=org.nrg.xdat.base.BaseElement.WrapItems(getChildItems("measures/surface/hemisphere"));
			}
			return (List<A>) _Measures_surface_hemisphere;
		} catch (Exception e1) {return (List<A>) new ArrayList<org.nrg.xdat.om.FsLongfsdataHemisphere>();}
	}

	/**
	 * Sets the value for measures/surface/hemisphere.
	 * @param v Value to Set.
	 */
	public void setMeasures_surface_hemisphere(ItemI v) throws Exception{
		_Measures_surface_hemisphere =null;
		try{
			if (v instanceof XFTItem)
			{
				getItem().setChild(SCHEMA_ELEMENT_NAME + "/measures/surface/hemisphere",v,true);
			}else{
				getItem().setChild(SCHEMA_ELEMENT_NAME + "/measures/surface/hemisphere",v.getItem(),true);
			}
		} catch (Exception e1) {logger.error(e1);throw e1;}
	}

	/**
	 * measures/surface/hemisphere
	 * Adds org.nrg.xdat.model.FsLongfsdataHemisphereI
	 */
	public <A extends org.nrg.xdat.model.FsLongfsdataHemisphereI> void addMeasures_surface_hemisphere(A item) throws Exception{
	setMeasures_surface_hemisphere((ItemI)item);
	}

	/**
	 * Removes the measures/surface/hemisphere of the given index.
	 * @param index Index of child to remove.
	 */
	public void removeMeasures_surface_hemisphere(int index) throws java.lang.IndexOutOfBoundsException {
		_Measures_surface_hemisphere =null;
		try{
			getItem().removeChild(SCHEMA_ELEMENT_NAME + "/measures/surface/hemisphere",index);
		} catch (FieldNotFoundException e1) {logger.error(e1);}
	}
	 private ArrayList<org.nrg.xdat.om.FsLongfsdataTimepoint> _Timepoints_timepoint =null;

	/**
	 * timepoints/timepoint
	 * @return Returns an List of org.nrg.xdat.om.FsLongfsdataTimepoint
	 */
	public <A extends org.nrg.xdat.model.FsLongfsdataTimepointI> List<A> getTimepoints_timepoint() {
		try{
			if (_Timepoints_timepoint==null){
				_Timepoints_timepoint=org.nrg.xdat.base.BaseElement.WrapItems(getChildItems("timepoints/timepoint"));
			}
			return (List<A>) _Timepoints_timepoint;
		} catch (Exception e1) {return (List<A>) new ArrayList<org.nrg.xdat.om.FsLongfsdataTimepoint>();}
	}

	/**
	 * Sets the value for timepoints/timepoint.
	 * @param v Value to Set.
	 */
	public void setTimepoints_timepoint(ItemI v) throws Exception{
		_Timepoints_timepoint =null;
		try{
			if (v instanceof XFTItem)
			{
				getItem().setChild(SCHEMA_ELEMENT_NAME + "/timepoints/timepoint",v,true);
			}else{
				getItem().setChild(SCHEMA_ELEMENT_NAME + "/timepoints/timepoint",v.getItem(),true);
			}
		} catch (Exception e1) {logger.error(e1);throw e1;}
	}

	/**
	 * timepoints/timepoint
	 * Adds org.nrg.xdat.model.FsLongfsdataTimepointI
	 */
	public <A extends org.nrg.xdat.model.FsLongfsdataTimepointI> void addTimepoints_timepoint(A item) throws Exception{
	setTimepoints_timepoint((ItemI)item);
	}

	/**
	 * Removes the timepoints/timepoint of the given index.
	 * @param index Index of child to remove.
	 */
	public void removeTimepoints_timepoint(int index) throws java.lang.IndexOutOfBoundsException {
		_Timepoints_timepoint =null;
		try{
			getItem().removeChild(SCHEMA_ELEMENT_NAME + "/timepoints/timepoint",index);
		} catch (FieldNotFoundException e1) {logger.error(e1);}
	}

	public static ArrayList<org.nrg.xdat.om.FsLongfsdata> getAllFsLongfsdatas(org.nrg.xft.security.UserI user,boolean preLoad)
	{
		ArrayList<org.nrg.xdat.om.FsLongfsdata> al = new ArrayList<org.nrg.xdat.om.FsLongfsdata>();

		try{
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetAllItems(SCHEMA_ELEMENT_NAME,user,preLoad);
			al = org.nrg.xdat.base.BaseElement.WrapItems(items.getItems());
		} catch (Exception e) {
			logger.error("",e);
		}

		al.trimToSize();
		return al;
	}

	public static ArrayList<org.nrg.xdat.om.FsLongfsdata> getFsLongfsdatasByField(String xmlPath, Object value, org.nrg.xft.security.UserI user,boolean preLoad)
	{
		ArrayList<org.nrg.xdat.om.FsLongfsdata> al = new ArrayList<org.nrg.xdat.om.FsLongfsdata>();
		try {
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetItems(xmlPath,value,user,preLoad);
			al = org.nrg.xdat.base.BaseElement.WrapItems(items.getItems());
		} catch (Exception e) {
			logger.error("",e);
		}

		al.trimToSize();
		return al;
	}

	public static ArrayList<org.nrg.xdat.om.FsLongfsdata> getFsLongfsdatasByField(org.nrg.xft.search.CriteriaCollection criteria, org.nrg.xft.security.UserI user,boolean preLoad)
	{
		ArrayList<org.nrg.xdat.om.FsLongfsdata> al = new ArrayList<org.nrg.xdat.om.FsLongfsdata>();
		try {
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetItems(criteria,user,preLoad);
			al = org.nrg.xdat.base.BaseElement.WrapItems(items.getItems());
		} catch (Exception e) {
			logger.error("",e);
		}

		al.trimToSize();
		return al;
	}

	public static FsLongfsdata getFsLongfsdatasById(Object value, org.nrg.xft.security.UserI user,boolean preLoad)
	{
		try {
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetItems("fs:longFSData/id",value,user,preLoad);
			ItemI match = items.getFirst();
			if (match!=null)
				return (FsLongfsdata) org.nrg.xdat.base.BaseElement.GetGeneratedItem(match);
			else
				 return null;
		} catch (Exception e) {
			logger.error("",e);
		}

		return null;
	}

	public static ArrayList wrapItems(ArrayList items)
	{
		ArrayList al = new ArrayList();
		al = org.nrg.xdat.base.BaseElement.WrapItems(items);
		al.trimToSize();
		return al;
	}

	public static ArrayList wrapItems(org.nrg.xft.collections.ItemCollection items)
	{
		return wrapItems(items.getItems());
	}

	public org.w3c.dom.Document toJoinedXML() throws Exception
	{
		ArrayList al = new ArrayList();
		al.add(this.getItem());
		al.add(org.nrg.xft.search.ItemSearch.GetItem("xnat:subjectData.ID",this.getItem().getProperty("xnat:mrSessionData.subject_ID"),getItem().getUser(),false));
		al.trimToSize();
		return org.nrg.xft.schema.Wrappers.XMLWrapper.XMLWriter.ItemListToDOM(al);
	}
	public ArrayList<ResourceFile> getFileResources(String rootPath, boolean preventLoop){
ArrayList<ResourceFile> _return = new ArrayList<ResourceFile>();
	 boolean localLoop = preventLoop;
	        localLoop = preventLoop;
	
	        //subjectAssessorData
	        XnatSubjectassessordata childSubjectassessordata = (XnatSubjectassessordata)this.getSubjectassessordata();
	            if (childSubjectassessordata!=null){
	              for(ResourceFile rf: ((XnatSubjectassessordata)childSubjectassessordata).getFileResources(rootPath, localLoop)) {
	                 rf.setXpath("subjectAssessorData[" + ((XnatSubjectassessordata)childSubjectassessordata).getItem().getPKString() + "]/" + rf.getXpath());
	                 rf.setXdatPath("subjectAssessorData/" + ((XnatSubjectassessordata)childSubjectassessordata).getItem().getPKString() + "/" + rf.getXpath());
	                 _return.add(rf);
	              }
	            }
	
	        localLoop = preventLoop;
	
	        //measures/volumetric/regions/region
	        for(org.nrg.xdat.model.FsLongfsdataRegionI childMeasures_volumetric_regions_region : this.getMeasures_volumetric_regions_region()){
	            if (childMeasures_volumetric_regions_region!=null){
	              for(ResourceFile rf: ((FsLongfsdataRegion)childMeasures_volumetric_regions_region).getFileResources(rootPath, localLoop)) {
	                 rf.setXpath("measures/volumetric/regions/region[" + ((FsLongfsdataRegion)childMeasures_volumetric_regions_region).getItem().getPKString() + "]/" + rf.getXpath());
	                 rf.setXdatPath("measures/volumetric/regions/region/" + ((FsLongfsdataRegion)childMeasures_volumetric_regions_region).getItem().getPKString() + "/" + rf.getXpath());
	                 _return.add(rf);
	              }
	            }
	        }
	
	        localLoop = preventLoop;
	
	        //measures/surface/hemisphere
	        for(org.nrg.xdat.model.FsLongfsdataHemisphereI childMeasures_surface_hemisphere : this.getMeasures_surface_hemisphere()){
	            if (childMeasures_surface_hemisphere!=null){
	              for(ResourceFile rf: ((FsLongfsdataHemisphere)childMeasures_surface_hemisphere).getFileResources(rootPath, localLoop)) {
	                 rf.setXpath("measures/surface/hemisphere[" + ((FsLongfsdataHemisphere)childMeasures_surface_hemisphere).getItem().getPKString() + "]/" + rf.getXpath());
	                 rf.setXdatPath("measures/surface/hemisphere/" + ((FsLongfsdataHemisphere)childMeasures_surface_hemisphere).getItem().getPKString() + "/" + rf.getXpath());
	                 _return.add(rf);
	              }
	            }
	        }
	
	        localLoop = preventLoop;
	
	        //timepoints/timepoint
	        for(org.nrg.xdat.model.FsLongfsdataTimepointI childTimepoints_timepoint : this.getTimepoints_timepoint()){
	            if (childTimepoints_timepoint!=null){
	              for(ResourceFile rf: ((FsLongfsdataTimepoint)childTimepoints_timepoint).getFileResources(rootPath, localLoop)) {
	                 rf.setXpath("timepoints/timepoint[" + ((FsLongfsdataTimepoint)childTimepoints_timepoint).getItem().getPKString() + "]/" + rf.getXpath());
	                 rf.setXdatPath("timepoints/timepoint/" + ((FsLongfsdataTimepoint)childTimepoints_timepoint).getItem().getPKString() + "/" + rf.getXpath());
	                 _return.add(rf);
	              }
	            }
	        }
	
	        localLoop = preventLoop;
	
	return _return;
}
}
