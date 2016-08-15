__author__ = 'damons'

import subprocess
import sys
import os
if __name__ == '__main__':
    MASIMATLAB_SPIDERS = sys.argv[1]
    if not os.path.isdir(MASIMATLAB_SPIDERS):
        sys.stderr.write('Directory %s does not exist' % MASIMATLAB_SPIDERS)

    files = os.listdir(MASIMATLAB_SPIDERS)
    for f in files:
        print f


        output = subprocess.Popen(["svn", "log",
                                   os.path.join(MASIMATLAB_SPIDERS,f)],
                                   stdout=subprocess.PIPE).communicate()[0]
        output  = output.replace('------------------------------------------------------------------------','')

        output = output.split('\n')
        output_keep = list()
        for line in output:
            if not line.startswith('r') and line != '\n':
                output_keep.append('\t%s\n' % line)
            elif not line.startswith('\n'):
                output_keep.append('%s\n' % line)

        rst_file = f.replace('py','rst').replace('Spider_','')
        if not os.path.isfile(rst_file):
            print "Warning: %s does not exist for %s. Please generate" % (rst_file, f)
        else:
            with open(rst_file,'a') as rst:
                rst.writelines(output_keep)


