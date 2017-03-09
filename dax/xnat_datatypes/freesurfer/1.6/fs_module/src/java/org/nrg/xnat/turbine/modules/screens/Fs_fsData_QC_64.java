package org.nrg.xnat.turbine.modules.screens;


import java.io.File;
import java.util.Iterator;

import org.apache.turbine.util.RunData;
import org.apache.velocity.context.Context;
import org.nrg.xdat.om.FsFsdata;
import org.nrg.xdat.om.XnatImagesessiondata;
import org.nrg.xdat.om.XnatResourcecatalog;
import org.nrg.xdat.turbine.modules.screens.SecureReport;

public class Fs_fsData_QC_64 extends SecureReport {
        public static org.apache.log4j.Logger logger = org.apache.log4j.Logger.getLogger(Fs_fsData_QC_64.class);
    public void finalProcessing(RunData data, Context context) {
        try{
            org.nrg.xdat.om.FsFsdata fs = new org.nrg.xdat.om.FsFsdata(item);
            context.put("fs",fs); 
            XnatImagesessiondata om = fs.getImageSessionData();
            context.put("mr",om);
        } catch(Exception e){
            logger.debug("Fs_fsData_QC_64", e);
        }
    }
}
