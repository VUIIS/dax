/*
 * GENERATED FILE
 * Created on Wed Oct 12 11:10:43 BST 2016
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
public class ProcSubjgenprocdataStudyBean extends BaseElement implements java.io.Serializable, org.nrg.xdat.model.ProcSubjgenprocdataStudyI {
	public static final Logger logger = Logger.getLogger(ProcSubjgenprocdataStudyBean.class);
	public static final String SCHEMA_ELEMENT_NAME="proc:subjGenProcData_Study";

	public String getSchemaElementName(){
		return "subjGenProcData_Study";
	}

	public String getFullSchemaElementName(){
		return "proc:subjGenProcData_Study";
	}

	//FIELD

	private String _Id=null;

	/**
	 * @return Returns the id.
	 */
	public String getId(){
		return _Id;
	}

	/**
	 * Sets the value for id.
	 * @param v Value to Set.
	 */
	public void setId(String v){
		_Id=v;
	}

	//FIELD

	private String _Studyuid=null;

	/**
	 * @return Returns the studyUID.
	 */
	public String getStudyuid(){
		return _Studyuid;
	}

	/**
	 * Sets the value for studyUID.
	 * @param v Value to Set.
	 */
	public void setStudyuid(String v){
		_Studyuid=v;
	}

	//FIELD

	private String _Studydate=null;

	/**
	 * @return Returns the studyDate.
	 */
	public String getStudydate(){
		return _Studydate;
	}

	/**
	 * Sets the value for studyDate.
	 * @param v Value to Set.
	 */
	public void setStudydate(String v){
		_Studydate=v;
	}

	//FIELD

	private String _Seriesnumber=null;

	/**
	 * @return Returns the seriesNumber.
	 */
	public String getSeriesnumber(){
		return _Seriesnumber;
	}

	/**
	 * Sets the value for seriesNumber.
	 * @param v Value to Set.
	 */
	public void setSeriesnumber(String v){
		_Seriesnumber=v;
	}

	//FIELD

	private String _Seriesuid=null;

	/**
	 * @return Returns the seriesUID.
	 */
	public String getSeriesuid(){
		return _Seriesuid;
	}

	/**
	 * Sets the value for seriesUID.
	 * @param v Value to Set.
	 */
	public void setSeriesuid(String v){
		_Seriesuid=v;
	}

	//FIELD

	private Integer _ProcSubjgenprocdataStudyId=null;

	/**
	 * @return Returns the proc_subjGenProcData_Study_id.
	 */
	public Integer getProcSubjgenprocdataStudyId() {
		return _ProcSubjgenprocdataStudyId;
	}

	/**
	 * Sets the value for proc_subjGenProcData_Study_id.
	 * @param v Value to Set.
	 */
	public void setProcSubjgenprocdataStudyId(Integer v){
		_ProcSubjgenprocdataStudyId=v;
	}

	/**
	 * Sets the value for a field via the XMLPATH.
	 * @param v Value to Set.
	 */
	public void setDataField(String xmlPath,String v) throws BaseElement.UnknownFieldException{
		if (xmlPath.equals("id")){
			setId(v);
		}else if (xmlPath.equals("studyUID")){
			setStudyuid(v);
		}else if (xmlPath.equals("studyDate")){
			setStudydate(v);
		}else if (xmlPath.equals("seriesNumber")){
			setSeriesnumber(v);
		}else if (xmlPath.equals("seriesUID")){
			setSeriesuid(v);
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
		if (xmlPath.equals("id")){
			return getId();
		}else if (xmlPath.equals("studyUID")){
			return getStudyuid();
		}else if (xmlPath.equals("studyDate")){
			return getStudydate();
		}else if (xmlPath.equals("seriesNumber")){
			return getSeriesnumber();
		}else if (xmlPath.equals("seriesUID")){
			return getSeriesuid();
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
		if (xmlPath.equals("id")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("studyUID")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("studyDate")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("seriesNumber")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("seriesUID")){
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
		all_fields.add("id");
		all_fields.add("studyUID");
		all_fields.add("studyDate");
		all_fields.add("seriesNumber");
		all_fields.add("seriesUID");
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
		writer.write("\n<proc:subjGenProcData_Study");
		TreeMap map = new TreeMap();
		map.putAll(getXMLAtts());
		map.put("xmlns:arc","http://nrg.wustl.edu/arc");
		map.put("xmlns:cat","http://nrg.wustl.edu/catalog");
		map.put("xmlns:pipe","http://nrg.wustl.edu/pipe");
		map.put("xmlns:proc","http://nrg.wustl.edu/proc");
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
		writer.write("\n</proc:subjGenProcData_Study>");
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
		if (_Id!=null)
			map.put("id",ValueParser(_Id,"string"));
		else map.put("id","");//REQUIRED FIELD

		return map;
	}


	protected boolean addXMLBody(java.io.Writer writer, int header) throws java.io.IOException{
		super.addXMLBody(writer,header);
		if (_Studyuid!=null){
			writer.write("\n" + createHeader(header++) + "<proc:studyUID");
			writer.write(">");
			writer.write(ValueParser(_Studyuid,"string"));
			writer.write("</proc:studyUID>");
			header--;
		}
		if (_Studydate!=null){
			writer.write("\n" + createHeader(header++) + "<proc:studyDate");
			writer.write(">");
			writer.write(ValueParser(_Studydate,"string"));
			writer.write("</proc:studyDate>");
			header--;
		}
		if (_Seriesnumber!=null){
			writer.write("\n" + createHeader(header++) + "<proc:seriesNumber");
			writer.write(">");
			writer.write(ValueParser(_Seriesnumber,"string"));
			writer.write("</proc:seriesNumber>");
			header--;
		}
		if (_Seriesuid!=null){
			writer.write("\n" + createHeader(header++) + "<proc:seriesUID");
			writer.write(">");
			writer.write(ValueParser(_Seriesuid,"string"));
			writer.write("</proc:seriesUID>");
			header--;
		}
	return true;
	}


	protected boolean hasXMLBodyContent(){
		if (_Studyuid!=null) return true;
		if (_Studydate!=null) return true;
		if (_Seriesnumber!=null) return true;
		if (_Seriesuid!=null) return true;
		if(super.hasXMLBodyContent())return true;
		return false;
	}
}
