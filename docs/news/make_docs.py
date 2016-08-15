import os
import sys
import re
if __name__ =='__main__':
    SPIDERS = os.listdir(sys.argv[1])
    SPIDERS.reverse()
    for SPIDER in SPIDERS:
        previous_fname=''
        if SPIDER.startswith('Spider_'):
            parts = SPIDER.split('_v')
            print parts[0]

            f_name = 'spiders/' + parts[0].replace('Spider_','').replace('.py','') + '.rst'
            fname_base = parts[0]
            if not os.path.isfile(f_name):
                with open(f_name, 'w') as f:
                    f.writelines(parts[0].replace('Spider_','')+'\n'+'='*len(parts[0].replace('Spider_',''))+
                                 '\nOverview:\n\nVersions:\n\n.. toctree::\n   :maxdepth: 5\n\n')
            with open(f_name,'a') as f2:
                f2.write('   spider_level/%s\n' % SPIDER.replace('.py','').replace('Spider_',''))

                previous_fname = fname_base





