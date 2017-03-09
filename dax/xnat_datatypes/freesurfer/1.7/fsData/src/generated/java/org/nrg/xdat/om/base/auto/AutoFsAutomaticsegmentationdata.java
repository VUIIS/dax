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
public abstract class AutoFsAutomaticsegmentationdata extends XnatMrassessordata implements org.nrg.xdat.model.FsAutomaticsegmentationdataI {
	public static final Logger logger = Logger.getLogger(AutoFsAutomaticsegmentationdata.class);
	public static final String SCHEMA_ELEMENT_NAME="fs:automaticSegmentationData";

	public AutoFsAutomaticsegmentationdata(ItemI item)
	{
		super(item);
	}

	public AutoFsAutomaticsegmentationdata(UserI user)
	{
		super(user);
	}

	/*
	 * @deprecated Use AutoFsAutomaticsegmentationdata(UserI user)
	 **/
	public AutoFsAutomaticsegmentationdata(){}

	public AutoFsAutomaticsegmentationdata(Hashtable properties,UserI user)
	{
		super(properties,user);
	}

	public String getSchemaElementName(){
		return "fs:automaticSegmentationData";
	}
	 private org.nrg.xdat.om.XnatMrassessordata _Mrassessordata =null;

	/**
	 * mrAssessorData
	 * @return org.nrg.xdat.om.XnatMrassessordata
	 */
	public org.nrg.xdat.om.XnatMrassessordata getMrassessordata() {
		try{
			if (_Mrassessordata==null){
				_Mrassessordata=((XnatMrassessordata)org.nrg.xdat.base.BaseElement.GetGeneratedItem((XFTItem)getProperty("mrAssessorData")));
				return _Mrassessordata;
			}else {
				return _Mrassessordata;
			}
		} catch (Exception e1) {return null;}
	}

	/**
	 * Sets the value for mrAssessorData.
	 * @param v Value to Set.
	 */
	public void setMrassessordata(ItemI v) throws Exception{
		_Mrassessordata =null;
		try{
			if (v instanceof XFTItem)
			{
				getItem().setChild(SCHEMA_ELEMENT_NAME + "/mrAssessorData",v,true);
			}else{
				getItem().setChild(SCHEMA_ELEMENT_NAME + "/mrAssessorData",v.getItem(),true);
			}
		} catch (Exception e1) {logger.error(e1);throw e1;}
	}

	/**
	 * mrAssessorData
	 * set org.nrg.xdat.model.XnatMrassessordataI
	 */
	public <A extends org.nrg.xdat.model.XnatMrassessordataI> void setMrassessordata(A item) throws Exception{
	setMrassessordata((ItemI)item);
	}

	/**
	 * Removes the mrAssessorData.
	 * */
	public void removeMrassessordata() {
		_Mrassessordata =null;
		try{
			getItem().removeChild(SCHEMA_ELEMENT_NAME + "/mrAssessorData",0);
		} catch (FieldNotFoundException e1) {logger.error(e1);}
		catch (java.lang.IndexOutOfBoundsException e1) {logger.error(e1);}
	}

	//FIELD

	private Integer _Icv=null;

	/**
	 * @return Returns the ICV.
	 */
	public Integer getIcv() {
		try{
			if (_Icv==null){
				_Icv=getIntegerProperty("ICV");
				return _Icv;
			}else {
				return _Icv;
			}
		} catch (Exception e1) {logger.error(e1);return null;}
	}

	/**
	 * Sets the value for ICV.
	 * @param v Value to Set.
	 */
	public void setIcv(Integer v){
		try{
		setProperty(SCHEMA_ELEMENT_NAME + "/ICV",v);
		_Icv=null;
		} catch (Exception e1) {logger.error(e1);}
	}
	 private ArrayList<org.nrg.xdat.om.XnatVolumetricregion> _Regions_region =null;

	/**
	 * regions/region
	 * @return Returns an List of org.nrg.xdat.om.XnatVolumetricregion
	 */
	public <A extends org.nrg.xdat.model.XnatVolumetricregionI> List<A> getRegions_region() {
		try{
			if (_Regions_region==null){
				_Regions_region=org.nrg.xdat.base.BaseElement.WrapItems(getChildItems("regions/region"));
			}
			return (List<A>) _Regions_region;
		} catch (Exception e1) {return (List<A>) new ArrayList<org.nrg.xdat.om.XnatVolumetricregion>();}
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
	 * Adds org.nrg.xdat.model.XnatVolumetricregionI
	 */
	public <A extends org.nrg.xdat.model.XnatVolumetricregionI> void addRegions_region(A item) throws Exception{
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

	public static ArrayList<org.nrg.xdat.om.FsAutomaticsegmentationdata> getAllFsAutomaticsegmentationdatas(org.nrg.xft.security.UserI user,boolean preLoad)
	{
		ArrayList<org.nrg.xdat.om.FsAutomaticsegmentationdata> al = new ArrayList<org.nrg.xdat.om.FsAutomaticsegmentationdata>();

		try{
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetAllItems(SCHEMA_ELEMENT_NAME,user,preLoad);
			al = org.nrg.xdat.base.BaseElement.WrapItems(items.getItems());
		} catch (Exception e) {
			logger.error("",e);
		}

		al.trimToSize();
		return al;
	}

	public static ArrayList<org.nrg.xdat.om.FsAutomaticsegmentationdata> getFsAutomaticsegmentationdatasByField(String xmlPath, Object value, org.nrg.xft.security.UserI user,boolean preLoad)
	{
		ArrayList<org.nrg.xdat.om.FsAutomaticsegmentationdata> al = new ArrayList<org.nrg.xdat.om.FsAutomaticsegmentationdata>();
		try {
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetItems(xmlPath,value,user,preLoad);
			al = org.nrg.xdat.base.BaseElement.WrapItems(items.getItems());
		} catch (Exception e) {
			logger.error("",e);
		}

		al.trimToSize();
		return al;
	}

	public static ArrayList<org.nrg.xdat.om.FsAutomaticsegmentationdata> getFsAutomaticsegmentationdatasByField(org.nrg.xft.search.CriteriaCollection criteria, org.nrg.xft.security.UserI user,boolean preLoad)
	{
		ArrayList<org.nrg.xdat.om.FsAutomaticsegmentationdata> al = new ArrayList<org.nrg.xdat.om.FsAutomaticsegmentationdata>();
		try {
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetItems(criteria,user,preLoad);
			al = org.nrg.xdat.base.BaseElement.WrapItems(items.getItems());
		} catch (Exception e) {
			logger.error("",e);
		}

		al.trimToSize();
		return al;
	}

	public static FsAutomaticsegmentationdata getFsAutomaticsegmentationdatasById(Object value, org.nrg.xft.security.UserI user,boolean preLoad)
	{
		try {
			org.nrg.xft.collections.ItemCollection items = org.nrg.xft.search.ItemSearch.GetItems("fs:automaticSegmentationData/id",value,user,preLoad);
			ItemI match = items.getFirst();
			if (match!=null)
				return (FsAutomaticsegmentationdata) org.nrg.xdat.base.BaseElement.GetGeneratedItem(match);
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
		XFTItem mr = org.nrg.xft.search.ItemSearch.GetItem("xnat:mrSessionData.ID",getItem().getProperty("fs:automaticSegmentationData.imageSession_ID"),getItem().getUser(),false);
		al.add(mr);
		al.add(org.nrg.xft.search.ItemSearch.GetItem("xnat:subjectData.ID",mr.getProperty("xnat:mrSessionData.subject_ID"),getItem().getUser(),false));
		al.trimToSize();
		return org.nrg.xft.schema.Wrappers.XMLWrapper.XMLWriter.ItemListToDOM(al);
	}
	public ArrayList<ResourceFile> getFileResources(String rootPath, boolean preventLoop){
ArrayList<ResourceFile> _return = new ArrayList<ResourceFile>();
	 boolean localLoop = preventLoop;
	        localLoop = preventLoop;
	
	        //mrAssessorData
	        XnatMrassessordata childMrassessordata = (XnatMrassessordata)this.getMrassessordata();
	            if (childMrassessordata!=null){
	              for(ResourceFile rf: ((XnatMrassessordata)childMrassessordata).getFileResources(rootPath, localLoop)) {
	                 rf.setXpath("mrAssessorData[" + ((XnatMrassessordata)childMrassessordata).getItem().getPKString() + "]/" + rf.getXpath());
	                 rf.setXdatPath("mrAssessorData/" + ((XnatMrassessordata)childMrassessordata).getItem().getPKString() + "/" + rf.getXpath());
	                 _return.add(rf);
	              }
	            }
	
	        localLoop = preventLoop;
	
	        //regions/region
	        for(org.nrg.xdat.model.XnatVolumetricregionI childRegions_region : this.getRegions_region()){
	            if (childRegions_region!=null){
	              for(ResourceFile rf: ((XnatVolumetricregion)childRegions_region).getFileResources(rootPath, localLoop)) {
	                 rf.setXpath("regions/region[" + ((XnatVolumetricregion)childRegions_region).getItem().getPKString() + "]/" + rf.getXpath());
	                 rf.setXdatPath("regions/region/" + ((XnatVolumetricregion)childRegions_region).getItem().getPKString() + "/" + rf.getXpath());
	                 _return.add(rf);
	              }
	            }
	        }
	
	        localLoop = preventLoop;
	
	return _return;
}
}
