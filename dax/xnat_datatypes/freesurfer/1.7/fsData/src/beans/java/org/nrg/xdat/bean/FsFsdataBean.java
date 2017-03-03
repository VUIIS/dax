/*
 * GENERATED FILE
 * Created on Tue Oct 11 11:22:11 BST 2016
 *
 */
package org.nrg.xdat.bean;
import org.apache.log4j.Logger;
import org.nrg.xdat.bean.base.BaseElement;

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
public class FsFsdataBean extends XnatImageassessordataBean implements java.io.Serializable, org.nrg.xdat.model.FsFsdataI {
	public static final Logger logger = Logger.getLogger(FsFsdataBean.class);
	public static final String SCHEMA_ELEMENT_NAME="fs:fsData";

	public String getSchemaElementName(){
		return "fsData";
	}

	public String getFullSchemaElementName(){
		return "fs:fsData";
	}

	//FIELD

	private String _Fsversion=null;

	/**
	 * @return Returns the fsversion.
	 */
	public String getFsversion(){
		return _Fsversion;
	}

	/**
	 * Sets the value for fsversion.
	 * @param v Value to Set.
	 */
	public void setFsversion(String v){
		_Fsversion=v;
	}

	//FIELD

	private Double _Measures_volumetric_icv=null;

	/**
	 * @return Returns the measures/volumetric/ICV.
	 */
	public Double getMeasures_volumetric_icv() {
		return _Measures_volumetric_icv;
	}

	/**
	 * Sets the value for measures/volumetric/ICV.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_icv(Double v){
		_Measures_volumetric_icv=v;
	}

	/**
	 * Sets the value for measures/volumetric/ICV.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_icv(String v)  {
		_Measures_volumetric_icv=formatDouble(v);
	}

	//FIELD

	private Double _Measures_volumetric_lhcortexvol=null;

	/**
	 * @return Returns the measures/volumetric/lhCortexVol.
	 */
	public Double getMeasures_volumetric_lhcortexvol() {
		return _Measures_volumetric_lhcortexvol;
	}

	/**
	 * Sets the value for measures/volumetric/lhCortexVol.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_lhcortexvol(Double v){
		_Measures_volumetric_lhcortexvol=v;
	}

	/**
	 * Sets the value for measures/volumetric/lhCortexVol.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_lhcortexvol(String v)  {
		_Measures_volumetric_lhcortexvol=formatDouble(v);
	}

	//FIELD

	private Double _Measures_volumetric_rhcortexvol=null;

	/**
	 * @return Returns the measures/volumetric/rhCortexVol.
	 */
	public Double getMeasures_volumetric_rhcortexvol() {
		return _Measures_volumetric_rhcortexvol;
	}

	/**
	 * Sets the value for measures/volumetric/rhCortexVol.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_rhcortexvol(Double v){
		_Measures_volumetric_rhcortexvol=v;
	}

	/**
	 * Sets the value for measures/volumetric/rhCortexVol.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_rhcortexvol(String v)  {
		_Measures_volumetric_rhcortexvol=formatDouble(v);
	}

	//FIELD

	private Double _Measures_volumetric_cortexvol=null;

	/**
	 * @return Returns the measures/volumetric/CortexVol.
	 */
	public Double getMeasures_volumetric_cortexvol() {
		return _Measures_volumetric_cortexvol;
	}

	/**
	 * Sets the value for measures/volumetric/CortexVol.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_cortexvol(Double v){
		_Measures_volumetric_cortexvol=v;
	}

	/**
	 * Sets the value for measures/volumetric/CortexVol.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_cortexvol(String v)  {
		_Measures_volumetric_cortexvol=formatDouble(v);
	}

	//FIELD

	private Double _Measures_volumetric_subcortgrayvol=null;

	/**
	 * @return Returns the measures/volumetric/SubCortGrayVol.
	 */
	public Double getMeasures_volumetric_subcortgrayvol() {
		return _Measures_volumetric_subcortgrayvol;
	}

	/**
	 * Sets the value for measures/volumetric/SubCortGrayVol.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_subcortgrayvol(Double v){
		_Measures_volumetric_subcortgrayvol=v;
	}

	/**
	 * Sets the value for measures/volumetric/SubCortGrayVol.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_subcortgrayvol(String v)  {
		_Measures_volumetric_subcortgrayvol=formatDouble(v);
	}

	//FIELD

	private Double _Measures_volumetric_totalgrayvol=null;

	/**
	 * @return Returns the measures/volumetric/TotalGrayVol.
	 */
	public Double getMeasures_volumetric_totalgrayvol() {
		return _Measures_volumetric_totalgrayvol;
	}

	/**
	 * Sets the value for measures/volumetric/TotalGrayVol.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_totalgrayvol(Double v){
		_Measures_volumetric_totalgrayvol=v;
	}

	/**
	 * Sets the value for measures/volumetric/TotalGrayVol.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_totalgrayvol(String v)  {
		_Measures_volumetric_totalgrayvol=formatDouble(v);
	}

	//FIELD

	private Double _Measures_volumetric_supratentorialvol=null;

	/**
	 * @return Returns the measures/volumetric/SupraTentorialVol.
	 */
	public Double getMeasures_volumetric_supratentorialvol() {
		return _Measures_volumetric_supratentorialvol;
	}

	/**
	 * Sets the value for measures/volumetric/SupraTentorialVol.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_supratentorialvol(Double v){
		_Measures_volumetric_supratentorialvol=v;
	}

	/**
	 * Sets the value for measures/volumetric/SupraTentorialVol.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_supratentorialvol(String v)  {
		_Measures_volumetric_supratentorialvol=formatDouble(v);
	}

	//FIELD

	private Double _Measures_volumetric_lhcorticalwhitemattervol=null;

	/**
	 * @return Returns the measures/volumetric/lhCorticalWhiteMatterVol.
	 */
	public Double getMeasures_volumetric_lhcorticalwhitemattervol() {
		return _Measures_volumetric_lhcorticalwhitemattervol;
	}

	/**
	 * Sets the value for measures/volumetric/lhCorticalWhiteMatterVol.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_lhcorticalwhitemattervol(Double v){
		_Measures_volumetric_lhcorticalwhitemattervol=v;
	}

	/**
	 * Sets the value for measures/volumetric/lhCorticalWhiteMatterVol.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_lhcorticalwhitemattervol(String v)  {
		_Measures_volumetric_lhcorticalwhitemattervol=formatDouble(v);
	}

	//FIELD

	private Double _Measures_volumetric_rhcorticalwhitemattervol=null;

	/**
	 * @return Returns the measures/volumetric/rhCorticalWhiteMatterVol.
	 */
	public Double getMeasures_volumetric_rhcorticalwhitemattervol() {
		return _Measures_volumetric_rhcorticalwhitemattervol;
	}

	/**
	 * Sets the value for measures/volumetric/rhCorticalWhiteMatterVol.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_rhcorticalwhitemattervol(Double v){
		_Measures_volumetric_rhcorticalwhitemattervol=v;
	}

	/**
	 * Sets the value for measures/volumetric/rhCorticalWhiteMatterVol.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_rhcorticalwhitemattervol(String v)  {
		_Measures_volumetric_rhcorticalwhitemattervol=formatDouble(v);
	}

	//FIELD

	private Double _Measures_volumetric_corticalwhitemattervol=null;

	/**
	 * @return Returns the measures/volumetric/CorticalWhiteMatterVol.
	 */
	public Double getMeasures_volumetric_corticalwhitemattervol() {
		return _Measures_volumetric_corticalwhitemattervol;
	}

	/**
	 * Sets the value for measures/volumetric/CorticalWhiteMatterVol.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_corticalwhitemattervol(Double v){
		_Measures_volumetric_corticalwhitemattervol=v;
	}

	/**
	 * Sets the value for measures/volumetric/CorticalWhiteMatterVol.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_corticalwhitemattervol(String v)  {
		_Measures_volumetric_corticalwhitemattervol=formatDouble(v);
	}
	 private List<org.nrg.xdat.bean.FsFsdataRegionBean> _Measures_volumetric_regions_region =new ArrayList<org.nrg.xdat.bean.FsFsdataRegionBean>();

	/**
	 * measures/volumetric/regions/region
	 * @return Returns an List of org.nrg.xdat.bean.FsFsdataRegionBean
	 */
	public <A extends org.nrg.xdat.model.FsFsdataRegionI> List<A> getMeasures_volumetric_regions_region() {
		return (List<A>) _Measures_volumetric_regions_region;
	}

	/**
	 * Sets the value for measures/volumetric/regions/region.
	 * @param v Value to Set.
	 */
	public void setMeasures_volumetric_regions_region(ArrayList<org.nrg.xdat.bean.FsFsdataRegionBean> v){
		_Measures_volumetric_regions_region=v;
	}

	/**
	 * Adds the value for measures/volumetric/regions/region.
	 * @param v Value to Set.
	 */
	public void addMeasures_volumetric_regions_region(org.nrg.xdat.bean.FsFsdataRegionBean v){
		_Measures_volumetric_regions_region.add(v);
	}

	/**
	 * measures/volumetric/regions/region
	 * Adds org.nrg.xdat.model.FsFsdataRegionI
	 */
	public <A extends org.nrg.xdat.model.FsFsdataRegionI> void addMeasures_volumetric_regions_region(A item) throws Exception{
	_Measures_volumetric_regions_region.add((org.nrg.xdat.bean.FsFsdataRegionBean)item);
	}

	/**
	 * Adds the value for measures/volumetric/regions/region.
	 * @param v Value to Set.
	 */
	public void addMeasures_volumetric_regions_region(Object v){
		if (v instanceof org.nrg.xdat.bean.FsFsdataRegionBean)
			_Measures_volumetric_regions_region.add((org.nrg.xdat.bean.FsFsdataRegionBean)v);
		else
			throw new IllegalArgumentException("Must be a valid org.nrg.xdat.bean.FsFsdataRegionBean");
	}
	 private List<org.nrg.xdat.bean.FsFsdataHemisphereBean> _Measures_surface_hemisphere =new ArrayList<org.nrg.xdat.bean.FsFsdataHemisphereBean>();

	/**
	 * measures/surface/hemisphere
	 * @return Returns an List of org.nrg.xdat.bean.FsFsdataHemisphereBean
	 */
	public <A extends org.nrg.xdat.model.FsFsdataHemisphereI> List<A> getMeasures_surface_hemisphere() {
		return (List<A>) _Measures_surface_hemisphere;
	}

	/**
	 * Sets the value for measures/surface/hemisphere.
	 * @param v Value to Set.
	 */
	public void setMeasures_surface_hemisphere(ArrayList<org.nrg.xdat.bean.FsFsdataHemisphereBean> v){
		_Measures_surface_hemisphere=v;
	}

	/**
	 * Adds the value for measures/surface/hemisphere.
	 * @param v Value to Set.
	 */
	public void addMeasures_surface_hemisphere(org.nrg.xdat.bean.FsFsdataHemisphereBean v){
		_Measures_surface_hemisphere.add(v);
	}

	/**
	 * measures/surface/hemisphere
	 * Adds org.nrg.xdat.model.FsFsdataHemisphereI
	 */
	public <A extends org.nrg.xdat.model.FsFsdataHemisphereI> void addMeasures_surface_hemisphere(A item) throws Exception{
	_Measures_surface_hemisphere.add((org.nrg.xdat.bean.FsFsdataHemisphereBean)item);
	}

	/**
	 * Adds the value for measures/surface/hemisphere.
	 * @param v Value to Set.
	 */
	public void addMeasures_surface_hemisphere(Object v){
		if (v instanceof org.nrg.xdat.bean.FsFsdataHemisphereBean)
			_Measures_surface_hemisphere.add((org.nrg.xdat.bean.FsFsdataHemisphereBean)v);
		else
			throw new IllegalArgumentException("Must be a valid org.nrg.xdat.bean.FsFsdataHemisphereBean");
	}

	//FIELD

	private String _Procstatus=null;

	/**
	 * @return Returns the procstatus.
	 */
	public String getProcstatus(){
		return _Procstatus;
	}

	/**
	 * Sets the value for procstatus.
	 * @param v Value to Set.
	 */
	public void setProcstatus(String v){
		_Procstatus=v;
	}

	//FIELD

	private String _Proctype=null;

	/**
	 * @return Returns the proctype.
	 */
	public String getProctype(){
		return _Proctype;
	}

	/**
	 * Sets the value for proctype.
	 * @param v Value to Set.
	 */
	public void setProctype(String v){
		_Proctype=v;
	}

	//FIELD

	private String _Jobid=null;

	/**
	 * @return Returns the jobid.
	 */
	public String getJobid(){
		return _Jobid;
	}

	/**
	 * Sets the value for jobid.
	 * @param v Value to Set.
	 */
	public void setJobid(String v){
		_Jobid=v;
	}

	//FIELD

	private String _Walltimeused=null;

	/**
	 * @return Returns the walltimeused.
	 */
	public String getWalltimeused(){
		return _Walltimeused;
	}

	/**
	 * Sets the value for walltimeused.
	 * @param v Value to Set.
	 */
	public void setWalltimeused(String v){
		_Walltimeused=v;
	}

	//FIELD

	private Date _Jobstartdate=null;

	/**
	 * @return Returns the jobstartdate.
	 */
	public Date getJobstartdate(){
		return _Jobstartdate;
	}

	/**
	 * Sets the value for jobstartdate.
	 * @param v Value to Set.
	 */
	public void setJobstartdate(Date v){
		_Jobstartdate=v;
	}

	/**
	 * Sets the value for jobstartdate.
	 * @param v Value to Set.
	 */
	public void setJobstartdate(Object v){
		throw new IllegalArgumentException();
	}

	/**
	 * Sets the value for jobstartdate.
	 * @param v Value to Set.
	 */
	public void setJobstartdate(String v)  {
		_Jobstartdate=formatDate(v);
	}

	//FIELD

	private String _Memused=null;

	/**
	 * @return Returns the memused.
	 */
	public String getMemused(){
		return _Memused;
	}

	/**
	 * Sets the value for memused.
	 * @param v Value to Set.
	 */
	public void setMemused(String v){
		_Memused=v;
	}

	//FIELD

	private String _Procversion=null;

	/**
	 * @return Returns the procversion.
	 */
	public String getProcversion(){
		return _Procversion;
	}

	/**
	 * Sets the value for procversion.
	 * @param v Value to Set.
	 */
	public void setProcversion(String v){
		_Procversion=v;
	}

	//FIELD

	private String _Jobnode=null;

	/**
	 * @return Returns the jobnode.
	 */
	public String getJobnode(){
		return _Jobnode;
	}

	/**
	 * Sets the value for jobnode.
	 * @param v Value to Set.
	 */
	public void setJobnode(String v){
		_Jobnode=v;
	}

	/**
	 * Sets the value for a field via the XMLPATH.
	 * @param v Value to Set.
	 */
	public void setDataField(String xmlPath,String v) throws BaseElement.UnknownFieldException{
		if (xmlPath.equals("fsversion")){
			setFsversion(v);
		}else if (xmlPath.equals("measures/volumetric/ICV")){
			setMeasures_volumetric_icv(v);
		}else if (xmlPath.equals("measures/volumetric/lhCortexVol")){
			setMeasures_volumetric_lhcortexvol(v);
		}else if (xmlPath.equals("measures/volumetric/rhCortexVol")){
			setMeasures_volumetric_rhcortexvol(v);
		}else if (xmlPath.equals("measures/volumetric/CortexVol")){
			setMeasures_volumetric_cortexvol(v);
		}else if (xmlPath.equals("measures/volumetric/SubCortGrayVol")){
			setMeasures_volumetric_subcortgrayvol(v);
		}else if (xmlPath.equals("measures/volumetric/TotalGrayVol")){
			setMeasures_volumetric_totalgrayvol(v);
		}else if (xmlPath.equals("measures/volumetric/SupraTentorialVol")){
			setMeasures_volumetric_supratentorialvol(v);
		}else if (xmlPath.equals("measures/volumetric/lhCorticalWhiteMatterVol")){
			setMeasures_volumetric_lhcorticalwhitemattervol(v);
		}else if (xmlPath.equals("measures/volumetric/rhCorticalWhiteMatterVol")){
			setMeasures_volumetric_rhcorticalwhitemattervol(v);
		}else if (xmlPath.equals("measures/volumetric/CorticalWhiteMatterVol")){
			setMeasures_volumetric_corticalwhitemattervol(v);
		}else if (xmlPath.equals("procstatus")){
			setProcstatus(v);
		}else if (xmlPath.equals("proctype")){
			setProctype(v);
		}else if (xmlPath.equals("jobid")){
			setJobid(v);
		}else if (xmlPath.equals("walltimeused")){
			setWalltimeused(v);
		}else if (xmlPath.equals("jobstartdate")){
			setJobstartdate(v);
		}else if (xmlPath.equals("memused")){
			setMemused(v);
		}else if (xmlPath.equals("procversion")){
			setProcversion(v);
		}else if (xmlPath.equals("jobnode")){
			setJobnode(v);
		}
		else{
			super.setDataField(xmlPath,v);
		}
	}

	/**
	 * Sets the value for a field via the XMLPATH.
	 * @param v Value to Set.
	 */
	public void setReferenceField(String xmlPath,BaseElement v) throws BaseElement.UnknownFieldException{
		if (xmlPath.equals("measures/volumetric/regions/region")){
			addMeasures_volumetric_regions_region(v);
		}else if (xmlPath.equals("measures/surface/hemisphere")){
			addMeasures_surface_hemisphere(v);
		}
		else{
			super.setReferenceField(xmlPath,v);
		}
	}

	/**
	 * Gets the value for a field via the XMLPATH.
	 * @param v Value to Set.
	 */
	public Object getDataFieldValue(String xmlPath) throws BaseElement.UnknownFieldException{
		if (xmlPath.equals("fsversion")){
			return getFsversion();
		}else if (xmlPath.equals("measures/volumetric/ICV")){
			return getMeasures_volumetric_icv();
		}else if (xmlPath.equals("measures/volumetric/lhCortexVol")){
			return getMeasures_volumetric_lhcortexvol();
		}else if (xmlPath.equals("measures/volumetric/rhCortexVol")){
			return getMeasures_volumetric_rhcortexvol();
		}else if (xmlPath.equals("measures/volumetric/CortexVol")){
			return getMeasures_volumetric_cortexvol();
		}else if (xmlPath.equals("measures/volumetric/SubCortGrayVol")){
			return getMeasures_volumetric_subcortgrayvol();
		}else if (xmlPath.equals("measures/volumetric/TotalGrayVol")){
			return getMeasures_volumetric_totalgrayvol();
		}else if (xmlPath.equals("measures/volumetric/SupraTentorialVol")){
			return getMeasures_volumetric_supratentorialvol();
		}else if (xmlPath.equals("measures/volumetric/lhCorticalWhiteMatterVol")){
			return getMeasures_volumetric_lhcorticalwhitemattervol();
		}else if (xmlPath.equals("measures/volumetric/rhCorticalWhiteMatterVol")){
			return getMeasures_volumetric_rhcorticalwhitemattervol();
		}else if (xmlPath.equals("measures/volumetric/CorticalWhiteMatterVol")){
			return getMeasures_volumetric_corticalwhitemattervol();
		}else if (xmlPath.equals("procstatus")){
			return getProcstatus();
		}else if (xmlPath.equals("proctype")){
			return getProctype();
		}else if (xmlPath.equals("jobid")){
			return getJobid();
		}else if (xmlPath.equals("walltimeused")){
			return getWalltimeused();
		}else if (xmlPath.equals("jobstartdate")){
			return getJobstartdate();
		}else if (xmlPath.equals("memused")){
			return getMemused();
		}else if (xmlPath.equals("procversion")){
			return getProcversion();
		}else if (xmlPath.equals("jobnode")){
			return getJobnode();
		}
		else{
			return super.getDataFieldValue(xmlPath);
		}
	}

	/**
	 * Gets the value for a field via the XMLPATH.
	 * @param v Value to Set.
	 */
	public Object getReferenceField(String xmlPath) throws BaseElement.UnknownFieldException{
		if (xmlPath.equals("measures/volumetric/regions/region")){
			return getMeasures_volumetric_regions_region();
		}else if (xmlPath.equals("measures/surface/hemisphere")){
			return getMeasures_surface_hemisphere();
		}
		else{
			return super.getReferenceField(xmlPath);
		}
	}

	/**
	 * Gets the value for a field via the XMLPATH.
	 * @param v Value to Set.
	 */
	public String getReferenceFieldName(String xmlPath) throws BaseElement.UnknownFieldException{
		if (xmlPath.equals("measures/volumetric/regions/region")){
			return "http://nrg.wustl.edu/fs:fsData_region";
		}else if (xmlPath.equals("measures/surface/hemisphere")){
			return "http://nrg.wustl.edu/fs:fsData_hemisphere";
		}
		else{
			return super.getReferenceFieldName(xmlPath);
		}
	}

	/**
	 * Returns whether or not this is a reference field
	 */
	public String getFieldType(String xmlPath) throws BaseElement.UnknownFieldException{
		if (xmlPath.equals("fsversion")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("measures/volumetric/ICV")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("measures/volumetric/lhCortexVol")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("measures/volumetric/rhCortexVol")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("measures/volumetric/CortexVol")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("measures/volumetric/SubCortGrayVol")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("measures/volumetric/TotalGrayVol")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("measures/volumetric/SupraTentorialVol")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("measures/volumetric/lhCorticalWhiteMatterVol")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("measures/volumetric/rhCorticalWhiteMatterVol")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("measures/volumetric/CorticalWhiteMatterVol")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("measures/volumetric/regions/region")){
			return BaseElement.field_multi_reference;
		}else if (xmlPath.equals("measures/surface/hemisphere")){
			return BaseElement.field_multi_reference;
		}else if (xmlPath.equals("procstatus")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("proctype")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("jobid")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("walltimeused")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("jobstartdate")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("memused")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("procversion")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("jobnode")){
			return BaseElement.field_data;
		}
		else{
			return super.getFieldType(xmlPath);
		}
	}

	/**
	 * Returns arraylist of all fields
	 */
	public ArrayList getAllFields() {
		ArrayList all_fields=new ArrayList();
		all_fields.add("fsversion");
		all_fields.add("measures/volumetric/ICV");
		all_fields.add("measures/volumetric/lhCortexVol");
		all_fields.add("measures/volumetric/rhCortexVol");
		all_fields.add("measures/volumetric/CortexVol");
		all_fields.add("measures/volumetric/SubCortGrayVol");
		all_fields.add("measures/volumetric/TotalGrayVol");
		all_fields.add("measures/volumetric/SupraTentorialVol");
		all_fields.add("measures/volumetric/lhCorticalWhiteMatterVol");
		all_fields.add("measures/volumetric/rhCorticalWhiteMatterVol");
		all_fields.add("measures/volumetric/CorticalWhiteMatterVol");
		all_fields.add("measures/volumetric/regions/region");
		all_fields.add("measures/surface/hemisphere");
		all_fields.add("procstatus");
		all_fields.add("proctype");
		all_fields.add("jobid");
		all_fields.add("walltimeused");
		all_fields.add("jobstartdate");
		all_fields.add("memused");
		all_fields.add("procversion");
		all_fields.add("jobnode");
		all_fields.addAll(super.getAllFields());
		return all_fields;
	}


	public String toString(){
		java.io.StringWriter sw = new java.io.StringWriter();
		try{this.toXML(sw,true);}catch(java.io.IOException e){}
		return sw.toString();
	}


	public void toXML(java.io.Writer writer,boolean prettyPrint) throws java.io.IOException{
		writer.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>");
		writer.write("\n<fs:Freesurfer");
		TreeMap map = new TreeMap();
		map.putAll(getXMLAtts());
		map.put("xmlns:arc","http://nrg.wustl.edu/arc");
		map.put("xmlns:cat","http://nrg.wustl.edu/catalog");
		map.put("xmlns:fs","http://nrg.wustl.edu/fs");
		map.put("xmlns:pipe","http://nrg.wustl.edu/pipe");
		map.put("xmlns:prov","http://www.nbirn.net/prov");
		map.put("xmlns:scr","http://nrg.wustl.edu/scr");
		map.put("xmlns:val","http://nrg.wustl.edu/val");
		map.put("xmlns:wrk","http://nrg.wustl.edu/workflow");
		map.put("xmlns:xdat","http://nrg.wustl.edu/security");
		map.put("xmlns:xnat","http://nrg.wustl.edu/xnat");
		map.put("xmlns:xnat_a","http://nrg.wustl.edu/xnat_assessments");
		map.put("xmlns:xsi","http://www.w3.org/2001/XMLSchema-instance");
		java.util.Iterator iter =map.keySet().iterator();
		while(iter.hasNext()){
			String key = (String)iter.next();
			writer.write(" " + key + "=\"" + map.get(key) + "\"");
		}
		int header = 0;
		if (prettyPrint)header++;
		writer.write(">");
		addXMLBody(writer,header);
		if (prettyPrint)header--;
		writer.write("\n</fs:Freesurfer>");
	}


	protected void addXMLAtts(java.io.Writer writer) throws java.io.IOException{
		TreeMap map = this.getXMLAtts();
		java.util.Iterator iter =map.keySet().iterator();
		while(iter.hasNext()){
			String key = (String)iter.next();
			writer.write(" " + key + "=\"" + map.get(key) + "\"");
		}
	}


	protected TreeMap getXMLAtts() {
		TreeMap map = super.getXMLAtts();
		return map;
	}


	protected boolean addXMLBody(java.io.Writer writer, int header) throws java.io.IOException{
		super.addXMLBody(writer,header);
		//REFERENCE FROM fsData -> imageAssessorData
		if (_Fsversion!=null){
			writer.write("\n" + createHeader(header++) + "<fs:fsversion");
			writer.write(">");
			writer.write(ValueParser(_Fsversion,"string"));
			writer.write("</fs:fsversion>");
			header--;
		}
			int child0=0;
			int att0=0;
			if(_Measures_volumetric_rhcortexvol!=null)
			child0++;
			if(_Measures_volumetric_icv!=null)
			child0++;
			if(_Measures_volumetric_corticalwhitemattervol!=null)
			child0++;
			child0+=_Measures_volumetric_regions_region.size();
			if(_Measures_volumetric_rhcorticalwhitemattervol!=null)
			child0++;
			if(_Measures_volumetric_totalgrayvol!=null)
			child0++;
			if(_Measures_volumetric_lhcortexvol!=null)
			child0++;
			if(_Measures_volumetric_cortexvol!=null)
			child0++;
			if(_Measures_volumetric_subcortgrayvol!=null)
			child0++;
			child0+=_Measures_surface_hemisphere.size();
			if(_Measures_volumetric_lhcorticalwhitemattervol!=null)
			child0++;
			if(_Measures_volumetric_supratentorialvol!=null)
			child0++;
			if(child0>0 || att0>0){
				writer.write("\n" + createHeader(header++) + "<fs:measures");
			if(child0==0){
				writer.write("/>");
			}else{
				writer.write(">");
			int child1=0;
			int att1=0;
			if(_Measures_volumetric_rhcortexvol!=null)
			child1++;
			if(_Measures_volumetric_icv!=null)
			child1++;
			if(_Measures_volumetric_corticalwhitemattervol!=null)
			child1++;
			child1+=_Measures_volumetric_regions_region.size();
			if(_Measures_volumetric_rhcorticalwhitemattervol!=null)
			child1++;
			if(_Measures_volumetric_totalgrayvol!=null)
			child1++;
			if(_Measures_volumetric_lhcortexvol!=null)
			child1++;
			if(_Measures_volumetric_cortexvol!=null)
			child1++;
			if(_Measures_volumetric_subcortgrayvol!=null)
			child1++;
			if(_Measures_volumetric_supratentorialvol!=null)
			child1++;
			if(_Measures_volumetric_lhcorticalwhitemattervol!=null)
			child1++;
			if(child1>0 || att1>0){
				writer.write("\n" + createHeader(header++) + "<fs:volumetric");
			if(child1==0){
				writer.write("/>");
			}else{
				writer.write(">");
		if (_Measures_volumetric_icv!=null){
			writer.write("\n" + createHeader(header++) + "<fs:ICV");
			writer.write(">");
			writer.write(ValueParser(_Measures_volumetric_icv,"float"));
			writer.write("</fs:ICV>");
			header--;
		}
		if (_Measures_volumetric_lhcortexvol!=null){
			writer.write("\n" + createHeader(header++) + "<fs:lhCortexVol");
			writer.write(">");
			writer.write(ValueParser(_Measures_volumetric_lhcortexvol,"float"));
			writer.write("</fs:lhCortexVol>");
			header--;
		}
		if (_Measures_volumetric_rhcortexvol!=null){
			writer.write("\n" + createHeader(header++) + "<fs:rhCortexVol");
			writer.write(">");
			writer.write(ValueParser(_Measures_volumetric_rhcortexvol,"float"));
			writer.write("</fs:rhCortexVol>");
			header--;
		}
		if (_Measures_volumetric_cortexvol!=null){
			writer.write("\n" + createHeader(header++) + "<fs:CortexVol");
			writer.write(">");
			writer.write(ValueParser(_Measures_volumetric_cortexvol,"float"));
			writer.write("</fs:CortexVol>");
			header--;
		}
		if (_Measures_volumetric_subcortgrayvol!=null){
			writer.write("\n" + createHeader(header++) + "<fs:SubCortGrayVol");
			writer.write(">");
			writer.write(ValueParser(_Measures_volumetric_subcortgrayvol,"float"));
			writer.write("</fs:SubCortGrayVol>");
			header--;
		}
		if (_Measures_volumetric_totalgrayvol!=null){
			writer.write("\n" + createHeader(header++) + "<fs:TotalGrayVol");
			writer.write(">");
			writer.write(ValueParser(_Measures_volumetric_totalgrayvol,"float"));
			writer.write("</fs:TotalGrayVol>");
			header--;
		}
		if (_Measures_volumetric_supratentorialvol!=null){
			writer.write("\n" + createHeader(header++) + "<fs:SupraTentorialVol");
			writer.write(">");
			writer.write(ValueParser(_Measures_volumetric_supratentorialvol,"float"));
			writer.write("</fs:SupraTentorialVol>");
			header--;
		}
		if (_Measures_volumetric_lhcorticalwhitemattervol!=null){
			writer.write("\n" + createHeader(header++) + "<fs:lhCorticalWhiteMatterVol");
			writer.write(">");
			writer.write(ValueParser(_Measures_volumetric_lhcorticalwhitemattervol,"float"));
			writer.write("</fs:lhCorticalWhiteMatterVol>");
			header--;
		}
		if (_Measures_volumetric_rhcorticalwhitemattervol!=null){
			writer.write("\n" + createHeader(header++) + "<fs:rhCorticalWhiteMatterVol");
			writer.write(">");
			writer.write(ValueParser(_Measures_volumetric_rhcorticalwhitemattervol,"float"));
			writer.write("</fs:rhCorticalWhiteMatterVol>");
			header--;
		}
		if (_Measures_volumetric_corticalwhitemattervol!=null){
			writer.write("\n" + createHeader(header++) + "<fs:CorticalWhiteMatterVol");
			writer.write(">");
			writer.write(ValueParser(_Measures_volumetric_corticalwhitemattervol,"float"));
			writer.write("</fs:CorticalWhiteMatterVol>");
			header--;
		}
			int child2=0;
			int att2=0;
			child2+=_Measures_volumetric_regions_region.size();
			if(child2>0 || att2>0){
				writer.write("\n" + createHeader(header++) + "<fs:regions");
			if(child2==0){
				writer.write("/>");
			}else{
				writer.write(">");
		//REFERENCE FROM fsData -> measures/volumetric/regions/region
		java.util.Iterator iter3=_Measures_volumetric_regions_region.iterator();
		while(iter3.hasNext()){
			org.nrg.xdat.bean.FsFsdataRegionBean child = (org.nrg.xdat.bean.FsFsdataRegionBean)iter3.next();
			writer.write("\n" + createHeader(header++) + "<fs:region");
			child.addXMLAtts(writer);
			if(!child.getFullSchemaElementName().equals("fs:fsData_region")){
				writer.write(" xsi:type=\"" + child.getFullSchemaElementName() + "\"");
			}
			if (child.hasXMLBodyContent()){
				writer.write(">");
				boolean return4 =child.addXMLBody(writer,header);
				if(return4){
					writer.write("\n" + createHeader(--header) + "</fs:region>");
				}else{
					writer.write("</fs:region>");
					header--;
				}
			}else {writer.write("/>");header--;}
		}
				writer.write("\n" + createHeader(--header) + "</fs:regions>");
			}
			}

				writer.write("\n" + createHeader(--header) + "</fs:volumetric>");
			}
			}

			int child4=0;
			int att4=0;
			child4+=_Measures_surface_hemisphere.size();
			if(child4>0 || att4>0){
				writer.write("\n" + createHeader(header++) + "<fs:surface");
			if(child4==0){
				writer.write("/>");
			}else{
				writer.write(">");
		//REFERENCE FROM fsData -> measures/surface/hemisphere
		java.util.Iterator iter5=_Measures_surface_hemisphere.iterator();
		while(iter5.hasNext()){
			org.nrg.xdat.bean.FsFsdataHemisphereBean child = (org.nrg.xdat.bean.FsFsdataHemisphereBean)iter5.next();
			writer.write("\n" + createHeader(header++) + "<fs:hemisphere");
			child.addXMLAtts(writer);
			if(!child.getFullSchemaElementName().equals("fs:fsData_hemisphere")){
				writer.write(" xsi:type=\"" + child.getFullSchemaElementName() + "\"");
			}
			if (child.hasXMLBodyContent()){
				writer.write(">");
				boolean return6 =child.addXMLBody(writer,header);
				if(return6){
					writer.write("\n" + createHeader(--header) + "</fs:hemisphere>");
				}else{
					writer.write("</fs:hemisphere>");
					header--;
				}
			}else {writer.write("/>");header--;}
		}
				writer.write("\n" + createHeader(--header) + "</fs:surface>");
			}
			}

				writer.write("\n" + createHeader(--header) + "</fs:measures>");
			}
			}

		if (_Procstatus!=null){
			writer.write("\n" + createHeader(header++) + "<fs:procstatus");
			writer.write(">");
			writer.write(ValueParser(_Procstatus,"string"));
			writer.write("</fs:procstatus>");
			header--;
		}
		if (_Proctype!=null){
			writer.write("\n" + createHeader(header++) + "<fs:proctype");
			writer.write(">");
			writer.write(ValueParser(_Proctype,"string"));
			writer.write("</fs:proctype>");
			header--;
		}
		if (_Jobid!=null){
			writer.write("\n" + createHeader(header++) + "<fs:jobid");
			writer.write(">");
			writer.write(ValueParser(_Jobid,"string"));
			writer.write("</fs:jobid>");
			header--;
		}
		if (_Walltimeused!=null){
			writer.write("\n" + createHeader(header++) + "<fs:walltimeused");
			writer.write(">");
			writer.write(ValueParser(_Walltimeused,"string"));
			writer.write("</fs:walltimeused>");
			header--;
		}
		if (_Jobstartdate!=null){
			writer.write("\n" + createHeader(header++) + "<fs:jobstartdate");
			writer.write(">");
			writer.write(ValueParser(_Jobstartdate,"date"));
			writer.write("</fs:jobstartdate>");
			header--;
		}
		if (_Memused!=null){
			writer.write("\n" + createHeader(header++) + "<fs:memused");
			writer.write(">");
			writer.write(ValueParser(_Memused,"string"));
			writer.write("</fs:memused>");
			header--;
		}
		if (_Procversion!=null){
			writer.write("\n" + createHeader(header++) + "<fs:procversion");
			writer.write(">");
			writer.write(ValueParser(_Procversion,"string"));
			writer.write("</fs:procversion>");
			header--;
		}
		if (_Jobnode!=null){
			writer.write("\n" + createHeader(header++) + "<fs:jobnode");
			writer.write(">");
			writer.write(ValueParser(_Jobnode,"string"));
			writer.write("</fs:jobnode>");
			header--;
		}
	return true;
	}


	protected boolean hasXMLBodyContent(){
		if (_Fsversion!=null) return true;
			if(_Measures_volumetric_rhcortexvol!=null) return true;
			if(_Measures_volumetric_icv!=null) return true;
			if(_Measures_volumetric_corticalwhitemattervol!=null) return true;
			if(_Measures_volumetric_regions_region.size()>0)return true;
			if(_Measures_volumetric_rhcorticalwhitemattervol!=null) return true;
			if(_Measures_volumetric_totalgrayvol!=null) return true;
			if(_Measures_volumetric_lhcortexvol!=null) return true;
			if(_Measures_volumetric_cortexvol!=null) return true;
			if(_Measures_volumetric_subcortgrayvol!=null) return true;
			if(_Measures_surface_hemisphere.size()>0)return true;
			if(_Measures_volumetric_lhcorticalwhitemattervol!=null) return true;
			if(_Measures_volumetric_supratentorialvol!=null) return true;
		if (_Procstatus!=null) return true;
		if (_Proctype!=null) return true;
		if (_Jobid!=null) return true;
		if (_Walltimeused!=null) return true;
		if (_Jobstartdate!=null) return true;
		if (_Memused!=null) return true;
		if (_Procversion!=null) return true;
		if (_Jobnode!=null) return true;
		if(super.hasXMLBodyContent())return true;
		return false;
	}
}
