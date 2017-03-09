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
public abstract class AutoFsFsdataHemisphere extends org.nrg.xdat.base.BaseElement implements org.nrg.xdat.model.FsFsdataHemisphereI {
	public static final Logger logger = Logger.getLogger(AutoFsFsdataHemisphere.class);
	public static final String SCHEMA_ELEMENT_NAME="fs:fsData_hemisphere";

	public AutoFsFsdataHemisphere(ItemI item)
	{
		super(item);
	}

	public AutoFsFsdataHemisphere(UserI user)
	{
		super(user);
	}

	/*
	 * @deprecated Use AutoFsFsdataHemisphere(UserI user)
	 **/
	public AutoFsFsdataHemisphere(){}

	public AutoFsFsdataHemisphere(Hashtable properties,UserI user)
	{
		super(properties,user);
	}

	public String getSchemaElementName(){
		return "fs:fsData_hemisphere";
	}

	//FIELD

	private Double _Numvert=null;

	/**
	 * @return Returns the NumVert.
	 */
	public Double getNumvert() {
		try{
			if (_Numvert==null){
				_Numvert=getDoubleProperty("NumVert");
				return _Numvert;
			}else {
				return _Numvert;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for NumVert.
	 * @param v Value to Set.
	 */
	public void setNumvert(Double v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/NumVert",v);
		_Numvert=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private Double _Surfarea=null;

	/**
	 * @return Returns the SurfArea.
	 */
	public Double getSurfarea() {
		try{
			if (_Surfarea==null){
				_Surfarea=getDoubleProperty("SurfArea");
				return _Surfarea;
			}else {
				return _Surfarea;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for SurfArea.
	 * @param v Value to Set.
	 */
	public void setSurfarea(Double v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/SurfArea",v);
		_Surfarea=null;
		} catch (Exception e1) {logger.error(e1);}
	}
	 private ArrayList<org.nrg.xdat.om.FsFsdataHemisphereRegion> _Regions_region =null;

	/**
	 * regions/region
	 * @return Returns an List of org.nrg.xdat.om.FsFsdataHemisphereRegion
	 */
	public <A extends org.nrg.xdat.model.FsFsdataHemisphereRegionI> List<A> getRegions_region() {
		try{
			if (_Regions_region==null){
				_Regions_region=org.nrg.xdat.base.BaseElement.WrapItems(getChildItems("regions/region"));
			}
			return (List<A>) _Regions_region;
		} catch (Exception e1) {return (List<A>) new ArrayList<org.nrg.xdat.om.FsFsdataHemisphereRegion>();}
	}

	/**
	 * Sets the value for regions/region.
	 * @param v Value to Set.
	 */
	public void setRegions_region(ItemI v) throws Exception{
		_Regions_region =null;
		try{
			if (v instanceof XFTItem)
			{
				getItem().setChild(SCHEMA_ELEMENT_NAME + "/regions/region",v,true);
			}else{
				getItem().setChild(SCHEMA_ELEMENT_NAME + "/regions/region",v.getItem(),true);
			}
		} catch (Exception e1) {logger.error(e1);throw e1;}
	}

	/**
	 * regions/region
	 * Adds org.nrg.xdat.model.FsFsdataHemisphereRegionI
	 */
	public <A extends org.nrg.xdat.model.FsFsdataHemisphereRegionI> void addRegions_region(A item) throws Exception{
	setRegions_region((ItemI)item);
	}

	/**
	 * Removes the regions/region of the given index.
	 * @param index Index of child to remove.
	 */
	public void removeRegions_region(int index) throws java.lang.IndexOutOfBoundsException {
		_Regions_region =null;
		try{
			getItem().removeChild(SCHEMA_ELEMENT_NAME + "/regions/region",index);
		} catch (FieldNotFoundException e1) {logger.error(e1);}
	}

	//FIELD

	private String _Name=null;

	/**
	 * @return Returns the name.
	 */
	public String getName(){
		try{
			if (_Name==null){
				_Name=getStringProperty("name");
				return _Name;
			}else {
				return _Name;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for name.
	 * @param v Value to Set.
	 */
	public void setName(String v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/name",v);
		_Name=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private Integer _FsFsdataHemisphereId=null;

	/**
	 * @return Returns the fs_fsData_hemisphere_id.
	 */
	public Integer getFsFsdataHemisphereId() {
		try{
			if (_FsFsdataHemisphereId==null){
				_FsFsdataHemisphereId=getIntegerProperty("fs_fsData_hemisphere_id");
				return _FsFsdataHemisphereId;
			}else {
				return _FsFsdataHemisphereId;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for fs_fsData_hemisphere_id.
	 * @param v Value to Set.
	 */
	public void setFsFsdataHemisphereId(Integer v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/fs_fsData_hemisphere_id",v);
		_FsFsdataHemisphereId=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	public static ArrayList<org.nrg.xdat.om.FsFsdataHemisphere> getAllFsFsdataHemispheres(org.nrg.xft.security.UserI user,boolean preLoad)
	{
		ArrayList<org.nrg.xdat.om.FsFsdataHemisphere> al = new ArrayList<org.nrg.xdat.om.FsFsdataHemisphere>();

		try{
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetAllItems(SCHEMA_ELEMENT_NAME,user,preLoad);
			al = org.nrg.xdat.base.BaseElement.WrapItems(items.getItems());
		} catch (Exception e) {
			logger.error("",e);
		}

		al.trimToSize();
		return al;
	}

	public static ArrayList<org.nrg.xdat.om.FsFsdataHemisphere> getFsFsdataHemispheresByField(String xmlPath, Object value, org.nrg.xft.security.UserI user,boolean preLoad)
	{
		ArrayList<org.nrg.xdat.om.FsFsdataHemisphere> al = new ArrayList<org.nrg.xdat.om.FsFsdataHemisphere>();
		try {
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetItems(xmlPath,value,user,preLoad);
			al = org.nrg.xdat.base.BaseElement.WrapItems(items.getItems());
		} catch (Exception e) {
			logger.error("",e);
		}

		al.trimToSize();
		return al;
	}

	public static ArrayList<org.nrg.xdat.om.FsFsdataHemisphere> getFsFsdataHemispheresByField(org.nrg.xft.search.CriteriaCollection criteria, org.nrg.xft.security.UserI user,boolean preLoad)
	{
		ArrayList<org.nrg.xdat.om.FsFsdataHemisphere> al = new ArrayList<org.nrg.xdat.om.FsFsdataHemisphere>();
		try {
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetItems(criteria,user,preLoad);
			al = org.nrg.xdat.base.BaseElement.WrapItems(items.getItems());
		} catch (Exception e) {
			logger.error("",e);
		}

		al.trimToSize();
		return al;
	}

	public static FsFsdataHemisphere getFsFsdataHemispheresByFsFsdataHemisphereId(Object value, org.nrg.xft.security.UserI user,boolean preLoad)
	{
		try {
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetItems("fs:fsData_hemisphere/fs_fsData_hemisphere_id",value,user,preLoad);
			ItemI match = items.getFirst();
			if (match!=null)
				return (FsFsdataHemisphere) org.nrg.xdat.base.BaseElement.GetGeneratedItem(match);
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
	
	        //regions/region
	        for(org.nrg.xdat.model.FsFsdataHemisphereRegionI childRegions_region : this.getRegions_region()){
	            if (childRegions_region!=null){
	              for(ResourceFile rf: ((FsFsdataHemisphereRegion)childRegions_region).getFileResources(rootPath, localLoop)) {
	                 rf.setXpath("regions/region[" + ((FsFsdataHemisphereRegion)childRegions_region).getItem().getPKString() + "]/" + rf.getXpath());
	                 rf.setXdatPath("regions/region/" + ((FsFsdataHemisphereRegion)childRegions_region).getItem().getPKString() + "/" + rf.getXpath());
	                 _return.add(rf);
	              }
	            }
	        }
	
	        localLoop = preventLoop;
	
	return _return;
}
}
