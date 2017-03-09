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
public class FsFsdataHemisphereBean extends BaseElement implements java.io.Serializable, org.nrg.xdat.model.FsFsdataHemisphereI {
	public static final Logger logger = Logger.getLogger(FsFsdataHemisphereBean.class);
	public static final String SCHEMA_ELEMENT_NAME="fs:fsData_hemisphere";

	public String getSchemaElementName(){
		return "fsData_hemisphere";
	}

	public String getFullSchemaElementName(){
		return "fs:fsData_hemisphere";
	}

	//FIELD

	private Double _Numvert=null;

	/**
	 * @return Returns the NumVert.
	 */
	public Double getNumvert() {
		return _Numvert;
	}

	/**
	 * Sets the value for NumVert.
	 * @param v Value to Set.
	 */
	public void setNumvert(Double v){
		_Numvert=v;
	}

	/**
	 * Sets the value for NumVert.
	 * @param v Value to Set.
	 */
	public void setNumvert(String v)  {
		_Numvert=formatDouble(v);
	}

	//FIELD

	private Double _Surfarea=null;

	/**
	 * @return Returns the SurfArea.
	 */
	public Double getSurfarea() {
		return _Surfarea;
	}

	/**
	 * Sets the value for SurfArea.
	 * @param v Value to Set.
	 */
	public void setSurfarea(Double v){
		_Surfarea=v;
	}

	/**
	 * Sets the value for SurfArea.
	 * @param v Value to Set.
	 */
	public void setSurfarea(String v)  {
		_Surfarea=formatDouble(v);
	}
	 private List<org.nrg.xdat.bean.FsFsdataHemisphereRegionBean> _Regions_region =new ArrayList<org.nrg.xdat.bean.FsFsdataHemisphereRegionBean>();

	/**
	 * regions/region
	 * @return Returns an List of org.nrg.xdat.bean.FsFsdataHemisphereRegionBean
	 */
	public <A extends org.nrg.xdat.model.FsFsdataHemisphereRegionI> List<A> getRegions_region() {
		return (List<A>) _Regions_region;
	}

	/**
	 * Sets the value for regions/region.
	 * @param v Value to Set.
	 */
	public void setRegions_region(ArrayList<org.nrg.xdat.bean.FsFsdataHemisphereRegionBean> v){
		_Regions_region=v;
	}

	/**
	 * Adds the value for regions/region.
	 * @param v Value to Set.
	 */
	public void addRegions_region(org.nrg.xdat.bean.FsFsdataHemisphereRegionBean v){
		_Regions_region.add(v);
	}

	/**
	 * regions/region
	 * Adds org.nrg.xdat.model.FsFsdataHemisphereRegionI
	 */
	public <A extends org.nrg.xdat.model.FsFsdataHemisphereRegionI> void addRegions_region(A item) throws Exception{
	_Regions_region.add((org.nrg.xdat.bean.FsFsdataHemisphereRegionBean)item);
	}

	/**
	 * Adds the value for regions/region.
	 * @param v Value to Set.
	 */
	public void addRegions_region(Object v){
		if (v instanceof org.nrg.xdat.bean.FsFsdataHemisphereRegionBean)
			_Regions_region.add((org.nrg.xdat.bean.FsFsdataHemisphereRegionBean)v);
		else
			throw new IllegalArgumentException("Must be a valid org.nrg.xdat.bean.FsFsdataHemisphereRegionBean");
	}

	//FIELD

	private String _Name=null;

	/**
	 * @return Returns the name.
	 */
	public String getName(){
		return _Name;
	}

	/**
	 * Sets the value for name.
	 * @param v Value to Set.
	 */
	public void setName(String v){
		_Name=v;
	}

	//FIELD

	private Integer _FsFsdataHemisphereId=null;

	/**
	 * @return Returns the fs_fsData_hemisphere_id.
	 */
	public Integer getFsFsdataHemisphereId() {
		return _FsFsdataHemisphereId;
	}

	/**
	 * Sets the value for fs_fsData_hemisphere_id.
	 * @param v Value to Set.
	 */
	public void setFsFsdataHemisphereId(Integer v){
		_FsFsdataHemisphereId=v;
	}

	/**
	 * Sets the value for a field via the XMLPATH.
	 * @param v Value to Set.
	 */
	public void setDataField(String xmlPath,String v) throws BaseElement.UnknownFieldException{
		if (xmlPath.equals("NumVert")){
			setNumvert(v);
		}else if (xmlPath.equals("SurfArea")){
			setSurfarea(v);
		}else if (xmlPath.equals("name")){
			setName(v);
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
		if (xmlPath.equals("regions/region")){
			addRegions_region(v);
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
		if (xmlPath.equals("NumVert")){
			return getNumvert();
		}else if (xmlPath.equals("SurfArea")){
			return getSurfarea();
		}else if (xmlPath.equals("name")){
			return getName();
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
		if (xmlPath.equals("regions/region")){
			return getRegions_region();
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
		if (xmlPath.equals("regions/region")){
			return "http://nrg.wustl.edu/fs:fsData_hemisphere_region";
		}
		else{
			return super.getReferenceFieldName(xmlPath);
		}
	}

	/**
	 * Returns whether or not this is a reference field
	 */
	public String getFieldType(String xmlPath) throws BaseElement.UnknownFieldException{
		if (xmlPath.equals("NumVert")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("SurfArea")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("regions/region")){
			return BaseElement.field_multi_reference;
		}else if (xmlPath.equals("name")){
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
		all_fields.add("NumVert");
		all_fields.add("SurfArea");
		all_fields.add("regions/region");
		all_fields.add("name");
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
		writer.write("\n<fs:fsData_hemisphere");
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
		writer.write("\n</fs:fsData_hemisphere>");
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
		if (_Name!=null)
			map.put("name",ValueParser(_Name,"string"));
		else map.put("name","");//REQUIRED FIELD

		return map;
	}


	protected boolean addXMLBody(java.io.Writer writer, int header) throws java.io.IOException{
		super.addXMLBody(writer,header);
		if (_Numvert!=null){
			writer.write("\n" + createHeader(header++) + "<fs:NumVert");
			writer.write(">");
			writer.write(ValueParser(_Numvert,"float"));
			writer.write("</fs:NumVert>");
			header--;
		}
		if (_Surfarea!=null){
			writer.write("\n" + createHeader(header++) + "<fs:SurfArea");
			writer.write(">");
			writer.write(ValueParser(_Surfarea,"float"));
			writer.write("</fs:SurfArea>");
			header--;
		}
			int child0=0;
			int att0=0;
			child0+=_Regions_region.size();
			if(child0>0 || att0>0){
				writer.write("\n" + createHeader(header++) + "<fs:regions");
			if(child0==0){
				writer.write("/>");
			}else{
				writer.write(">");
		//REFERENCE FROM fsData_hemisphere -> regions/region
		java.util.Iterator iter1=_Regions_region.iterator();
		while(iter1.hasNext()){
			org.nrg.xdat.bean.FsFsdataHemisphereRegionBean child = (org.nrg.xdat.bean.FsFsdataHemisphereRegionBean)iter1.next();
			writer.write("\n" + createHeader(header++) + "<fs:region");
			child.addXMLAtts(writer);
			if(!child.getFullSchemaElementName().equals("fs:fsData_hemisphere_region")){
				writer.write(" xsi:type=\"" + child.getFullSchemaElementName() + "\"");
			}
			if (child.hasXMLBodyContent()){
				writer.write(">");
				boolean return2 =child.addXMLBody(writer,header);
				if(return2){
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

	return true;
	}


	protected boolean hasXMLBodyContent(){
		if (_Numvert!=null) return true;
		if (_Surfarea!=null) return true;
			if(_Regions_region.size()>0)return true;
		if(super.hasXMLBodyContent())return true;
		return false;
	}
}
