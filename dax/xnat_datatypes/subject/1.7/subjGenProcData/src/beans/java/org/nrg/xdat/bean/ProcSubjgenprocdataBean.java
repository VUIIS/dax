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
public class ProcSubjgenprocdataBean extends XnatSubjectassessordataBean implements java.io.Serializable, org.nrg.xdat.model.ProcSubjgenprocdataI {
	public static final Logger logger = Logger.getLogger(ProcSubjgenprocdataBean.class);
	public static final String SCHEMA_ELEMENT_NAME="proc:subjGenProcData";

	public String getSchemaElementName(){
		return "subjGenProcData";
	}

	public String getFullSchemaElementName(){
		return "proc:subjGenProcData";
	}
	 private List<org.nrg.xdat.bean.ProcSubjgenprocdataStudyBean> _Includedstudies_study =new ArrayList<org.nrg.xdat.bean.ProcSubjgenprocdataStudyBean>();

	/**
	 * includedStudies/Study
	 * @return Returns an List of org.nrg.xdat.bean.ProcSubjgenprocdataStudyBean
	 */
	public <A extends org.nrg.xdat.model.ProcSubjgenprocdataStudyI> List<A> getIncludedstudies_study() {
		return (List<A>) _Includedstudies_study;
	}

	/**
	 * Sets the value for includedStudies/Study.
	 * @param v Value to Set.
	 */
	public void setIncludedstudies_study(ArrayList<org.nrg.xdat.bean.ProcSubjgenprocdataStudyBean> v){
		_Includedstudies_study=v;
	}

	/**
	 * Adds the value for includedStudies/Study.
	 * @param v Value to Set.
	 */
	public void addIncludedstudies_study(org.nrg.xdat.bean.ProcSubjgenprocdataStudyBean v){
		_Includedstudies_study.add(v);
	}

	/**
	 * includedStudies/Study
	 * Adds org.nrg.xdat.model.ProcSubjgenprocdataStudyI
	 */
	public <A extends org.nrg.xdat.model.ProcSubjgenprocdataStudyI> void addIncludedstudies_study(A item) throws Exception{
	_Includedstudies_study.add((org.nrg.xdat.bean.ProcSubjgenprocdataStudyBean)item);
	}

	/**
	 * Adds the value for includedStudies/Study.
	 * @param v Value to Set.
	 */
	public void addIncludedstudies_study(Object v){
		if (v instanceof org.nrg.xdat.bean.ProcSubjgenprocdataStudyBean)
			_Includedstudies_study.add((org.nrg.xdat.bean.ProcSubjgenprocdataStudyBean)v);
		else
			throw new IllegalArgumentException("Must be a valid org.nrg.xdat.bean.ProcSubjgenprocdataStudyBean");
	}

	//FIELD

	private String _Procstatus=null;

	/**
	 * @return Returns the procstatus.
	 */
	public String getProcstatus(){
		return _Procstatus;
	}

	/**
	 * Sets the value for procstatus.
	 * @param v Value to Set.
	 */
	public void setProcstatus(String v){
		_Procstatus=v;
	}

	//FIELD

	private String _Proctype=null;

	/**
	 * @return Returns the proctype.
	 */
	public String getProctype(){
		return _Proctype;
	}

	/**
	 * Sets the value for proctype.
	 * @param v Value to Set.
	 */
	public void setProctype(String v){
		_Proctype=v;
	}

	//FIELD

	private String _Procversion=null;

	/**
	 * @return Returns the procversion.
	 */
	public String getProcversion(){
		return _Procversion;
	}

	/**
	 * Sets the value for procversion.
	 * @param v Value to Set.
	 */
	public void setProcversion(String v){
		_Procversion=v;
	}

	//FIELD

	private String _Jobid=null;

	/**
	 * @return Returns the jobid.
	 */
	public String getJobid(){
		return _Jobid;
	}

	/**
	 * Sets the value for jobid.
	 * @param v Value to Set.
	 */
	public void setJobid(String v){
		_Jobid=v;
	}

	//FIELD

	private String _Walltimeused=null;

	/**
	 * @return Returns the walltimeused.
	 */
	public String getWalltimeused(){
		return _Walltimeused;
	}

	/**
	 * Sets the value for walltimeused.
	 * @param v Value to Set.
	 */
	public void setWalltimeused(String v){
		_Walltimeused=v;
	}

	//FIELD

	private Integer _Memusedmb=null;

	/**
	 * @return Returns the memusedmb.
	 */
	public Integer getMemusedmb(){
		return _Memusedmb;
	}

	/**
	 * Sets the value for proc:subjGenProcData/memusedmb.
	 * @param v Value to Set.
	 */
	public void setMemusedmb(Integer v) {
		_Memusedmb=v;
	}

	/**
	 * Sets the value for proc:subjGenProcData/memusedmb.
	 * @param v Value to Set.
	 */
	public void setMemusedmb(String v)  {
		_Memusedmb=formatInteger(v);
	}

	//FIELD

	private Date _Jobstartdate=null;

	/**
	 * @return Returns the jobstartdate.
	 */
	public Date getJobstartdate(){
		return _Jobstartdate;
	}

	/**
	 * Sets the value for jobstartdate.
	 * @param v Value to Set.
	 */
	public void setJobstartdate(Date v){
		_Jobstartdate=v;
	}

	/**
	 * Sets the value for jobstartdate.
	 * @param v Value to Set.
	 */
	public void setJobstartdate(Object v){
		throw new IllegalArgumentException();
	}

	/**
	 * Sets the value for jobstartdate.
	 * @param v Value to Set.
	 */
	public void setJobstartdate(String v)  {
		_Jobstartdate=formatDate(v);
	}

	//FIELD

	private String _Memused=null;

	/**
	 * @return Returns the memused.
	 */
	public String getMemused(){
		return _Memused;
	}

	/**
	 * Sets the value for memused.
	 * @param v Value to Set.
	 */
	public void setMemused(String v){
		_Memused=v;
	}

	//FIELD

	private String _Jobnode=null;

	/**
	 * @return Returns the jobnode.
	 */
	public String getJobnode(){
		return _Jobnode;
	}

	/**
	 * Sets the value for jobnode.
	 * @param v Value to Set.
	 */
	public void setJobnode(String v){
		_Jobnode=v;
	}

	//FIELD

	private String _Type=null;

	/**
	 * @return Returns the type.
	 */
	public String getType(){
		return _Type;
	}

	/**
	 * Sets the value for type.
	 * @param v Value to Set.
	 */
	public void setType(String v){
		_Type=v;
	}

	/**
	 * Sets the value for a field via the XMLPATH.
	 * @param v Value to Set.
	 */
	public void setDataField(String xmlPath,String v) throws BaseElement.UnknownFieldException{
		if (xmlPath.equals("procstatus")){
			setProcstatus(v);
		}else if (xmlPath.equals("proctype")){
			setProctype(v);
		}else if (xmlPath.equals("procversion")){
			setProcversion(v);
		}else if (xmlPath.equals("jobid")){
			setJobid(v);
		}else if (xmlPath.equals("walltimeused")){
			setWalltimeused(v);
		}else if (xmlPath.equals("memusedmb")){
			setMemusedmb(v);
		}else if (xmlPath.equals("jobstartdate")){
			setJobstartdate(v);
		}else if (xmlPath.equals("memused")){
			setMemused(v);
		}else if (xmlPath.equals("jobnode")){
			setJobnode(v);
		}else if (xmlPath.equals("type")){
			setType(v);
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
		if (xmlPath.equals("includedStudies/Study")){
			addIncludedstudies_study(v);
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
		if (xmlPath.equals("procstatus")){
			return getProcstatus();
		}else if (xmlPath.equals("proctype")){
			return getProctype();
		}else if (xmlPath.equals("procversion")){
			return getProcversion();
		}else if (xmlPath.equals("jobid")){
			return getJobid();
		}else if (xmlPath.equals("walltimeused")){
			return getWalltimeused();
		}else if (xmlPath.equals("memusedmb")){
			return getMemusedmb();
		}else if (xmlPath.equals("jobstartdate")){
			return getJobstartdate();
		}else if (xmlPath.equals("memused")){
			return getMemused();
		}else if (xmlPath.equals("jobnode")){
			return getJobnode();
		}else if (xmlPath.equals("type")){
			return getType();
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
		if (xmlPath.equals("includedStudies/Study")){
			return getIncludedstudies_study();
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
		if (xmlPath.equals("includedStudies/Study")){
			return "http://nrg.wustl.edu/proc:subjGenProcData_Study";
		}
		else{
			return super.getReferenceFieldName(xmlPath);
		}
	}

	/**
	 * Returns whether or not this is a reference field
	 */
	public String getFieldType(String xmlPath) throws BaseElement.UnknownFieldException{
		if (xmlPath.equals("includedStudies/Study")){
			return BaseElement.field_multi_reference;
		}else if (xmlPath.equals("procstatus")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("proctype")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("procversion")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("jobid")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("walltimeused")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("memusedmb")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("jobstartdate")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("memused")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("jobnode")){
			return BaseElement.field_data;
		}else if (xmlPath.equals("type")){
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
		all_fields.add("includedStudies/Study");
		all_fields.add("procstatus");
		all_fields.add("proctype");
		all_fields.add("procversion");
		all_fields.add("jobid");
		all_fields.add("walltimeused");
		all_fields.add("memusedmb");
		all_fields.add("jobstartdate");
		all_fields.add("memused");
		all_fields.add("jobnode");
		all_fields.add("type");
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
		writer.write("\n<proc:Longitudinal Processing");
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
		writer.write("\n</proc:Longitudinal Processing>");
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
		if (_Type!=null)
			map.put("type",ValueParser(_Type,"string"));
		//NOT REQUIRED FIELD

		return map;
	}


	protected boolean addXMLBody(java.io.Writer writer, int header) throws java.io.IOException{
		super.addXMLBody(writer,header);
		//REFERENCE FROM subjGenProcData -> subjectAssessorData
			int child0=0;
			int att0=0;
			child0+=_Includedstudies_study.size();
			if(child0>0 || att0>0){
				writer.write("\n" + createHeader(header++) + "<proc:includedStudies");
			if(child0==0){
				writer.write("/>");
			}else{
				writer.write(">");
		//REFERENCE FROM subjGenProcData -> includedStudies/Study
		java.util.Iterator iter1=_Includedstudies_study.iterator();
		while(iter1.hasNext()){
			org.nrg.xdat.bean.ProcSubjgenprocdataStudyBean child = (org.nrg.xdat.bean.ProcSubjgenprocdataStudyBean)iter1.next();
			writer.write("\n" + createHeader(header++) + "<proc:Study");
			child.addXMLAtts(writer);
			if(!child.getFullSchemaElementName().equals("proc:subjGenProcData_Study")){
				writer.write(" xsi:type=\"" + child.getFullSchemaElementName() + "\"");
			}
			if (child.hasXMLBodyContent()){
				writer.write(">");
				boolean return2 =child.addXMLBody(writer,header);
				if(return2){
					writer.write("\n" + createHeader(--header) + "</proc:Study>");
				}else{
					writer.write("</proc:Study>");
					header--;
				}
			}else {writer.write("/>");header--;}
		}
				writer.write("\n" + createHeader(--header) + "</proc:includedStudies>");
			}
			}

		if (_Procstatus!=null){
			writer.write("\n" + createHeader(header++) + "<proc:procstatus");
			writer.write(">");
			writer.write(ValueParser(_Procstatus,"string"));
			writer.write("</proc:procstatus>");
			header--;
		}
		if (_Proctype!=null){
			writer.write("\n" + createHeader(header++) + "<proc:proctype");
			writer.write(">");
			writer.write(ValueParser(_Proctype,"string"));
			writer.write("</proc:proctype>");
			header--;
		}
		if (_Procversion!=null){
			writer.write("\n" + createHeader(header++) + "<proc:procversion");
			writer.write(">");
			writer.write(ValueParser(_Procversion,"string"));
			writer.write("</proc:procversion>");
			header--;
		}
		if (_Jobid!=null){
			writer.write("\n" + createHeader(header++) + "<proc:jobid");
			writer.write(">");
			writer.write(ValueParser(_Jobid,"string"));
			writer.write("</proc:jobid>");
			header--;
		}
		if (_Walltimeused!=null){
			writer.write("\n" + createHeader(header++) + "<proc:walltimeused");
			writer.write(">");
			writer.write(ValueParser(_Walltimeused,"string"));
			writer.write("</proc:walltimeused>");
			header--;
		}
		if (_Memusedmb!=null){
			writer.write("\n" + createHeader(header++) + "<proc:memusedmb");
			writer.write(">");
			writer.write(ValueParser(_Memusedmb,"integer"));
			writer.write("</proc:memusedmb>");
			header--;
		}
		if (_Jobstartdate!=null){
			writer.write("\n" + createHeader(header++) + "<proc:jobstartdate");
			writer.write(">");
			writer.write(ValueParser(_Jobstartdate,"date"));
			writer.write("</proc:jobstartdate>");
			header--;
		}
		if (_Memused!=null){
			writer.write("\n" + createHeader(header++) + "<proc:memused");
			writer.write(">");
			writer.write(ValueParser(_Memused,"string"));
			writer.write("</proc:memused>");
			header--;
		}
		if (_Jobnode!=null){
			writer.write("\n" + createHeader(header++) + "<proc:jobnode");
			writer.write(">");
			writer.write(ValueParser(_Jobnode,"string"));
			writer.write("</proc:jobnode>");
			header--;
		}
	return true;
	}


	protected boolean hasXMLBodyContent(){
			if(_Includedstudies_study.size()>0)return true;
		if (_Procstatus!=null) return true;
		if (_Proctype!=null) return true;
		if (_Procversion!=null) return true;
		if (_Jobid!=null) return true;
		if (_Walltimeused!=null) return true;
		if (_Memusedmb!=null) return true;
		if (_Jobstartdate!=null) return true;
		if (_Memused!=null) return true;
		if (_Jobnode!=null) return true;
		if(super.hasXMLBodyContent())return true;
		return false;
	}
}
