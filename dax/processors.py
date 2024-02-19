""" Processor class define for Scan and Session."""

import logging
import re
import os
import json
import itertools
import requests

from uuid import uuid4
from datetime import date

from . import XnatUtils, task
from . import assessor_utils
from . import processor_parser
from . import yaml_doc
from .errors import AutoProcessorError
from .dax_settings import DEFAULT_FS_DATATYPE, DEFAULT_DATATYPE
from .task import NeedInputsException
from .processors_v3 import Processor_v3, SgpProcessor


__copyright__ = 'Copyright 2013 Vanderbilt University. All Rights Reserved'
__all__ = ['Processor', 'AutoProcessor']

# Logger for logs
LOGGER = logging.getLogger('dax')


class Processor(object):
    """ Base class for processor """
    def __init__(self, walltime_str, memreq_mb, spider_path,
                 version=None, ppn=1, env=None, suffix_proc='',
                 xsitype='proc:genProcData',
                 job_template=None):
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
        self.job_template = job_template
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

    def create_assessor(self, xnatsession, inputs, relabel=False):
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
                if relabel:
                    _proj = assessor.parent().parent().parent().label()
                    _subj = assessor.parent().parent().label()
                    _sess = assessor.parent().label()
                    label = '-x-'.join([_proj, _subj, _sess, self.name, guid])
                else:
                    label = guid

                # Set creation date to today
                date_key = '{}/date'.format(self.xsitype.lower())
                date_val = str(date.today())
                kwargs[date_key] = date_val

                # Create the assessor
                assessor.create(assessors=self.xsitype.lower(),
                                ID=guid, label=label,
                                **kwargs)
                return assessor

            attempts += 1

    def _serialize_inputs(self, inputs):
        return json.dumps(inputs)

    def _deserialize_inputs(self, assessor):
        return json.loads(
            XnatUtils.parse_assessor_inputs(assessor.attrs.get('inputs')))


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
            raise AutoProcessorError(
                "Parameter 'yaml_source' must be provided")

        self.xnat = xnat
        self.user_overrides = dict()
        self.extra_user_overrides = dict()

        self._read_yaml(yaml_source)

        # Edit the values from user inputs:
        if user_inputs is not None:
            self._edit_inputs(user_inputs, yaml_source)

        self.parser = processor_parser.ProcessorParser(
            yaml_source.contents, self.proctype)

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
        yaml_name = yaml_source.source_id

        for key, val in list(user_inputs.items()):
            LOGGER.debug('overriding:key={}, file={}'.format(key, yaml_name))
            tags = key.split('.')
            if key.startswith('inputs.default'):
                # change value in inputs
                if tags[-1] in list(self.user_overrides.keys()):
                    self.user_overrides[tags[-1]] = val
                elif tags[-1] in list(self.extra_user_overrides.keys()):
                    self.extra_user_overrides[tags[-1]] = val
                else:
                    msg = 'key not found in default inputs:key={}, file={}'
                    msg = msg.format(tags[-1], yaml_name)
                    LOGGER.error(msg)
                    raise AutoProcessorError(msg)

            elif key.startswith('inputs.xnat'):
                # change value in self.xnat_inputs
                if tags[2] not in list(self.xnat_inputs.keys()):
                    msg = 'key not found in xnat inputs:key={}, file={}'
                    msg = msg.format(tags[3], yaml_name)
                    LOGGER.error(msg)
                    raise AutoProcessorError(msg)

                # Match the scan number or assessor number (e.g: scan1)
                sobj = None
                for obj in self.xnat_inputs[tags[2]]:
                    if tags[3] == obj['name']:
                        sobj = obj
                        break

                if sobj is None:
                    msg = 'invalid override:key={}, file={}'
                    msg = msg.format(key, yaml_name)
                    LOGGER.error(msg)
                    raise AutoProcessorError(msg)

                if tags[4] == 'resources':
                    if tags[6] == 'fmatch':
                        # Match the resource name
                        robj = None
                        for obj in sobj['resources']:
                            if tags[5] == obj['varname']:
                                robj = obj
                                break

                        if robj is None:
                            msg = 'invalid override:key={}, file={}'
                            LOGGER.error(msg)
                            raise AutoProcessorError(msg)

                        msg = 'overriding fmatch:key={}, val={}'
                        msg = msg.format(key, val)
                        LOGGER.debug(msg)
                        robj['fmatch'] = val
                    else:
                        msg = 'invalid override:key={}, file={}'
                        msg = msg.format(key, yaml_name)
                        LOGGER.error(msg)
                        raise AutoProcessorError(msg)
                else:
                    LOGGER.info('overriding:{}:{}'.format(tags[4], str(val)))
                    obj[tags[4]] = val

            elif key.startswith('attrs'):
                # change value in self.attrs
                if tags[-1] in list(self.attrs.keys()):
                    self.attrs[tags[-1]] = val
                else:
                    msg = 'key not found in attrs:key={}, file={}'
                    msg = msg.format(tags[-1], yaml_name)
                    LOGGER.error(msg)
                    raise AutoProcessorError(msg)

            else:
                msg = 'invalid override:key={}, file={}'
                msg = msg.format(key, yaml_name)
                LOGGER.error(msg)
                raise AutoProcessorError(msg)

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

        # Set attributes:
        self.spider_path = self.user_overrides.get('spider_path')
        self.name = self.proctype

        # Override template
        if doc.get('jobtemplate'):
            _tmp = doc.get('jobtemplate')

            # Make sure we have the full path
            if not os.path.isabs(_tmp):
                # If only filename, we assume it is same folder as default
                _tmp = os.path.join(os.path.dirname(self.job_template), _tmp)

            # Override it
            self.job_template = os.path.join(_tmp)

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
                          (attrs, 'memory'),
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

    def parse_session(self, csess, sessions, pets=None):
        """
        Method to run the processor parser on this session, in order to
        calculate the pattern matches for this processor and the sessions
        provided
        :param csess: the active session. For non-longitudinal studies, this is
        the session that the pattern matching is performed on. For longitudinal
        studies, this is the 'current' session from which all prior sessions
        are numbered for the purposes of pattern matching
        :param sessions: the full, time-ordered list of sessions that should be
        considered for longitudinal studies.
        :return: None
        """
        return self.parser.parse_session(csess, sessions, pets)

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
        assessor_inputs = [i for i in list(self.parser.inputs.values()) if i['artefact_type'] == 'assessor']
        assessors = [i['types'] for i in assessor_inputs]

        return list(itertools.chain.from_iterable(assessors))

    # TODO: BenM/assessor_of_assessor/this method is no longer suitable for
    # execution on a single assessor, as it generates commands for the whole
    # session. In any case, the command should be written out to the xnat
    # assessor schema so that it can simply be launched, rather than performing
    # this reconstruction each time the dax launch command is called
    def get_cmds(self, assr, jobdir):
        """Method to generate the spider command for cluster job.

        :param assessor: pyxnat assessor object
        :param jobdir: jobdir where the job's output will be generated
        :return: command to execute the spider in the job script
        """

        # TODO: BenM/assessor_of_assessors/parse each scan / assessor and
        # any select statements and generate one or more corresponding commands

        # self.parser.generate_command(cassr, )

        # combine the user overrides with the input parameters for each
        # distinct command
        commands = []
        variable_set = self.parser.get_variable_set(assr)
        combined_params = {}
        for k, v in list(variable_set.items()):
            combined_params[k] = v
        for k, v in list(self.user_overrides.items()):
            combined_params[k] = v

        cmd = self.command.format(**combined_params)

        for key, value in list(self.extra_user_overrides.items()):
            cmd = '{} --{} {}'.format(cmd, key, value)

        # TODO: BenM/assessor_of_assessor/each assessor is separate and
        # has a different label; change the code to fetch the label from
        # the assessor
        # Add assr and jobdir:
        assr_full_name =\
            assessor_utils.full_label_from_assessor(assr)
        if ' -a ' not in cmd and ' --assessor ' not in cmd:
            cmd = '{} -a {}'.format(cmd, assr_full_name)
        if ' -d ' not in cmd:
            cmd = '{} -d {}'.format(cmd, jobdir)

        commands.append(cmd)

        return commands


class MoreAutoProcessor(AutoProcessor):
    """ More Auto Processor class for AutoSpider using YAML files"""

    def __init__(self, xnat, yaml_source, user_inputs=None,
                 singularity_imagedir=None, job_template='~/job_template.txt'):

        """
        Entry point for the auto processor

        :param yaml_file: yaml file defining the processor
        :return: None

        """

        # Load outputs
        self.outputs = dict()

        # Save location of singularity imagedir
        self.singularity_imagedir = singularity_imagedir

        # Set the template to the global default, it could be overwritten by
        # processor yaml
        self.job_template = job_template

        super(MoreAutoProcessor, self).__init__(xnat, yaml_source, user_inputs)

    def _read_yaml(self, yaml_source):
        """
        Method to read the processor arguments and there default value.

        :param yaml_file: path to yaml file defining the processor
        """
        if yaml_source.source_type is None:
            raise AutoProcessorError('Empty yaml source provided')

        doc = yaml_source.contents

        # Set Inputs from Yaml
        self._check_default_keys(yaml_source.source_id, doc)
        self.attrs = doc.get('attrs')
        self.command = doc.get('command')

        # Set Inputs from Yaml
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

        # Container path, prepend singularity imagedir
        self.container_path = inputs.get('default').get('container_path')
        if ((self.container_path.endswith('.simg') or
                self.container_path.endswith('.img') or
                self.container_path.endswith('.sif')) and
                not os.path.isabs(self.container_path) and
                self.singularity_imagedir):
            self.container_path = os.path.join(
                self.singularity_imagedir, self.container_path)

        # Overwrite container_path for building script
        self.user_overrides['container_path'] = self.container_path

        # Getting proctype and version from Yaml
        if doc.get('procversion'):
            self.version = doc.get('procversion')
        else:
            self.version = self.parse_procversion()

        if doc.get('procname'):
            procname = doc.get('procname')
        else:
            procname = self.parse_procname()

        if doc.get('proctype'):
            self.proctype = doc.get('proctype')
        else:
            self.proctype = '{}_v{}'.format(
                procname, self.version.split('.')[0]
            )

        suffix = self.attrs.get('suffix', None)
        if suffix:
            if suffix[0] != '_':
                suffix = '_{}'.format(suffix)

            suffix = re.sub('[^a-zA-Z0-9]', '_', suffix)

            if suffix[-1] == '_':
                suffix = suffix[:-1]

            self.proctype = '{}{}'.format(self.proctype, suffix)

        # Set attributes:
        self.name = self.proctype

        # Set Outputs from Yaml
        self.outputs = doc.get('outputs')

        # Override template
        if doc.get('jobtemplate'):
            _tmp = doc.get('jobtemplate')

            # Make sure we have the full path
            if not os.path.isabs(_tmp):
                # If only filename, we assume it is same folder as default
                _tmp = os.path.join(os.path.dirname(self.job_template), _tmp)

            # Override it
            self.job_template = os.path.join(_tmp)

    def _check_default_keys(self, source_id, doc):
        """ Static method to raise error if key not found in dictionary from
        yaml file.

        :param yaml_file: path to yaml file defining the processor
        :param doc: doc dictionary extracted from the yaml file
        :param key: key to check in the doc
        """
        # first level
        for key in ['inputs', 'command', 'attrs', 'outputs']:
            self._raise_yaml_error_if_no_key(doc, source_id, key)

        # Second level in inputs and attrs:
        inputs = doc.get('inputs')
        attrs = doc.get('attrs')
        for _doc, key in [(inputs, 'default'), (inputs, 'xnat'),
                          (attrs, 'memory'),
                          (attrs, 'walltime')]:
            self._raise_yaml_error_if_no_key(_doc, source_id, key)

        # third level for default:
        default = doc.get('inputs').get('default')

        for key in ['container_path']:
            self._raise_yaml_error_if_no_key(default, source_id, key)

    def parse_procname(self):
        tmp = self.container_path
        tmp = tmp.split('://')[-1]
        tmp = tmp.rsplit('/')[-1]

        if len(re.split('/*[_:]v[0-9]/*', tmp)) > 1:
            tmp = re.split('/*[_:]v[0-9]/*', tmp)[0]

        if tmp.startswith('Spider_'):
            tmp = tmp[len('Spider_'):]

        return tmp

    def parse_procversion(self):
        tmp = self.container_path

        tmp = tmp.split('://')[-1]
        tmp = tmp.rsplit('/')[-1]

        if tmp.endswith('.img'):
            tmp = tmp.split('.img')[0]
        elif tmp.endswith('.simg'):
            tmp = tmp.split('.simg')[0]
        elif tmp.endswith('.py'):
            tmp = tmp.split('.py')[0]

        if len(re.split('/*_v[0-9]/*', tmp)) > 1:
            tmp = tmp.split('_v')[-1].replace('_', '.')
        elif len(re.split('/*:v[0-9]/*', tmp)) > 1:
            tmp = tmp.split(':v')[-1].replace('_', '.')

        return tmp

    def build_cmds(self, assr, assr_label, sessions, jobdir, resdir):
        """Method to generate the spider command for cluster job.
        :param jobdir: jobdir where the job's output will be generated
        :return: command to execute the spider in the job script
        """
        assr_inputs = XnatUtils.get_assessor_inputs(assr, sessions)

        # Make every input a list, so we can iterate later
        for k in assr_inputs:
            if not isinstance(assr_inputs[k], list):
                assr_inputs[k] = [assr_inputs[k]]

        # Find values for the xnat inputs
        var2val, input_list = self.parser.find_inputs(
            assr, sessions, assr_inputs)

        # Append other stuff
        for k, v in list(self.user_overrides.items()):
            var2val[k] = v

        for k, v in list(self.extra_user_overrides.items()):
            var2val[k] = v

        # Include the assessor label
        var2val['assessor'] = assr_label

        # Handle xnat attributes
        for attr_in in self.xnat_inputs.get('attrs', list()):
            _var = attr_in['varname']
            _attr = attr_in['attr']
            _obj = attr_in['object']
            _val = ''

            if _obj == 'subject':
                _val = assr.parent().parent().attrs.get(_attr)
            elif _obj == 'session':
                _val = assr.parent().attrs.get(_attr)
            elif _obj == 'scan':
                _ref = attr_in['ref']
                _refval = [a.rsplit('/', 1)[1] for a in assr_inputs[_ref]]
                _val = ','.join(
                    [assr.parent().scan(r).attrs.get(_attr) for r in _refval])
            elif _obj == 'assessor':
                if 'ref' in attr_in:
                    _ref = attr_in['ref']
                    _refval = [a.rsplit('/', 1)[1] for a in assr_inputs[_ref]]
                    _val = ','.join(
                        [assr.parent().assessor(r).attrs.get(_attr) for r in _refval])
                else:
                    _val = assr.attrs.get(_attr)
            else:
                LOGGER.error('invalid YAML')
                err = 'YAML File:contains invalid attribute:{}'
                raise AutoProcessorError(err.format(_attr))

            if _val == '':
                raise NeedInputsException('Missing ' + _attr)
            else:
                var2val[_var] = _val

        # Handle edits
        edit_res = assr.out_resource(task.EDITS_RESOURCE)
        if edit_res.exists():
            file_list = edit_res.files().get()
            assr_path = '/projects/{}/subjects/{}/experiments/{}/assessors/{}'.format(
                assr.parent().parent().parent().label(),
                assr.parent().parent().label(),
                assr.parent().label(),
                assr.label()
                )

            for edit_in in self.xnat_inputs.get('edits', list()):
                _fpref = edit_in['fpref']
                _var = edit_in['varname']

                # Filter files that match prefix
                cur_list = [f for f in file_list if f.startswith(_fpref)]

                if cur_list:
                    # Sort and grab the last file
                    _val = sorted(cur_list)[-1]

                    # Build full uri
                    _uri = '{}/data{}/out/resources/{}/files/{}'.format(
                        assr._intf.host,
                        assr_path,
                        task.EDITS_RESOURCE,
                        _val)

                    # Append to inputs to be downloaded
                    input_list.append({
                        'fdest': _fpref,
                        'ftype': 'FILE',
                        'fpath': _uri,
                        'ddest': ''
                    })

                    # Set the value for command text
                    var2val[_var] = '/INPUTS/'+_fpref

                else:
                    # None found
                    var2val[_var] = ''
        else:
            for edit_in in self.xnat_inputs.get('edits', list()):
                var2val[edit_in['varname']] = ''

        # Build the command text
        dstdir = os.path.join(resdir, assr_label)
        assr_dir = os.path.join(jobdir, assr_label)
        cmd = self.build_text(
            var2val, input_list, assr_dir, dstdir,
            assr._intf.host, assr._intf.user)

        return [cmd]

    def build_text(self, var2val, input_list, jobdir, dstdir, host, user):
        # Initialize commands
        cmd = '\n\n'

        # Append the list of inputs, URL-encoding the fpath to handle special chars in URLs
        cmd += 'INLIST=(\n'
        for cur in input_list:
            cur['fpath'] = requests.utils.quote(cur['fpath'],safe=":/")
            cmd += '{fdest},{ftype},{fpath},{ddest}\n'.format(**cur)

        cmd += ')\n\n'

        # Append the list on outputs
        cmd += 'OUTLIST=(\n'
        for cur in self.outputs:
            cmd += '{path},{type},{resource}\n'.format(**cur)

        cmd += ')\n\n'

        # Append other paths
        cmd += 'VERSION={}\n'.format(self.version)
        cmd += 'JOBDIR=$(mktemp -d "{}.XXXXXXXXX") || '.format(jobdir)
        cmd += '{ echo "mktemp failed"; exit 1; }\n'
        cmd += 'INDIR=$JOBDIR/INPUTS\n'
        cmd += 'OUTDIR=$JOBDIR/OUTPUTS\n'
        cmd += 'DSTDIR={}\n\n'.format(dstdir)
        cmd += 'CONTAINERPATH={}\n\n'.format(self.container_path)
        cmd += 'XNATHOST={}\n\n'.format(host)
        cmd += 'XNATUSER={}\n\n'.format(user)

        # Append the main command
        cmd += 'MAINCMD=\"'
        cmd += self.command.format(**var2val)
        cmd += '\"\n'

        return cmd


def processors_by_type(proc_list):
    """
    Organize the processor types and return a list of session processors
     first, then scan

    :param proc_list: List of Processor classes from the DAX settings file
    :return: Lists of processors by type

    """
    auto_proc_list = list()

    # Build list of processors by type
    if proc_list is not None:
        for proc in proc_list:
            if isinstance(proc, Processor_v3):
                auto_proc_list.append(proc)
            elif issubclass(proc.__class__, AutoProcessor):
                auto_proc_list.append(proc)
            else:
                LOGGER.warn('unknown processor type: %s' % proc)

    return auto_proc_list


def load_from_yaml(xnat, filepath, user_inputs=None,
                   singularity_imagedir=None, job_template=None):
    """
    Load processor from yaml
    :param filepath: path to yaml file
    :return: processor
    """
    yaml_obj = yaml_doc.YamlDoc().from_file(filepath)

    # Load file based on yaml version and data type
    if yaml_obj.contents.get('inputs').get('xnat').get('sessions', False):
        # This must be a subjgenproc
        return SgpProcessor(
            xnat, filepath, user_inputs, singularity_imagedir, job_template)
    elif yaml_obj.contents.get('procyamlversion', '') == '3.0.0-dev.0':
        LOGGER.debug('loading as Processor_v3:{}'.format(filepath))
        return Processor_v3(
            xnat, filepath, user_inputs, singularity_imagedir, job_template)
    elif yaml_obj.contents.get('moreauto'):
        return MoreAutoProcessor(xnat, yaml_obj, user_inputs,
                                 singularity_imagedir, job_template)
    else:
        return AutoProcessor(xnat, yaml_obj, user_inputs)
