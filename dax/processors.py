""" Processor class define for Scan and Session."""

import os
import re
import task
import logging
import XnatUtils


__copyright__ = 'Copyright 2013 Vanderbilt University. All Rights Reserved'
__all__ = ['Processor', 'ScanProcessor', 'SessionProcessor']
# Logger for logs
LOGGER = logging.getLogger('dax')


class Processor(object):
    """ Base class for processor """
    def __init__(self, walltime_str, memreq_mb, spider_path,
                 version=None, ppn=1, suffix_proc='',
                 xsitype='proc:genProcData'):
        """
        Entry point of the Base class for processor.

        :param walltime_str: Amount of walltime to request for the process
        :param memreq_mb: Number of megabytes of memory to use
        :param spider_path: Fully qualified path to the spider to run
        :param version: Version of the spider
        :param ppn: Number of processors per not to use.
        :param suffix_proc: Processor suffix (if desired)
        :param xsitype: the XNAT xsiType.
        :return: None

        """
        self.walltime_str = walltime_str  # 00:00:00 format
        self.memreq_mb = memreq_mb   # memory required in megabytes
        # default values:
        self.version = "1.0.0"
        # Suffix
        if suffix_proc and suffix_proc[0] != '_':
            self.suffix_proc = '_'+suffix_proc
        else:
            self.suffix_proc = suffix_proc
        self.suffix_proc = re.sub('[^a-zA-Z0-9]', '_', self.suffix_proc)
        self.name = None
        self.spider_path = spider_path
        self.ppn = ppn
        self.xsitype = xsitype
        # getting name and version from spider_path
        self.set_spider_settings(spider_path, version)
        # if suffix_proc is empty, set it to "" for the spider call:
        if not suffix_proc:
            self.suffix_proc = ''

    # get the spider_path right with the version:
    def set_spider_settings(self, spider_path, version):
        """
        Method to set the spider version, path, and name from filepath

        :param spider_path: Fully qualified path and file of the spider
        :param version: version of the spider
        :return: None

        """
        if version:
            # get the proc_name
            proc_name = os.path.basename(spider_path)[7:-3]
            # remove any version if there is one
            proc_name = re.split("/*_v[0-9]/*", proc_name)[0]
            # setting the version and name of the spider
            self.version = version
            self.name = '''{procname}_v{version}{suffix}'''.format(
                    procname=proc_name, version=self.version.split('.')[0],
                    suffix=self.suffix_proc)
            spider_name = '''Spider_{procname}_v{version}.py'''.format(
                    procname=proc_name, version=version.replace('.', '_'))
            self.spider_path = os.path.join(os.path.dirname(spider_path),
                                            spider_name)
        else:
            self.default_settings_spider(spider_path)

    def default_settings_spider(self, spider_path):
        """
        Get the default spider version and name

        :param spider_path: Fully qualified path and file of the spider
        :return: None

        """
        # set spider path
        self.spider_path = spider_path
        # set the name and the version of the spider
        if len(re.split("/*_v[0-9]/*", spider_path)) > 1:
            basename = os.path.basename(spider_path)
            self.version = basename[7:-3].split('_v')[-1].replace('_', '.')
            spidername = basename[7:-3]
            self.name = '''{procname}_v{version}{suffix}'''.format(
                procname=re.split("/*_v[0-9]/*", spidername)[0],
                version=self.version.split('.')[0], suffix=self.suffix_proc)
        else:
            self.name = os.path.basename(spider_path)[7:-3]+self.suffix_proc

    # has_inputs - does this object have the required inputs?
    # e.g. NIFTI format of the required scan type and quality
    #      and are there no conflicting inputs.
    # i.e. only 1 required by 2 found?
    # other arguments here, could be Proj/Subj/Sess/Scan/Assessor depending
    # on processor type?
    def has_inputs(self):
        """
        Check to see if the spider has all the inputs necessary to run.

        :raises: NotImplementedError if user does not override
        :return: None

        """
        raise NotImplementedError()

    # should_run - is the object of the proper object type?
    # e.g. is it a scan? and is it the required scan type?
    # e.g. is it a T1?
    # other arguments here, could be Proj/Subj/Sess/Scan/Assessor depending
    # on processor type?
    def should_run(self):
        """
        Responsible for determining if the assessor should shouw up in session.

        :raises: NotImplementedError if not overridden.
        :return: None

        """
        raise NotImplementedError()

    def build_cmds(self, cobj, dir):

        """
        Build the commands that will go in the PBS/SLURM script
        :raises: NotImplementedError if not overridden from base class.
        :return: None
        """
        raise NotImplementedError()


class ScanProcessor(Processor):
    """ Scan Processor class for processor on a scan on XNAT """
    def __init__(self, scan_types, walltime_str, memreq_mb, spider_path,
                 version=None, ppn=1, suffix_proc=''):
        """
        Entry point of the ScanProcessor Class.

        :param scan_types: Types of scans that the spider should run on
        :param walltime_str: Amount of walltime to request for the process
        :param memreq_mb: Amount of memory in MB to request for the process
        :param spider_path: Absolute path to the spider
        :param version: Version of the spider (taken from the file name)
        :param ppn: Number of processors per node to request
        :param suffix_proc: Processor suffix
        :return: None

        """
        super(ScanProcessor, self).__init__(walltime_str, memreq_mb,
                                            spider_path, version, ppn,
                                            suffix_proc)
        if isinstance(scan_types, list):
            self.scan_types = scan_types
        elif isinstance(scan_types, str):
            if scan_types == 'all':
                self.scan_types = 'all'
            else:
                self.scan_types = scan_types.split(',')
        else:
            self.scan_types = []

    def has_inputs(self):
        """
        Method to check and see that the process has all of the inputs
         that it needs to run.

        :raises: NotImplementedError if not overridden.
        :return: None

        """
        raise NotImplementedError()

    def get_assessor_name(self, cscan):
        """
        Returns the label of the assessor

        :param cscan: CachedImageScan object from XnatUtils
        :return: String of the assessor label

        """
        scan_dict = cscan.info()
        subj_label = scan_dict['subject_label']
        sess_label = scan_dict['session_label']
        proj_label = scan_dict['project_label']
        scan_label = scan_dict['scan_label']
        return '-x-'.join([proj_label, subj_label, sess_label, scan_label,
                           self.name])

    def get_task(self, intf, cscan, upload_dir):
        """
        Get the Task object

        :param intf: XNAT interface (pyxnat.Interface class)
        :param cscan: CachedImageScan object from XnatUtils
        :param upload_dir: the directory to put the processed data when the
         process is done
        :return: Task object

        """
        scan_dict = cscan.info()
        assessor_name = self.get_assessor_name(cscan)
        scan = XnatUtils.get_full_object(intf, scan_dict)
        assessor = scan.parent().assessor(assessor_name)
        return task.Task(self, assessor, upload_dir)

    def should_run(self, scan_dict):
        """
        Method to see if the assessor should appear in the session.

        :param scan_dict: Dictionary of information about the scan
        :return: True if it should run, false if it shouldn't

        """
        if self.scan_types == 'all':
            return True
        else:
            for exp in self.scan_types:
                regex = re.compile(exp)
                if regex.match(scan_dict['scan_type']):
                    return True
            return False


class SessionProcessor(Processor):
    """ Session Processor class for processor on a session on XNAT """
    def __init__(self, walltime_str, memreq_mb, spider_path, version=None,
                 ppn=1, suffix_proc=''):
        """
        Entry point for the session processor

        :param walltime_str: Amount of walltime to request for the process
        :param memreq_mb: Amount of memory in MB to request for the process
        :param spider_path: Absolute path to the spider
        :param version: Version of the spider (taken from the file name)
        :param ppn: Number of processors per node to request
        :param suffix_proc: Processor suffix
        :return: None

        """
        super(SessionProcessor, self).__init__(walltime_str, memreq_mb,
                                               spider_path, version, ppn,
                                               suffix_proc)

    def has_inputs(self):
        """
        Check to see that the session has the required inputs to run.

        :raises: NotImplementedError if not overriden from base class.
        :return: None
        """
        raise NotImplementedError()

    def should_run(self, session_dict):
        """
        By definition, this should always run, so it just returns true
         with no checks

        :param session_dict: Dictionary of session information for
         XnatUtils.list_experiments()
        :return: True

        """
        return True

    def get_assessor_name(self, csess):
        """
        Get the name of the assessor

        :param csess: CachedImageSession from XnatUtils
        :return: String of the assessor label

        """
        session_dict = csess.info()
        proj_label = session_dict['project']
        subj_label = session_dict['subject_label']
        sess_label = session_dict['label']
        return proj_label+'-x-'+subj_label+'-x-'+sess_label+'-x-'+self.name

    def get_task(self, intf, csess, upload_dir):
        """
        Return the Task object

        :param intf: XNAT interface see pyxnat.Interface
        :param csess: CachedImageSession from XnatUtils
        :param upload_dir: directory to put the data after run on the node
        :return: Task object of the assessor

        """
        sess_info = csess.info()
        assessor_name = self.get_assessor_name(csess)
        session = XnatUtils.get_full_object(intf, sess_info)
        assessor = session.assessor(assessor_name)
        return task.Task(self, assessor, upload_dir)


def processors_by_type(proc_list):
    """
    Organize the processor types and return a list of session processors
     first, then scan

    :param proc_list: List of Processor classes from the DAX settings file
    :return: List of SessionProcessors, and list of ScanProcessors

    """
    sess_proc_list = list()
    scan_proc_list = list()

    # Build list of processors by type
    for proc in proc_list:
        if issubclass(proc.__class__, ScanProcessor):
            scan_proc_list.append(proc)
        elif issubclass(proc.__class__, SessionProcessor):
            sess_proc_list.append(proc)
        else:
            LOGGER.warn('unknown processor type:'+proc)

    return sess_proc_list, scan_proc_list
