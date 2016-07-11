White_Matter_Stamper
====================

* **What does it do?**

* **Requirements**

* **Resources**
| OUTLOG - STDOUT and STDERR from the process on the grid
| PBS - The DRMAA compliant batch script to run the job
| PDF - The output PDF file for determining QA status
| SNAPSHOTS - Thumbnail of the first page of the PDF resource for viewing on XNAT
| Intra_Session_Reg -
| Peripheral_White_Matter_Labels -
| WM_LABELS -
| All_RAW_EVE_Labels -
| STATS -

* **References**

* **Version History**
<revision> <name> <date> <lines changed>
r2960 | bdb | 2015-07-06 10:34:37 -0500 (Mon, 06 Jul 2015) | 1 line
	Add suffix_proc option for dax 0.3.1, also change vX.X.X to vX_X_X
r2682 | yben | 2015-05-13 10:58:49 -0500 (Wed, 13 May 2015) | 1 line
	settinge verbose to true
r2655 | yben | 2015-05-11 09:02:40 -0500 (Mon, 11 May 2015) | 1 line
	Switching Modules/Processors/spiders for the version 0.3.0 of dax package (generic functions build in dax)
r1992 | yben | 2014-10-16 12:46:53 -0500 (Thu, 16 Oct 2014) | 2 lines
	Removing MASIMATLAB_PATH called from dax and instead getting path from VUIIS_path_settings.py in processors/
	Adding all the path to processors/VUIIS_path_settings.py for each imaging software used.
r1979 | yben | 2014-10-10 15:07:51 -0500 (Fri, 10 Oct 2014) | 2 lines
	Adding "-singleCompThread" to every matlab called from regular spiders.
	Fixing bedpost problem (using fa.nii instead of dti)
r1903 | yben | 2014-08-15 11:42:56 -0500 (Fri, 15 Aug 2014) | 2 lines
	Final commit to work with the new package dax.
	Fix some imports for modules/spiders/processors/Xnat_tools (fs)
r1901 | yben | 2014-08-15 09:05:31 -0500 (Fri, 15 Aug 2014) | 4 lines
	Important commit:
	1) Adding new spiders using the new template
	2) Switching old spiders to new template
	3) Using new package dax
r1688 | yben | 2014-04-15 08:56:58 -0500 (Tue, 15 Apr 2014) | 1 line
	typo error
r1686 | plassaaj | 2014-04-14 13:50:56 -0500 (Mon, 14 Apr 2014) | 1 line
r1502 | yben | 2014-02-19 08:44:06 -0600 (Wed, 19 Feb 2014) | 1 line
	Error in the call of the function to add_file for EndOfSpider
r1416 | masispider | 2014-02-01 10:27:50 -0600 (Sat, 01 Feb 2014) | 1 line
	Increase White Matter Stamper walltime to 10hours to be sure and Fix the last issues with spiders
r1415 | masispider | 2014-01-31 18:15:26 -0600 (Fri, 31 Jan 2014) | 1 line
	Intra / nonrigid registration spider in fixing mode like EVE
r1401 | yben | 2014-01-30 11:21:11 -0600 (Thu, 30 Jan 2014) | 1 line
	switching one os.path.isdir to os.path.isfile
r1400 | yben | 2014-01-30 11:19:42 -0600 (Thu, 30 Jan 2014) | 1 line
	Find reg_aladin command in the folder if given or use the direct path if reg_aladin is a file (full path to reg_aladin software given in the options)
r1399 | yben | 2014-01-30 11:03:43 -0600 (Thu, 30 Jan 2014) | 1 line
	Removing masi-fusion from the spider/processor for White Matter Stamper. Everything is in masimatlab.
r1392 | masispider | 2014-01-29 15:33:30 -0600 (Wed, 29 Jan 2014) | 1 line
	Editing Spider nonrigid and WhiteMatter
r1383 | masispider | 2014-01-29 10:17:15 -0600 (Wed, 29 Jan 2014) | 1 line
	Spider_intra_sess_reg fixed / working on nonrigid spider
r1375 | masispider | 2014-01-28 13:40:54 -0600 (Tue, 28 Jan 2014) | 1 line
	Debugging WMS
r1371 | yben | 2014-01-28 11:43:05 -0600 (Tue, 28 Jan 2014) | 1 line
	Debugging WMS
r1370 | masispider | 2014-01-28 10:28:23 -0600 (Tue, 28 Jan 2014) | 1 line
	fixing EVE spider and processors
r1369 | masispider | 2014-01-27 16:16:58 -0600 (Mon, 27 Jan 2014) | 1 line
	fixing more error on WMS spider
r1367 | yben | 2014-01-27 13:47:41 -0600 (Mon, 27 Jan 2014) | 1 line
	Fixing some directory path error in WMS spider.
r1365 | masispider | 2014-01-27 10:03:16 -0600 (Mon, 27 Jan 2014) | 1 line
	Fixing WM spider
r1364 | masispider | 2014-01-27 08:26:42 -0600 (Mon, 27 Jan 2014) | 1 line
	fixing dtiqa saving the FA map
r1355 | yben | 2014-01-24 13:19:49 -0600 (Fri, 24 Jan 2014) | 1 line
	Debugging White_Matter_Stamper to work on only one dtiqa and Multi Atlas per session (if several, set one to passed)
r1301 | yben | 2014-01-15 15:23:21 -0600 (Wed, 15 Jan 2014) | 1 line
	Debugging ...
r1299 | yben | 2014-01-15 08:53:00 -0600 (Wed, 15 Jan 2014) | 1 line
	Debugging ...
r1294 | yben | 2014-01-14 17:39:45 -0600 (Tue, 14 Jan 2014) | 3 lines
	Changing tbss and tracula processor to check the passed in the status in lower case for both if someone set it to passed instead of Passed, it will still work.
	Working on WMStamper processor to make it work for any dtiqa complete with a FA and one multi_Atlas working.
r1259 | plassaaj | 2014-01-09 08:41:15 -0600 (Thu, 09 Jan 2014) | 2 lines
	updated white matter spider
r1258 | plassaaj | 2014-01-09 08:38:55 -0600 (Thu, 09 Jan 2014) | 2 lines
	updated white matter spider
r1234 | plassaaj | 2013-12-20 16:16:02 -0600 (Fri, 20 Dec 2013) | 1 line
	Updated white matter spider to work
r1231 | plassaaj | 2013-12-20 15:59:16 -0600 (Fri, 20 Dec 2013) | 1 line
	Updated White Matter Spider
r1119 | plassaaj | 2013-12-02 12:23:43 -0600 (Mon, 02 Dec 2013) | 1 line
	Added White Matter Processors

**Current Contact Person**
<date> <name> <email / URL> 

	
	
