/*
 * GENERATED FILE
 * Created on Tue Oct 11 11:43:59 BST 2016
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
public abstract class AutoProcGenprocdata extends XnatImageassessordata implements org.nrg.xdat.model.ProcGenprocdataI {
	public static final Logger logger = Logger.getLogger(AutoProcGenprocdata.class);
	public static final String SCHEMA_ELEMENT_NAME="proc:genProcData";

	public AutoProcGenprocdata(ItemI item)
	{
		super(item);
	}

	public AutoProcGenprocdata(UserI user)
	{
		super(user);
	}

	/*
	 * @deprecated Use AutoProcGenprocdata(UserI user)
	 **/
	public AutoProcGenprocdata(){}

	public AutoProcGenprocdata(Hashtable properties,UserI user)
	{
		super(properties,user);
	}

	public String getSchemaElementName(){
		return "proc:genProcData";
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
	 private ArrayList<org.nrg.xdat.om.ProcGenprocdataScan> _Scans_scan =null;

	/**
	 * scans/scan
	 * @return Returns an List of org.nrg.xdat.om.ProcGenprocdataScan
	 */
	public <A extends org.nrg.xdat.model.ProcGenprocdataScanI> List<A> getScans_scan() {
		try{
			if (_Scans_scan==null){
				_Scans_scan=org.nrg.xdat.base.BaseElement.WrapItems(getChildItems("scans/scan"));
			}
			return (List<A>) _Scans_scan;
		} catch (Exception e1) {return (List<A>) new ArrayList<org.nrg.xdat.om.ProcGenprocdataScan>();}
	}

	/**
	 * Sets the value for scans/scan.
	 * @param v Value to Set.
	 */
	public void setScans_scan(ItemI v) throws Exception{
		_Scans_scan =null;
		try{
			if (v instanceof XFTItem)
			{
				getItem().setChild(SCHEMA_ELEMENT_NAME + "/scans/scan",v,true);
			}else{
				getItem().setChild(SCHEMA_ELEMENT_NAME + "/scans/scan",v.getItem(),true);
			}
		} catch (Exception e1) {logger.error(e1);throw e1;}
	}

	/**
	 * scans/scan
	 * Adds org.nrg.xdat.model.ProcGenprocdataScanI
	 */
	public <A extends org.nrg.xdat.model.ProcGenprocdataScanI> void addScans_scan(A item) throws Exception{
	setScans_scan((ItemI)item);
	}

	/**
	 * Removes the scans/scan of the given index.
	 * @param index Index of child to remove.
	 */
	public void removeScans_scan(int index) throws java.lang.IndexOutOfBoundsException {
		_Scans_scan =null;
		try{
			getItem().removeChild(SCHEMA_ELEMENT_NAME + "/scans/scan",index);
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

	private Integer _Memusedmb=null;

	/**
	 * @return Returns the memusedmb.
	 */
	public Integer getMemusedmb() {
		try{
			if (_Memusedmb==null){
				_Memusedmb=getIntegerProperty("memusedmb");
				return _Memusedmb;
			}else {
				return _Memusedmb;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for memusedmb.
	 * @param v Value to Set.
	 */
	public void setMemusedmb(Integer v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/memusedmb",v);
		_Memusedmb=null;
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

	public static ArrayList<org.nrg.xdat.om.ProcGenprocdata> getAllProcGenprocdatas(org.nrg.xft.security.UserI user,boolean preLoad)
	{
		ArrayList<org.nrg.xdat.om.ProcGenprocdata> al = new ArrayList<org.nrg.xdat.om.ProcGenprocdata>();

		try{
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetAllItems(SCHEMA_ELEMENT_NAME,user,preLoad);
			al = org.nrg.xdat.base.BaseElement.WrapItems(items.getItems());
		} catch (Exception e) {
			logger.error("",e);
		}

		al.trimToSize();
		return al;
	}

	public static ArrayList<org.nrg.xdat.om.ProcGenprocdata> getProcGenprocdatasByField(String xmlPath, Object value, org.nrg.xft.security.UserI user,boolean preLoad)
	{
		ArrayList<org.nrg.xdat.om.ProcGenprocdata> al = new ArrayList<org.nrg.xdat.om.ProcGenprocdata>();
		try {
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetItems(xmlPath,value,user,preLoad);
			al = org.nrg.xdat.base.BaseElement.WrapItems(items.getItems());
		} catch (Exception e) {
			logger.error("",e);
		}

		al.trimToSize();
		return al;
	}

	public static ArrayList<org.nrg.xdat.om.ProcGenprocdata> getProcGenprocdatasByField(org.nrg.xft.search.CriteriaCollection criteria, org.nrg.xft.security.UserI user,boolean preLoad)
	{
		ArrayList<org.nrg.xdat.om.ProcGenprocdata> al = new ArrayList<org.nrg.xdat.om.ProcGenprocdata>();
		try {
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetItems(criteria,user,preLoad);
			al = org.nrg.xdat.base.BaseElement.WrapItems(items.getItems());
		} catch (Exception e) {
			logger.error("",e);
		}

		al.trimToSize();
		return al;
	}

	public static ProcGenprocdata getProcGenprocdatasById(Object value, org.nrg.xft.security.UserI user,boolean preLoad)
	{
		try {
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetItems("proc:genProcData/id",value,user,preLoad);
			ItemI match = items.getFirst();
			if (match!=null)
				return (ProcGenprocdata) org.nrg.xdat.base.BaseElement.GetGeneratedItem(match);
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
	
	        //scans/scan
	        for(org.nrg.xdat.model.ProcGenprocdataScanI childScans_scan : this.getScans_scan()){
	            if (childScans_scan!=null){
	              for(ResourceFile rf: ((ProcGenprocdataScan)childScans_scan).getFileResources(rootPath, localLoop)) {
	                 rf.setXpath("scans/scan[" + ((ProcGenprocdataScan)childScans_scan).getItem().getPKString() + "]/" + rf.getXpath());
	                 rf.setXdatPath("scans/scan/" + ((ProcGenprocdataScan)childScans_scan).getItem().getPKString() + "/" + rf.getXpath());
	                 _return.add(rf);
	              }
	            }
	        }
	
	        localLoop = preventLoop;
	
	return _return;
}
}
