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
public abstract class AutoFsLongfsdataTimepoint extends org.nrg.xdat.base.BaseElement implements org.nrg.xdat.model.FsLongfsdataTimepointI {
	public static final Logger logger = Logger.getLogger(AutoFsLongfsdataTimepoint.class);
	public static final String SCHEMA_ELEMENT_NAME="fs:longFSData_timepoint";

	public AutoFsLongfsdataTimepoint(ItemI item)
	{
		super(item);
	}

	public AutoFsLongfsdataTimepoint(UserI user)
	{
		super(user);
	}

	/*
	 * @deprecated Use AutoFsLongfsdataTimepoint(UserI user)
	 **/
	public AutoFsLongfsdataTimepoint(){}

	public AutoFsLongfsdataTimepoint(Hashtable properties,UserI user)
	{
		super(properties,user);
	}

	public String getSchemaElementName(){
		return "fs:longFSData_timepoint";
	}

	//FIELD

	private String _Imagesessionid=null;

	/**
	 * @return Returns the imageSessionID.
	 */
	public String getImagesessionid(){
		try{
			if (_Imagesessionid==null){
				_Imagesessionid=getStringProperty("imageSessionID");
				return _Imagesessionid;
			}else {
				return _Imagesessionid;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for imageSessionID.
	 * @param v Value to Set.
	 */
	public void setImagesessionid(String v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/imageSessionID",v);
		_Imagesessionid=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private String _Label=null;

	/**
	 * @return Returns the label.
	 */
	public String getLabel(){
		try{
			if (_Label==null){
				_Label=getStringProperty("label");
				return _Label;
			}else {
				return _Label;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for label.
	 * @param v Value to Set.
	 */
	public void setLabel(String v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/label",v);
		_Label=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private String _VisitId=null;

	/**
	 * @return Returns the visit_id.
	 */
	public String getVisitId(){
		try{
			if (_VisitId==null){
				_VisitId=getStringProperty("visit_id");
				return _VisitId;
			}else {
				return _VisitId;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for visit_id.
	 * @param v Value to Set.
	 */
	public void setVisitId(String v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/visit_id",v);
		_VisitId=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private String _Project=null;

	/**
	 * @return Returns the project.
	 */
	public String getProject(){
		try{
			if (_Project==null){
				_Project=getStringProperty("project");
				return _Project;
			}else {
				return _Project;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for project.
	 * @param v Value to Set.
	 */
	public void setProject(String v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/project",v);
		_Project=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private Integer _FsLongfsdataTimepointId=null;

	/**
	 * @return Returns the fs_longFSData_timepoint_id.
	 */
	public Integer getFsLongfsdataTimepointId() {
		try{
			if (_FsLongfsdataTimepointId==null){
				_FsLongfsdataTimepointId=getIntegerProperty("fs_longFSData_timepoint_id");
				return _FsLongfsdataTimepointId;
			}else {
				return _FsLongfsdataTimepointId;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for fs_longFSData_timepoint_id.
	 * @param v Value to Set.
	 */
	public void setFsLongfsdataTimepointId(Integer v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/fs_longFSData_timepoint_id",v);
		_FsLongfsdataTimepointId=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	public static ArrayList<org.nrg.xdat.om.FsLongfsdataTimepoint> getAllFsLongfsdataTimepoints(org.nrg.xft.security.UserI user,boolean preLoad)
	{
		ArrayList<org.nrg.xdat.om.FsLongfsdataTimepoint> al = new ArrayList<org.nrg.xdat.om.FsLongfsdataTimepoint>();

		try{
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetAllItems(SCHEMA_ELEMENT_NAME,user,preLoad);
			al = org.nrg.xdat.base.BaseElement.WrapItems(items.getItems());
		} catch (Exception e) {
			logger.error("",e);
		}

		al.trimToSize();
		return al;
	}

	public static ArrayList<org.nrg.xdat.om.FsLongfsdataTimepoint> getFsLongfsdataTimepointsByField(String xmlPath, Object value, org.nrg.xft.security.UserI user,boolean preLoad)
	{
		ArrayList<org.nrg.xdat.om.FsLongfsdataTimepoint> al = new ArrayList<org.nrg.xdat.om.FsLongfsdataTimepoint>();
		try {
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetItems(xmlPath,value,user,preLoad);
			al = org.nrg.xdat.base.BaseElement.WrapItems(items.getItems());
		} catch (Exception e) {
			logger.error("",e);
		}

		al.trimToSize();
		return al;
	}

	public static ArrayList<org.nrg.xdat.om.FsLongfsdataTimepoint> getFsLongfsdataTimepointsByField(org.nrg.xft.search.CriteriaCollection criteria, org.nrg.xft.security.UserI user,boolean preLoad)
	{
		ArrayList<org.nrg.xdat.om.FsLongfsdataTimepoint> al = new ArrayList<org.nrg.xdat.om.FsLongfsdataTimepoint>();
		try {
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetItems(criteria,user,preLoad);
			al = org.nrg.xdat.base.BaseElement.WrapItems(items.getItems());
		} catch (Exception e) {
			logger.error("",e);
		}

		al.trimToSize();
		return al;
	}

	public static FsLongfsdataTimepoint getFsLongfsdataTimepointsByFsLongfsdataTimepointId(Object value, org.nrg.xft.security.UserI user,boolean preLoad)
	{
		try {
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetItems("fs:longFSData_timepoint/fs_longFSData_timepoint_id",value,user,preLoad);
			ItemI match = items.getFirst();
			if (match!=null)
				return (FsLongfsdataTimepoint) org.nrg.xdat.base.BaseElement.GetGeneratedItem(match);
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
