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
public abstract class AutoFsFsdata extends XnatImageassessordata implements org.nrg.xdat.model.FsFsdataI {
	public static final Logger logger = Logger.getLogger(AutoFsFsdata.class);
	public static final String SCHEMA_ELEMENT_NAME="fs:fsData";

	public AutoFsFsdata(ItemI item)
	{
		super(item);
	}

	public AutoFsFsdata(UserI user)
	{
		super(user);
	}

	/*
	 * @deprecated Use AutoFsFsdata(UserI user)
	 **/
	public AutoFsFsdata(){}

	public AutoFsFsdata(Hashtable properties,UserI user)
	{
		super(properties,user);
	}

	public String getSchemaElementName(){
		return "fs:fsData";
	}
	 private org.nrg.xdat.om.XnatImageassessordata _Imageassessordata =null;

	/**
	 * imageAssessorData
	 * @return org.nrg.xdat.om.XnatImageassessordata
	 */
	public org.nrg.xdat.om.XnatImageassessordata getImageassessordata() {
		try{
			if (_Imageassessordata==null){
				_Imageassessordata=((XnatImageassessordata)org.nrg.xdat.base.BaseElement.GetGeneratedItem((XFTItem)getProperty("imageAssessorData")));
				return _Imageassessordata;
			}else {
				return _Imageassessordata;
			}
		} catch (Exception e1) {return null;}
	}

	/**
	 * Sets the value for imageAssessorData.
	 * @param v Value to Set.
	 */
	public void setImageassessordata(ItemI v) throws Exception{
		_Imageassessordata =null;
		try{
			if (v instanceof XFTItem)
			{
				getItem().setChild(SCHEMA_ELEMENT_NAME + "/imageAssessorData",v,true);
			}else{
				getItem().setChild(SCHEMA_ELEMENT_NAME + "/imageAssessorData",v.getItem(),true);
			}
		} catch (Exception e1) {logger.error(e1);throw e1;}
	}

	/**
	 * imageAssessorData
	 * set org.nrg.xdat.model.XnatImageassessordataI
	 */
	public <A extends org.nrg.xdat.model.XnatImageassessordataI> void setImageassessordata(A item) throws Exception{
	setImageassessordata((ItemI)item);
	}

	/**
	 * Removes the imageAssessorData.
	 * */
	public void removeImageassessordata() {
		_Imageassessordata =null;
		try{
			getItem().removeChild(SCHEMA_ELEMENT_NAME + "/imageAssessorData",0);
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
	 private ArrayList<org.nrg.xdat.om.FsFsdataRegion> _Measures_volumetric_regions_region =null;

	/**
	 * measures/volumetric/regions/region
	 * @return Returns an List of org.nrg.xdat.om.FsFsdataRegion
	 */
	public <A extends org.nrg.xdat.model.FsFsdataRegionI> List<A> getMeasures_volumetric_regions_region() {
		try{
			if (_Measures_volumetric_regions_region==null){
				_Measures_volumetric_regions_region=org.nrg.xdat.base.BaseElement.WrapItems(getChildItems("measures/volumetric/regions/region"));
			}
			return (List<A>) _Measures_volumetric_regions_region;
		} catch (Exception e1) {return (List<A>) new ArrayList<org.nrg.xdat.om.FsFsdataRegion>();}
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
	 * Adds org.nrg.xdat.model.FsFsdataRegionI
	 */
	public <A extends org.nrg.xdat.model.FsFsdataRegionI> void addMeasures_volumetric_regions_region(A item) throws Exception{
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
	 private ArrayList<org.nrg.xdat.om.FsFsdataHemisphere> _Measures_surface_hemisphere =null;

	/**
	 * measures/surface/hemisphere
	 * @return Returns an List of org.nrg.xdat.om.FsFsdataHemisphere
	 */
	public <A extends org.nrg.xdat.model.FsFsdataHemisphereI> List<A> getMeasures_surface_hemisphere() {
		try{
			if (_Measures_surface_hemisphere==null){
				_Measures_surface_hemisphere=org.nrg.xdat.base.BaseElement.WrapItems(getChildItems("measures/surface/hemisphere"));
			}
			return (List<A>) _Measures_surface_hemisphere;
		} catch (Exception e1) {return (List<A>) new ArrayList<org.nrg.xdat.om.FsFsdataHemisphere>();}
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
	 * Adds org.nrg.xdat.model.FsFsdataHemisphereI
	 */
	public <A extends org.nrg.xdat.model.FsFsdataHemisphereI> void addMeasures_surface_hemisphere(A item) throws Exception{
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

	//FIELD

	private String _Procstatus=null;

	/**
	 * @return Returns the procstatus.
	 */
	public String getProcstatus(){
		try{
			if (_Procstatus==null){
				_Procstatus=getStringProperty("procstatus");
				return _Procstatus;
			}else {
				return _Procstatus;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for procstatus.
	 * @param v Value to Set.
	 */
	public void setProcstatus(String v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/procstatus",v);
		_Procstatus=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private String _Proctype=null;

	/**
	 * @return Returns the proctype.
	 */
	public String getProctype(){
		try{
			if (_Proctype==null){
				_Proctype=getStringProperty("proctype");
				return _Proctype;
			}else {
				return _Proctype;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for proctype.
	 * @param v Value to Set.
	 */
	public void setProctype(String v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/proctype",v);
		_Proctype=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private String _Jobid=null;

	/**
	 * @return Returns the jobid.
	 */
	public String getJobid(){
		try{
			if (_Jobid==null){
				_Jobid=getStringProperty("jobid");
				return _Jobid;
			}else {
				return _Jobid;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for jobid.
	 * @param v Value to Set.
	 */
	public void setJobid(String v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/jobid",v);
		_Jobid=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private String _Walltimeused=null;

	/**
	 * @return Returns the walltimeused.
	 */
	public String getWalltimeused(){
		try{
			if (_Walltimeused==null){
				_Walltimeused=getStringProperty("walltimeused");
				return _Walltimeused;
			}else {
				return _Walltimeused;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for walltimeused.
	 * @param v Value to Set.
	 */
	public void setWalltimeused(String v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/walltimeused",v);
		_Walltimeused=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private Object _Jobstartdate=null;

	/**
	 * @return Returns the jobstartdate.
	 */
	public Object getJobstartdate(){
		try{
			if (_Jobstartdate==null){
				_Jobstartdate=getProperty("jobstartdate");
				return _Jobstartdate;
			}else {
				return _Jobstartdate;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for jobstartdate.
	 * @param v Value to Set.
	 */
	public void setJobstartdate(Object v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/jobstartdate",v);
		_Jobstartdate=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private String _Memused=null;

	/**
	 * @return Returns the memused.
	 */
	public String getMemused(){
		try{
			if (_Memused==null){
				_Memused=getStringProperty("memused");
				return _Memused;
			}else {
				return _Memused;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for memused.
	 * @param v Value to Set.
	 */
	public void setMemused(String v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/memused",v);
		_Memused=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private String _Procversion=null;

	/**
	 * @return Returns the procversion.
	 */
	public String getProcversion(){
		try{
			if (_Procversion==null){
				_Procversion=getStringProperty("procversion");
				return _Procversion;
			}else {
				return _Procversion;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for procversion.
	 * @param v Value to Set.
	 */
	public void setProcversion(String v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/procversion",v);
		_Procversion=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private String _Jobnode=null;

	/**
	 * @return Returns the jobnode.
	 */
	public String getJobnode(){
		try{
			if (_Jobnode==null){
				_Jobnode=getStringProperty("jobnode");
				return _Jobnode;
			}else {
				return _Jobnode;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for jobnode.
	 * @param v Value to Set.
	 */
	public void setJobnode(String v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/jobnode",v);
		_Jobnode=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	public static ArrayList<org.nrg.xdat.om.FsFsdata> getAllFsFsdatas(org.nrg.xft.security.UserI user,boolean preLoad)
	{
		ArrayList<org.nrg.xdat.om.FsFsdata> al = new ArrayList<org.nrg.xdat.om.FsFsdata>();

		try{
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetAllItems(SCHEMA_ELEMENT_NAME,user,preLoad);
			al = org.nrg.xdat.base.BaseElement.WrapItems(items.getItems());
		} catch (Exception e) {
			logger.error("",e);
		}

		al.trimToSize();
		return al;
	}

	public static ArrayList<org.nrg.xdat.om.FsFsdata> getFsFsdatasByField(String xmlPath, Object value, org.nrg.xft.security.UserI user,boolean preLoad)
	{
		ArrayList<org.nrg.xdat.om.FsFsdata> al = new ArrayList<org.nrg.xdat.om.FsFsdata>();
		try {
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetItems(xmlPath,value,user,preLoad);
			al = org.nrg.xdat.base.BaseElement.WrapItems(items.getItems());
		} catch (Exception e) {
			logger.error("",e);
		}

		al.trimToSize();
		return al;
	}

	public static ArrayList<org.nrg.xdat.om.FsFsdata> getFsFsdatasByField(org.nrg.xft.search.CriteriaCollection criteria, org.nrg.xft.security.UserI user,boolean preLoad)
	{
		ArrayList<org.nrg.xdat.om.FsFsdata> al = new ArrayList<org.nrg.xdat.om.FsFsdata>();
		try {
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetItems(criteria,user,preLoad);
			al = org.nrg.xdat.base.BaseElement.WrapItems(items.getItems());
		} catch (Exception e) {
			logger.error("",e);
		}

		al.trimToSize();
		return al;
	}

	public static FsFsdata getFsFsdatasById(Object value, org.nrg.xft.security.UserI user,boolean preLoad)
	{
		try {
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetItems("fs:fsData/id",value,user,preLoad);
			ItemI match = items.getFirst();
			if (match!=null)
				return (FsFsdata) org.nrg.xdat.base.BaseElement.GetGeneratedItem(match);
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
	public ArrayList<ResourceFile> getFileResources(String rootPath, boolean preventLoop){
ArrayList<ResourceFile> _return = new ArrayList<ResourceFile>();
	 boolean localLoop = preventLoop;
	        localLoop = preventLoop;
	
	        //imageAssessorData
	        XnatImageassessordata childImageassessordata = (XnatImageassessordata)this.getImageassessordata();
	            if (childImageassessordata!=null){
	              for(ResourceFile rf: ((XnatImageassessordata)childImageassessordata).getFileResources(rootPath, localLoop)) {
	                 rf.setXpath("imageAssessorData[" + ((XnatImageassessordata)childImageassessordata).getItem().getPKString() + "]/" + rf.getXpath());
	                 rf.setXdatPath("imageAssessorData/" + ((XnatImageassessordata)childImageassessordata).getItem().getPKString() + "/" + rf.getXpath());
	                 _return.add(rf);
	              }
	            }
	
	        localLoop = preventLoop;
	
	        //measures/volumetric/regions/region
	        for(org.nrg.xdat.model.FsFsdataRegionI childMeasures_volumetric_regions_region : this.getMeasures_volumetric_regions_region()){
	            if (childMeasures_volumetric_regions_region!=null){
	              for(ResourceFile rf: ((FsFsdataRegion)childMeasures_volumetric_regions_region).getFileResources(rootPath, localLoop)) {
	                 rf.setXpath("measures/volumetric/regions/region[" + ((FsFsdataRegion)childMeasures_volumetric_regions_region).getItem().getPKString() + "]/" + rf.getXpath());
	                 rf.setXdatPath("measures/volumetric/regions/region/" + ((FsFsdataRegion)childMeasures_volumetric_regions_region).getItem().getPKString() + "/" + rf.getXpath());
	                 _return.add(rf);
	              }
	            }
	        }
	
	        localLoop = preventLoop;
	
	        //measures/surface/hemisphere
	        for(org.nrg.xdat.model.FsFsdataHemisphereI childMeasures_surface_hemisphere : this.getMeasures_surface_hemisphere()){
	            if (childMeasures_surface_hemisphere!=null){
	              for(ResourceFile rf: ((FsFsdataHemisphere)childMeasures_surface_hemisphere).getFileResources(rootPath, localLoop)) {
	                 rf.setXpath("measures/surface/hemisphere[" + ((FsFsdataHemisphere)childMeasures_surface_hemisphere).getItem().getPKString() + "]/" + rf.getXpath());
	                 rf.setXdatPath("measures/surface/hemisphere/" + ((FsFsdataHemisphere)childMeasures_surface_hemisphere).getItem().getPKString() + "/" + rf.getXpath());
	                 _return.add(rf);
	              }
	            }
	        }
	
	        localLoop = preventLoop;
	
	return _return;
}
}
