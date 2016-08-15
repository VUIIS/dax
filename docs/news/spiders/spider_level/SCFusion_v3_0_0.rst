SCFusion_v3_0_0
===============

* **What does it do?**

* **Requirements**

* **Resources**
| OUTLOG - STDOUT and STDERR from the process on the grid
| PBS - The DRMAA compliant batch script to run the job
| PDF - The output PDF file for determining QA status
| SNAPSHOTS - Thumbnail of the first page of the PDF resource for viewing on XNAT
| init -
| info -
| aasmseg -
| jlfseg -
| map -
| QA -
| SEG -
| STATS -
| MATLAB -

* **References**

* **Version History**
<revision> <name> <date> <lines changed>

r4052 | damons | 2016-01-05 14:00:26 -0600 (Tue, 05 Jan 2016) | 1 line
	switch to untouch since we just need to know size
r4050 | damons | 2016-01-05 13:36:22 -0600 (Tue, 05 Jan 2016) | 1 line
	dont gunzip
r4049 | damons | 2016-01-05 13:28:43 -0600 (Tue, 05 Jan 2016) | 1 line
	remove unused arg and re-route the data_dir which is apparently the input directory
r4048 | damons | 2016-01-04 16:08:47 -0600 (Mon, 04 Jan 2016) | 1 line
	new scv3 spider using zhoubing's magic
r3983 | damons | 2015-12-07 10:19:26 -0600 (Mon, 07 Dec 2015) | 1 line
	paths are not intelligentaly joined. hard coding as a bandaid
r3733 | damons | 2015-11-02 08:29:50 -0600 (Mon, 02 Nov 2015) | 1 line
	i got lied to. atlases are not in masimatlab
r3732 | damons | 2015-11-02 08:25:21 -0600 (Mon, 02 Nov 2015) | 1 line
	toast the directory if it runs on the same node twice
r3728 | damons | 2015-10-31 11:41:46 -0500 (Sat, 31 Oct 2015) | 1 line
	needs data_dir for pdf
r3726 | damons | 2015-10-31 11:14:42 -0500 (Sat, 31 Oct 2015) | 1 line
	string formatting hell
r3725 | damons | 2015-10-31 11:08:44 -0500 (Sat, 31 Oct 2015) | 1 line
	outputs not done, but everything else looks ok

**Current Contact Person**
<date> <name> <email / URL> 

	
	
