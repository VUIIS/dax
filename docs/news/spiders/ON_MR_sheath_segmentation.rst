ON_MR_sheath_segmentation
=========================

* **What does it do?**

* **Requirements**

* **Resources** *
| OUTLOG - STDOUT and STDERR from the process on the grid
| PBS - The DRMAA compliant batch script to run the job
| PDF - The output PDF file for determining QA status
| SNAPSHOTS - Thumbnail of the first page of the PDF resource for viewing on XNAT
| RADII -
| MATLAB -

* **References**

* **Version History**
<revision> <name> <date> <lines changed>

r3167 | robharrigan | 2015-08-11 13:13:30 -0500 (Tue, 11 Aug 2015) | 3 lines
	fixed difference in centroid naming
r3166 | robharrigan | 2015-08-11 11:08:51 -0500 (Tue, 11 Aug 2015) | 1 line
	fixed what ben broke
r3165 | robharrigan | 2015-08-11 10:14:57 -0500 (Tue, 11 Aug 2015) | 1 line
	switched to better pdf for sheath
r3032 | robharrigan | 2015-07-16 08:13:40 -0500 (Thu, 16 Jul 2015) | 1 line
	fixed bug created by argparse magic
r2960 | bdb | 2015-07-06 10:34:37 -0500 (Mon, 06 Jul 2015) | 1 line
	Add suffix_proc option for dax 0.3.1, also change vX.X.X to vX_X_X
r2854 | masispider | 2015-06-10 09:05:24 -0500 (Wed, 10 Jun 2015) | 1 line
	fixed pdf call in sheath spider
r2823 | robharrigan | 2015-06-08 14:08:15 -0500 (Mon, 08 Jun 2015) | 1 line
	updating pdf call
r2655 | yben | 2015-05-11 09:02:40 -0500 (Mon, 11 May 2015) | 1 line
	Switching Modules/Processors/spiders for the version 0.3.0 of dax package (generic functions build in dax)
r2196 | parvatp | 2015-02-09 13:58:24 -0600 (Mon, 09 Feb 2015) | 1 line
	string comparison fix SMD
r2194 | robharrigan | 2015-02-09 12:03:06 -0600 (Mon, 09 Feb 2015) | 1 line
	saving centroids
r1992 | yben | 2014-10-16 12:46:53 -0500 (Thu, 16 Oct 2014) | 2 lines
	Removing MASIMATLAB_PATH called from dax and instead getting path from VUIIS_path_settings.py in processors/
	Adding all the path to processors/VUIIS_path_settings.py for each imaging software used.
r1979 | yben | 2014-10-10 15:07:51 -0500 (Fri, 10 Oct 2014) | 2 lines
	Adding "-singleCompThread" to every matlab called from regular spiders.
	Fixing bedpost problem (using fa.nii instead of dti)
r1932 | robharrigan | 2014-09-15 15:33:51 -0500 (Mon, 15 Sep 2014) | 1 line
	finally fixed verbose behavior
r1931 | robharrigan | 2014-09-15 15:29:46 -0500 (Mon, 15 Sep 2014) | 1 line
	fixed pdf verbosity
r1930 | robharrigan | 2014-09-15 15:28:49 -0500 (Mon, 15 Sep 2014) | 1 line
	fixing output
r1929 | robharrigan | 2014-09-15 15:11:19 -0500 (Mon, 15 Sep 2014) | 2 lines
	fixed verbosity option
r1928 | robharrigan | 2014-09-15 15:04:11 -0500 (Mon, 15 Sep 2014) | 2 lines
	fixed verbosity option
r1927 | robharrigan | 2014-09-15 14:55:57 -0500 (Mon, 15 Sep 2014) | 1 line
	updated subprocess call
r1926 | masispider | 2014-09-15 14:32:53 -0500 (Mon, 15 Sep 2014) | 1 line
	updated sheath segmentation to get stdout
r1903 | yben | 2014-08-15 11:42:56 -0500 (Fri, 15 Aug 2014) | 2 lines
	Final commit to work with the new package dax.
	Fix some imports for modules/spiders/processors/Xnat_tools (fs)
r1901 | yben | 2014-08-15 09:05:31 -0500 (Fri, 15 Aug 2014) | 4 lines
	Important Commit:
	1) Adding new spiders using the new template
	2) Switching old spiders to new template
	3) Using new package dax
r1836 | robharrigan | 2014-06-13 09:15:52 -0500 (Fri, 13 Jun 2014) | 1 line
	turned off smoothing on interp
r1832 | robharrigan | 2014-06-12 15:57:50 -0500 (Thu, 12 Jun 2014) | 1 line
	fixed ants stuff
r1831 | robharrigan | 2014-06-12 15:51:25 -0500 (Thu, 12 Jun 2014) | 1 line
	added resampling to spider
r1824 | yben | 2014-06-10 11:39:24 -0500 (Tue, 10 Jun 2014) | 1 line
	Switching print to sys.stdout.write to see outlog from spider and matlab in the right order
r1821 | robharrigan | 2014-06-10 09:45:45 -0500 (Tue, 10 Jun 2014) | 1 line
	updated version which saves all radius results
r1790 | robharrigan | 2014-06-03 10:34:09 -0500 (Tue, 03 Jun 2014) | 1 line
	fixing bugs
r1788 | robharrigan | 2014-06-03 10:22:29 -0500 (Tue, 03 Jun 2014) | 1 line
	minor fixes and verbosity
r1784 | robharrigan | 2014-06-03 10:06:26 -0500 (Tue, 03 Jun 2014) | 1 line
	pdf path
r1781 | robharrigan | 2014-06-03 09:49:59 -0500 (Tue, 03 Jun 2014) | 1 line
	added PDF to sheath seg
r1779 | robharrigan | 2014-06-03 07:28:25 -0500 (Tue, 03 Jun 2014) | 1 line
	changed resource to RADII, lowered resources requested
r1763 | robharrigan | 2014-05-29 13:03:55 -0500 (Thu, 29 May 2014) | 1 line
	fixed trees loading
r1758 | robharrigan | 2014-05-28 11:09:17 -0500 (Wed, 28 May 2014) | 1 line
	added sheath spider

**Current Contact Person**
<date> <name> <email / URL> 

	
	
