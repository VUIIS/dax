/*
 * GENERATED FILE
 * Created on Tue Oct 11 11:22:11 BST 2016
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
public abstract class BaseFsFsdata extends AutoFsFsdata {

	public BaseFsFsdata(ItemI item)
	{
		super(item);
	}

	public BaseFsFsdata(UserI user)
	{
		super(user);
	}

	/*
	 * @deprecated Use BaseFsFsdata(UserI user)
	 **/
	public BaseFsFsdata()
	{}

	public BaseFsFsdata(Hashtable properties, UserI user)
	{
		super(properties,user);
	}

}
