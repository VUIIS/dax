import socket
import os


def check_lockfile(file, logger):
    # Try to read host-PID from lockfile
    try:
        with open(file, 'r') as f:
            line = f.readline()

        host, pid = line.split('-')
        pid = int(pid)

        # Compare host to current host
        this_host = socket.gethostname().split('.')[0]
        if host != this_host:
            logger.debug('different host, cannot check PID:{}', format(file))
        elif pid_exists(pid):
            logger.debug('host matches and PID exists:{}'.format(str(pid)))
        else:
            logger.debug('host matches and PID not running, deleting lockfile')
            os.remove(file)
    except IOError:
        logger.debug('failed to read from lock file:{}'.format(file))
    except ValueError:
        logger.debug('failed to parse lock file:{}'.format(file))


def clean_lockfiles(lock_dir, logger):
    lock_list = os.listdir(lock_dir)

    # Make full paths
    lock_list = [os.path.join(lock_dir, f) for f in lock_list]

    # Check each lock file
    for file in lock_list:
        logger.debug('checking lock file:{}'.format(file))
        check_lockfile(file, logger)


def pid_exists(pid):
    if pid < 0:
        return False   # NOTE: pid == 0 returns True
    try:
        os.kill(pid, 0)
    except ProcessLookupError:   # errno.ESRCH
        return False  # No such process
    except PermissionError:  # errno.EPERM
        return True  # Operation not permitted (i.e., process exists)
    else:
        return True  # no error, we can send a signal to the process


def lock_flagfile(lock_file):
    """
    Create the flagfile to lock the process

    :param lock_file: flag file use to lock the process
    :return: True if the file didn't exist, False otherwise
    """
    if os.path.exists(lock_file):
        return False
    else:
        open(lock_file, 'w').close()

        # Write hostname-PID to lock file
        _pid = os.getpid()
        _host = socket.gethostname().split('.')[0]
        with open(lock_file, 'w') as f:
            f.write('{}-{}'.format(_host, _pid))

        return True


def unlock_flagfile(lock_file):
    """
    Remove the flagfile to unlock the process

    :param lock_file: flag file use to lock the process
    :return: None
    """
    if os.path.exists(lock_file):
        os.remove(lock_file)
