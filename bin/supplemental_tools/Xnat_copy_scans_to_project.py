#!/usr/bin/env python

from dax import XnatUtils
import argparse
import tempfile

parser = argparse.ArgumentParser()
parser.add_argument('--srcproj',help='Source project',required=True)
parser.add_argument('--srcsubj',help='Source subject',required=True)
parser.add_argument('--srcsess',help='Source session',required=True)
parser.add_argument('--dstproj',help='Destination project',required=True)
parser.add_argument('--dstsubj',help='Destination subject',required=True)
parser.add_argument('--dstsess',help='Destination session',required=True)
args = parser.parse_args()

with XnatUtils.get_interface() as xnat:
	srcscans = xnat.get_scans(args.srcproj,args.srcsubj,args.srcsess)
	for srcscan in srcscans:

		# Create new scan or bail if it already exists
		dstscan = xnat.select_scan(args.dstproj,args.dstsubj,args.dstsess,
			f'{args.srcsess}_{srcscan["scan_id"]}')
		if dstscan.exists():
			raise Exception('Destination scan already exists')

		dstparams = {
			'ID':f'{args.srcsess}_{srcscan["scan_id"]}',
			'type':srcscan['scan_type'],
			'xnat:mrScanData/quality':'questionable',
			'xnat:mrScanData/series_description':srcscan['scan_description']
			}
		dstscan.create(**dstparams)
		
		srcrsrcs = xnat.get_scan_resources(srcscan['project_id'],srcscan['subject_id'],
			srcscan['session_id'],srcscan['scan_id'])
		
		for srcrsrc in srcrsrcs:
			
			r = xnat.select_scan_resource(srcscan['project_id'],srcscan['subject_id'],
				srcscan['session_id'],srcscan['scan_id'],srcrsrc['label'])
			print(r)
			with tempfile.TemporaryDirectory() as tmpdir:
				files = r.get(tmpdir,extract=True)
				r2 = xnat.select_scan_resource(args.dstproj,args.dstsubj,
					args.dstsess,dstparams['ID'],srcrsrc['label'])
				r2.put(files)



# ID                     f'{srcsess}_{srcscan["scan_id"]}'
# type                   r['scan_type']
# xnat:mrScanData
#   quality              questionable
#   series_description   r['scan_description']


# xnat.select_scan
# xnat.get_scan_resources
# xnat.select_scan_resource
# XnatUtils.upload_folder

