import sys
import logging

from dax.noxnat.launcher_noxnat import TaskLauncherNoXnat

if __name__ == '__main__':

	if '--debug' in sys.argv:
		logging.basicConfig(level=logging.DEBUG)
	else:
		logging.basicConfig(level=logging.INFO)

	TaskLauncherNoXnat(sys.argv[1]).cancel_running()
