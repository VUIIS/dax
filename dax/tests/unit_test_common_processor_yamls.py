

def generate_yaml(procname="Proc",
                  procversion="1_0_0",
                  scans=[],
                  assessors=[]):

    processor_text_ = ('---\n'
                       'inputs:\n'
                       '  default:\n'
                       '    spider_path: ./spiderpath/Spider_{procname}_v{procversion}.py\n'
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
    scan_text_ = ('      - name: {name}\n'
                  '        types: {types}\n'
                  '{qc}'
                  '{select}'
                  '{select_session}'
                  '{res_block}')

    asrs_text_ = '    assessors:\n{}'
    asr_text_ = ('      - name: {name}\n'
                 '        proctypes: {types}\n'
                 '{qc}'
                 '{select}'
                 '{select_session}'
                 '{res_block}')

    res_block_ = '        resources:\n{}'
    res_text_ = ('          - resource: {res_name}\n'
                 '            varname: {var_name}\n'
                 '{required}')

    req_text_ = '            required: {}\n'

    qc_text_ = '        needs_qc: {}\n'

    select_text_ = '        select: {}\n'
    select_session_text_ = '        select-session: {}\n'

    proc_a_cmd_ =\
        'command: python {spider_path} --t1 {t1} --dbt {db} --exe {nipype_exe}'

    proc_a_scan_text = ('    scans:\n'
                        '      - name: scan1\n'
                        '        types: T1\n'
                        '{qc}'
                        '        resources:\n'
                        '          - resource: NIFTI\n'
                        '            varname: t1\n')

    def generate_input_block(artefact_type, inputs):

        if not artefact_type in ['scan', 'assessor']:
            raise RuntimeError(
                'artefact_type must be one of ''scan'' or ''assessor''')

        if artefact_type == 'scan':
            input_block_ = scans_text_
            input_text_ = scan_text_
        else:
            input_block_ = asrs_text_
            input_text_ = asr_text_

        # create the input block
        if len(inputs) == 0:
            input_block = ''
        else:
            input_entries = []
            for i in inputs:

                # create the select keyword text
                select_value = i.get('select', None)
                if select_value != None:
                    select = select_text_.format(select_value)
                else:
                    select = ''

                # create the select-session keyword text
                select_session_value = i.get('select-session', None)
                if select_session_value != None:
                    select_session =\
                        select_session_text_.format(select_session_value)
                else:
                    select_session = ''

                # create the resource block
                if len(i['resources']) == 0:
                    res_block = ''
                else:
                    res_entries = []
                    for r in i['resources']:
                        required_value = r.get('required', None)
                        if required_value == True:
                            req_text = req_text_.format('True')
                        elif required_value == False:
                            req_text = req_text_.format('False')
                        else:
                            req_text = ''
                        res_entries.append(res_text_.format(res_name=r['type'],
                                                            var_name=r['name'],
                                                            required=req_text))
                    res_block =\
                        res_block_.format(''.join(res_entries))

                qc_value = i.get('qc', None)
                if qc_value == True:
                    qc_text = qc_text_.format('True')
                elif qc_value == False:
                    qc_text = qc_text_.format('False')
                else:
                    qc_text = ''

                if artefact_type == 'scan':
                    input_entries.append(
                        input_text_.format(name=i['name'],
                                           types=i['types'],
                                           select=select,
                                           select_session=select_session,
                                           qc=qc_text,
                                           res_block=res_block))
                else:
                    input_entries.append(
                        input_text_.format(name=i['name'],
                                           types=i['types'],
                                           select=select,
                                           select_session=select_session,
                                           qc=qc_text,
                                           res_block=res_block))

            input_block = input_block_.format(''.join(input_entries))

        return input_block

    if not isinstance(scans, list):
        raise ValueError('scans must be a list')
    if not isinstance(assessors, list):
        raise ValueError('assessors must be a list')

    scan_block = generate_input_block('scan', scans)
    asr_block = generate_input_block('assessor', assessors)

    processor = processor_text_.format(procname=procname,
                                       procversion=procversion,
                                       scans_block=scan_block,
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
      - name: scan1
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
      - name: scan1
        types: T1W,T1w,MPRAGE 
        resources:
          - resource: NIFTI
            varname: T1
    assessors:
      - name: assessor1
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
