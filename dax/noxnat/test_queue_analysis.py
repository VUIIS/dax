import sys

from dax.noxnat.analysis_noxnat import AnalysisLauncherNoXnat

if __name__ == '__main__':
    rootdir = sys.argv[1]
    analysis = sys.argv[2]

    # Get an analysis launcher
    alauncher = AnalysisLauncherNoXnat(rootdir)

    # Queue requested analysis
    alauncher.queue_analysis(analysis)
