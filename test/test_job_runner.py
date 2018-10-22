import datetime
import os
import sys
import time

from dax import dax_settings


if __name__ == '__main__':


  with open('./log_test_job_runner.txt', 'a') as f:
    ts = datetime.datetime.fromtimestamp(time.time())
    f.write('{}: {}\n'.format(ts, sys.argv))

    settings = dax_settings.DAX_Settings()
    results_dir = settings.get_results_dir()
    try:
      i = sys.argv.index('-a')
      folder_to_create = os.path.join(results_dir, sys.argv[i+1])
      if not os.path.exists(folder_to_create):
        os.makedirs(folder_to_create)
      file_to_create = os.path.join(folder_to_create, 'READY_TO_UPLOAD.txt')
      print 'file_to_create =', file_to_create
      with open(file_to_create, 'w') as g:
        os.write('')
    except Exception as e:
      f.write('{}: {}\n'.format(ts, e))



# 2018-06-27 15:38:24.683594: [
#   '/home/ben/git/refactordax/bin/dax_tools/test_job_runner.py',
#   'python',
#   '/home/ben/git/comic100_dax_config/pipelines/Proc_A/v1.0.0/Proc_A_v1_0_0.py',
#   '--t1',
#   '/projects/proj1/subjects/subj1/experiments/sess1/scans/1/resources/NIFTI',
#   '--flair',
#   '/projects/proj1/subjects/subj1/experiments/sess1/scans/11/resources/NIFTI',
#   '--working_dir',
#   '/home/ben/dax/scratch',
#   '--nipype_exe',
#   'proc_a.py',
#   '-a',
#   'proj1-x-subj1-x-sess1-x-54bd8ffc-0a2a-49c4-b0d1-00c159192d2a',
#   '-d',
#   '/home/ben/dax/scratch/proj1-x-subj1-x-sess1-x-54bd8ffc-0a2a-49c4-b0d1-00c159192d2a',
#   '/home/ben/dax/upload/OUTLOG/proj1-x-subj1-x-sess1-x-54bd8ffc-0a2a-49c4-b0d1-00c159192d2a.output']
