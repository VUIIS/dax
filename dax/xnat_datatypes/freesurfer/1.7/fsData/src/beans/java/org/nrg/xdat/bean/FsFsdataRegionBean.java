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
public class FsFsdataRegionBean extends BaseElement implements java.io.Serializable, org.nrg.xdat.model.FsFsdataRegionI {
	public static final Logger logger = Logger.getLogger(FsFsdataRegionBean.class);
	public static final String SCHEMA_ELEMENT_NAME="fs:fsData_region";

	public String getSchemaElementName(){
		return "fsData_region";
	}

	public String getFullSchemaElementName(){
		return "fs:fsData_region";
	}

	//FIELD

	private Double _Nvoxels=null;

	/**
	 * @return Returns the NVoxels.
	 */
	public Double getNvoxels() {
		return _Nvoxels;
	}

	/**
	 * Sets the value for NVoxels.
	 * @param v Value to Set.
	 */
	public void setNvoxels(Double v){
		_Nvoxels=v;
	}

	/**
	 * Sets the value for NVoxels.
	 * @param v Value to Set.
	 */
	public void setNvoxels(String v)  {
		_Nvoxels=formatDouble(v);
	}

	//FIELD

	private Double _Volume=null;

	/**
	 * @return Returns the Volume.
	 */
	public Double getVolume() {
		return _Volume;
	}

	/**
	 * Sets the value for Volume.
	 * @param v Value to Set.
	 */
	public void setVolume(Double v){
		_Volume=v;
	}

	/**
	 * Sets the value for Volume.
	 * @param v Value to Set.
	 */
	public void setVolume(String v)  {
		_Volume=formatDouble(v);
	}

	//FIELD

	private Double _Normmean=null;

	/**
	 * @return Returns the normMean.
	 */
	public Double getNormmean() {
		return _Normmean;
	}

	/**
	 * Sets the value for normMean.
	 * @param v Value to Set.
	 */
	public void setNormmean(Double v){
		_Normmean=v;
	}

	/**
	 * Sets the value for normMean.
	 * @param v Value to Set.
	 */
	public void setNormmean(String v)  {
		_Normmean=formatDouble(v);
	}

	//FIELD

	private Double _Normstddev=null;

	/**
	 * @return Returns the normStdDev.
	 */
	public Double getNormstddev() {
		return _Normstddev;
	}

	/**
	 * Sets the value for normStdDev.
	 * @param v Value to Set.
	 */
	public void setNormstddev(Double v){
		_Normstddev=v;
	}

	/**
	 * Sets the value for normStdDev.
	 * @param v Value to Set.
	 */
	public void setNormstddev(String v)  {
		_Normstddev=formatDouble(v);
	}

	//FIELD

	private Double _Normmin=null;

	/**
	 * @return Returns the normMin.
	 */
	public Double getNormmin() {
		return _Normmin;
	}

	/**
	 * Sets the value for normMin.
	 * @param v Value to Set.
	 */
	public void setNormmin(Double v){
		_Normmin=v;
	}

	/**
	 * Sets the value for normMin.
	 * @param v Value to Set.
	 */
	public void setNormmin(String v)  {
		_Normmin=formatDouble(v);
	}

	//FIELD

	private Double _Normmax=null;

	/**
	 * @return Returns the normMax.
	 */
	public Double getNormmax() {
		return _Normmax;
	}

	/**
	 * Sets the value for normMax.
	 * @param v Value to Set.
	 */
	public void setNormmax(Double v){
		_Normmax=v;
	}

	/**
	 * Sets the value for normMax.
	 * @param v Value to Set.
	 */
	public void setNormmax(String v)  {
		_Normmax=formatDouble(v);
	}

	//FIELD

	private Double _Normrange=null;

	/**
	 * @return Returns the normRange.
	 */
	public Double getNormrange() {
		return _Normrange;
	}

	/**
	 * Sets the value for normRange.
	 * @param v Value to Set.
	 */
	public void setNormrange(Double v){
		_Normrange=v;
	}

	/**
	 * Sets the value for normRange.
	 * @param v Value to Set.
	 */
	public void setNormrange(String v)  {
		_Normrange=formatDouble(v);
	}

	//FIELD

	private String _Segid=null;

	/**
	 * @return Returns the SegId.
	 */
	public String getSegid(){
		return _Segid;
	}

	/**
	 * Sets the value for SegId.
	 * @param v Value to Set.
	 */
	public void setSegid(String v){
		_Segid=v;
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

	private String _Hemisphere=null;

	/**
	 * @return Returns the hemisphere.
	 */
	public String getHemisphere(){
		return _Hemisphere;
	}

	/**
	 * Sets the value for hemisphere.
	 * @param v Value to Set.
	 */
	public void setHemisphere(String v){
		_Hemisphere=v;
	}

	//FIELD

	private Integer _FsFsdataVolRegionId=null;

	/**
	 * @return Returns the fs_fsData_vol_region_id.
	 */
	public Integer getFsFsdataVolRegionId() {
		return _FsFsdataVolRegionId;
	}

	/**
	 * Sets the value for fs_fsData_vol_region_id.
	 * @param v Value to Set.
	 */
	public void setFsFsdataVolRegionId(Integer v){
		_FsFsdataVolRegionId=v;
	}

	/**
	 * Sets the value for a field via the XMLPATH.
	 * @param v Value to Set.
	 */
	public void setDataField(String xmlPath,String v) throws BaseElement.UnknownFieldException{
		if (xmlPath.equals("NVoxels")){
			setNvoxels(v);
		}else if (xmlPath.equals("Volume")){
			setVolume(v);
		}else if (xmlPath.equals("normMean")){
			setNormmean(v);
		}else if (xmlPath.equals("normStdDev")){
			setNormstddev(v);
		}else if (xmlPath.equals("normMin")){
			setNormmin(v);
		}else if (xmlPath.equals("normMax")){
			setNormmax(v);
		}else if (xmlPath.equals("normRange")){
			setNormrange(v);
		}else if (xmlPath.equals("SegId")){
			setSegid(v);
		}else if (xmlPath.equals("name")){
			setName(v);
		}else if (xmlPath.equals("hemisphere")){
			setHemisphere(v);
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
		if (xmlPath.equals("NVoxels")){
			return getNvoxels();
		}else if (xmlPath.equals("Volume")){
			return getVolume();
		}else if (xmlPath.equals("normMean")){
			return getNormmean();
		}else if (xmlPath.equals("normStdDev")){
			return getNormstddev();
		}else if (xmlPath.equals("normMin")){
			return getNormmin();
		}else if (xmlPath.equals("normMax")){
			return getNormmax();
		}else if (xmlPath.equals("normRange")){
			return getNormrange();
		}else if (xmlPath.equals("SegId")){
			return getSegid();
		}else if (xmlPath.equals("name")){
			return getName();
		}else if (xmlPath.equals("hemisphere")){
			return getHemisphere();
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
		if (xmlPath.equals("NVoxels")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("Volume")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("normMean")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("normStdDev")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("normMin")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("normMax")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("normRange")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("SegId")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("name")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("hemisphere")){
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
		all_fields.add("NVoxels");
		all_fields.add("Volume");
		all_fields.add("normMean");
		all_fields.add("normStdDev");
		all_fields.add("normMin");
		all_fields.add("normMax");
		all_fields.add("normRange");
		all_fields.add("SegId");
		all_fields.add("name");
		all_fields.add("hemisphere");
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
		writer.write("\n<fs:fsData_region");
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
		writer.write("\n</fs:fsData_region>");
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
		if (_Segid!=null)
			map.put("SegId",ValueParser(_Segid,"string"));
		//NOT REQUIRED FIELD

		if (_Name!=null)
			map.put("name",ValueParser(_Name,"string"));
		else map.put("name","");//REQUIRED FIELD

		if (_Hemisphere!=null)
			map.put("hemisphere",ValueParser(_Hemisphere,"string"));
		//NOT REQUIRED FIELD

		return map;
	}


	protected boolean addXMLBody(java.io.Writer writer, int header) throws java.io.IOException{
		super.addXMLBody(writer,header);
		if (_Nvoxels!=null){
			writer.write("\n" + createHeader(header++) + "<fs:NVoxels");
			writer.write(">");
			writer.write(ValueParser(_Nvoxels,"float"));
			writer.write("</fs:NVoxels>");
			header--;
		}
		if (_Volume!=null){
			writer.write("\n" + createHeader(header++) + "<fs:Volume");
			writer.write(">");
			writer.write(ValueParser(_Volume,"float"));
			writer.write("</fs:Volume>");
			header--;
		}
		if (_Normmean!=null){
			writer.write("\n" + createHeader(header++) + "<fs:normMean");
			writer.write(">");
			writer.write(ValueParser(_Normmean,"float"));
			writer.write("</fs:normMean>");
			header--;
		}
		if (_Normstddev!=null){
			writer.write("\n" + createHeader(header++) + "<fs:normStdDev");
			writer.write(">");
			writer.write(ValueParser(_Normstddev,"float"));
			writer.write("</fs:normStdDev>");
			header--;
		}
		if (_Normmin!=null){
			writer.write("\n" + createHeader(header++) + "<fs:normMin");
			writer.write(">");
			writer.write(ValueParser(_Normmin,"float"));
			writer.write("</fs:normMin>");
			header--;
		}
		if (_Normmax!=null){
			writer.write("\n" + createHeader(header++) + "<fs:normMax");
			writer.write(">");
			writer.write(ValueParser(_Normmax,"float"));
			writer.write("</fs:normMax>");
			header--;
		}
		if (_Normrange!=null){
			writer.write("\n" + createHeader(header++) + "<fs:normRange");
			writer.write(">");
			writer.write(ValueParser(_Normrange,"float"));
			writer.write("</fs:normRange>");
			header--;
		}
	return true;
	}


	protected boolean hasXMLBodyContent(){
		if (_Nvoxels!=null) return true;
		if (_Volume!=null) return true;
		if (_Normmean!=null) return true;
		if (_Normstddev!=null) return true;
		if (_Normmin!=null) return true;
		if (_Normmax!=null) return true;
		if (_Normrange!=null) return true;
		if(super.hasXMLBodyContent())return true;
		return false;
	}
}
