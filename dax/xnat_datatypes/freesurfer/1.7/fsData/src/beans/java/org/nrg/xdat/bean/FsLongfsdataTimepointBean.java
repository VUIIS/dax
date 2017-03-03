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
public class FsLongfsdataTimepointBean extends BaseElement implements java.io.Serializable, org.nrg.xdat.model.FsLongfsdataTimepointI {
	public static final Logger logger = Logger.getLogger(FsLongfsdataTimepointBean.class);
	public static final String SCHEMA_ELEMENT_NAME="fs:longFSData_timepoint";

	public String getSchemaElementName(){
		return "longFSData_timepoint";
	}

	public String getFullSchemaElementName(){
		return "fs:longFSData_timepoint";
	}

	//FIELD

	private String _Imagesessionid=null;

	/**
	 * @return Returns the imageSessionID.
	 */
	public String getImagesessionid(){
		return _Imagesessionid;
	}

	/**
	 * Sets the value for imageSessionID.
	 * @param v Value to Set.
	 */
	public void setImagesessionid(String v){
		_Imagesessionid=v;
	}

	//FIELD

	private String _Label=null;

	/**
	 * @return Returns the label.
	 */
	public String getLabel(){
		return _Label;
	}

	/**
	 * Sets the value for label.
	 * @param v Value to Set.
	 */
	public void setLabel(String v){
		_Label=v;
	}

	//FIELD

	private String _VisitId=null;

	/**
	 * @return Returns the visit_id.
	 */
	public String getVisitId(){
		return _VisitId;
	}

	/**
	 * Sets the value for visit_id.
	 * @param v Value to Set.
	 */
	public void setVisitId(String v){
		_VisitId=v;
	}

	//FIELD

	private String _Project=null;

	/**
	 * @return Returns the project.
	 */
	public String getProject(){
		return _Project;
	}

	/**
	 * Sets the value for project.
	 * @param v Value to Set.
	 */
	public void setProject(String v){
		_Project=v;
	}

	//FIELD

	private Integer _FsLongfsdataTimepointId=null;

	/**
	 * @return Returns the fs_longFSData_timepoint_id.
	 */
	public Integer getFsLongfsdataTimepointId() {
		return _FsLongfsdataTimepointId;
	}

	/**
	 * Sets the value for fs_longFSData_timepoint_id.
	 * @param v Value to Set.
	 */
	public void setFsLongfsdataTimepointId(Integer v){
		_FsLongfsdataTimepointId=v;
	}

	/**
	 * Sets the value for a field via the XMLPATH.
	 * @param v Value to Set.
	 */
	public void setDataField(String xmlPath,String v) throws BaseElement.UnknownFieldException{
		if (xmlPath.equals("imageSessionID")){
			setImagesessionid(v);
		}else if (xmlPath.equals("label")){
			setLabel(v);
		}else if (xmlPath.equals("visit_id")){
			setVisitId(v);
		}else if (xmlPath.equals("project")){
			setProject(v);
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
			super.setReferenceField(xmlPath,v);
	}

	/**
	 * Gets the value for a field via the XMLPATH.
	 * @param v Value to Set.
	 */
	public Object getDataFieldValue(String xmlPath) throws BaseElement.UnknownFieldException{
		if (xmlPath.equals("imageSessionID")){
			return getImagesessionid();
		}else if (xmlPath.equals("label")){
			return getLabel();
		}else if (xmlPath.equals("visit_id")){
			return getVisitId();
		}else if (xmlPath.equals("project")){
			return getProject();
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
			return super.getReferenceField(xmlPath);
	}

	/**
	 * Gets the value for a field via the XMLPATH.
	 * @param v Value to Set.
	 */
	public String getReferenceFieldName(String xmlPath) throws BaseElement.UnknownFieldException{
			return super.getReferenceFieldName(xmlPath);
	}

	/**
	 * Returns whether or not this is a reference field
	 */
	public String getFieldType(String xmlPath) throws BaseElement.UnknownFieldException{
		if (xmlPath.equals("imageSessionID")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("label")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("visit_id")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("project")){
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
		all_fields.add("imageSessionID");
		all_fields.add("label");
		all_fields.add("visit_id");
		all_fields.add("project");
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
		writer.write("\n<fs:longFSData_timepoint");
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
		writer.write("\n</fs:longFSData_timepoint>");
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
		if (_Imagesessionid!=null)
			map.put("imageSessionID",ValueParser(_Imagesessionid,"string"));
		else map.put("imageSessionID","");//REQUIRED FIELD

		if (_Label!=null)
			map.put("label",ValueParser(_Label,"string"));
		//NOT REQUIRED FIELD

		if (_VisitId!=null)
			map.put("visit_id",ValueParser(_VisitId,"string"));
		//NOT REQUIRED FIELD

		if (_Project!=null)
			map.put("project",ValueParser(_Project,"string"));
		//NOT REQUIRED FIELD

		return map;
	}


	protected boolean addXMLBody(java.io.Writer writer, int header) throws java.io.IOException{
		super.addXMLBody(writer,header);
	return true;
	}


	protected boolean hasXMLBodyContent(){
		if(super.hasXMLBodyContent())return true;
		return false;
	}
}
