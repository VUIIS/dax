/*
 * GENERATED FILE
 * Created on Tue Oct 11 11:43:59 BST 2016
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
public class ProcGenprocdataBean extends XnatImageassessordataBean implements java.io.Serializable, org.nrg.xdat.model.ProcGenprocdataI {
	public static final Logger logger = Logger.getLogger(ProcGenprocdataBean.class);
	public static final String SCHEMA_ELEMENT_NAME="proc:genProcData";

	public String getSchemaElementName(){
		return "genProcData";
	}

	public String getFullSchemaElementName(){
		return "proc:genProcData";
	}
	 private List<org.nrg.xdat.bean.ProcGenprocdataScanBean> _Scans_scan =new ArrayList<org.nrg.xdat.bean.ProcGenprocdataScanBean>();

	/**
	 * scans/scan
	 * @return Returns an List of org.nrg.xdat.bean.ProcGenprocdataScanBean
	 */
	public <A extends org.nrg.xdat.model.ProcGenprocdataScanI> List<A> getScans_scan() {
		return (List<A>) _Scans_scan;
	}

	/**
	 * Sets the value for scans/scan.
	 * @param v Value to Set.
	 */
	public void setScans_scan(ArrayList<org.nrg.xdat.bean.ProcGenprocdataScanBean> v){
		_Scans_scan=v;
	}

	/**
	 * Adds the value for scans/scan.
	 * @param v Value to Set.
	 */
	public void addScans_scan(org.nrg.xdat.bean.ProcGenprocdataScanBean v){
		_Scans_scan.add(v);
	}

	/**
	 * scans/scan
	 * Adds org.nrg.xdat.model.ProcGenprocdataScanI
	 */
	public <A extends org.nrg.xdat.model.ProcGenprocdataScanI> void addScans_scan(A item) throws Exception{
	_Scans_scan.add((org.nrg.xdat.bean.ProcGenprocdataScanBean)item);
	}

	/**
	 * Adds the value for scans/scan.
	 * @param v Value to Set.
	 */
	public void addScans_scan(Object v){
		if (v instanceof org.nrg.xdat.bean.ProcGenprocdataScanBean)
			_Scans_scan.add((org.nrg.xdat.bean.ProcGenprocdataScanBean)v);
		else
			throw new IllegalArgumentException("Must be a valid org.nrg.xdat.bean.ProcGenprocdataScanBean");
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
	 * Sets the value for proc:genProcData/memusedmb.
	 * @param v Value to Set.
	 */
	public void setMemusedmb(Integer v) {
		_Memusedmb=v;
	}

	/**
	 * Sets the value for proc:genProcData/memusedmb.
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
		if (xmlPath.equals("scans/scan")){
			addScans_scan(v);
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
		if (xmlPath.equals("scans/scan")){
			return getScans_scan();
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
		if (xmlPath.equals("scans/scan")){
			return "http://nrg.wustl.edu/proc:genProcData_scan";
		}
		else{
			return super.getReferenceFieldName(xmlPath);
		}
	}

	/**
	 * Returns whether or not this is a reference field
	 */
	public String getFieldType(String xmlPath) throws BaseElement.UnknownFieldException{
		if (xmlPath.equals("scans/scan")){
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
		all_fields.add("scans/scan");
		all_fields.add("procstatus");
		all_fields.add("proctype");
		all_fields.add("procversion");
		all_fields.add("jobid");
		all_fields.add("walltimeused");
		all_fields.add("memusedmb");
		all_fields.add("jobstartdate");
		all_fields.add("memused");
		all_fields.add("jobnode");
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
		writer.write("\n<proc:Processing");
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
		writer.write("\n</proc:Processing>");
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
		return map;
	}


	protected boolean addXMLBody(java.io.Writer writer, int header) throws java.io.IOException{
		super.addXMLBody(writer,header);
		//REFERENCE FROM genProcData -> imageAssessorData
			int child0=0;
			int att0=0;
			child0+=_Scans_scan.size();
			if(child0>0 || att0>0){
				writer.write("\n" + createHeader(header++) + "<proc:scans");
			if(child0==0){
				writer.write("/>");
			}else{
				writer.write(">");
		//REFERENCE FROM genProcData -> scans/scan
		java.util.Iterator iter1=_Scans_scan.iterator();
		while(iter1.hasNext()){
			org.nrg.xdat.bean.ProcGenprocdataScanBean child = (org.nrg.xdat.bean.ProcGenprocdataScanBean)iter1.next();
			writer.write("\n" + createHeader(header++) + "<proc:scan");
			child.addXMLAtts(writer);
			if(!child.getFullSchemaElementName().equals("proc:genProcData_scan")){
				writer.write(" xsi:type=\"" + child.getFullSchemaElementName() + "\"");
			}
			if (child.hasXMLBodyContent()){
				writer.write(">");
				boolean return2 =child.addXMLBody(writer,header);
				if(return2){
					writer.write("\n" + createHeader(--header) + "</proc:scan>");
				}else{
					writer.write("</proc:scan>");
					header--;
				}
			}else {writer.write("/>");header--;}
		}
				writer.write("\n" + createHeader(--header) + "</proc:scans>");
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
			if(_Scans_scan.size()>0)return true;
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
