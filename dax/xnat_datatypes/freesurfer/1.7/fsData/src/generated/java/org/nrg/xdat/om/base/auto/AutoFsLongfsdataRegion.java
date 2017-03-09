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
public abstract class AutoFsLongfsdataRegion extends org.nrg.xdat.base.BaseElement implements org.nrg.xdat.model.FsLongfsdataRegionI {
	public static final Logger logger = Logger.getLogger(AutoFsLongfsdataRegion.class);
	public static final String SCHEMA_ELEMENT_NAME="fs:longFSData_region";

	public AutoFsLongfsdataRegion(ItemI item)
	{
		super(item);
	}

	public AutoFsLongfsdataRegion(UserI user)
	{
		super(user);
	}

	/*
	 * @deprecated Use AutoFsLongfsdataRegion(UserI user)
	 **/
	public AutoFsLongfsdataRegion(){}

	public AutoFsLongfsdataRegion(Hashtable properties,UserI user)
	{
		super(properties,user);
	}

	public String getSchemaElementName(){
		return "fs:longFSData_region";
	}

	//FIELD

	private Double _Nvoxels=null;

	/**
	 * @return Returns the NVoxels.
	 */
	public Double getNvoxels() {
		try{
			if (_Nvoxels==null){
				_Nvoxels=getDoubleProperty("NVoxels");
				return _Nvoxels;
			}else {
				return _Nvoxels;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for NVoxels.
	 * @param v Value to Set.
	 */
	public void setNvoxels(Double v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/NVoxels",v);
		_Nvoxels=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private Double _Volume=null;

	/**
	 * @return Returns the Volume.
	 */
	public Double getVolume() {
		try{
			if (_Volume==null){
				_Volume=getDoubleProperty("Volume");
				return _Volume;
			}else {
				return _Volume;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for Volume.
	 * @param v Value to Set.
	 */
	public void setVolume(Double v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/Volume",v);
		_Volume=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private Double _Normmean=null;

	/**
	 * @return Returns the normMean.
	 */
	public Double getNormmean() {
		try{
			if (_Normmean==null){
				_Normmean=getDoubleProperty("normMean");
				return _Normmean;
			}else {
				return _Normmean;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for normMean.
	 * @param v Value to Set.
	 */
	public void setNormmean(Double v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/normMean",v);
		_Normmean=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private Double _Normstddev=null;

	/**
	 * @return Returns the normStdDev.
	 */
	public Double getNormstddev() {
		try{
			if (_Normstddev==null){
				_Normstddev=getDoubleProperty("normStdDev");
				return _Normstddev;
			}else {
				return _Normstddev;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for normStdDev.
	 * @param v Value to Set.
	 */
	public void setNormstddev(Double v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/normStdDev",v);
		_Normstddev=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private Double _Normmin=null;

	/**
	 * @return Returns the normMin.
	 */
	public Double getNormmin() {
		try{
			if (_Normmin==null){
				_Normmin=getDoubleProperty("normMin");
				return _Normmin;
			}else {
				return _Normmin;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for normMin.
	 * @param v Value to Set.
	 */
	public void setNormmin(Double v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/normMin",v);
		_Normmin=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private Double _Normmax=null;

	/**
	 * @return Returns the normMax.
	 */
	public Double getNormmax() {
		try{
			if (_Normmax==null){
				_Normmax=getDoubleProperty("normMax");
				return _Normmax;
			}else {
				return _Normmax;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for normMax.
	 * @param v Value to Set.
	 */
	public void setNormmax(Double v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/normMax",v);
		_Normmax=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private Double _Normrange=null;

	/**
	 * @return Returns the normRange.
	 */
	public Double getNormrange() {
		try{
			if (_Normrange==null){
				_Normrange=getDoubleProperty("normRange");
				return _Normrange;
			}else {
				return _Normrange;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for normRange.
	 * @param v Value to Set.
	 */
	public void setNormrange(Double v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/normRange",v);
		_Normrange=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private String _Segid=null;

	/**
	 * @return Returns the SegId.
	 */
	public String getSegid(){
		try{
			if (_Segid==null){
				_Segid=getStringProperty("SegId");
				return _Segid;
			}else {
				return _Segid;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for SegId.
	 * @param v Value to Set.
	 */
	public void setSegid(String v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/SegId",v);
		_Segid=null;
		} catch (Exception e1) {logger.error(e1);}
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

	private String _Hemisphere=null;

	/**
	 * @return Returns the hemisphere.
	 */
	public String getHemisphere(){
		try{
			if (_Hemisphere==null){
				_Hemisphere=getStringProperty("hemisphere");
				return _Hemisphere;
			}else {
				return _Hemisphere;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for hemisphere.
	 * @param v Value to Set.
	 */
	public void setHemisphere(String v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/hemisphere",v);
		_Hemisphere=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private Integer _FsLongfsdataVolRegionId=null;

	/**
	 * @return Returns the fs_longFSData_vol_region_id.
	 */
	public Integer getFsLongfsdataVolRegionId() {
		try{
			if (_FsLongfsdataVolRegionId==null){
				_FsLongfsdataVolRegionId=getIntegerProperty("fs_longFSData_vol_region_id");
				return _FsLongfsdataVolRegionId;
			}else {
				return _FsLongfsdataVolRegionId;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for fs_longFSData_vol_region_id.
	 * @param v Value to Set.
	 */
	public void setFsLongfsdataVolRegionId(Integer v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/fs_longFSData_vol_region_id",v);
		_FsLongfsdataVolRegionId=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	public static ArrayList<org.nrg.xdat.om.FsLongfsdataRegion> getAllFsLongfsdataRegions(org.nrg.xft.security.UserI user,boolean preLoad)
	{
		ArrayList<org.nrg.xdat.om.FsLongfsdataRegion> al = new ArrayList<org.nrg.xdat.om.FsLongfsdataRegion>();

		try{
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetAllItems(SCHEMA_ELEMENT_NAME,user,preLoad);
			al = org.nrg.xdat.base.BaseElement.WrapItems(items.getItems());
		} catch (Exception e) {
			logger.error("",e);
		}

		al.trimToSize();
		return al;
	}

	public static ArrayList<org.nrg.xdat.om.FsLongfsdataRegion> getFsLongfsdataRegionsByField(String xmlPath, Object value, org.nrg.xft.security.UserI user,boolean preLoad)
	{
		ArrayList<org.nrg.xdat.om.FsLongfsdataRegion> al = new ArrayList<org.nrg.xdat.om.FsLongfsdataRegion>();
		try {
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetItems(xmlPath,value,user,preLoad);
			al = org.nrg.xdat.base.BaseElement.WrapItems(items.getItems());
		} catch (Exception e) {
			logger.error("",e);
		}

		al.trimToSize();
		return al;
	}

	public static ArrayList<org.nrg.xdat.om.FsLongfsdataRegion> getFsLongfsdataRegionsByField(org.nrg.xft.search.CriteriaCollection criteria, org.nrg.xft.security.UserI user,boolean preLoad)
	{
		ArrayList<org.nrg.xdat.om.FsLongfsdataRegion> al = new ArrayList<org.nrg.xdat.om.FsLongfsdataRegion>();
		try {
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetItems(criteria,user,preLoad);
			al = org.nrg.xdat.base.BaseElement.WrapItems(items.getItems());
		} catch (Exception e) {
			logger.error("",e);
		}

		al.trimToSize();
		return al;
	}

	public static FsLongfsdataRegion getFsLongfsdataRegionsByFsLongfsdataVolRegionId(Object value, org.nrg.xft.security.UserI user,boolean preLoad)
	{
		try {
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetItems("fs:longFSData_region/fs_longFSData_vol_region_id",value,user,preLoad);
			ItemI match = items.getFirst();
			if (match!=null)
				return (FsLongfsdataRegion) org.nrg.xdat.base.BaseElement.GetGeneratedItem(match);
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
