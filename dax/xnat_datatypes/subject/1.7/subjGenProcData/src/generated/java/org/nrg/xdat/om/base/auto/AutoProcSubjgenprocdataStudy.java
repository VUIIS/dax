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
public abstract class AutoProcSubjgenprocdataStudy extends org.nrg.xdat.base.BaseElement implements org.nrg.xdat.model.ProcSubjgenprocdataStudyI {
	public static final Logger logger = Logger.getLogger(AutoProcSubjgenprocdataStudy.class);
	public static final String SCHEMA_ELEMENT_NAME="proc:subjGenProcData_Study";

	public AutoProcSubjgenprocdataStudy(ItemI item)
	{
		super(item);
	}

	public AutoProcSubjgenprocdataStudy(UserI user)
	{
		super(user);
	}

	/*
	 * @deprecated Use AutoProcSubjgenprocdataStudy(UserI user)
	 **/
	public AutoProcSubjgenprocdataStudy(){}

	public AutoProcSubjgenprocdataStudy(Hashtable properties,UserI user)
	{
		super(properties,user);
	}

	public String getSchemaElementName(){
		return "proc:subjGenProcData_Study";
	}

	//FIELD

	private String _Id=null;

	/**
	 * @return Returns the id.
	 */
	public String getId(){
		try{
			if (_Id==null){
				_Id=getStringProperty("id");
				return _Id;
			}else {
				return _Id;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for id.
	 * @param v Value to Set.
	 */
	public void setId(String v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/id",v);
		_Id=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private String _Studyuid=null;

	/**
	 * @return Returns the studyUID.
	 */
	public String getStudyuid(){
		try{
			if (_Studyuid==null){
				_Studyuid=getStringProperty("studyUID");
				return _Studyuid;
			}else {
				return _Studyuid;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for studyUID.
	 * @param v Value to Set.
	 */
	public void setStudyuid(String v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/studyUID",v);
		_Studyuid=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private String _Studydate=null;

	/**
	 * @return Returns the studyDate.
	 */
	public String getStudydate(){
		try{
			if (_Studydate==null){
				_Studydate=getStringProperty("studyDate");
				return _Studydate;
			}else {
				return _Studydate;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for studyDate.
	 * @param v Value to Set.
	 */
	public void setStudydate(String v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/studyDate",v);
		_Studydate=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private String _Seriesnumber=null;

	/**
	 * @return Returns the seriesNumber.
	 */
	public String getSeriesnumber(){
		try{
			if (_Seriesnumber==null){
				_Seriesnumber=getStringProperty("seriesNumber");
				return _Seriesnumber;
			}else {
				return _Seriesnumber;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for seriesNumber.
	 * @param v Value to Set.
	 */
	public void setSeriesnumber(String v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/seriesNumber",v);
		_Seriesnumber=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private String _Seriesuid=null;

	/**
	 * @return Returns the seriesUID.
	 */
	public String getSeriesuid(){
		try{
			if (_Seriesuid==null){
				_Seriesuid=getStringProperty("seriesUID");
				return _Seriesuid;
			}else {
				return _Seriesuid;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for seriesUID.
	 * @param v Value to Set.
	 */
	public void setSeriesuid(String v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/seriesUID",v);
		_Seriesuid=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private Integer _ProcSubjgenprocdataStudyId=null;

	/**
	 * @return Returns the proc_subjGenProcData_Study_id.
	 */
	public Integer getProcSubjgenprocdataStudyId() {
		try{
			if (_ProcSubjgenprocdataStudyId==null){
				_ProcSubjgenprocdataStudyId=getIntegerProperty("proc_subjGenProcData_Study_id");
				return _ProcSubjgenprocdataStudyId;
			}else {
				return _ProcSubjgenprocdataStudyId;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for proc_subjGenProcData_Study_id.
	 * @param v Value to Set.
	 */
	public void setProcSubjgenprocdataStudyId(Integer v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/proc_subjGenProcData_Study_id",v);
		_ProcSubjgenprocdataStudyId=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	public static ArrayList<org.nrg.xdat.om.ProcSubjgenprocdataStudy> getAllProcSubjgenprocdataStudys(org.nrg.xft.security.UserI user,boolean preLoad)
	{
		ArrayList<org.nrg.xdat.om.ProcSubjgenprocdataStudy> al = new ArrayList<org.nrg.xdat.om.ProcSubjgenprocdataStudy>();

		try{
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetAllItems(SCHEMA_ELEMENT_NAME,user,preLoad);
			al = org.nrg.xdat.base.BaseElement.WrapItems(items.getItems());
		} catch (Exception e) {
			logger.error("",e);
		}

		al.trimToSize();
		return al;
	}

	public static ArrayList<org.nrg.xdat.om.ProcSubjgenprocdataStudy> getProcSubjgenprocdataStudysByField(String xmlPath, Object value, org.nrg.xft.security.UserI user,boolean preLoad)
	{
		ArrayList<org.nrg.xdat.om.ProcSubjgenprocdataStudy> al = new ArrayList<org.nrg.xdat.om.ProcSubjgenprocdataStudy>();
		try {
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetItems(xmlPath,value,user,preLoad);
			al = org.nrg.xdat.base.BaseElement.WrapItems(items.getItems());
		} catch (Exception e) {
			logger.error("",e);
		}

		al.trimToSize();
		return al;
	}

	public static ArrayList<org.nrg.xdat.om.ProcSubjgenprocdataStudy> getProcSubjgenprocdataStudysByField(org.nrg.xft.search.CriteriaCollection criteria, org.nrg.xft.security.UserI user,boolean preLoad)
	{
		ArrayList<org.nrg.xdat.om.ProcSubjgenprocdataStudy> al = new ArrayList<org.nrg.xdat.om.ProcSubjgenprocdataStudy>();
		try {
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetItems(criteria,user,preLoad);
			al = org.nrg.xdat.base.BaseElement.WrapItems(items.getItems());
		} catch (Exception e) {
			logger.error("",e);
		}

		al.trimToSize();
		return al;
	}

	public static ProcSubjgenprocdataStudy getProcSubjgenprocdataStudysByProcSubjgenprocdataStudyId(Object value, org.nrg.xft.security.UserI user,boolean preLoad)
	{
		try {
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetItems("proc:subjGenProcData_Study/proc_subjGenProcData_Study_id",value,user,preLoad);
			ItemI match = items.getFirst();
			if (match!=null)
				return (ProcSubjgenprocdataStudy) org.nrg.xdat.base.BaseElement.GetGeneratedItem(match);
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
	
	return _return;
}
}
