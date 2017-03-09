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
public abstract class AutoFsFsdataHemisphereRegion extends org.nrg.xdat.base.BaseElement implements org.nrg.xdat.model.FsFsdataHemisphereRegionI {
	public static final Logger logger = Logger.getLogger(AutoFsFsdataHemisphereRegion.class);
	public static final String SCHEMA_ELEMENT_NAME="fs:fsData_hemisphere_region";

	public AutoFsFsdataHemisphereRegion(ItemI item)
	{
		super(item);
	}

	public AutoFsFsdataHemisphereRegion(UserI user)
	{
		super(user);
	}

	/*
	 * @deprecated Use AutoFsFsdataHemisphereRegion(UserI user)
	 **/
	public AutoFsFsdataHemisphereRegion(){}

	public AutoFsFsdataHemisphereRegion(Hashtable properties,UserI user)
	{
		super(properties,user);
	}

	public String getSchemaElementName(){
		return "fs:fsData_hemisphere_region";
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

	//FIELD

	private Double _Grayvol=null;

	/**
	 * @return Returns the GrayVol.
	 */
	public Double getGrayvol() {
		try{
			if (_Grayvol==null){
				_Grayvol=getDoubleProperty("GrayVol");
				return _Grayvol;
			}else {
				return _Grayvol;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for GrayVol.
	 * @param v Value to Set.
	 */
	public void setGrayvol(Double v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/GrayVol",v);
		_Grayvol=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private Double _Thickavg=null;

	/**
	 * @return Returns the ThickAvg.
	 */
	public Double getThickavg() {
		try{
			if (_Thickavg==null){
				_Thickavg=getDoubleProperty("ThickAvg");
				return _Thickavg;
			}else {
				return _Thickavg;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for ThickAvg.
	 * @param v Value to Set.
	 */
	public void setThickavg(Double v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/ThickAvg",v);
		_Thickavg=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private Double _Thickstd=null;

	/**
	 * @return Returns the ThickStd.
	 */
	public Double getThickstd() {
		try{
			if (_Thickstd==null){
				_Thickstd=getDoubleProperty("ThickStd");
				return _Thickstd;
			}else {
				return _Thickstd;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for ThickStd.
	 * @param v Value to Set.
	 */
	public void setThickstd(Double v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/ThickStd",v);
		_Thickstd=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private Double _Meancurv=null;

	/**
	 * @return Returns the MeanCurv.
	 */
	public Double getMeancurv() {
		try{
			if (_Meancurv==null){
				_Meancurv=getDoubleProperty("MeanCurv");
				return _Meancurv;
			}else {
				return _Meancurv;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for MeanCurv.
	 * @param v Value to Set.
	 */
	public void setMeancurv(Double v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/MeanCurv",v);
		_Meancurv=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private Double _Gauscurv=null;

	/**
	 * @return Returns the GausCurv.
	 */
	public Double getGauscurv() {
		try{
			if (_Gauscurv==null){
				_Gauscurv=getDoubleProperty("GausCurv");
				return _Gauscurv;
			}else {
				return _Gauscurv;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for GausCurv.
	 * @param v Value to Set.
	 */
	public void setGauscurv(Double v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/GausCurv",v);
		_Gauscurv=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private Double _Foldind=null;

	/**
	 * @return Returns the FoldInd.
	 */
	public Double getFoldind() {
		try{
			if (_Foldind==null){
				_Foldind=getDoubleProperty("FoldInd");
				return _Foldind;
			}else {
				return _Foldind;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for FoldInd.
	 * @param v Value to Set.
	 */
	public void setFoldind(Double v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/FoldInd",v);
		_Foldind=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	//FIELD

	private Double _Curvind=null;

	/**
	 * @return Returns the CurvInd.
	 */
	public Double getCurvind() {
		try{
			if (_Curvind==null){
				_Curvind=getDoubleProperty("CurvInd");
				return _Curvind;
			}else {
				return _Curvind;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for CurvInd.
	 * @param v Value to Set.
	 */
	public void setCurvind(Double v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/CurvInd",v);
		_Curvind=null;
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

	private Integer _FsFsdataSurfRegionId=null;

	/**
	 * @return Returns the fs_fsData_surf_region_id.
	 */
	public Integer getFsFsdataSurfRegionId() {
		try{
			if (_FsFsdataSurfRegionId==null){
				_FsFsdataSurfRegionId=getIntegerProperty("fs_fsData_surf_region_id");
				return _FsFsdataSurfRegionId;
			}else {
				return _FsFsdataSurfRegionId;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for fs_fsData_surf_region_id.
	 * @param v Value to Set.
	 */
	public void setFsFsdataSurfRegionId(Integer v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/fs_fsData_surf_region_id",v);
		_FsFsdataSurfRegionId=null;
		} catch (Exception e1) {logger.error(e1);}
	}

	public static ArrayList<org.nrg.xdat.om.FsFsdataHemisphereRegion> getAllFsFsdataHemisphereRegions(org.nrg.xft.security.UserI user,boolean preLoad)
	{
		ArrayList<org.nrg.xdat.om.FsFsdataHemisphereRegion> al = new ArrayList<org.nrg.xdat.om.FsFsdataHemisphereRegion>();

		try{
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetAllItems(SCHEMA_ELEMENT_NAME,user,preLoad);
			al = org.nrg.xdat.base.BaseElement.WrapItems(items.getItems());
		} catch (Exception e) {
			logger.error("",e);
		}

		al.trimToSize();
		return al;
	}

	public static ArrayList<org.nrg.xdat.om.FsFsdataHemisphereRegion> getFsFsdataHemisphereRegionsByField(String xmlPath, Object value, org.nrg.xft.security.UserI user,boolean preLoad)
	{
		ArrayList<org.nrg.xdat.om.FsFsdataHemisphereRegion> al = new ArrayList<org.nrg.xdat.om.FsFsdataHemisphereRegion>();
		try {
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetItems(xmlPath,value,user,preLoad);
			al = org.nrg.xdat.base.BaseElement.WrapItems(items.getItems());
		} catch (Exception e) {
			logger.error("",e);
		}

		al.trimToSize();
		return al;
	}

	public static ArrayList<org.nrg.xdat.om.FsFsdataHemisphereRegion> getFsFsdataHemisphereRegionsByField(org.nrg.xft.search.CriteriaCollection criteria, org.nrg.xft.security.UserI user,boolean preLoad)
	{
		ArrayList<org.nrg.xdat.om.FsFsdataHemisphereRegion> al = new ArrayList<org.nrg.xdat.om.FsFsdataHemisphereRegion>();
		try {
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetItems(criteria,user,preLoad);
			al = org.nrg.xdat.base.BaseElement.WrapItems(items.getItems());
		} catch (Exception e) {
			logger.error("",e);
		}

		al.trimToSize();
		return al;
	}

	public static FsFsdataHemisphereRegion getFsFsdataHemisphereRegionsByFsFsdataSurfRegionId(Object value, org.nrg.xft.security.UserI user,boolean preLoad)
	{
		try {
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetItems("fs:fsData_hemisphere_region/fs_fsData_surf_region_id",value,user,preLoad);
			ItemI match = items.getFirst();
			if (match!=null)
				return (FsFsdataHemisphereRegion) org.nrg.xdat.base.BaseElement.GetGeneratedItem(match);
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
