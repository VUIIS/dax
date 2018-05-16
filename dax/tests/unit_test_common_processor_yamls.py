
processor_text_pre = """
---
inputs:
  default:
    spider_path: ./spiderpath/not_a_real_script.py
    working_dir: ./workingdir
    nipype_exe: not_a_real_script.py
    db: ./not_a_real_db_path/no.db"""

processor_text_post = """
command: python {spider_path} --t1 {t1} --dbt {db} --exe {nipype_exe}
attrs:
  suffix:
  xsitype: proc:genProcData
  walltime: 24:00:00
  memory: 3850
  ppn: 4
  env: /envpath/not_a_real_env_path.sh
  type: scan
  scan_nb: scan1"""

proc_a_inputs = """
  xnat:
    scans:
      - scan1:
        types: T1
        needs_qc: True
        resources:
          - resource: NIFTI
            varname: t1"""

proc_a = processor_text_pre + proc_a_inputs + processor_text_post


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
