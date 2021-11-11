from .suppdf import make_suppdf

if __name__ == '__main__':
    infile = '/Users/boydb1/TEST-fmri_msit/report_test3b.pdf'
    outfile = '/Users/boydb1/TEST-fmri_msit/report_test3b_sup.pdf'
    info = {}

    info['assessor'] = 'REMBRANDT-x-28034-x-28034a-x-fmri_msit_v2-x-6a8dcef0'
    info['proctype'] = 'fmri_msit_v2'
    info['procversion'] = '2.0.0'
    info['procdate'] = '2021/10/31'
    info['description'] = '''
1. Write conditions file
2. Write contrasts file
3. Realign/Motion-correction of FMRI
4. Coregister/Estimate mean FMRI to original T1
5. Segment & Normalize T1 to MNI space and segment
6. Apply warps and reslice FMRI and T1
7. ART outliers using CONN liberal settings
8. Skull-strip mean functional and apply to others
9. Create smoothed fmri'''

    info['inputs'] = (
        ('scan_anat', '3', '/projects/REMBRANDT/subjects/28043/experiments/28043a/scans/3'),
        ('scan_fmri', '14', '/projects/REMBRANDT/subjects/28043/experiments/28043a/scans/14'))
    
    info['outputs'] = [
        {
            'path': 'report*.pdf',
            'type': 'FILE',
            'resource': 'PDF'
        }, 
        {
            'path': 'stats.txt',
            'type': 'FILE',
            'resource': 'STATS',
        },
        {
            'path': 'PREPROC',
            'type': 'DIR',
            'resource': 'PREPROC',
        },
        {
            'path': '1stLEVEL',
            'type': 'DIR',
            'resource': '1stLEVEL'
        }
    ]

    info['session'] = {
        'PROJECT': 'REMBRANDT',
        'SUBJECT': '28043',
        'SESSION': '28043a'}

    info['proc'] = {
        'dax_version': '2.3.0',
        'dax_manager': 'vuiis_daily_singularity@hickory'}

    info['job'] = {
        'jobid': '33269491',
        'duration': '00:34:07',
        'memory': '2296336'}

    make_suppdf(infile, outfile, info)
