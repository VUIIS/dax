from task import NeedInputsException, OPEN_STATUS_LIST, NEEDS_QA, NEED_INPUTS, JOB_PENDING, REPROC, RERUN


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
        super(SgpProcessor, self).__init__(xnat,
        yaml_file,
        user_inputs=user_inputs,
        singularity_imagedir=singularity_imagedir,
        job_template=job_template)

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
        #self._edit_inputs()
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

            if curc.get('primary', False):
                self.container_path = curc.get('path')

            # Add to our containers list
            self.containers.append(curc)

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
        # Make every input a list, so we can iterate later
        inputs = info['inputs']
        for k in inputs:
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
                _val = ','.join(
                    [assr.parent().experiment(r).attrs.get(_attr) for r in _refval]
                )
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

        # Build the command text
        dstdir = os.path.join(resdir, assr_label)
        assr_dir = os.path.join(jobdir, assr_label)
        _host = assr._intf.host
        _user = assr._intf.user
        cmd = self.build_text(
            var2val, input_list, assr_dir, dstdir, _host, _user)

        return [cmd]

    def create_assessor(self, xnatsubject, inputs):
    #def create_subjgenproc(xnat, project, subject, proctype, procversion, inputs, plugin_version='2'):

        # returns assr pyxnat object
        # info dict of assessor info

        serialized_inputs = json.dumps(inputs)
        guidchars = 8  # how many characters in the guid?
        today = str(date.today())

        # Get a unique ID
        count = 0
        max_count = 100
        while count < max_count:
            count += 1
            guid = str(uuid4())

            #assr = xnat.select('/projects/{}/subjects/{}/experiments/{}'.format(
            #    project, subject, guid))
            assr = xnatsubject.experiment(guid)

            if not assr.exists():
                break

        if count == max_count:
            LOGGER.error('failed to find unique ID, cannot create assessor!')
            raise AutoProcessorError()

        # Build the assessor attributes as key/value pairs
        assr_label = '-x-'.join([project, subject, proctype, guid[:guidchars]])

        kwargs = {
            'label': assr_label,
            'ID': guid,
            'proc:subjgenprocdata/proctype': proctype,
            'proc:subjgenprocdata/procversion': procversion,
            'proc:subjgenprocdata/procstatus': NEED_INPUTS,
            'proc:subjgenprocdata/date': today,
            'proc:subjgenprocdata/inputs': serialized_inputs}

        # Create the assessor
        LOGGER.info('creating subject asssessor:{}'.format(assr_label))
        assr.create(experiments='proc:subjgenprocdata', **kwargs)

        info = {
            'ASSR':assr_label,
            'QCSTATUS': JOB_PENDING,
            'XSITYPE': 'proc:subjgenprocdata',
            'PROCTYPE': proctype,
            'PROCVERSION': procversion,
            'PROCSTATUS': NEED_INPUTS,
            'INPUTS': serialized_inputs}

        return (assr, info)
        

    def _serialize_inputs(self, inputs):
        return json.dumps(inputs)

    def _deserialize_inputs(self, assessor):
        return json.loads(XnatUtils.parse_assessor_inputs(assessor.attrs.get('inputs')))

    def parse_subject(self, subject, project_data):
        """
        Parse a subject to determine what assessors should exist for
        this processor

        :return: None
        """

        #artefacts = parse_artefacts(csess, pets)

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

        artefacts_by_input = self._map_artefacts_to_inputs(project_data)

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

        # This will raise an exception if any inputs aren't ready
        verify_artefact_status(self.proc_inputs, inputs, project_data)

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

            types = [_.strip() for _ in a['proctypes'].split(',')]
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


def get_scan_status(project_data, scan_path):
    path_parts = scan_path.split('/')
    sess_label = path_parts[6]
    scan_label = path_parts[8]

    "scan_fmri": "/projects/DepMIND2/subjects/7500/experiments/7500a/scans/401"

    # TODO: better search, maybe we need an index with the project class

    for s in project_data.get('scans'):
        if s['SESSION'] == sess_label and s['SCANID'] == scan_label:
                return s['QUALITY']

    raise XnatUtilsError('Invalid scan path:' + scan_path)

def get_assr_status(project_data, assr_path):
    path_parts = assr_path.split('/')
    sess_label = path_parts[6]
    assr_label = path_parts[8]

    for a in project_data.get('assessors'):
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
