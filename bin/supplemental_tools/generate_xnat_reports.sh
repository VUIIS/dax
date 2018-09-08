PROJECT=WOODWARD_TCP,WoodwardPGPP,HeckersFEPH3T

Xnatreport -p "${PROJECT}" -c report_scan_`date "+%Y%m%d"`.csv --format \
	object_type,project_id,subject_label,session_label,scan_id,type,series_description,quality,note

Xnatreport -p "${PROJECT}" -c report_assr_`date "+%Y%m%d"`.csv --format \
	object_type,project_id,subject_label,session_label,assessor_label,proctype,procstatus,qcstatus,version

