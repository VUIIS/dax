/*
 * GENERATED FILE
 * Created on Wed Oct 12 11:10:43 BST 2016
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
public abstract class AutoProcSubjgenprocdata extends XnatSubjectassessordata implements org.nrg.xdat.model.ProcSubjgenprocdataI {
	public static final Logger logger = Logger.getLogger(AutoProcSubjgenprocdata.class);
	public static final String SCHEMA_ELEMENT_NAME="proc:subjGenProcData";

	public AutoProcSubjgenprocdata(ItemI item)
	{
		super(item);
	}

	public AutoProcSubjgenprocdata(UserI user)
	{
		super(user);
	}

	/*
	 * @deprecated Use AutoProcSubjgenprocdata(UserI user)
	 **/
	public AutoProcSubjgenprocdata(){}

	public AutoProcSubjgenprocdata(Hashtable properties,UserI user)
	{
		super(properties,user);
	}

	public String getSchemaElementName(){
		return "proc:subjGenProcData";
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
	 private ArrayList<org.nrg.xdat.om.ProcSubjgenprocdataStudy> _Includedstudies_study =null;

	/**
	 * includedStudies/Study
	 * @return Returns an List of org.nrg.xdat.om.ProcSubjgenprocdataStudy
	 */
	public <A extends org.nrg.xdat.model.ProcSubjgenprocdataStudyI> List<A> getIncludedstudies_study() {
		try{
			if (_Includedstudies_study==null){
				_Includedstudies_study=org.nrg.xdat.base.BaseElement.WrapItems(getChildItems("includedStudies/Study"));
			}
			return (List<A>) _Includedstudies_study;
		} catch (Exception e1) {return (List<A>) new ArrayList<org.nrg.xdat.om.ProcSubjgenprocdataStudy>();}
	}

	/**
	 * Sets the value for includedStudies/Study.
	 * @param v Value to Set.
	 */
	public void setIncludedstudies_study(ItemI v) throws Exception{
		_Includedstudies_study =null;
		try{
			if (v instanceof XFTItem)
			{
				getItem().setChild(SCHEMA_ELEMENT_NAME + "/includedStudies/Study",v,true);
			}else{
				getItem().setChild(SCHEMA_ELEMENT_NAME + "/includedStudies/Study",v.getItem(),true);
			}
		} catch (Exception e1) {logger.error(e1);throw e1;}
	}

	/**
	 * includedStudies/Study
	 * Adds org.nrg.xdat.model.ProcSubjgenprocdataStudyI
	 */
	public <A extends org.nrg.xdat.model.ProcSubjgenprocdataStudyI> void addIncludedstudies_study(A item) throws Exception{
	setIncludedstudies_study((ItemI)item);
	}

	/**
	 * Removes the includedStudies/Study of the given index.
	 * @param index Index of child to remove.
	 */
	public void removeIncludedstudies_study(int index) throws java.lang.IndexOutOfBoundsException {
		_Includedstudies_study =null;
		try{
			getItem().removeChild(SCHEMA_ELEMENT_NAME + "/includedStudies/Study",index);
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

	//FIELD

	private String _Type=null;

	/**
	 * @return Returns the type.
	 */
	public String getType(){
		try{
			if (_Type==null){
				_Type=getStringProperty("type");
				return _Type;
			}else {
				return _Type;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for type.
	 * @param v Value to Set.
	 */
	public void setType(String v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/type",v);
		_Type=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	public static ArrayList<org.nrg.xdat.om.ProcSubjgenprocdata> getAllProcSubjgenprocdatas(org.nrg.xft.security.UserI user,boolean preLoad)
	{
		ArrayList<org.nrg.xdat.om.ProcSubjgenprocdata> al = new ArrayList<org.nrg.xdat.om.ProcSubjgenprocdata>();

		try{
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetAllItems(SCHEMA_ELEMENT_NAME,user,preLoad);
			al = org.nrg.xdat.base.BaseElement.WrapItems(items.getItems());
		} catch (Exception e) {
			logger.error("",e);
		}

		al.trimToSize();
		return al;
	}

	public static ArrayList<org.nrg.xdat.om.ProcSubjgenprocdata> getProcSubjgenprocdatasByField(String xmlPath, Object value, org.nrg.xft.security.UserI user,boolean preLoad)
	{
		ArrayList<org.nrg.xdat.om.ProcSubjgenprocdata> al = new ArrayList<org.nrg.xdat.om.ProcSubjgenprocdata>();
		try {
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetItems(xmlPath,value,user,preLoad);
			al = org.nrg.xdat.base.BaseElement.WrapItems(items.getItems());
		} catch (Exception e) {
			logger.error("",e);
		}

		al.trimToSize();
		return al;
	}

	public static ArrayList<org.nrg.xdat.om.ProcSubjgenprocdata> getProcSubjgenprocdatasByField(org.nrg.xft.search.CriteriaCollection criteria, org.nrg.xft.security.UserI user,boolean preLoad)
	{
		ArrayList<org.nrg.xdat.om.ProcSubjgenprocdata> al = new ArrayList<org.nrg.xdat.om.ProcSubjgenprocdata>();
		try {
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetItems(criteria,user,preLoad);
			al = org.nrg.xdat.base.BaseElement.WrapItems(items.getItems());
		} catch (Exception e) {
			logger.error("",e);
		}

		al.trimToSize();
		return al;
	}

	public static ProcSubjgenprocdata getProcSubjgenprocdatasById(Object value, org.nrg.xft.security.UserI user,boolean preLoad)
	{
		try {
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetItems("proc:subjGenProcData/id",value,user,preLoad);
			ItemI match = items.getFirst();
			if (match!=null)
				return (ProcSubjgenprocdata) org.nrg.xdat.base.BaseElement.GetGeneratedItem(match);
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
	
	        //includedStudies/Study
	        for(org.nrg.xdat.model.ProcSubjgenprocdataStudyI childIncludedstudies_study : this.getIncludedstudies_study()){
	            if (childIncludedstudies_study!=null){
	              for(ResourceFile rf: ((ProcSubjgenprocdataStudy)childIncludedstudies_study).getFileResources(rootPath, localLoop)) {
	                 rf.setXpath("includedStudies/Study[" + ((ProcSubjgenprocdataStudy)childIncludedstudies_study).getItem().getPKString() + "]/" + rf.getXpath());
	                 rf.setXdatPath("includedStudies/Study/" + ((ProcSubjgenprocdataStudy)childIncludedstudies_study).getItem().getPKString() + "/" + rf.getXpath());
	                 _return.add(rf);
	              }
	            }
	        }
	
	        localLoop = preventLoop;
	
	return _return;
}
}
