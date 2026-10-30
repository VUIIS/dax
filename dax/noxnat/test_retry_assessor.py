import sys

from dax.noxnat.launcher_noxnat import TaskLauncherNoXnat

if __name__ == '__main__':
    rootdir = sys.argv[1]
    assr = sys.argv[2]

    print(f'{assr=}')

    launcher = TaskLauncherNoXnat(sys.argv[1])

    assessors = launcher._data['assessors'].to_dict('records')
    for a in assessors:
        if a['ASSR'] == assr:
            launcher._retry(a)
