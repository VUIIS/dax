
def generate_yaml(scan_inputs):
    processor_text_ = (
        '---\n'
        'inputs:\n'
        '  default:\n'
        '    spider_path: ./spiderpath/not_a_real_script.py\n'
        '    working_dir: ./workindir\n'
        '    nypype_exe: not_a_real_script.py\n'
        '    db: not_a_real_db_path/no.db\n'
        '  xnat:\n'
        '{scans_block}'
        '{assessors_block}'
        '{command}\n'
        'attrs:\n'
        '  suffix:\n'
        '  xsitype: proc:genProcData\n'
        '  walltime: 24:00:00\n'
        '  memory: 3850\n'
        '  ppn: 4\n'
        '  env: /envpath/not_a_real_env_path.sh\n'
        '  type: {scan_type}\n'
        '  scan_nb: {scan_nb}\n')

    cmd_text_ = \
        'command: python {spider_path} --t1 {t1} --dbt {db} --exe {nipype_exe}'

    scans_text_ = '    scans:\n{}'
    scan_text_ = ('      - {scan_name}:\n'
                 '        types: {scan_types}\n'
                 '{scan_qc}'
                 '{res_block}')

    asrs_text_ = '     assessors:\n{}'
    asr_text_ = ('       - {asr_name}:\n'
                '         proctypes: {asr_types}\n'
                '{scan_qc}'
                '{res_block}')

    res_block_ = ('        resources:\n'
                 '{resources}')
    res_text_ = ('          - resource: {res_name}\n'
                '            varname: {var_name}\n'
                '{required}')
    req_text_ = '            required: {req_value}\n'

    qc_text_= '        needs_qc: {qc}\n'

    proc_a_cmd_ =\
        'command: python {spider_path} --t1 {t1} --dbt {db} --exe {nipype_exe}'


    # create the scan block
    if len(scan_inputs) == 0:
        scan_block = ''
    else:
        scan_entries = []
        for s in scan_inputs:

            # create the resource block
            if len(s[2]) == 0:
                res_block = ''
            else:
                res_entries = []
                for r in s[2]:
                    if r[2] == True:
                        req_text = req_text_.format('True')
                    elif r[2] == False:
                        req_text = req_text_.format('False')
                    else:
                        req_text = ''
                    res_entries.append(res_text_.format(res_name=r[0],
                                                        var_name=r[1],
                                                        required=req_text))
                res_block = res_block_.format(resources=''.join(res_entries))

            if s[3] == True:
                scan_qc = qc_text_.format(qc='True')
            elif s[3] == False:
                scan_qc = qc_text_.format(qc='False')
            else:
                scan_qc = ''

            scan_entries.append(scan_text_.format(scan_name=s[0],
                                                  scan_types=s[1],
                                                  scan_qc=scan_qc,
                                                  res_block=res_block))

        scan_block = scans_text_.format(''.join(scan_entries))

    processor = processor_text_.format(scans_block=scan_block,
                                       assessors_block='',
                                       command=cmd_text_,
                                       scan_type='scan',
                                       scan_nb='scan1')
    return processor



scan_gif_parcellation_yaml = """
---
inputs:
  default:
    spider_path: /home/dax/Xnat-management/comic100_dax_config/pipelines/GIF_parcellation/v3.0.0/Spider_GIF_Parcellation_v3_0_0.py
    working_dir: /scratch0/dax/
    nipype_exe: perform_gif_propagation.py
    db: /share/apps/cmic/GIF/db/db.xml
  xnat:
    scans:
      - scan1:
        types: T1w,MPRAGE,T1,T1W
        resources:
          - resource: NIFTI
            varname: t1
command: python {spider_path} --t1 {t1} --dbt {db} --exe {nipype_exe}
attrs:
  suffix:
  xsitype: proc:genProcData
  walltime: 24:00:00
  memory: 3850
  ppn: 4
  env: /share/apps/cmic/NiftyPipe/v2.0/setup_v2.0.sh
  type: scan
  scan_nb: scan1
"""


scan_brain_tiv_from_gif_yaml = """
---
inputs:
  default:
    spider_path: /home/dax/Xnat-management/comic100_dax_config/pipelines/BrainTivFromGIF/v1.0.0/Spider_BrainTivFromGIF_v1_0_0.py
    working_dir: /scratch0/dax/
    nipype_exe: perform_brain_tiv_from_gif.py
  xnat:
    scans:
      - scan1:
        types: T1W,T1w,MPRAGE 
        resources:
          - resource: NIFTI
            varname: T1
    assessors:
      - assessor1:
        proctypes: GIF_Parcellation_v3
        resources:
          - resource: SEG
            varname: seg
            required: True
command: python {spider_path} --exe {nipype_exe} --seg {seg}
attrs:
  suffix:
  xsitype: proc:genProcData
  walltime: 01:00:00
  memory: 4096
  ppn: 1
  env: /share/apps/cmic/NiftyPipe/v2.0/setup_v2.0.sh
  type: scan
  scan_nb: scan1 
"""
