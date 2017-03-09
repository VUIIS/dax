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
public abstract class AutoProcGenprocdataScan extends org.nrg.xdat.base.BaseElement implements org.nrg.xdat.model.ProcGenprocdataScanI {
	public static final Logger logger = Logger.getLogger(AutoProcGenprocdataScan.class);
	public static final String SCHEMA_ELEMENT_NAME="proc:genProcData_scan";

	public AutoProcGenprocdataScan(ItemI item)
	{
		super(item);
	}

	public AutoProcGenprocdataScan(UserI user)
	{
		super(user);
	}

	/*
	 * @deprecated Use AutoProcGenprocdataScan(UserI user)
	 **/
	public AutoProcGenprocdataScan(){}

	public AutoProcGenprocdataScan(Hashtable properties,UserI user)
	{
		super(properties,user);
	}

	public String getSchemaElementName(){
		return "proc:genProcData_scan";
	}

	//FIELD

	private Integer _ProcGenprocdataScanId=null;

	/**
	 * @return Returns the proc_genProcData_scan_id.
	 */
	public Integer getProcGenprocdataScanId() {
		try{
			if (_ProcGenprocdataScanId==null){
				_ProcGenprocdataScanId=getIntegerProperty("proc_genProcData_scan_id");
				return _ProcGenprocdataScanId;
			}else {
				return _ProcGenprocdataScanId;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for proc_genProcData_scan_id.
	 * @param v Value to Set.
	 */
	public void setProcGenprocdataScanId(Integer v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/proc_genProcData_scan_id",v);
		_ProcGenprocdataScanId=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	public static ArrayList<org.nrg.xdat.om.ProcGenprocdataScan> getAllProcGenprocdataScans(org.nrg.xft.security.UserI user,boolean preLoad)
	{
		ArrayList<org.nrg.xdat.om.ProcGenprocdataScan> al = new ArrayList<org.nrg.xdat.om.ProcGenprocdataScan>();

		try{
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetAllItems(SCHEMA_ELEMENT_NAME,user,preLoad);
			al = org.nrg.xdat.base.BaseElement.WrapItems(items.getItems());
		} catch (Exception e) {
			logger.error("",e);
		}

		al.trimToSize();
		return al;
	}

	public static ArrayList<org.nrg.xdat.om.ProcGenprocdataScan> getProcGenprocdataScansByField(String xmlPath, Object value, org.nrg.xft.security.UserI user,boolean preLoad)
	{
		ArrayList<org.nrg.xdat.om.ProcGenprocdataScan> al = new ArrayList<org.nrg.xdat.om.ProcGenprocdataScan>();
		try {
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetItems(xmlPath,value,user,preLoad);
			al = org.nrg.xdat.base.BaseElement.WrapItems(items.getItems());
		} catch (Exception e) {
			logger.error("",e);
		}

		al.trimToSize();
		return al;
	}

	public static ArrayList<org.nrg.xdat.om.ProcGenprocdataScan> getProcGenprocdataScansByField(org.nrg.xft.search.CriteriaCollection criteria, org.nrg.xft.security.UserI user,boolean preLoad)
	{
		ArrayList<org.nrg.xdat.om.ProcGenprocdataScan> al = new ArrayList<org.nrg.xdat.om.ProcGenprocdataScan>();
		try {
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetItems(criteria,user,preLoad);
			al = org.nrg.xdat.base.BaseElement.WrapItems(items.getItems());
		} catch (Exception e) {
			logger.error("",e);
		}

		al.trimToSize();
		return al;
	}

	public static ProcGenprocdataScan getProcGenprocdataScansByProcGenprocdataScanId(Object value, org.nrg.xft.security.UserI user,boolean preLoad)
	{
		try {
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetItems("proc:genProcData_scan/proc_genProcData_scan_id",value,user,preLoad);
			ItemI match = items.getFirst();
			if (match!=null)
				return (ProcGenprocdataScan) org.nrg.xdat.base.BaseElement.GetGeneratedItem(match);
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
