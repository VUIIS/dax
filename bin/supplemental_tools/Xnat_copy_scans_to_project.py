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
	
	# Check that source and destination sessions exist
	src = xnat.select_session(args.srcproj,args.srcsubj,args.srcsess)
	if not src.exists():
		raise Exception('Source session does not exist on XNAT')
	dst = xnat.select_session(args.dstproj,args.dstsubj,args.dstsess)
	if not dst.exists():
		raise Exception('Destination session does not exist on XNAT')
	
	# Go through the list of scans in the source session
	srcscans = xnat.get_scans(args.srcproj,args.srcsubj,args.srcsess)
	for srcscan in srcscans:

		# Create new scan in the dest session, or bail if it already exists.
		# Dest scan ID will include the source session label for clarity/uniqueness
		print(
			f'From: {args.srcproj} {args.srcsubj} {args.srcsess} '
			f'{srcscan["scan_id"]} {srcscan["scan_type"]}'
			)
		print(
			f'  To: {args.dstproj} {args.dstsubj} {args.dstsess} '
			f'{args.srcsess}_{srcscan["scan_id"]}'
			)
		dstscan = xnat.select_scan(
			args.dstproj,
			args.dstsubj,
			args.dstsess,
			f'{args.srcsess}_{srcscan["scan_id"]}'
			)
		if dstscan.exists():
			print('  Destination scan exists: SKIPPING')
			continue

		dstparams = {
			'ID':f'{args.srcsess}_{srcscan["scan_id"]}',
			'type':srcscan['scan_type'],
			'xnat:mrScanData/quality':'questionable',
			'xnat:mrScanData/series_description':srcscan['scan_description']
			}
		dstscan.create(**dstparams)
		
		# For each scan, go through resources, download from source,
		# upload to destination.
		srcrsrcs = xnat.get_scan_resources(
			srcscan['project_id'],
			srcscan['subject_id'],
			srcscan['session_id'],
			srcscan['scan_id']
			)
		
		for srcrsrc in srcrsrcs:
			print(f'  Copying resource {srcrsrc["label"]}')
			r = xnat.select_scan_resource(
				srcscan['project_id'],
				srcscan['subject_id'],
				srcscan['session_id'],
				srcscan['scan_id'],srcrsrc['label']
				)
			with tempfile.TemporaryDirectory() as tmpdir:
				files = r.get(tmpdir,extract=True)
				r2 = xnat.select_scan_resource(
					args.dstproj,
					args.dstsubj,
					args.dstsess,
					dstparams['ID'],srcrsrc['label']
					)
				r2.put(files)

