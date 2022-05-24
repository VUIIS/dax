import logging
import re
import os
import json
import requests
import itertools
import copy
from uuid import uuid4
from datetime import date

from . import XnatUtils, task
from .XnatUtils import XnatUtilsError
from . import yaml_doc
from .errors import AutoProcessorError
from .task import NeedInputsException
from .task import (
    NEED_INPUTS,
    OPEN_STATUS_LIST,
    BAD_QA_STATUS,
    JOB_PENDING,
    REPROC,
    RERUN,
    FAILED_NEEDS_REPROC,
    NEEDS_QA,
)
from . import utilities

# Processor handles the pipeline specifications and builds each pipeline on
# given inputs.

# TODO: figure out if we can reduce the complexity of "parse_inputs",
# and find better names for everything

# This regex is used to match YAML file names, e.g. my_proc_v1.0.0.yaml
# The prefix can be any word characters plus the dash character.
# The suffix must be an underscore followed by the letter v and then the
# semantic versioning version X.Y.Z and finally it must end with .yaml
# 2/1/22 now using the official semver matching expression
YAML_PATTERN = '^[\w-]*_v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?.yaml$'

# Logger for logs
LOGGER = logging.getLogger('dax')

# The default singularity command includes the cleanenv/contain options and
# binds an INPUTS and OUTPUTS. The command is included in the job_template
# which will already have the variables set for $INDIR and $OUTDIR
SINGULARITY_BASEOPTS = (
    '--contain --cleanenv '
    '--home $JOBDIR '
    '--bind $INDIR:/INPUTS '
    '--bind $OUTDIR:/OUTPUTS '
    '--bind $JOBDIR:/tmp '
    '--bind $JOBDIR:/dev/shm '
    )

class ParserArtefact:
    def __init__(self, path, resources, entity):
        self.name = path.split('/')[-1]
        self.path = path
        self.resources = resources
        self.entity = entity

    def __repr__(self):
        return '{}(path = {}, resources = {}, entity = {})'.format(
            self.__class__.__name__, self.path, self.resources, self.entity
        )


def validate_yaml_filename(filename):
    # Try to match against our pattern
    if not re.match(YAML_PATTERN, os.path.basename(filename)):
        raise AutoProcessorError('invalid filename:{}'.format(filename))

    return True


class Processor_v3(object):
    """Processor class for v3 YAML files"""

    def __init__(
        self,
        xnat,
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

        # Cache connection back to xnat
        self.xnat = xnat

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

    def build_cmds(self, assr, assr_label, sessions, jobdir, resdir):
        """Method to generate the spider command for cluster job.
        :param jobdir: jobdir where the job's output will be generated
        :return: command to execute the spider in the job script
        """

        # Query xnat for the artefact inputs
        assr_inputs = XnatUtils.get_assessor_inputs(assr, sessions)

        # Make every input a list, so we can iterate later
        for k in assr_inputs:
            if not isinstance(assr_inputs[k], list):
                assr_inputs[k] = [assr_inputs[k]]

        # Find values for the xnat inputs
        var2val, input_list = self.find_inputs(assr, sessions, assr_inputs)

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
                _refval = [a.rsplit('/', 1)[1] for a in assr_inputs[_ref]]
                _val = ','.join(
                    [assr.parent().scan(r).attrs.get(_attr) for r in _refval]
                )
            elif _obj == 'assessor':
                if 'ref' in attr_in:
                    _ref = attr_in['ref']
                    _refval = [a.rsplit('/', 1)[1] for a in assr_inputs[_ref]]
                    _val = ','.join(
                        [assr.parent().assessor(r).attrs.get(_attr) for r in _refval]
                    )
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
                assr.label(),
            )

            for edit_in in self.proc_edits:
                _fpref = edit_in['fpref']
                _var = edit_in['varname']

                # Filter files that match prefix
                cur_list = [f for f in file_list if f.startswith(_fpref)]

                if cur_list:
                    # Sort and grab the last file
                    _val = sorted(cur_list)[-1]

                    # Build full uri
                    _uri = '{}/data{}/out/resources/{}/files/{}'.format(
                        assr._intf.host, assr_path, task.EDITS_RESOURCE, _val
                    )

                    # Append to inputs to be downloaded
                    input_list.append(
                        {'fdest': _fpref, 'ftype': 'FILE', 'fpath': _uri, 'ddest': ''}
                    )

                    # Set the value for command text
                    var2val[_var] = '/INPUTS/' + _fpref

                else:
                    # None found
                    var2val[_var] = ''
        else:
            for edit_in in self.proc_edits:
                var2val[edit_in['varname']] = ''

        # Build the command text
        dstdir = os.path.join(resdir, assr_label)
        assr_dir = os.path.join(jobdir, assr_label)
        _host = assr._intf.host
        _user = assr._intf.user
        cmd = self.build_text(
            var2val, input_list, assr_dir, dstdir, _host, _user)

        return [cmd]

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

    def create_assessor(self, xnatsession, inputs, relabel=False):
        guidchars = 8  # how many characters in the guid?
        attempts = 0
        while attempts < 100:
            attempts += 1
            guid = str(uuid4())
            assessor = xnatsession.assessor(guid)
            if assessor.exists():
                continue

            kwargs = {}
            proctype = '{}/proctype'.format(self.xsitype.lower())
            kwargs[proctype] = self.proctype
            procversion = '{}/procversion'.format(self.xsitype.lower())
            kwargs[procversion] = self.procversion
            input_key = '{}/inputs'.format(self.xsitype.lower())
            kwargs[input_key] = self._serialize_inputs(inputs)
            procstatus = '{}/procstatus'.format(self.xsitype.lower())
            kwargs[procstatus] = NEED_INPUTS
            if relabel:
                _proj = assessor.parent().parent().parent().label()
                _subj = assessor.parent().parent().label()
                _sess = assessor.parent().label()
                _type = self.proctype
                label = '-x-'.join([_proj, _subj, _sess, _type, guid[:guidchars]])
            else:
                label = guid

            # Set creation date to today
            date_key = '{}/date'.format(self.xsitype.lower())
            date_val = str(date.today())
            kwargs[date_key] = date_val

            # Create the assessor
            assessor.create(
                assessors=self.xsitype.lower(), ID=guid, label=label, **kwargs
            )
            return assessor

    def _serialize_inputs(self, inputs):
        return json.dumps(inputs)

    def _deserialize_inputs(self, assessor):
        return json.loads(XnatUtils.parse_assessor_inputs(assessor.attrs.get('inputs')))

    def get_assessor_input_types(self):
        """
        Enumerate the assessor input types for this. The default implementation
        returns an empty collection; override this method if you are inheriting
        from a non-yaml processor.
        :return: a list of input assessor types
        """
        assessor_inputs = [
            i
            for i in list(self.proc_inputs.values())
            if i['artefact_type'] == 'assessor'
        ]
        assessors = [i['types'] for i in assessor_inputs]

        return list(itertools.chain.from_iterable(assessors))

    def parse_session(self, csess, sessions, pets=None):
        """
        Parse a session to determine what assessors should exist for
        this processor and identify any that already exist.
        This call populates assessor_parameter_map.

        :param csess: the session in question
        :param sessions: the full list of sessions, including csess, for the
        subject

        :return: None
        """

        # BDB 6/5/21
        # only include pets if this is the first mr session
        if sessions.index(csess) == (len(sessions) - 1):
            LOGGER.debug('session is first, including pets')
        else:
            LOGGER.debug('session is not first, not including pets')
            pets = []

        artefacts = parse_artefacts(csess, pets)

        # BDB 6/5/21
        # The artefacts are a dictionary where the index key is the
        # relative path of scan or assessor:
        # /projects/PROJ/subjects/SUBJ/experiments/SESS/assessors/ASSR
        # for every single assessor or scan. the value in the dictionary
        # is a ParserArtefact object the includes a list of the scan/assr's
        # resources and a CachedAssessor object. This can be used later
        # to quickly access this information

        # BDB 6/5/21
        # next we will create a dictionary of just the artefacts for each of
        # the inputs map the artefacts to the inputs, this is where
        # we filter down the whole session to the types of scan/assessors we
        # want. Then we decide what to do with the different combinations of
        # those scans/assessors if we find multiple per input.
        # maybe we should change the names?
        # artefacts --> all_artefacts or all_session_arefacts
        # artefacts_by_inputs --> input_artefacts_by_input or something

        artefacts_by_input = self._map_artefacts_to_inputs(csess, pets)

        # BDB 6/5/21
        # at this point the pet scan should be just like any other input or
        # artefact, it's just a path

        # BDB 6/5/21
        # artefacts_by_input is a dictionary where the key is the
        # input name and the value is a list of artefact paths that match
        # the input.
        # These artefact paths are keys into the artefacts dictionary.

        # BPR 4 Mar 2022
        # artefacts_by_input has been filtered already in _map_artefacts_to_inputs
        # by the skip_unusable and keep_multis options, if so requested.
        #
        # Really insidious error case here: if an element of artefacts_by_input
        # is not a list, the build will "leak" past what has been requested and
        # start building every project. This is now checked in _map_artefacts_to_inputs

        parameter_matrix = self._generate_parameter_matrix(
            artefacts, artefacts_by_input
        )

        # BDB 6/5/21
        # parameter_matrix is the combinations of inputs from the lists in
        # artefacts_by_inputs. I think these are the cartesian product
        # of lists in artefacts_by_input.

        # BDB 6/5/21
        # Next we filter down the combinations by applying
        # any filters included in the yaml. currently
        # the only filter supported is a match filter
        # which help us only include combinations where one of the inputs
        # is the same, e.g. the same T1 input
        # This functions uses the artefacts dictionary to get the inputs field
        # from each artefact for comparison.
        parameter_matrix = self._filter_matrix(parameter_matrix, artefacts)

        # BDB 6/5/21
        # And now we use the parameter matrix as a list of what set of inputs
        # we need assessors for
        # by mapping to what assessors already exist by comparing
        # the inputs field on existing assessors with our list of inputs
        assessor_parameter_map = self._compare_to_existing(csess, parameter_matrix)

        # BDB 6/5/21
        # assessor_parameter_map is list of tuples
        # where each tuple is(inputs, assessor(s))(if assesors exists already),
        # if assessors don't exist assessors will empty list
        # so what we are returning is a list of tuples
        # (set of inputs, existing assessors for these inputs)
        return list(assessor_parameter_map)

    def get_container_path(self, name):
        cpath = None

        # Find the matching container
        for c in self.containers:
            if c['name'] == name:
                cpath = c['path']
                break

        return cpath

    def find_inputs(self, assr, sessions, assr_inputs):
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

        # Check artefact status
        LOGGER.debug('checking status of each artefact')
        for artk, artv in list(assr_inputs.items()):
            LOGGER.debug('checking status:' + artk)
            inp = self.proc_inputs[artk]
            art_type = inp['artefact_type']

            if art_type == 'scan' and not inp['needs_qc']:
                # Not checking qc status
                continue

            if art_type == 'scan':
                # Check status of each input scan
                for vinput in artv:
                    qstatus = XnatUtils.get_scan_status(sessions, vinput)
                    if qstatus.lower() == 'unusable':
                        raise NeedInputsException(artk + ': Not Usable')
            else:
                # Check status of each input assr
                for vinput in artv:
                    pstatus, qstatus = XnatUtils.get_assr_status(sessions, vinput)
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

        # Map from parameters to input resources
        LOGGER.debug('mapping params to artefact resources')
        for k, v in list(self.variables_to_inputs.items()):
            LOGGER.debug('mapping:' + k)
            inp = self.proc_inputs[v['input']]
            resource = v['resource']

            # Find the resource
            cur_res = None
            for inp_res in inp['resources']:
                if inp_res['varname'] == k:
                    cur_res = inp_res
                    break

            # TODO: optimize this to get resource list only once
            for vnum, vinput in enumerate(assr_inputs[v['input']]):
                fname = None
                robj = get_resource(assr._intf, vinput, resource)

                # Get list of all files in the resource, relative paths
                file_list = [x._urn for x in robj.files().get('path')]
                if len(file_list) == 0:
                    LOGGER.debug('empty or missing resource')
                    raise NeedInputsException('No Resource')

                if 'fmatch' in cur_res:
                    fmatch = cur_res['fmatch']
                elif cur_res['ftype'] == 'FILE':
                    # Default to all
                    fmatch = '*'
                else:
                    fmatch = None

                if 'filepath' in cur_res:
                    fpath = cur_res['filepath']
                    res_path = resource + '/files/' + fpath

                    # Get base file name to be downloaded
                    fname = os.path.basename(fpath)
                elif fmatch:
                    # Filter list based on regex matching
                    regex = utilities.extract_exp(fmatch, full_regex=False)
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
                            raise NeedInputsException(artk + ': multiple files')

                    # Create the full path to the file on the resource
                    res_path = '{}/files/{}'.format(resource, file_list[0])

                    # Get just the filename for later
                    fname = os.path.basename(file_list[0])
                else:
                    # We want the whole resource
                    res_path = resource + '/files'

                    # Get just the resource name for later
                    fname = resource

                variable_set[k] = get_uri(assr._intf.host, vinput, res_path)

                if 'fdest' not in cur_res:
                    # Use the original file/resource name
                    fdest = fname
                elif len(assr_inputs[v['input']]) > 1:
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

            # Consider an MR scan for an input if it's marked Unusable?
            skip_unusable = s.get('skip_unusable', False)

            # Include the 'first', or 'all', matching scans as possible inputs
            keep_multis = s.get('keep_multis', 'all')

            self.proc_inputs[name] = {
                'types': types,
                'artefact_type': 'scan',
                'needs_qc': needs_qc,
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

            resources = p.get('resources')

            self.proc_inputs[name] = {
                'types': types,
                'artefact_type': 'scan',
                'needs_qc': p.get('needs_qc', False),
                'resources': p.get('resources', []),
                'required': True,
                'tracer': tracer,
            }

        if 'filters' in self.xnat_inputs:
            self._parse_filters(self.xnat_inputs.get('filters'))

        self._populate_proc_inputs()
        self._parse_variables()

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

    def _map_artefacts_to_inputs(self, csess, pets):
        inputs = self.proc_inputs

        # BDB 6/5/21
        # here is where we should do something different for
        # the pet scans I think? are we treating assessors scans differently
        # here or not?
        artefacts_by_input = {k: [] for k in inputs}
        artefact_ids_by_input = {k: [] for k in inputs}

        for i, iv in list(inputs.items()):
            # BDB 6/5/21
            # here we do something to filter the list of sessions based
            # on the select types in the inputs???
            # I'm not sure what's going on here, are we only selecting
            # one of the sessions at this point? when and where
            # do we use multiple sessions?

            if 'tracer' in iv:
                # The input is a petscan so look in the pets
                for p in pets:
                    # Match the tracer name
                    tracer_name = p.get('xnat:tracer/name')
                    tracer_match = False
                    for expression in iv['tracer']:
                        regex = utilities.extract_exp(expression)
                        if regex.match(tracer_name):
                            # found a match so exit the loop
                            tracer_match = True
                            break

                    if not tracer_match:
                        # None of the expressions matched
                        LOGGER.debug(
                            'tracer not matched:{}:{}'.format(tracer_name, iv['tracer'])
                        )
                        continue

                    # Now try to match the scan type
                    for pscan in p.scans():
                        for expression in iv['types']:
                            regex = utilities.extract_exp(expression)
                            if regex.match(pscan.type()):
                                # Found a match, now check quality
                                if pscan.info().get('quality') == 'unusable':
                                    LOGGER.info('excluding unusable scan')
                                else:
                                    artefacts_by_input[i].append(pscan.full_path())

            else:

                # Find matching scans in the session, if asked for a scan
                if iv['artefact_type'] == 'scan':
                    for cscan in csess.scans():
                        for expression in iv['types']:
                            regex = utilities.extract_exp(expression)
                            if regex.match(cscan.type()):
                                if iv['skip_unusable'] and cscan.info().get('quality') == 'unusable':
                                    LOGGER.info(f'Excluding unusable scan {cscan.label()}')
                                else:
                                    # Get scan path, scan ID for each matching scan.
                                    # Break if the scan matches so we don't find it again comparing
                                    # vs a different requested type
                                    artefacts_by_input[i].append(cscan.full_path())
                                    artefact_ids_by_input[i].append(cscan.info().get('ID'))
                                    break

                    # If requested, check for multiple matching scans in the list and only keep
                    # the first. Sort lowercase by alpha, on scan ID.
                    if iv['keep_multis'] != 'all':
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
                                LOGGER.error(msg)
                                raise AutoProcessorError(msg)
                        artefacts_by_input[i] = [sorted_info[idx_multi-1][0]]
                        LOGGER.info(
                            f'Keeping only the {idx_multi}th scan found for '
                            f'{i}: {sorted_info[idx_multi-1][0]}'
                            )

                # Find matching assessors in the session, if asked for an assessor
                elif iv['artefact_type'] == 'assessor':
                    for cassr in csess.assessors():
                        try:
                            if cassr.type() in iv['types']:
                                artefacts_by_input[i].append(cassr.full_path())
                        except:
                            # Perhaps type/proctype is missing
                            LOGGER.warning(f'Unable to check match of {cassr.label()} - ignoring')

        # Validate - each value of artefacts_by_input must be a list
        for k, v in artefacts_by_input.items():
            if not isinstance(v, list):
                msg = f'Non-list found in artefacts_by_input field {k}: {v}'
                LOGGER.error(msg)
                raise AutoProcessorError(msg)

        return artefacts_by_input

    def _generate_parameter_matrix(self, artefacts, artefacts_by_input):
        inputs = self.proc_inputs
        iteration_sources = self.iteration_sources

        # generate n dimensional input matrix based on iteration sources
        all_inputs = []
        input_dimension_map = []

        # check whether all inputs are present
        for i, iv in list(inputs.items()):
            if len(artefacts_by_input[i]) == 0 and iv['required'] is True:
                return []

        # add in None for optional inputs so that the matrix can be generated
        # without artefacts present for those inputs
        sanitised_inputs = {}
        for i, iv in list(inputs.items()):
            if len(artefacts_by_input[i]) == 0:
                sanitised_inputs[i] = [list().append(None)]
            else:
                sanitised_inputs[i] = artefacts_by_input[i]

        for i in iteration_sources:
            # find other inputs that map to this iteration source
            mapped_inputs = [i]
            cur_input_vector = sanitised_inputs[i][:]

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

    def _compare_to_existing(self, csess, parameter_matrix):
        assessors = [[] for _ in range(len(parameter_matrix))]

        # Get of list assessors that have already been 
        # created on xnat for this processor/proctype
        existing_assessors = []
        for casr in csess.assessors():
            # Check that proc type matches this processor
            try:
                proc_type_matches = (casr.type() == self.proctype)
                if proc_type_matches:
                    existing_assessors.append(casr)
            except:
                LOGGER.warning(f'Unable to check match of {casr.label()} - ignoring')
                continue

        # Check for any missing inputs fields in the existing assessors
        for casr in existing_assessors:
            # Check for empty inputs. If ANY of the assessors on this session
            # have an empty inputs, then we cannot determine which input sets
            # need to be built. We refuse to do anything by returning
            # an empty list.
            if casr.get_inputs() is None:
                LOGGER.warn('assessor with empty inputs field, cannot build processor for session' + casr.label())
                return list()

        # Compare existing to the "to build" assessors in parameter_matrix
        for casr in existing_assessors:
            for pi, p in enumerate(parameter_matrix):
                if casr.get_inputs() == p:
                    # BDB  6/5/21 do we ever have more than one assessor
                    #             with the same set of inputs?
                    assessors[pi].append(casr)

        return list(zip(copy.deepcopy(parameter_matrix), assessors))

    def _filter_matrix(self, parameter_matrix, artefacts):
        match_filters = self.match_filters

        filtered_matrix = []
        for cur_param in parameter_matrix:
            # Reset matching for this param set
            all_match = True

            for cur_filter in match_filters:
                # Get the first value to compare with others
                first_val = get_input_value(cur_filter[0], cur_param, artefacts)

                # Compare other values with first value
                for cur_input in cur_filter[1:]:
                    cur_val = get_input_value(cur_input, cur_param, artefacts)

                    if cur_val is None:
                        LOGGER.warn('cannot match, empty inputs:{}'.format(cur_input))
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


def get_input_value(input_name, parameter, artefacts):
    if '/' not in input_name:
        # Matching on parent so keep this value
        _val = parameter[input_name]
    else:
        # Match is on a parent so parse out the parent/child
        (_parent_name, _child_name) = input_name.split('/')
        _parent_val = parameter[_parent_name]
        _parent_art = artefacts[_parent_val]

        _parent_art_inputs = _parent_art.entity.get_inputs()
        if _parent_art_inputs is None:
            # Check that inputs field is not empty
            LOGGER.warn('inputs field is empty:' + _parent_val)
            _val = None
        else:
            # Get the inputs field from the child
            _parent_inputs = _parent_art_inputs
            _val = _parent_inputs[_child_name]

    return _val


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


# Returns the full URI for the resource_path as a child of input path which
# can be either a scan or an assessor
def get_uri(host, input_path, resource_path):
    if '/scans/' in input_path:
        uri_path = '{0}/data{1}/resources/{2}'.format(host, input_path, resource_path)
    else:
        uri_path = '{0}/data{1}/out/resources/{2}'.format(
            host, input_path, resource_path
        )

    return uri_path


# Returns an xnat object for the resource that is a child of input_path
# which can be either a scan or an assessor
def get_resource(xnat, input_path, resource):
    if '/scans/' in input_path:
        resource_path = '{0}/resources/{1}'
    else:
        resource_path = '{0}/out/resources/{1}'

    rpath = resource_path.format(input_path, resource)
    robj = xnat.select(rpath)

    return robj


# Returns the processing type (proctype) as parsed from the already
# validated yaml file name
def parse_proctype(yaml_file):
    # At this point we assume the yaml file name is valid
    tmp = os.path.basename(yaml_file)
    tmp = tmp.rsplit('.')[-4]
    return tmp


# Returns the processing version (procversion) as parsed from the already
# validated yaml file name
def parse_procversion(yaml_file):
    # At this point we assume the yaml file name is valid
    tmp = os.path.basename(yaml_file)
    tmp = os.path.splitext(yaml_file)[0]
    tmp = tmp.rsplit('_v')[1]
    return tmp


class SgpProcessor(Processor_v3):
    """Processor class for SGP v3 YAML files"""

    def __init__(
        self,
        xnat,
        yaml_file,
        user_inputs=None,
        singularity_imagedir=None,
        job_template='~/job_template.txt',
    ):
        super(SgpProcessor, self).__init__(
            xnat,
            yaml_file,
            user_inputs=user_inputs,
            singularity_imagedir=singularity_imagedir,
            job_template=job_template)

        self.xsitype = "proc:subjgenprocdata"

    def get_assessor(self, xnat, subject, inputs, project_data):
        proctype = self.get_proctype()
        dfa = project_data['sgp']
        dfa = dfa[(dfa.SUBJECT == subject) & (dfa.PROCTYPE == proctype)]
        dfa = dfa[(dfa.INPUTS == inputs)]

        if len(dfa) > 0:
            # Get the info for the assessor
            info = dfa.to_dict('records')[0]

            LOGGER.debug('matches existing:{}'.format(info['ASSR']))

            # Get the assessor object
            assr = xnat.select_experiment(
                info['PROJECT'],
                info['SUBJECT'],
                info['ASSR'])
        else:
            LOGGER.debug('no existing assessors found, creating a new one')
            (assr, info) = self.create_assessor(
                xnat,
                project_data.get('name'),
                subject,
                inputs)

            LOGGER.debug('created:{}'.format(info['ASSR']))

        return (assr, info)

    def _read_yaml(self, yaml_file):
        """
        Method to read the processor

        :param yaml_file: path to yaml file defining the processor
        """
        LOGGER.debug('reading processor from yaml:{}'.format(yaml_file))
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
        # TODO: self._edit_inputs()
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

    def build_cmds(self, assr, info, project_data, jobdir, resdir):
        assr_label = info['ASSR']

        # Make every input a list, so we can iterate later
        inputs = info['INPUTS']
        for k in inputs.keys():
            if not isinstance(inputs[k], list):
                inputs[k] = [inputs[k]]

        # Find values for the xnat inputs
        var2val, input_list = self.find_inputs(assr, inputs, project_data)

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
                _val = assr.parent().attrs.get(_attr)
            elif _obj == 'session':
                _val = assr.parent().attrs.get(_attr)
                _ref = attr_in['ref']
                _refval = [a.rsplit('/', 1)[1] for a in inputs[_ref]]
                _val = ','.join([assr.parent().experiment(r).attrs.get(_attr) for r in _refval])
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
                LOGGER.error('invalid YAML')
                err = 'YAML File:contains invalid attribute:{}'
                raise AutoProcessorError(err.format(_attr))

            if _val == '':
                raise NeedInputsException('Missing ' + _attr)
            else:
                var2val[_var] = _val

        # Build the command text
        dstdir = os.path.join(resdir, assr_label)
        assr_dir = os.path.join(jobdir, assr_label)
        _host = assr._intf.host
        _user = assr._intf.user
        cmd = self.build_text(
            var2val, input_list, assr_dir, dstdir, _host, _user)

        return [cmd]

    def create_assessor(self, xnat, project, subject, inputs):
        # returns assr pyxnat object
        # info dict of assessor info

        xnatsubject = xnat.select_subject(project, subject)

        serialized_inputs = json.dumps(inputs)
        guidchars = 8  # how many characters in the guid?
        today = str(date.today())

        # Get a unique ID
        count = 0
        max_count = 100
        while count < max_count:
            count += 1
            guid = str(uuid4())
            assr = xnatsubject.experiment(guid)

            if not assr.exists():
                break

        if count == max_count:
            LOGGER.error('failed to find unique ID, cannot create assessor!')
            raise AutoProcessorError()

        # Build the assessor attributes as key/value pairs
        assr_label = '-x-'.join([
            project,
            subject,
            self.proctype,
            guid[:guidchars]])

        kwargs = {
            'label': assr_label,
            'ID': guid,
            'proc:subjgenprocdata/proctype': self.proctype,
            'proc:subjgenprocdata/procversion': self.procversion,
            'proc:subjgenprocdata/procstatus': NEED_INPUTS,
            'proc:subjgenprocdata/date': today,
            'proc:subjgenprocdata/inputs': serialized_inputs}

        # Create the assessor
        LOGGER.info('creating subject asssessor:{}'.format(assr_label))
        assr.create(experiments='proc:subjgenprocdata', **kwargs)

        # We keep the inputs as a dictionary in the returned info
        # this is also how load_sgp_data behaves
        info = {
            'ASSR': assr_label,
            'QCSTATUS': JOB_PENDING,
            'XSITYPE': 'proc:subjgenprocdata',
            'PROCTYPE': self.proctype,
            'PROCVERSION': self.procversion,
            'PROCSTATUS': NEED_INPUTS,
            'INPUTS': inputs}

        return (assr, info)

    def parse_subject(self, subject, project_data):
        LOGGER.debug('parsing subject:{}'.format(subject))
        """
        Parse a subject to determine what assessors *should* exist for
        this processor
        """

        artefacts_by_input = self._map_inputs(
            subject, project_data)
        # print('artefacts_by_input=', artefacts_by_input)

        parameter_matrix = self._generate_parameter_matrix(artefacts_by_input)
        # print('parameter_matrix=', parameter_matrix)

        # TODO: filter down the combinations by applying any filters

        return parameter_matrix

    def find_inputs(self, assr, inputs, project_data):
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

        # This will raise a NeedInputs exception if any inputs aren't ready
        verify_artefact_status(self.proc_inputs, inputs, project_data)

        # print(self.variables_to_inputs.items())

        # Map from parameters to input resources
        LOGGER.debug('mapping params to artefact resources')
        for k, v in list(self.variables_to_inputs.items()):
            LOGGER.debug('mapping:' + k, v)
            inp = self.proc_inputs[v['input']]
            resource = v['resource']

            # print('vinput=', v['input'])
            # print('resource=', resource)
            # print(inp['resources'])

            # Find the resource
            cur_res = None
            for inp_res in inp['resources']:
                if inp_res['varname'] == k:
                    cur_res = inp_res
                    break

            # TODO: optimize this to get resource list only once
            for vnum, vinput in enumerate(inputs[v['input']]):
                # print(vnum, vinput)
                fname = None
                robj = get_resource(assr._intf, vinput, resource)

                # Get list of all files in the resource, relative paths
                file_list = [x._urn for x in robj.files().get('path')]
                if len(file_list) == 0:
                    LOGGER.debug('empty or missing resource')
                    raise NeedInputsException('No Resource')

                if 'fmatch' in cur_res:
                    fmatch = cur_res['fmatch']
                elif cur_res['ftype'] == 'FILE':
                    # Default to all
                    fmatch = '*'
                else:
                    fmatch = None

                if 'filepath' in cur_res:
                    fpath = cur_res['filepath']
                    res_path = resource + '/files/' + fpath

                    # Get base file name to be downloaded
                    fname = os.path.basename(fpath)
                elif fmatch:
                    # Filter list based on regex matching
                    regex = utilities.extract_exp(fmatch, full_regex=False)
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
                            raise NeedInputsException(artk + ': multiple files')

                    # Create the full path to the file on the resource
                    res_path = '{}/files/{}'.format(resource, file_list[0])

                    # Get just the filename for later
                    fname = os.path.basename(file_list[0])
                else:
                    # We want the whole resource
                    res_path = resource + '/files'

                    # Get just the resource name for later
                    fname = resource

                variable_set[k] = get_uri(assr._intf.host, vinput, res_path)

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

        # get sessions
        sessions = self.xnat_inputs.get('sessions', list())

        for sess in sessions:
            sesstypes = [_.strip() for _ in sess['types'].split(',')]

            # get scans
            scans = sess.get('scans', list())
            for s in scans:
                name = s.get('name')
                self.iteration_sources.add(name)

                types = [_.strip() for _ in s['types'].split(',')]

                resources = s.get('resources', [])

                if 'nifti' in s:
                    # Add a NIFTI resource using value as fdest
                    resources.append(
                        {'resource': 'NIFTI', 'fdest': s['nifti']})

                if 'edat' in s:
                    # Add an EDAT resource using value as fdest
                    resources.append(
                        {'resource': 'EDAT', 'fdest': s['edat']})

                needs_qc = s.get('needs_qc', False)

                # Consider an MR scan for an input if it's marked Unusable?
                skip_unusable = s.get('skip_unusable', False)

                # Include 'first' or 'all' matching scans as possible inputs
                keep_multis = s.get('keep_multis', 'all')

                self.proc_inputs[name] = {
                    'sesstypes': sesstypes,
                    'types': types,
                    'artefact_type': 'scan',
                    'needs_qc': needs_qc,
                    'resources': resources,
                    'required': True,
                    'skip_unusable': skip_unusable,
                    'keep_multis': keep_multis,
                }

            # get assessors
            asrs = sess.get('assessors', list())
            for a in asrs:
                name = a.get('name')
                self.iteration_sources.add(name)

                types = [_.strip() for _ in a['types'].split(',')]
                resources = a.get('resources', [])
                artefact_required = False
                for r in resources:
                    r['required'] = r.get('required', True)
                artefact_required = artefact_required or r['required']

                self.proc_inputs[name] = {
                    'sesstypes': sesstypes,
                    'types': types,
                    'artefact_type': 'assessor',
                    'needs_qc': a.get('needs_qc', False),
                    'resources': resources,
                    'required': artefact_required,
                }

        if 'filters' in self.xnat_inputs:
            self._parse_filters(self.xnat_inputs.get('filters'))

        self._populate_proc_inputs()
        self._parse_variables()

    def _map_inputs(self, subject, project_data):
        inputs = self.proc_inputs
        artefacts_by_input = {k: [] for k in inputs}

        # Get lists for scans/assrs for this subject
        scans = project_data.get('scans').to_dict('records')
        scans = [x for x in scans if x['SUBJECT'] == subject]
        assrs = project_data.get('assessors').to_dict('records')
        assrs = [x for x in assrs if x['SUBJECT'] == subject]

        # Find list of scans/assessors that match each specified input
        # for i, iv in list(inputs.items()):
        for i, iv in sorted(inputs.items()):
            if iv['artefact_type'] == 'scan':
                # Input is a scan, so we iterate subject scans
                # to look for matches
                for cscan in scans:
                    # First we try to match the session type of the scan
                    for typeexp in iv['sesstypes']:
                        regex = utilities.extract_exp(typeexp)
                        if regex.match(cscan.get('SESSTYPE')):
                            # Sess type matches, now match scan type
                            for expression in iv['types']:
                                regex = utilities.extract_exp(expression)
                                if regex.match(cscan.get('SCANTYPE')):
                                    scanid = cscan.get('ID')
                                    if iv['skip_unusable'] and cscan.get('QUALITY') == 'unusable':
                                        LOGGER.info(f'Excluding unusable scan {scanid}')
                                    else:
                                        # Get scan path, scan ID for each matching scan.
                                        # Break if the scan matches so we don't find it again comparing
                                        # vs a different requested type
                                        artefacts_by_input[i].append(cscan.get('full_path'))
                                        break

            elif iv['artefact_type'] == 'assessor':
                for typeexp in iv['sesstypes']:
                    for cassr in assrs:
                        regex = utilities.extract_exp(typeexp)
                        sesstype = cassr.get('SESSTYPE')
                        proctype = cassr.get('PROCTYPE')
                        # print(typeexp, sesstype, proctype, iv['types'])
                        if regex.match(sesstype) and proctype in iv['types']:
                            #print('MATCH!')
                            # Session type and proc type both match
                            artefacts_by_input[i].append(cassr.get('full_path'))
                        else:
                            #print('nope')
                            pass

        return artefacts_by_input

    def _generate_parameter_matrix(self, artefacts_by_input):
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


def get_scan_status(project_data, scan_path):
    path_parts = scan_path.split('/')
    sess_label = path_parts[6]
    scan_label = path_parts[8]

    scans = project_data.get('scans').to_dict('records')
    for s in scans:
        if s['SESSION'] == sess_label and s['SCANID'] == scan_label:
            return s['QUALITY']

    raise XnatUtilsError('Invalid scan path:' + scan_path)


def get_assr_status(project_data, assr_path):
    path_parts = assr_path.split('/')
    sess_label = path_parts[6]
    assr_label = path_parts[8]

    assrs = project_data.get('assessors').to_dict('records')
    for a in assrs:
        if a['SESSION'] == sess_label and a['ASSR'] == assr_label:
            return a['PROCSTATUS'], a['QCSTATUS']

    raise XnatUtilsError('Invalid assessor path:' + assr_path)


def verify_artefact_status(proc_inputs, assr_inputs, project_data):

    # Check artefact status
    LOGGER.debug('checking status of each artefact')
    for artk, artv in list(assr_inputs.items()):
        LOGGER.debug('checking status:' + artk)
        inp = proc_inputs[artk]
        art_type = inp['artefact_type']

        if art_type == 'scan' and not inp['needs_qc']:
            # Not checking qc status
            continue

        if art_type == 'scan':
            # Check status of each input scan
            for vinput in artv:
                qstatus = get_scan_status(project_data, vinput)
                if qstatus.lower() == 'unusable':
                    raise NeedInputsException(artk + ': Not Usable')
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
