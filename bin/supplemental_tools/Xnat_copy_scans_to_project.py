#!/usr/bin/env python

import argparse
import tempfile

from dax import XnatUtils


parser = argparse.ArgumentParser()
parser.add_argument('--srcproj', help='Source project', required=True)
parser.add_argument('--srcsubj', help='Source subject', required=True)
parser.add_argument('--srcsess', help='Source session', required=False)
parser.add_argument('--dstproj', help='Destination project', required=True)
parser.add_argument('--dstsubj', help='Destination subject', required=True)
parser.add_argument('--dstsess', help='Destination session', required=False)
args = parser.parse_args()

# If session not supplied, assume it's the same as subject
if not args.srcsess:
    srcsess = args.srcsubj
else:
    srcsess = args.srcsess
if not args.dstsess:
    dstsess = args.dstsubj
else:
    dstsess = args.dstsess


with XnatUtils.get_interface() as xnat:

    # Check that source and destination sessions exist
    src = xnat.select_session(args.srcproj, args.srcsubj, srcsess)
    if not src.exists():
        raise Exception('Source session does not exist on XNAT')
    dst = xnat.select_session(args.dstproj, args.dstsubj, dstsess)
    if not dst.exists():
        raise Exception('Destination session does not exist on XNAT')

    # Go through the list of scans in the source session
    srcscans = xnat.get_scans(args.srcproj, args.srcsubj, srcsess)
    for srcscan in srcscans:

        # Create new scan in the dest session, or bail if it already exists.
        # Dest scan ID will include the source session label for clarity,
        # uniqueness
        print(
            f'From: {args.srcproj} {args.srcsubj} {srcsess} '
            f'{srcscan["scan_id"]} {srcscan["scan_type"]}'
            )
        print(
            f'  To: {args.dstproj} {args.dstsubj} {dstsess} '
            f'{srcsess}_{srcscan["scan_id"]}'
            )
        dstscan = xnat.select_scan(
            args.dstproj,
            args.dstsubj,
            dstsess,
            f'{srcsess}_{srcscan["scan_id"]}'
            )
        if dstscan.exists():
            print('  Destination scan exists: SKIPPING')
            continue

        dstparams = {
            'ID': f'{srcsess}_{srcscan["scan_id"]}',
            'type': srcscan['scan_type'],
            'xnat:mrScanData/quality': 'questionable',
            'xnat:mrScanData/series_description': srcscan['scan_description']
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
                srcscan['scan_id'],
                srcrsrc['label']
                )
            with tempfile.TemporaryDirectory() as tmpdir:
                files = r.get(tmpdir, extract=True)
                r2 = xnat.select_scan_resource(
                    args.dstproj,
                    args.dstsubj,
                    dstsess,
                    dstparams['ID'],
                    srcrsrc['label']
                    )
                r2.put(files)
