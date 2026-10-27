import os
import re
import fnmatch
import logging
import copy
import itertools
import json
from datetime import date

import requests

from .. import yaml_doc
from ..processors_v3 import validate_yaml_filename, parse_proctype, parse_procversion, SINGULARITY_BASEOPTS
from ..errors import AutoProcessorError
from ..task import NeedInputsException
from ..task import (
    NEED_INPUTS,
    OPEN_STATUS_LIST,
    BAD_QA_STATUS,
    JOB_PENDING,
    REPROC,
    RERUN,
    NEEDS_QA,
)


# Logger for logs
LOGGER = logging.getLogger('dax')


def load_from_yaml_noxnat(
    filepath,
    user_inputs=None,
    singularity_imagedir=None,
    job_template=None):
    """
    Load processor from yaml
    :param filepath: path to yaml file
    :return: processor
    """
    yaml_obj = yaml_doc.YamlDoc().from_file(filepath)

    # Load file based on yaml version and data type
    if yaml_obj.contents.get('inputs').get('xnat').get('sessions', False):
        print('load as subject assessor sgp')
        # This must be a subjgenproc
        return SgpProcessorNoXnat(filepath, user_inputs, singularity_imagedir, job_template)
    elif yaml_obj.contents.get('procyamlversion', '') == '3.0.0-dev.0':
        print('load as session assessor')
        return ProcessorNoXnat(filepath, user_inputs, singularity_imagedir, job_template)
    else:
        raise Exception('failed to load from yaml, invalid file')


class ProcessorNoXnat(object):
    """Processor class YAML files"""

    def __init__(
        self,
        yaml_file,
        user_inputs=None,
        singularity_imagedir=None,
        job_template='~/job_template.txt',
    ):
        """
        Entry point for the auto processor

        :param yaml_file: yaml file defining the processor
        :return: None

        """

        # Initialize class members
        self.proc_inputs = {}
        self.proc_edits = []
        self.xnat_attrs = []
        self.iteration_sources = set()
        self.match_filters = {}
        self.variables_to_inputs = {}
        self.xnat_inputs = {}
        self.command = {}
        self.container_path = None
        self.walltime_str = None
        self.memreq_mb = None
        self.ppn = 1
        self.env = None
        self.outputs = []
        self.user_overrides = {}
        self.extra_user_overrides = {}
        self.xsitype = "proc:genProcData"

        if user_inputs:
            self.user_inputs = user_inputs   # used to override default values
        else:
            self.user_inputs = {}

        validate_yaml_filename(yaml_file)
        # TODO: validate_yaml_file contents(yaml_file)

        # Cache input file path
        self.yaml_file = yaml_file

        # Cache location of singularity imagedir
        self.singularity_imagedir = singularity_imagedir

        # Init job template as global default, could be overwritten by yaml
        self.job_template = job_template

        # Get processor name/type/version from yaml file name
        self.proctype = parse_proctype(yaml_file)
        self.procversion = parse_procversion(yaml_file)
        self.name = self.proctype  # launcher.py still uses "name"

        # Load the yaml
        self._read_yaml(yaml_file)

    def _edit_inputs(self):
        """
        Method to override inputs from the YAML file based on the user inputs

        """
        for key, val in self.user_inputs.items():
            LOGGER.debug('overriding:key={}'.format(key))
            tags = key.split('.')
            if key.startswith('inputs.xnat'):
                # change value
                if tags[2] not in list(self.xnat_inputs.keys()):
                    msg = 'key not found in xnat inputs:key={}'
                    msg = msg.format(tags[3])
                    LOGGER.error(msg)
                    raise AutoProcessorError(msg)

                # Match the scan number or assessor number (e.g: scan1)
                sobj = None
                for obj in self.xnat_inputs[tags[2]]:
                    if tags[3] == obj['name']:
                        sobj = obj
                        break

                if sobj is None:
                    msg = 'invalid override:key={}'
                    msg = msg.format(key)
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
                            msg = 'invalid override:key={}'
                            LOGGER.error(msg)
                            raise AutoProcessorError(msg)

                        msg = 'overriding fmatch:key={}'
                        msg = msg.format(key, val)
                        LOGGER.debug(msg)
                        robj['fmatch'] = val
                    else:
                        msg = 'invalid override:key={}'
                        msg = msg.format(key)
                        LOGGER.error(msg)
                        raise AutoProcessorError(msg)
                else:
                    LOGGER.info('overriding:{}:{}'.format(tags[4], str(val)))
                    obj[tags[4]] = val

            elif key in ['walltime', 'attrs.walltime']:
                self.walltime_str = val
            elif key in ['memory', 'attrs.memory']:
                self.memreq_mb = val
            else:
                msg = 'invalid override:key={}'
                msg = msg.format(key)
                LOGGER.error(msg)
                raise AutoProcessorError(msg)

    def _read_yaml(self, yaml_file):
        """
        Method to read the processor

        :param yaml_file: path to yaml file defining the processor
        """
        doc = yaml_doc.YamlDoc().from_file(yaml_file).contents

        # NOTE: we are assuming this yaml has already been validated

        # Set version from yaml
        self.procyamlversion = doc.get('procyamlversion')

        # Set requirements from Yaml
        reqs = doc.get('requirements')
        self.walltime_str = reqs.get('walltime', '0-2')
        self.memreq_mb = reqs.get('memory', '16G')
        self.ppn = reqs.get('ppn', 1)
        self.env = reqs.get('env', None)

        # Load the command text
        self.command = doc.get('command')
        self.command_pre = doc.get('pre', None)
        self.command_post = doc.get('post', None)

        # Set Inputs from Yaml
        inputs = doc.get('inputs')

        # Handle vars
        for key, value in inputs.get('vars', {}).items():
            # If value is a key in command
            k_str = '{{{}}}'.format(key)
            if k_str in self.command:
                self.user_overrides[key] = value
            else:
                if isinstance(value, bool) and value is True:
                    self.extra_user_overrides[key] = ''
                elif value and value != 'None':
                    self.extra_user_overrides[key] = value

        # Get xnat inputs, apply edits, then parse
        self.xnat_inputs = inputs.get('xnat')
        self._edit_inputs()
        self._parse_xnat_inputs()

        # Containers
        self.containers = []
        for c in doc.get('containers'):
            curc = copy.deepcopy(c)

            # Set container path
            cpath = curc['path']

            if not os.path.isabs(cpath) and self.singularity_imagedir:
                # Prepend singularity imagedir
                curc['path'] = os.path.join(self.singularity_imagedir, cpath)

            # Add to our containers list
            self.containers.append(curc)

        # Set the primary container path
        container_name = self.command['container']
        for c in self.containers:
            if c.get('name') == container_name:
                self.container_path = c.get('path')

        # Check primary container
        if not self.container_path:
            if len(self.containers) == 1:
                self.container_path = self.containers[0].get('path')
            else:
                msg = 'multiple containers requires a primary to be set'
                LOGGER.error(msg)
                raise AutoProcessorError(msg)

        # Outputs from Yaml
        self._parse_outputs(doc.get('outputs'))

        # Override template
        if doc.get('jobtemplate'):
            _tmp = doc.get('jobtemplate')

            # Make sure we have the full path
            if not os.path.isabs(_tmp):
                # If only filename, we assume it is same folder as default
                _tmp = os.path.join(os.path.dirname(self.job_template), _tmp)

            # Override it
            self.job_template = os.path.join(_tmp)
        else:
            self.job_template = os.path.join(
                os.path.dirname(self.job_template),
                'job_template_v3.txt')

    def build_var2val(self, info, project_data):
        assr_label = info['ASSR']

        # Make every input a list, so we can iterate later
        inputs = info['INPUTS']
        for k in inputs.keys():
            if not isinstance(inputs[k], list):
                inputs[k] = [inputs[k]]

        # Find values for the xnat inputs
        var2val, input_list = self.find_inputs_pd(inputs, project_data)

        # Append other stuff
        for k, v in self.user_overrides.items():
            var2val[k] = v

        for k, v in self.extra_user_overrides.items():
            var2val[k] = v

        # Include the assessor label
        var2val['assessor'] = assr_label

        # Handle xnat attributes
        for attr_in in self.xnat_attrs:
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
                _refval = [a.rsplit('/', 1)[1] for a in inputs[_ref]]
                _val = ','.join(
                    [assr.parent().scan(r).attrs.get(_attr) for r in _refval]
                )
            elif _obj == 'assessor':
                if 'ref' in attr_in:
                    _ref = attr_in['ref']
                    _refval = [a.rsplit('/', 1)[1] for a in inputs[_ref]]
                    _val = ','.join([assr.parent().assessor(r).attrs.get(_attr) for r in _refval])
                else:
                    _val = assr.attrs.get(_attr)
            else:
                logger.error('invalid YAML')
                err = 'YAML File:contains invalid attribute:{}'
                raise AutoProcessorError(err.format(_attr))

            if _val == '':
                raise NeedInputsException('Missing ' + _attr)
            else:
                var2val[_var] = _val

        return var2val, input_list

    def _parse_outputs(self, outputs):
        self.outputs = []

        for c in outputs:
            # Check for keywords
            if 'pdf' in c:
                _path = c['pdf']
                _type = 'FILE'
                _res = 'PDF'
            elif 'dir' in c:
                _path = c['dir']
                _type = 'DIR'
                _res = c['dir']
            elif 'stats' in c:
                _path = c['stats']
                _type = 'FILE'
                _res = 'STATS'

            # Get explicitly set path, type, resource
            # These will override anything set by keywords
            if 'path' in c:
                _path = c['path']

            if 'type' in c:
                _type = c['type']

            if 'resource' in c:
                _res = c['resource']

            # Add to our outputs list
            self.outputs.append({'path': _path, 'type': _type, 'resource': _res})

    def get_proctype(self):
        return self.proctype


    def build_text(self, var2val, input_list, jobdir, dstdir, host, user):
        # Initialize commands
        cmd = '\n\n'

        # Append the list of inputs
        cmd += self.build_inputs_text(input_list)

        # Append the list of outputs
        cmd += self.build_outputs_text(self.outputs)

        # Append other paths
        cmd += 'VERSION={}\n'.format(self.procversion)
        cmd += 'JOBDIR=$(mktemp -d "{}.XXXXXXXXX") || '.format(jobdir)
        cmd += '{ echo "mktemp failed"; exit 1; }\n'
        cmd += 'INDIR=$JOBDIR/INPUTS\n'
        cmd += 'OUTDIR=$JOBDIR/OUTPUTS\n'
        cmd += 'DSTDIR={}\n\n'.format(dstdir)
        cmd += 'CONTAINERPATH={}\n\n'.format(self.container_path)
        cmd += 'XNATHOST={}\n\n'.format(host)
        cmd += 'XNATUSER={}\n\n'.format(user)

        # Append main commands
        cmd += self.build_main_text(var2val)

        return cmd

    def build_singularity_cmd(self, runexec, command, var2val):

        if 'container' not in command:
            err = 'singularity modes require a container to be set'
            LOGGER.error(err)
            raise AutoProcessorError(err)

        if runexec not in ['run', 'exec']:
            err = f'singularity mode {runexec} not known'
            LOGGER.error(err)
            raise AutoProcessorError(err)

        # Use the container name to get the path
        cpath = self.get_container_path(command['container'])

        if not cpath:
            err = 'container path not found'
            LOGGER.error(err)
            raise AutoProcessorError(err)

        # Initialize command
        if 'opts' in command:
            # Get the user defined opts
            _opts = command['opts']
            # Prepend clean and contain
            _opts = f'--contain --cleanenv {_opts}'
            command_txt = f'singularity {runexec} {_opts}'
        else:
            command_txt = f'singularity {runexec} {SINGULARITY_BASEOPTS}'

        # Append extra options
        _extra = command.get('extraopts', None)
        if _extra:
            command_txt = '{} {}'.format(command_txt, _extra)

        # Append container name
        command_txt = '{} {}'.format(command_txt, cpath)

        # Append arguments for the singularity entrypoint
        cargs = command.get('args', None)
        if cargs:
            # Unescape and then escape double quotes
            cargs = cargs.replace('\\"', '"').replace('"', '\\\"')
            command_txt = '{} {}'.format(command_txt, cargs)

        # Replace vars with values from var2val
        command_txt = command_txt.format(**var2val)

        return command_txt

    def build_main_text(self, var2val):
        txt = 'MAINCMD=\"'

        # Build and append the pre command that runs before main
        if self.command_pre:
            txt += self.build_command(self.command_pre, var2val)
            txt += ' && '

        # Build and append the main command
        txt += self.build_command(self.command, var2val)

        # Append the post command that runs after main
        if self.command_post:
            txt += ' && '
            txt += self.build_command(self.command_post, var2val)

        # Finish with a newline
        txt += '\"\n'

        # Return the whole command lines
        return txt

    def build_command(self, command, var2val):
        txt = ''

        # Build and append the post command
        if 'type' not in command:
            err = 'command type not set'
            LOGGER.error(err)
            raise AutoProcessorError(err)

        if command['type'] == 'singularity_run':
            txt = self.build_singularity_cmd('run', command, var2val)

        elif command['type'] == 'singularity_exec':
            txt = self.build_singularity_cmd('exec', command, var2val)

        else:
            err = 'invalid command type: {}'.format(command['type'])
            LOGGER.error(err)
            raise AutoProcessorError(err)

        return txt

    def build_outputs_text(self, outputs):
        txt = 'OUTLIST=(\n'

        for cur in outputs:
            txt += '{path},{type},{resource}\n'.format(**cur)

        txt += ')\n\n'

        return txt

    def build_inputs_text(self, inputs):
        txt = 'INLIST=(\n'

        for cur in inputs:
            cur['fpath'] = requests.utils.quote(cur['fpath'], safe=":/")
            txt += '{fdest},{ftype},{fpath},{ddest}\n'.format(**cur)

        txt += ')\n\n'

        return txt

    def write_processor_spec(self, filename):
        # Write a file with the path to the base processor and any overrides
        # The file is intended to be written to diskq using the assessor
        # label as the filename
        with open(filename, 'w') as f:
            # write processor yaml filename
            f.write('{}\n'.format(self.yaml_file))

            # write customizations
            if self.user_inputs:
                for k, v in self.user_inputs.items():
                    f.write('{}={}\n'.format(k, v))

            # singularity_imagedir
            f.write('{}={}\n'.format('singularity_imagedir', self.singularity_imagedir))

            # job_template
            f.write('{}={}\n'.format('job_template', self.job_template))

            # extra blank line
            f.write('\n')

    def parse_session_pd(self, session, project_data):
        LOGGER.debug(f'parsing session with project data:{session}')
        """
        Parse a session to determine what assessors *should* exist for
        this processor
        """

        artefacts_by_input = self._map_inputs(session, project_data)
        LOGGER.debug(f'artefacts_by_input={artefacts_by_input}')

        param_sets = self._generate_parameter_matrix_pd(artefacts_by_input)
        LOGGER.debug(f'parameter_matrix={param_sets}')

        # Apply filters (e.g., remove parameter sets where inputs don't match)
        artefact_inputs = {}
        for i, a in enumerate(project_data['assessors']):
            artefact_inputs[a['full_path']] = a['INPUTS']

        param_sets = self._filter_matrix_pd(param_sets, artefact_inputs)
        LOGGER.debug(f'filtered={param_sets}')

        return param_sets

    def get_container_path(self, name):
        cpath = None

        # Find the matching container
        for c in self.containers:
            if c['name'] == name:
                cpath = c['path']
                break

        return cpath

    def find_inputs_pd(self, inputs, project_data):
        """
        Find the files or directories on xnat for the inputs

        takes an assessor, its input artefacts, its relevant sessions
        and returns the full paths to the input files/directories

        :param assr:
        :param sessions:
        :param assr_inputs:

        :return: variable_set, input_list:

        """
        variable_set = {}
        input_list = []
        rootdir = project_data['rootdir']

        # This will raise a NeedInputs exception if any inputs aren't ready
        verify_artefact_status(self.proc_inputs, inputs, project_data)

        LOGGER.debug(self.variables_to_inputs.items())

        # Map from parameters to input resources
        LOGGER.debug('mapping params to artefact resources')
        for k, v in list(self.variables_to_inputs.items()):
            LOGGER.debug('mapping:' + k, v)
            inp = self.proc_inputs[v['input']]
            resource = v['resource']

            LOGGER.debug('vinput={}'.format(v['input']))
            LOGGER.debug(f'resource={resource}')
            LOGGER.debug(inp['resources'])

            # Find the resource
            cur_res = None
            for inp_res in inp['resources']:
                if inp_res['varname'] == k:
                    cur_res = inp_res
                    break

            for vnum, vinput in enumerate(inputs[v['input']]):
                fname = None

                # Get list of all files in the resource, relative paths
                resource_dir = _get_resource_dir(rootdir, vinput, resource)
                file_list = _get_file_list(resource_dir, resource)

                if len(file_list) == 0:
                    LOGGER.debug('empty or missing resource')
                    raise NeedInputsException(f'No Resource:{resource}')

                if 'fmatch' in cur_res:
                    fmatch = cur_res['fmatch']
                elif cur_res['ftype'] == 'FILE':
                    # Default to all
                    fmatch = '*'
                else:
                    fmatch = None

                if 'filepath' in cur_res:
                    fpath = cur_res['filepath']
                    res_path = resource_dir + '/' + fpath

                    # Get base file name to be downloaded
                    fname = os.path.basename(fpath)
                elif fmatch:
                    # Filter list based on regex matching
                    regex = re.compile(fnmatch.translate(fmatch))
                    file_list = [x for x in file_list if regex.match(x)]

                    if len(file_list) == 0:
                        LOGGER.debug('no matching files found on resource')
                        raise NeedInputsException('No Files')

                    if len(file_list) > 1:
                        # Multiple files found, we only support explicit
                        # declaration of fmulti==any1, which tells dax to use
                        # any of the multiple files. We may later support
                        # other options

                        if 'fmulti' in cur_res and cur_res['fmulti'] == 'any1':
                            LOGGER.debug('multiple files, fmulti==any1, using first found')
                        else:
                            LOGGER.debug('multiple files, fmulti not set')
                            raise NeedInputsException(str(k) + ': multiple files')

                    # Create the full path to the file on the resource
                    res_path = '{}/{}'.format(resource_dir, file_list[0])

                    # Get just the filename for later
                    fname = os.path.basename(file_list[0])
                else:
                    # We want the whole resource
                    res_path = resource_dir

                    # Get just the resource name for later
                    fname = resource

                variable_set[k] = res_path

                if 'fdest' not in cur_res:
                    # Use the original file/resource name
                    fdest = fname
                elif len(inputs[v['input']]) > 1:
                    fdest = str(vnum) + cur_res['fdest']
                else:
                    fdest = cur_res['fdest']

                if 'ddest' in cur_res:
                    ddest = cur_res['ddest']
                else:
                    ddest = ''

                # Append to inputs to be downloaded
                input_list.append(
                    {
                        'fdest': fdest,
                        'ftype': cur_res['ftype'],
                        'fpath': variable_set[k],
                        'ddest': ddest,
                    }
                )

                # Replace path with destination path after download
                if 'varname' in cur_res:
                    variable_set[k] = fdest

        LOGGER.debug('finished mapping params to artefact resources')

        return variable_set, input_list

    def _parse_xnat_inputs(self):
        # Get the xnat attributes
        # TODO: validate these
        self.xnat_attrs = self.xnat_inputs.get('attrs', list())

        # Get the xnat edits
        # TODO: validate these
        self.proc_edits = self.xnat_inputs.get('edits', list())

        # get scans
        scans = self.xnat_inputs.get('scans', list())
        for s in scans:
            name = s.get('name')
            self.iteration_sources.add(name)

            types = [_.strip() for _ in s['types'].split(',')]

            resources = s.get('resources', [])

            if 'nifti' in s:
                # Add a NIFTI resource using value as fdest
                resources.append({'resource': 'NIFTI', 'fdest': s['nifti']})

            if 'edat' in s:
                # Add an EDAT resource using value as fdest
                resources.append({'resource': 'EDAT', 'fdest': s['edat']})

            # 2021-11-14 bdb Is anyone using this?
            artefact_required = False
            for r in resources:
                r['required'] = r.get('required', True)
                artefact_required = artefact_required or r['required']

            needs_qc = s.get('needs_qc', False)

            # Require scan is explicitly marked usable?
            require_usable = s.get('require_usable', False)

            # Consider an MR scan for an input if it's marked Unusable?
            skip_unusable = s.get('skip_unusable', False)

            # Include the 'first', or 'all', matching scans as possible inputs
            keep_multis = s.get('keep_multis', 'all')

            self.proc_inputs[name] = {
                'types': types,
                'artefact_type': 'scan',
                'needs_qc': needs_qc,
                'require_usable': require_usable,
                'resources': resources,
                'required': artefact_required,
                'skip_unusable': skip_unusable,
                'keep_multis': keep_multis,
            }

        # get assessors
        asrs = self.xnat_inputs.get('assessors', list())
        for a in asrs:
            name = a.get('name')
            self.iteration_sources.add(name)

            if 'proctypes' in a:
                types = [_.strip() for _ in a['proctypes'].split(',')]
            elif 'types' in a:
                types = [_.strip() for _ in a['types'].split(',')]
            else:
                msg = 'no types for assessor:{}'.format(name)
                LOGGER.error(msg)
                raise AutoProcessorError(msg)

            resources = a.get('resources', [])
            artefact_required = False
            for r in resources:
                r['required'] = r.get('required', True)
            artefact_required = artefact_required or r['required']

            self.proc_inputs[name] = {
                'types': types,
                'artefact_type': 'assessor',
                'needs_qc': a.get('needs_qc', False),
                'resources': resources,
                'required': artefact_required,
            }

        # Handle petscans section
        petscans = self.xnat_inputs.get('petscans', list())
        for p in petscans:
            name = p.get('name')
            self.iteration_sources.add(name)
            types = [x.strip() for x in p['scantypes'].split(',')]
            tracer = [x.strip() for x in p['tracer'].split(',')]

            resources = p.get('resources', [])

            if 'nifti' in p:
                # Add a NIFTI resource using value as fdest
                resources.append(
                    {'resource': 'NIFTI', 'fdest': p['nifti']})

            self.proc_inputs[name] = {
                'types': types,
                'artefact_type': 'scan',
                'needs_qc': p.get('needs_qc', False),
                'require_usable': p.get('require_usable', False),
                'resources': resources,
                'required': True,
                'tracer': tracer,
            }

        if 'filters' in self.xnat_inputs:
            self._parse_filters(self.xnat_inputs.get('filters'))

        self._populate_proc_inputs()
        self._parse_variables()

    def _get_petscans(self, session, project_data):
        petscans = []
        scans = project_data.get('scans')
        subject = ''

        for s in scans:
            if s['SESSION'] == session:
                subject = s['SUBJECT']
                break

        if subject:
            petscans = [x for x in scans if x['SUBJECT'] == subject and x['MODALITY'] == 'PET']

        return petscans

    def is_first_mr_session(self, session, project_data):
        is_first = True

        # Get the sessions/dates for this subject
        scans = project_data.get('scans')
        subject = [x for x in scans if x['SESSION'] == session][0]['SUBJECT']
        LOGGER.debug(f'is_first_mr_session:{session}:{subject}:getting scans')
        scans = [x for x in scans if x['SUBJECT'] == subject and x['MODALITY'] == 'MR']
        scans = sorted(scans, key=lambda x: x['DATE'])

        # Check if this is the first
        if len(scans) > 0 and scans[0]['SESSION'] != session:
            LOGGER.debug(f'is_first_mr_session:{session}:nope')
            is_first = False

        return is_first

    def _map_inputs(self, session, project_data):
        inputs = self.proc_inputs
        artefacts_by_input = {k: [] for k in inputs}
        artefact_ids_by_input = {k: [] for k in inputs}

        # Get lists for scans/assrs for this session
        LOGGER.debug('prepping session data')
        scans = [x for x in project_data.get('scans') if x['SESSION'] == session]
        assrs = [x for x in project_data.get('assessors') if x['SESSION'] == session]

        petscans = []
        # if this is the first mri, add scans
        if self.is_first_mr_session(session, project_data):
            LOGGER.debug(f'is first mri, adding pets:{session}')
            petscans = self._get_petscans(session, project_data)

        LOGGER.debug('matching artefacts')
        # Find list of scans/assessors that match each specified input
        # for i, iv in list(inputs.items()):
        for i, iv in sorted(inputs.items()):
            if 'tracer' in iv and iv['tracer']:
                # PET scan
                for p in petscans:
                    # Match the tracer name
                    tracer_name = p['TRACER']
                    tracer_match = False
                    for expression in iv['tracer']:
                        regex = re.compile(fnmatch.translate(expression))
                        if regex.match(tracer_name):
                            # found a match so exit the loop
                            tracer_match = True
                            break

                    if not tracer_match:
                        # None of the expressions matched
                        continue

                    # Now try to match the scan type
                    for expression in iv['types']:
                        regex = re.compile(fnmatch.translate(expression))
                        if regex.match(p['SCANTYPE']):
                            # Found a match, now check quality
                            if p['QUALITY'] == 'unusable':
                                LOGGER.debug('excluding unusable scan')
                            else:
                                artefacts_by_input[i].append(p['full_path'])

            elif iv['artefact_type'] == 'scan':
                # Input is a scan, so we iterate subject scans
                # to look for matches
                for cscan in scans:
                    # First we try to match the session type of the scan
                    # match scan type
                    for expression in iv['types']:
                        regex = re.compile(fnmatch.translate(expression))
                        if regex.match(cscan.get('SCANTYPE')):
                            scanid = cscan.get('SCANID')
                            LOGGER.debug('match found!')
                            if iv['skip_unusable'] and cscan.get('QUALITY') == 'unusable':
                                LOGGER.info(f'Excluding unusable scan:{scanid}')
                            else:
                                # Get scan path, scan ID for each matching scan.
                                # Break if the scan matches so we don't find it again comparing
                                # vs a different requested type
                                artefacts_by_input[i].append(cscan['full_path'])
                                artefact_ids_by_input[i].append(scanid)
                                break

                # If requested, check for multiple matching scans in the list and only keep
                # the first. Sort lowercase by alpha, on scan ID.
                if len(artefacts_by_input[i]) > 0 and iv['keep_multis'] != 'all':
                    scan_info = zip(
                        artefacts_by_input[i],
                        artefact_ids_by_input[i],
                        )
                    sorted_info = sorted(scan_info, key=lambda x: str(x[1]).lower())
                    num_scans = sum(1 for _ in sorted_info)
                    if iv['keep_multis'] == 'first':
                        idx_multi = 1
                    elif iv['keep_multis'] == 'last':
                        idx_multi = num_scans
                    else:
                        try:
                            idx_multi = int(iv['keep_multis'])
                        except:
                            msg = f'For {i}, keep_multis must be first, last, or index 1,2,3,...'
                            LOGGER.error(msg)
                            raise AutoProcessorError(msg)

                    if idx_multi > num_scans:
                        msg = f'Requested {idx_multi}th scan for {i}, but only {num_scans} found'
                        LOGGER.info(msg)
                        artefacts_by_input[i] = []
                    else:
                        artefacts_by_input[i] = [sorted_info[idx_multi-1][0]]
                        LOGGER.debug(
                            f'Keeping only the {idx_multi}th scan found for '
                            f'{i}: {sorted_info[idx_multi-1][0]}'
                            )

            elif iv['artefact_type'] == 'assessor':
                for cassr in assrs:
                    proctype = cassr.get('PROCTYPE')
                    if proctype in iv['types']:
                        # Session type and proc type both match
                        artefacts_by_input[i].append(cassr['full_path'])

        return artefacts_by_input

    def _parse_filters(self, filters):
        match_list = []

        # Parse out filters, currently only filters of type match are supported
        for f in filters:
            _type = f['type']
            if _type == 'match':
                # Split the comma-separated list of inputs
                _inputs = f['inputs'].split(',')
                match_list.append(_inputs)
            else:
                LOGGER.error('invalid filter type:{}'.format(_type))

        self.match_filters = match_list

    def _generate_parameter_matrix_pd(self, artefacts_by_input):
        inputs = self.proc_inputs
        iteration_sources = self.iteration_sources

        # generate n dimensional input matrix based on iteration sources
        all_inputs = []
        input_dimension_map = []

        # check whether all inputs are present
        for i, iv in list(inputs.items()):
            if len(artefacts_by_input[i]) == 0 and iv['required'] is True:
                return []

        for i in iteration_sources:
            # find other inputs that map to this iteration source
            mapped_inputs = [i]
            cur_input_vector = artefacts_by_input[i][:]

            # build up the set of mapped input vectors one by one based on
            # the select mode of the mapped input
            combined_input_vector = [cur_input_vector]

            # 'trim' the input vectors to the number of entries of the
            # shortest vector. We don't actually truncate the datasets but
            # just use the number when transposing, below
            min_entry_count = min((len(e) for e in combined_input_vector))

            # transpose from list of input vectors to input entry lists,
            # one per combination of inputs
            merged_input_vector = [
                [None for col in range(len(combined_input_vector))]
                for row in range(min_entry_count)
            ]
            for row in range(min_entry_count):
                for col in range(len(combined_input_vector)):
                    merged_input_vector[row][col] = combined_input_vector[col][row]

            all_inputs.append(mapped_inputs)
            input_dimension_map.append(merged_input_vector)

        # perform a cartesian product of the dimension map entries to get the
        # final input combinations
        matrix = [
            list(itertools.chain.from_iterable(x))
            for x in itertools.product(*input_dimension_map)
        ]

        matrix_headers = list(itertools.chain.from_iterable(all_inputs))

        # rebuild the matrix to order the inputs consistently
        final_matrix = []
        for r in matrix:
            row = dict()
            for i in range(len(matrix_headers)):
                row[matrix_headers[i]] = r[i]
            final_matrix.append(row)

        return final_matrix

    def _filter_matrix_pd(self, parameter_matrix, artefact_inputs):
        match_filters = self.match_filters

        filtered_matrix = []
        for cur_param in parameter_matrix:
            # Reset matching for this param set
            all_match = True

            for cur_filter in match_filters:
                # Get the first value to compare with others
                first_val = get_input_value_pd(
                    cur_filter[0], cur_param, artefact_inputs)

                # Compare other values with first value
                for cur_input in cur_filter[1:]:
                    cur_val = get_input_value_pd(
                        cur_input, cur_param, artefact_inputs)

                    if cur_val is None:
                        logger.warn(f'cannot match, empty inputs:{cur_input}')
                        all_match = False
                        break

                    if cur_val != first_val:
                        # A single non-match breaks the whole thing
                        all_match = False
                        break

            if all_match:
                # Keep this param set if everything matches
                filtered_matrix.append(cur_param)

        return filtered_matrix

    def _populate_proc_inputs(self):
        for ik, iv in self.proc_inputs.items():
            for i, r in enumerate(iv['resources']):
                # Complete varname
                if 'varname' not in r:
                    r['varname'] = '{}-{}-{}'.format(ik, r['resource'], i)

                # Complete ftype
                if 'ftype' not in r:
                    r['ftype'] = 'FILE'

    def _parse_variables(self):
        for ik, iv in self.proc_inputs.items():
            for r in iv['resources']:
                v = r.get('varname')
                self.variables_to_inputs[v] = {
                    'input': ik,
                    'resource': r['resource']}


def get_input_value_pd(input_name, parameter, artefact_inputs):
    if '/' not in input_name:
        # Matching on parent so keep this value
        val = parameter[input_name]
    else:
        # Match is on a parent so parse out the parent/child
        (parent_name, child_name) = input_name.split('/')
        parent_val = parameter[parent_name]
        parent_inputs = artefact_inputs[parent_val]

        if parent_inputs is None:
            # Check that inputs field is not empty
            LOGGER.info(f'inputs field is empty:{parent_val}')
            val = None
        else:
            # Get the inputs field from the child
            val = parent_inputs[child_name]

    return val


def parse_artefacts(csess, pets=[]):
    def parse(carts, arts):
        for cart in carts:
            resources = {}
            for cres in cart.resources():
                resources[cres.label()] = cres
            full_path = cart.full_path()
            arts[full_path] = ParserArtefact(full_path, resources, cart)

    artefacts = {}
    parse(csess.scans(), artefacts)
    parse(csess.assessors(), artefacts)

    # BDB 6/5/21
    # Add the pet scans (we are not supporting pet assessors at this time)
    for p in pets:
        parse(p.scans(), artefacts)

    return artefacts


def get_scan_status(project_data, scan_path):
    # scans/NIFTI/PROJECT/SUBJECT/SESSION/SCAN
    path_parts = scan_path.split('/')
    sess_label = path_parts[4]
    scan_label = path_parts[5]
    scan_id = scan_label.split('-x-')[0]

    scans = project_data.get('scans')
    for s in scans:
        if s['SESSION'] == sess_label and s['SCANID'] == scan_id:
            return s['QUALITY']

    raise XnatUtilsError('Invalid scan path:' + scan_path)


def get_assr_status(project_data, assr_path):
    # assessors/PROJECT/ASSESSOR
    path_parts = assr_path.split('/')
    assr_label = path_parts[2]

    assrs = project_data.get('assessors')
    for a in assrs:
        if a['ASSR'] == assr_label:
            return a['PROCSTATUS'], a['QCSTATUS']

    raise XnatUtilsError('Invalid assessor path:' + assr_path)


def verify_artefact_status(proc_inputs, assr_inputs, project_data):

    # Check artefact status
    LOGGER.debug('checking status of each artefact')
    for artk, artv in list(assr_inputs.items()):
        inp = proc_inputs[artk]
        art_type = inp['artefact_type']

        if art_type == 'scan' and not inp['needs_qc']:
            # Not checking qc status
            LOGGER.debug('not checking status:' + artk)
            continue

        LOGGER.debug('checking status:' + artk)

        if art_type == 'scan':
            # Check status of each input scan
            for vinput in artv:
                qstatus = get_scan_status(project_data, vinput)
                if qstatus.lower() == 'unusable':
                    raise NeedInputsException(artk + ': Scan Unusable')
                if qstatus.lower() != 'usable' and inp['require_usable']:
                    raise NeedInputsException(artk + ': Scan not marked usable')
        else:
            # Check status of each input assr
            for vinput in artv:
                pstatus, qstatus = get_assr_status(project_data, vinput)
                if pstatus in OPEN_STATUS_LIST + [NEED_INPUTS]:
                    raise NeedInputsException(artk + ': Not Ready')

                if qstatus in [JOB_PENDING, REPROC, RERUN]:
                    raise NeedInputsException(artk + ': Not Ready')

                if not inp['needs_qc']:
                    # Not checking qc status
                    continue

                if qstatus in [FAILED_NEEDS_REPROC, NEEDS_QA]:
                    raise NeedInputsException(artk + ': Needs QC')

                for badstatus in BAD_QA_STATUS:
                    if badstatus.lower() in qstatus.split(' ')[0].lower():
                        raise NeedInputsException(artk + ': Bad QC')


def _get_resource_dir(root_dir, artefact_path, resource):
    if artefact_path.startswith('scans/NIFTI'):
        return f'{root_dir}/{artefact_path}'
    elif artefact_path.startswith('assessors'):
        return f'{root_dir}/{artefact_path}/{resource}'
    else:
        raise f'unsupported resource:{artefact_path}:{resource}'


def _get_file_list(resource_dir, resource):
    file_list = [x for x in os.listdir(resource_dir) if not x.startswith('.')]
    if resource == 'NIFTI':
        file_list = [x for x in file_list if x.endswith('.nii.gz')]
    elif resource == 'JSON':
        file_list = [x for x in file_list if x.endswith('.json')]

    return file_list
