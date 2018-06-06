""" Processor class define for Scan and Session."""

from builtins import object
from past.builtins import basestring

import logging
import re
import os
import json
import itertools
from uuid import uuid4


from . import XnatUtils, task
from . import processor_parser
from .errors import AutoProcessorError
from .dax_settings import DEFAULT_FS_DATATYPE, DEFAULT_DATATYPE


try:
    basestring
except NameError:
    basestring = str

__copyright__ = 'Copyright 2013 Vanderbilt University. All Rights Reserved'
__all__ = ['Processor', 'ScanProcessor', 'SessionProcessor', 'AutoProcessor']
# Logger for logs
LOGGER = logging.getLogger('dax')


class Processor(object):
    """ Base class for processor """
    def __init__(self, walltime_str, memreq_mb, spider_path,
                 version=None, ppn=1, env=None, suffix_proc='',
                 xsitype='proc:genProcData'):
        """
        Entry point of the Base class for processor.

        :param walltime_str: Amount of walltime to request for the process
        :param memreq_mb: Number of megabytes of memory to use
        :param spider_path: Fully qualified path to the spider to run
        :param version: Version of the spider
        :param ppn: Number of processors per job to use.
        :param env: Environment file to source.
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
            self.suffix_proc = '_%s' % suffix_proc
        else:
            self.suffix_proc = suffix_proc
        self.suffix_proc = re.sub('[^a-zA-Z0-9]', '_', self.suffix_proc)
        self.name = None
        self.spider_path = spider_path
        self.ppn = ppn
        if env:
            self.env = env
        else:
            self.env = os.path.join(os.environ['HOME'], '.bashrc')
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
            nformat = '''{procname}_v{version}{suffix}'''
            self.name = nformat.format(procname=proc_name,
                                       version=self.version.split('.')[0],
                                       suffix=self.suffix_proc)
            sformat = '''Spider_{procname}_v{version}.py'''
            spider_name = sformat.format(procname=proc_name,
                                         version=version.replace('.', '_'))
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
            self.name = os.path.basename(spider_path)[7:-3] + self.suffix_proc

    def get_proctype(self):
        """
        Return the processor name for this processor. Override this method if
        you are inheriting from a non-yaml processor.
        :return: the name of the processor type
        """

        return None

    def get_assessor_input_types(self):
        """
        Enumerate the assessor input types for this. The default implementation
        returns an empty collection; override this method if you are inheriting
        from a non-yaml processor.
        :return: a list of input assessor types
        """
        return []

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

    def create_assessor(self, xnatsession, inputs):
        attempts = 0
        while attempts < 100:
            guid = str(uuid4())
            assessor = xnatsession.assessor(guid)
            if not assessor.exists():
                kwargs = {}
                if self.xsitype.lower() == DEFAULT_FS_DATATYPE.lower():
                    fsversion = '{}/fsversion'.format(self.xsitype.lower())
                    kwargs[fsversion] = 0
                elif self.xsitype.lower() == DEFAULT_DATATYPE.lower():
                    proctype = '{}/proctype'.format(self.xsitype.lower())
                    kwargs[proctype] = self.name
                    procversion = '{}/procversion'.format(self.xsitype.lower())
                    kwargs[procversion] = self.version
                input_key = '{}/inputs'.format(self.xsitype.lower())
                kwargs[input_key] = self._serialize_inputs(inputs)
                assessor.create(assessors=self.xsitype.lower(),
                                ID=guid,
                                **kwargs)
                return assessor

            attempts += 1

    def _serialize_inputs(self, inputs):
        return json.dumps(inputs)

    def _deserialize_inputs(self, assessor):
        input_key = '{}/inputs'.format(self.xsitype.lower())
        return json.loads(assessor.attrs.get('inputs'))


class ScanProcessor(Processor):
    """ Scan Processor class for processor on a scan on XNAT """
    def __init__(self, scan_types, walltime_str, memreq_mb, spider_path,
                 version=None, ppn=1, env=None, suffix_proc='',
                 full_regex=False):
        """
        Entry point of the ScanProcessor Class.

        :param scan_types: Types of scans that the spider should run on
        :param walltime_str: Amount of walltime to request for the process
        :param memreq_mb: Amount of memory in MB to request for the process
        :param spider_path: Absolute path to the spider
        :param version: Version of the spider (taken from the file name)
        :param ppn: Number of processors per node to request
        :param env: Environment file to source
        :param suffix_proc: Processor suffix
        :param full_regex: use full regex
        :return: None

        """
        super(ScanProcessor, self).__init__(walltime_str, memreq_mb,
                                            spider_path, version, ppn,
                                            env, suffix_proc)
        self.full_regex = full_regex
        if isinstance(scan_types, list):
            self.scan_types = scan_types
        elif isinstance(scan_types, basestring):
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
        assr_name = '-x-'.join([proj_label, subj_label, sess_label, scan_label,
                                self.name])

        # Check if shared project:
        csess = cscan.parent()
        proj_shared = csess.has_shared_project()
        assr_name_shared = None
        if proj_shared is not None:
            assr_name_shared = '-x-'.join([proj_shared, subj_label, sess_label,
                                           scan_label, self.name])

        # Look for existing assessor
        assr_label = assr_name
        for assr in csess.assessors():
            if assr_name_shared is not None and \
               assr.info()['label'] == assr_name_shared:
                assr_label = assr_name_shared
                break
            if assr.info()['label'] == assr_name:
                break

        return assr_label

    def get_assessor(self, cscan):
        """
        Returns the assessor object depending on cscan and the assessor label.

        :param cscan: CachedImageScan object from XnatUtils
        :return: String of the assessor label

        """
        assessor_name = self.get_assessor_name(cscan)

        # Look for existing assessor
        csess = cscan.parent()
        p_assr = None
        for assr in csess.assessors():
            if assr.info()['label'] == assessor_name:
                p_assr = assr
                break

        return p_assr, assessor_name

    def get_task(self, cscan, upload_dir):
        """
        Get the Task object

        :param intf: XNAT interface (pyxnat.Interface class)
        :param cscan: CachedImageScan object from XnatUtils
        :param upload_dir: the directory to put the processed data when the
         process is done
        :return: Task object

        """
        assessor_name = self.get_assessor_name(cscan)
        scan = cscan.full_object()
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
            for expression in self.scan_types:
                regex = XnatUtils.extract_exp(expression, self.full_regex)
                if regex.match(scan_dict['scan_type']):
                    return True
            return False


class SessionProcessor(Processor):
    """ Session Processor class for processor on a session on XNAT """
    def __init__(self, walltime_str, memreq_mb, spider_path, version=None,
                 ppn=1, env=None, suffix_proc=''):
        """
        Entry point for the session processor

        :param walltime_str: Amount of walltime to request for the process
        :param memreq_mb: Amount of memory in MB to request for the process
        :param spider_path: Absolute path to the spider
        :param version: Version of the spider (taken from the file name)
        :param ppn: Number of processors per node to request
        :param env: Environment file to source
        :param suffix_proc: Processor suffix
        :return: None

        """
        super(SessionProcessor, self).__init__(walltime_str, memreq_mb,
                                               spider_path, version, ppn,
                                               env, suffix_proc)

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
        Returns the label of the assessor

        :param csess: CachedImageSession object from XnatUtils
        :return: String of the assessor label

        """
        session_dict = csess.info()
        proj_label = session_dict['project_id']
        subj_label = session_dict['subject_label']
        sess_label = session_dict['label']
        assr_name = '-x-'.join([proj_label, subj_label, sess_label, self.name])

        # Check if shared project:
        proj_shared = csess.has_shared_project()
        assr_name_shared = None
        if proj_shared is not None:
            assr_name_shared = '-x-'.join([proj_shared, subj_label, sess_label,
                                           self.name])

        # Look for existing assessor
        assr_label = assr_name
        for assr in csess.assessors():
            if assr_name_shared is not None and \
               assr.info()['label'] == assr_name_shared:
                assr_label = assr_name_shared
                break
            if assr.info()['label'] == assr_name:
                break

        return assr_label

    def get_assessor(self, csess):
        """
        Returns the assessor object depending on csess and the assessor label.

        :param csess: CachedImageSession object from XnatUtils
        :return: String of the assessor label

        """
        # TODO: BenM/id_refactor/currently returns null if the assessor doesn't
        # exist; this adds unnecessary complexity downstream - consider adding
        # a method that returns assessors that need construction and one for
        # assessors that exist
        assessor_name = self.get_assessor_name(csess)

        # Look for existing assessor
        p_assr = None
        for assr in csess.assessors():
            if assr.info()['label'] == assessor_name:
                p_assr = assr
                break

        return p_assr, assessor_name

    def get_task(self, csess, upload_dir):
        """
        Return the Task object

        :param csess: CachedImageSession from XnatUtils
        :param upload_dir: directory to put the data after run on the node
        :return: Task object of the assessor

        """
        assessor_name = self.get_assessor_name(csess)
        session = csess.full_object()
        assessor = session.assessor(assessor_name)
        return task.Task(self, assessor, upload_dir)


class AutoProcessor(Processor):
    """ Auto Processor class for AutoSpider using YAML files"""
    def __init__(self, xnat, yaml_source, user_inputs=None):
        """
        Entry point for the auto processor
        :param xnat: xnat context object (XnatUtils in production contexts)
        :param yaml_source: dictionary containing source_type -> string,\
                            source_id -> string, document -> yaml document
        :param user_inputs: a dictionary of user overrides to the yaml\
                            source document
        :return: None

        """
        if not xnat:
            raise AutoProcessorError("Parameter 'xnat' must be provided")
        if not yaml_source:
            raise AutoProcessorError("Parameter 'yaml_source' must be provided")

        self.xnat = xnat
        self.user_overrides = dict()
        self.extra_user_overrides = dict()

        self._read_yaml(yaml_source)

        # Edit the values from user inputs:
        if user_inputs is not None:
            self._edit_inputs(user_inputs, yaml_source)

        self.parser = processor_parser.ProcessorParser(yaml_source.contents)

        # Set up attrs:
        self.walltime_str = self.attrs.get('walltime')
        self.memreq_mb = self.attrs.get('memory')
        self.ppn = self.attrs.get('ppn', 1)
        self.env = self.attrs.get('env', None)
        self.xsitype = self.attrs.get('xsitype', 'proc:genProcData')
        self.full_regex = self.attrs.get('fullregex', False)
        self.suffix = self.attrs.get('suffix', None)


    def _edit_inputs(self, user_inputs, yaml_source):
        """
        Method to edit the inputs from the YAML file by the user inputs.

        :param user_inputs: dictionary of tag, value. E.G:
            user_inputs = {'default.spider_path': /.../Spider....py'}
        """
        for key, val in list(user_inputs.items()):
            tags = key.split('.')
            if key.startswith('inputs.default'):
                # change value in inputs
                if tags[-1] in list(self.user_overrides.keys()):
                    self.user_overrides[tags[-1]] = val
                elif tags[-1] in list(self.extra_user_overrides.keys()):
                    self.extra_user_overrides[tags[-1]] = val
                else:
                    msg = 'key {} not found in the default inputs for \
auto processor defined by yaml file {}'
                    LOGGER.warn(msg.format(tags[-1], yaml_source.source_id))
            elif key.startswith('inputs.xnat'):
                # change value in self.xnat_inputs
                if tags[2] in list(self.xnat_inputs.keys()):
                    # scan number or assessor number (e.g: scan1)
                    for obj in self.xnat_inputs[tags[2]]:
                        if tags[3] in list(obj.keys()) and \
                           tags[4] in list(obj.keys()):
                            if tags[4] == 'resources':
                                msg = 'You can not change the resources \
tag from the processor yaml file {}. Unauthorised operation.'
                                LOGGER.warn(msg.format(yaml_source.source_id))
                            else:
                                obj[tags[4]] = val
                else:
                    msg = 'key {} not found in the xnat inputs for auto \
processor defined by yaml file {}'
                    LOGGER.warn(msg.format(tags[3], yaml_source.source_id))
            elif key.startswith('attrs'):
                # change value in self.attrs
                if tags[-1] in list(self.attrs.keys()):
                    self.attrs[tags[-1]] = val
                else:
                    msg = 'key {} not found in the attrs for auto processor \
defined by yaml file {}'
                    LOGGER.warn(msg.format(tags[-1], yaml_source.source_id))


    def _read_yaml(self, yaml_source):
        """
        Method to parse the processor arguments and their default values.

        :param yaml_source: YamlDoc object containing the yaml file contents
        """
        if yaml_source.source_type is None:
            raise AutoProcessorError('Empty yaml source provided')

        doc = yaml_source.contents

        # Set Inputs from Yaml
        self._check_default_keys(yaml_source.source_id, doc)
        self.attrs = doc.get('attrs')
        self.command = doc.get('command')
        inputs = doc.get('inputs')
        self.xnat_inputs = inputs.get('xnat')
        for key, value in list(inputs.get('default').items()):
            # If value is a key in command
            k_str = '{{{}}}'.format(key)
            if k_str in self.command:
                self.user_overrides[key] = value
            else:
                if isinstance(value, bool) and value is True:
                    self.extra_user_overrides[key] = ''
                elif value and value != 'None':
                    self.extra_user_overrides[key] = value

        # Getting proctype from Yaml
        self.proctype, self.version = self.xnat.get_proctype(
            self.user_overrides.get('spider_path'),
            self.attrs.get('suffix', None))

        # Set attributs:
        self.spider_path = self.user_overrides.get('spider_path')
        self.name = self.proctype
        self.type = self.attrs.get('type')


    def _check_default_keys(self, source_id, doc):
        """ Static method to raise error if key not found in dictionary from
        yaml file.

        :param source_id: dictionary containing source_type -> string,\
                            source_id -> string, document -> yaml document
        :param key: key to check in the doc
        """
        # first level
        for key in ['inputs', 'command', 'attrs']:
            self._raise_yaml_error_if_no_key(doc, source_id, key)
        # Second level in inputs and attrs:
        inputs = doc.get('inputs')
        attrs = doc.get('attrs')
        for _doc, key in [(inputs, 'default'), (inputs, 'xnat'),
                          (attrs, 'type'), (attrs, 'memory'),
                          (attrs, 'walltime')]:
            self._raise_yaml_error_if_no_key(_doc, source_id, key)
        # third level for default:
        default = doc.get('inputs').get('default')
        for key in ['spider_path']:
            self._raise_yaml_error_if_no_key(default, source_id, key)


    @ staticmethod
    def _raise_yaml_error_if_no_key(doc, source_id, key):
        """Method to raise an execption if the key is not in the dict

        :param doc: dict to check
        :param source_id: YAML source identifier string for logging
        :param key: key to search
        """
        if key not in list(doc.keys()):
            err = 'YAML source {} does not have {} defined. See example.'
            raise AutoProcessorError(err.format(source_id, key))


    # TODO: BenM/assessor_of_assessor/assessors are described by a type/inputs
    # tuple now, so we need to check the inputs of each assessor of the
    # appropriate type
    def get_assessor_mapping(self):
        return self.parser.assessor_parameter_map


    def parse_session(self, csess):
        self.parser.parse_session(csess)


    def should_run(self, obj_dict):
        """
        Method to see if the assessor should appear in the session.

        :param obj_dict: Dictionary of information about the scan or sesion
        :return: True if it should run, false if it shouldn't

        """
        # TODO: BenM/assessor_of_assessor/this method checks whether a given
        # processor type runs on a session - figure out if this is still
        # necessary
        if 'scan_type' in obj_dict:
            scantypes = self.scaninfo.get('types', '').split(',')
            if scantypes == 'all':
                return True
            else:
                for expression in scantypes:
                    regex = self.xnat.extract_exp(expression, self.full_regex)
                    if regex.match(obj_dict['scan_type']):
                        return True
                return False
        else:
            # By definition, this should always run, so it just returns true
            # with no checks for session
            return True


    def get_proctype(self):
        return self.name
    # ***** Names still need fixing! *****


    def get_assessor_input_types(self):
        """
        Enumerate the assessor input types for this. The default implementation
        returns an empty collection; override this method if you are inheriting
        from a non-yaml processor.
        :return: a list of input assessor types
        """
        assessor_inputs = filter(lambda i: i['artefact_type'] == 'assessor',
                                 self.parser.inputs.itervalues())
        assessors = map(lambda i: i['types'], assessor_inputs)

        return list(itertools.chain.from_iterable(assessors))


    # TODO: BenM/assessor_of_assessor/replace with processor_parser
    # functionality
    def has_inputs(self, cobj):
        """Method to check the inputs.

        By definition:
            status = 0  -> NEED_INPUTS, for session asr inputs and resources
            status = 1  -> NEED_TO_RUN
            status = -1 -> NO_DATA, for scan primary input isn't usable
            qcstatus needs a value only when -1 or 0.
        You need to set qcstatus to a short string that explain
        why it's no ready to run. e.g: No NIFTI

        :param cobj: cached object define in dax.XnatUtils (Session or Scan)
                     (see XnatUtils in dax for information)
        :return: status, qcstatus
        """
        return self.parser.has_inputs(cobj)


    # TODO: BenM/assessor_of_assessor/this method is no longer suitable for
    # execution on a single assessor, as it generates commands for the whole
    # session. In any case, the command should be written out to the xnat
    # assessor schema so that it can simply be launched, rather than performing
    # this reconstruction each time the dax launch command is called
    def get_cmds(self, cassr, jobdir):
        """Method to generate the spider command for cluster job.

        :param assessor: pyxnat assessor object
        :param jobdir: jobdir where the job's output will be generated
        :return: command to execute the spider in the job script
        """
        # Add the jobidr and the assessor label:
        assr_label = cassr.label()

        # Get the csess:
        csess = cassr.session()

        # TODO: BenM/assessor_of_assessors/parse each scan / assessor and
        # any select statements and generate one or more corresponding commands

        self.parser.command_params

        # combine the user overrides with the input parameters for each
        # distinct command
        commands = []
        for variable_set in self.parser.command_params:
            combined_params = {}
            for k, v in variable_set.iteritems():
                combined_params[k] = v
            for k, v in self.user_overrides.iteritems():
                combined_params[k] = v

            cmd = self.command.format(combined_params)

            for key, value in list(self.extra_user_overrides.items()):
                cmd = '{} --{} {}'.format(cmd, key, value)

            # TODO: BenM/assessor_of_assessor/each assessor is separate and
            # has a different label; change the code to fetch the label from
            # the assessor
            # Add assr and jobidr:
            if ' -a ' not in cmd and ' --assessor ' not in cmd:
                cmd = '{} -a {}'.format(cmd, assr_label)
            if ' -d ' not in cmd:
                cmd = '{} -d {}'.format(cmd, jobdir)

            commands.append(cmd)

        return commands


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
    if proc_list is not None:
        for proc in proc_list:
            if issubclass(proc.__class__, ScanProcessor):
                scan_proc_list.append(proc)
            elif issubclass(proc.__class__, SessionProcessor):
                sess_proc_list.append(proc)
            elif issubclass(proc.__class__, AutoProcessor):
                if proc.type == 'scan':
                    scan_proc_list.append(proc)
                else:
                    sess_proc_list.append(proc)
            else:
                LOGGER.warn('unknown processor type: %s' % proc)

    return sess_proc_list, scan_proc_list
