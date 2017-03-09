/*
 * GENERATED FILE
 * Created on Tue Oct 11 11:43:59 BST 2016
 *
 */
package org.nrg.xdat.om.base;
import org.nrg.xdat.om.base.auto.*;
import org.nrg.xft.*;
import org.nrg.xft.security.UserI;

import java.util.*;

/**
 * @author XDAT
 *
 *//*
 ******************************** 
 * DO NOT MODIFY THIS FILE HERE
 *
 * TO MODIFY, COPY THIS FILE to src/main/java/org/nrg/xdat/om/base/ and modify it there 
 ********************************/
@SuppressWarnings({"unchecked","rawtypes"})
public abstract class BaseProcGenprocdata extends AutoProcGenprocdata {

	public BaseProcGenprocdata(ItemI item)
	{
		super(item);
	}

	public BaseProcGenprocdata(UserI user)
	{
		super(user);
	}

	/*
	 * @deprecated Use BaseProcGenprocdata(UserI user)
	 **/
	public BaseProcGenprocdata()
	{}

	public BaseProcGenprocdata(Hashtable properties, UserI user)
	{
		super(properties,user);
	}

}
