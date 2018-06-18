import datetime
import os
import sys
import time


if __name__ == '__main__':
  print sys.argv
  print os.getcwd()
  #with open(os.path.join(os.getcwd(), 'log_test_job_runner.txt'), 'a') as f:
  with open('./log_test_job_runner.txt', 'a') as f:
    ts = datetime.datetime.fromtimestamp(time.time())
    f.write('{}: {}\n'.format(ts, sys.argv))
