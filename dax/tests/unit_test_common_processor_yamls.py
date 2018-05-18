
def generate_yaml(scans=[], assessors=[]):
    processor_text_ = ('---\n'
                       'inputs:\n'
                       '  default:\n'
                       '    spider_path: ./spiderpath/not_a_real_script.py\n'
                       '    working_dir: ./workingdir\n'
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
    scan_text_ = ('      - {name}:\n'
                  '        types: {types}\n'
                  '{qc}'
                  '{select}'
                  '{res_block}')

    asrs_text_ = '    assessors:\n{}'
    asr_text_ = ('      - {name}:\n'
                 '        proctypes: {types}\n'
                 '{qc}'
                 '{select}'
                 '{res_block}')

    res_block_ = '        resources:\n{}'
    res_text_ = ('          - resource: {res_name}\n'
                 '            varname: {var_name}\n'
                 '{required}')

    req_text_ = '            required: {req_value}\n'

    qc_text_ = '        needs_qc: {qc}\n'

    select_text_ = '        select: {}\n'

    proc_a_cmd_ =\
        'command: python {spider_path} --t1 {t1} --dbt {db} --exe {nipype_exe}'

    proc_a_scan_text = ('    scans:\n'
                        '      - scan1:\n'
                        '        types: T1\n'
                        '{qc}'
                        '        resources:\n'
                        '          - resource: NIFTI\n'
                        '            varname: t1\n')

    def input_block(inputs,
                    input_block_, input_text_,
                    select_text_,
                    res_block_, res_text_):

        # create the input block
        if len(inputs) == 0:
            input_block = ''
        else:
            input_entries = []
            for i in inputs:

                # create the select keyword text
                if i['select'] != None:
                    select = select_text_.format(i['select'])
                else:
                    select = ''

                # create the resource block
                if len(i['resources']) == 0:
                    res_block = ''
                else:
                    res_entries = []
                    for r in i['resources']:
                        if r['required'] == True:
                            req_text = req_text_.format('True')
                        elif r['required'] == False:
                            req_text = req_text_.format('False')
                        else:
                            req_text = ''
                        res_entries.append(res_text_.format(res_name=r['type'],
                                                            var_name=r['name'],
                                                            required=req_text))
                    res_block =\
                        res_block_.format(''.join(res_entries))

                if i['qc'] == True:
                    scan_qc = qc_text_.format(qc='True')
                elif i['qc'] == False:
                    scan_qc = qc_text_.format(qc='False')
                else:
                    scan_qc = ''

                input_entries.append(input_text_.format(name=i['name'],
                                                        types=i['types'],
                                                        select=select,
                                                        qc=scan_qc,
                                                        res_block=res_block))

            input_block = input_block_.format(''.join(input_entries))

        return input_block

    scan_block = input_block(
        scans, scans_text_, scan_text_, select_text_, res_block_, res_text_)
    asr_block = input_block(
        assessors, asrs_text_, asr_text_, select_text_, res_block_, res_text_)

    processor = processor_text_.format(scans_block=scan_block,
                                       assessors_block=asr_block,
                                       command=cmd_text_,
                                       scan_type='scan',
                                       scan_nb='scan1')
    return processor

proc_a = generate_yaml(
    scans=[
        {
            'name': 'scan1', 'types': 'T1', 'select': 'foreach', 'qc': None,
            'resources': [
                {'type': 'NIFTI', 'name': 't1', 'required': None}]
        },
        {
            'name': 'scan2', 'types': 'FLAIR', 'select': None, 'qc': None,
            'resources': [
                {'type': 'NIFTI', 'name': 'flair', 'required': None}]
        }
    ],
    assessors=[
        {
            'name': 'asr1', 'types': 'proc1', 'select': 'foreach', 'qc': None,
            'resources': [
                {'type': 'SEG', 'name': 'seg', 'required': None},
                {'type': 'STUFF', 'name': 'stuff', 'required': None}]
        }
    ]
)



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
