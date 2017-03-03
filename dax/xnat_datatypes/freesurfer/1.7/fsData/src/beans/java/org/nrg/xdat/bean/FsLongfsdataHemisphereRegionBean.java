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
public class FsLongfsdataHemisphereRegionBean extends BaseElement implements java.io.Serializable, org.nrg.xdat.model.FsLongfsdataHemisphereRegionI {
	public static final Logger logger = Logger.getLogger(FsLongfsdataHemisphereRegionBean.class);
	public static final String SCHEMA_ELEMENT_NAME="fs:longFSData_hemisphere_region";

	public String getSchemaElementName(){
		return "longFSData_hemisphere_region";
	}

	public String getFullSchemaElementName(){
		return "fs:longFSData_hemisphere_region";
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

	//FIELD

	private Double _Grayvol=null;

	/**
	 * @return Returns the GrayVol.
	 */
	public Double getGrayvol() {
		return _Grayvol;
	}

	/**
	 * Sets the value for GrayVol.
	 * @param v Value to Set.
	 */
	public void setGrayvol(Double v){
		_Grayvol=v;
	}

	/**
	 * Sets the value for GrayVol.
	 * @param v Value to Set.
	 */
	public void setGrayvol(String v)  {
		_Grayvol=formatDouble(v);
	}

	//FIELD

	private Double _Thickavg=null;

	/**
	 * @return Returns the ThickAvg.
	 */
	public Double getThickavg() {
		return _Thickavg;
	}

	/**
	 * Sets the value for ThickAvg.
	 * @param v Value to Set.
	 */
	public void setThickavg(Double v){
		_Thickavg=v;
	}

	/**
	 * Sets the value for ThickAvg.
	 * @param v Value to Set.
	 */
	public void setThickavg(String v)  {
		_Thickavg=formatDouble(v);
	}

	//FIELD

	private Double _Thickstd=null;

	/**
	 * @return Returns the ThickStd.
	 */
	public Double getThickstd() {
		return _Thickstd;
	}

	/**
	 * Sets the value for ThickStd.
	 * @param v Value to Set.
	 */
	public void setThickstd(Double v){
		_Thickstd=v;
	}

	/**
	 * Sets the value for ThickStd.
	 * @param v Value to Set.
	 */
	public void setThickstd(String v)  {
		_Thickstd=formatDouble(v);
	}

	//FIELD

	private Double _Meancurv=null;

	/**
	 * @return Returns the MeanCurv.
	 */
	public Double getMeancurv() {
		return _Meancurv;
	}

	/**
	 * Sets the value for MeanCurv.
	 * @param v Value to Set.
	 */
	public void setMeancurv(Double v){
		_Meancurv=v;
	}

	/**
	 * Sets the value for MeanCurv.
	 * @param v Value to Set.
	 */
	public void setMeancurv(String v)  {
		_Meancurv=formatDouble(v);
	}

	//FIELD

	private Double _Gauscurv=null;

	/**
	 * @return Returns the GausCurv.
	 */
	public Double getGauscurv() {
		return _Gauscurv;
	}

	/**
	 * Sets the value for GausCurv.
	 * @param v Value to Set.
	 */
	public void setGauscurv(Double v){
		_Gauscurv=v;
	}

	/**
	 * Sets the value for GausCurv.
	 * @param v Value to Set.
	 */
	public void setGauscurv(String v)  {
		_Gauscurv=formatDouble(v);
	}

	//FIELD

	private Double _Foldind=null;

	/**
	 * @return Returns the FoldInd.
	 */
	public Double getFoldind() {
		return _Foldind;
	}

	/**
	 * Sets the value for FoldInd.
	 * @param v Value to Set.
	 */
	public void setFoldind(Double v){
		_Foldind=v;
	}

	/**
	 * Sets the value for FoldInd.
	 * @param v Value to Set.
	 */
	public void setFoldind(String v)  {
		_Foldind=formatDouble(v);
	}

	//FIELD

	private Double _Curvind=null;

	/**
	 * @return Returns the CurvInd.
	 */
	public Double getCurvind() {
		return _Curvind;
	}

	/**
	 * Sets the value for CurvInd.
	 * @param v Value to Set.
	 */
	public void setCurvind(Double v){
		_Curvind=v;
	}

	/**
	 * Sets the value for CurvInd.
	 * @param v Value to Set.
	 */
	public void setCurvind(String v)  {
		_Curvind=formatDouble(v);
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

	private Integer _FsLongfsdataSurfRegionId=null;

	/**
	 * @return Returns the fs_longFSData_surf_region_id.
	 */
	public Integer getFsLongfsdataSurfRegionId() {
		return _FsLongfsdataSurfRegionId;
	}

	/**
	 * Sets the value for fs_longFSData_surf_region_id.
	 * @param v Value to Set.
	 */
	public void setFsLongfsdataSurfRegionId(Integer v){
		_FsLongfsdataSurfRegionId=v;
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
		}else if (xmlPath.equals("GrayVol")){
			setGrayvol(v);
		}else if (xmlPath.equals("ThickAvg")){
			setThickavg(v);
		}else if (xmlPath.equals("ThickStd")){
			setThickstd(v);
		}else if (xmlPath.equals("MeanCurv")){
			setMeancurv(v);
		}else if (xmlPath.equals("GausCurv")){
			setGauscurv(v);
		}else if (xmlPath.equals("FoldInd")){
			setFoldind(v);
		}else if (xmlPath.equals("CurvInd")){
			setCurvind(v);
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
			super.setReferenceField(xmlPath,v);
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
		}else if (xmlPath.equals("GrayVol")){
			return getGrayvol();
		}else if (xmlPath.equals("ThickAvg")){
			return getThickavg();
		}else if (xmlPath.equals("ThickStd")){
			return getThickstd();
		}else if (xmlPath.equals("MeanCurv")){
			return getMeancurv();
		}else if (xmlPath.equals("GausCurv")){
			return getGauscurv();
		}else if (xmlPath.equals("FoldInd")){
			return getFoldind();
		}else if (xmlPath.equals("CurvInd")){
			return getCurvind();
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
		if (xmlPath.equals("NumVert")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("SurfArea")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("GrayVol")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("ThickAvg")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("ThickStd")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("MeanCurv")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("GausCurv")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("FoldInd")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("CurvInd")){
			return BaseElement.field_data;
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
		all_fields.add("GrayVol");
		all_fields.add("ThickAvg");
		all_fields.add("ThickStd");
		all_fields.add("MeanCurv");
		all_fields.add("GausCurv");
		all_fields.add("FoldInd");
		all_fields.add("CurvInd");
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
		writer.write("\n<fs:longFSData_hemisphere_region");
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
		writer.write("\n</fs:longFSData_hemisphere_region>");
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
		if (_Grayvol!=null){
			writer.write("\n" + createHeader(header++) + "<fs:GrayVol");
			writer.write(">");
			writer.write(ValueParser(_Grayvol,"float"));
			writer.write("</fs:GrayVol>");
			header--;
		}
		if (_Thickavg!=null){
			writer.write("\n" + createHeader(header++) + "<fs:ThickAvg");
			writer.write(">");
			writer.write(ValueParser(_Thickavg,"float"));
			writer.write("</fs:ThickAvg>");
			header--;
		}
		if (_Thickstd!=null){
			writer.write("\n" + createHeader(header++) + "<fs:ThickStd");
			writer.write(">");
			writer.write(ValueParser(_Thickstd,"float"));
			writer.write("</fs:ThickStd>");
			header--;
		}
		if (_Meancurv!=null){
			writer.write("\n" + createHeader(header++) + "<fs:MeanCurv");
			writer.write(">");
			writer.write(ValueParser(_Meancurv,"float"));
			writer.write("</fs:MeanCurv>");
			header--;
		}
		if (_Gauscurv!=null){
			writer.write("\n" + createHeader(header++) + "<fs:GausCurv");
			writer.write(">");
			writer.write(ValueParser(_Gauscurv,"float"));
			writer.write("</fs:GausCurv>");
			header--;
		}
		if (_Foldind!=null){
			writer.write("\n" + createHeader(header++) + "<fs:FoldInd");
			writer.write(">");
			writer.write(ValueParser(_Foldind,"float"));
			writer.write("</fs:FoldInd>");
			header--;
		}
		if (_Curvind!=null){
			writer.write("\n" + createHeader(header++) + "<fs:CurvInd");
			writer.write(">");
			writer.write(ValueParser(_Curvind,"float"));
			writer.write("</fs:CurvInd>");
			header--;
		}
	return true;
	}


	protected boolean hasXMLBodyContent(){
		if (_Numvert!=null) return true;
		if (_Surfarea!=null) return true;
		if (_Grayvol!=null) return true;
		if (_Thickavg!=null) return true;
		if (_Thickstd!=null) return true;
		if (_Meancurv!=null) return true;
		if (_Gauscurv!=null) return true;
		if (_Foldind!=null) return true;
		if (_Curvind!=null) return true;
		if(super.hasXMLBodyContent())return true;
		return false;
	}
}
