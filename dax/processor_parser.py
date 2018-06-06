
import copy
import itertools

from . import utilities
from . import XnatUtils


# TODO: BenM/assessor_of_assessor/
# support lack of input field on old assessors
# support lack of schema number & schema number (maybe on processor)
# support the ability to fix broken inputs
# support partial node ordering of processor dependencies

session_namespace = {
    'foreach': {'args': [{'optional': True, 'type': str}]},
    'one': {'args': []},
    'some': {'args': [{'optional': False, 'type': int}]},
    'all': {'args': []},
    'from': {'args': [{'optional': False, 'type': str}]}
}


no_scans_error = 'No scan of the required type/s ({}) found for input {}'
no_asrs_error = 'No assessors of the require type/s ({}) found for input {}'
scan_unusable_error = 'Scan {} is unusable for input {}'
asr_unusable_error = 'Assessor {} is unusable for input {}'

# base_path = '/projects/{0}/subjects/{1}/experiments/{2}/'
# assr_path = base_path + 'assessors/{3}/out/resources/{4}'
# scan_path = base_path + 'scans/{3}/resources/{4}'
# artefact_paths = {'assessor': assr_path, 'scan': scan_path}
resource_paths = {
    'assessor': '{0}/out/resources/{1}',
    'scan': '{0}/resources/{1}'
}


# parser pipeline
# . check whether artefacts of the appropriate type are present for a given
#   assessor
# . if they are, map them to inputs with the appropriate iteration
#   . if no foreach select statements are present, generate one set of command
#     parameters
#   . if one or more foreach select statements are present, generate the
#     appropriate cartesian product of command parameters
# . for each set of command parameters generated, create an assessor depending
#   on the state of the artefacts listed in the command parameters
#   . if one or more artefacts are of inappropriate quality

class ParserArtefact:
    def __init__(self, path, resources, entity):
        self.name = path.split('/')[-1]
        self.path = path
        self.resources = resources,
        self.entity = entity

    def __repr__(self):
        return '{}(path = {}, resources = {}, entity = {})'.format(
            self.__class__.__name__, self.path, self.resources, self.entity
        )



class ProcessorParser:

    __schema_dict_v1 = {
        'top': set(['schema', 'inputs', 'xnat', 'attrs']),
        'xnat': set(['scans', 'assessors']),
        'scans': set(['select', 'types', 'nargs', 'resources', 'needs_qc']),
        'assessors': set(['select', 'proctypes', 'nargs', 'resources',
                         'needs_qc']),
        'resources': set(['resource', 'varname', 'required'])
    }

    def __init__(self, yaml_source):
        self.yaml_source = yaml_source

        self.inputs,\
        self.inputs_by_type,\
        self.iteration_sources,\
        self.iteration_map =\
            ProcessorParser.parse_inputs(yaml_source)

        self.variables_to_inputs = ProcessorParser.parse_variables(self.inputs)

        self.csess = None
        self.artefacts = None
        self.artefacts_by_input = None
        self.parameter_matrix = None
        self.assessor_parameter_map = None
        self.command_params = None

        self.xsitype = yaml_source['attrs'].get('xsitype', 'proc:genProcData')
        self.proctype = XnatUtils.get_proctype(
            yaml_source['inputs']['default']['spider_path'])[0]


    def parse_session(self, csess):
        self.csess = None
        self.artefacts = None
        self.artefacts_by_input = None
        self.parameter_matrix = None
        self.assessor_parameter_map = None
        self.command_params = None

        artefacts = ProcessorParser.parse_artefacts(csess)

        artefacts_by_input = \
            ProcessorParser.map_artefacts_to_inputs(csess, self.inputs_by_type)

        parameter_matrix = \
            ProcessorParser.generate_parameter_matrix(
                self.inputs,
                self.iteration_sources,
                self.iteration_map,
                artefacts_by_input)

        assessor_parameter_map = \
            ProcessorParser.compare_to_existing(csess,
                                                self.proctype,
                                                parameter_matrix)

        command_params = ProcessorParser.generate_commands(
            csess,
            self.inputs,
            self.variables_to_inputs,
            parameter_matrix)

        self.csess = csess
        self.artefacts = artefacts
        self.artefacts_by_input = artefacts_by_input
        self.parameter_matrix = parameter_matrix
        self.assessor_parameter_map = assessor_parameter_map
        self.command_params = command_params


    @staticmethod
    def _get_yaml_checker(version):
        if version == '1':
            return ProcessorParser.__check_yaml_v1
        return None

    @staticmethod
    def _get_schema_dictionary(version):
        if version == '1':
            return ProcessorParser.__schema_dict_v1

    @staticmethod
    def __check_yaml_v1(yaml_source):
        errors = []
        schema_number = yaml_source.get('schema', '1')
        if schema_number != '1':
            errors.append('Error: Invalid schema number {}'.format(schema_number))

        if 'xnat' not in yaml_source:
            errors.append('Error: Missing xnat section')
        xnat_section = yaml_source['xnat']
        scan_section = xnat_section.get('scans', {})
        for k, v in scan_section.iteritems():
            pass

        assr_section = xnat_section.get('assessors', {})
        for k, v in assr_section.iteritems():
            pass



    @staticmethod
    def _get_args(statement):
        leftindex = statement.find('(')
        rightindex = statement.find(')')
        if leftindex == -1 and rightindex == -1:
            return [statement]
        elif leftindex != -1 and rightindex != -1:
            return [statement[:leftindex]] +\
                   [s.strip()
                    for s in statement[leftindex+1:rightindex].split(',')]
        else:
            raise ValueError('statement is malformed')


    @staticmethod
    def _parse_select(statement):
        if statement is None:
            statement = 'foreach'
        statement = statement.strip()
        return ProcessorParser._get_args(statement)


    @staticmethod
    def _register_iteration_references(name, iteration_args, iteration_sources,
                                       iteration_map):
        if iteration_args[0] == 'foreach':
            if len(iteration_args) == 1:
                iteration_sources.add(name)
            else:
                iteration_map[name] = iteration_args[1]
        elif iteration_args[0] == 'one':
            iteration_sources.add(name)
        elif iteration_args[0] == 'all':
            iteration_sources.add(name)
        elif iteration_args[0] == 'from':
            iteration_map[name] = iteration_args[1].split('/')[0]



    @staticmethod
    def _register_input_types(input_types, inputs_by_type, name):
        for t in input_types:
            ts = inputs_by_type.get(t, set())
            ts.add(name)
            inputs_by_type[t] = ts


    # TODO: BenM/general refactor/update yaml schema so scan name is an explicit
    # field
    @staticmethod
    def _input_name(artefact):
        # candidates = list(filter(lambda v: v[1] is None, scan.iteritems()))
        # if len(candidates) != 1:
        #     raise ValueError(
        #         "invalid scan entry format; scan name cannot be determined")
        # return candidates[0][0]
        return artefact['name']


    @staticmethod
    def parse_inputs(yaml_source):
        # TODO: BenM/assessor_of_assessor/check error conditions on inputs:
        # . resource should be set
        # . no repeated input names
        # . ambiguous overlaps for input types (this may not be a problem)?

        inputs_by_type = {}
        iteration_sources = set()
        iteration_map = {}

        # get inputs: pass 1
        input_dict = yaml_source['inputs']
        xnat = input_dict['xnat']
        if xnat == None:
            raise ValueError(
                'yaml processor is missing xnat keyword contents')

        inputs = {}
        # get scans
        scans = xnat.get('scans', list())
        for s in scans:
            name = ProcessorParser._input_name(s)
            select = s.get('select', None)
            parsed_select = ProcessorParser._parse_select(select)
            ProcessorParser._register_iteration_references(
                name,
                parsed_select,
                iteration_sources,
                iteration_map)

            types = [_.strip() for _ in s['types'].split(',')]
            ProcessorParser._register_input_types(types, inputs_by_type, name)

            resources = s.get('resources', [])
            artefact_required = False
            for r in resources:
                r['required'] = r.get('required', True)
                artefact_required = artefact_required or r['required']

            inputs[name] = {
                'types': types,
                'select': parsed_select,
                'artefact_type': 'scan',
                'needs_qc': s.get('needs_qc', False),
                'resources': s.get('resources', []),
                'required': artefact_required
            }

        # get assessors
        asrs = xnat.get('assessors', list())
        for a in asrs:
            name = ProcessorParser._input_name(a)
            select = a.get('select', None)
            parsed_select = ProcessorParser._parse_select(select)

            ProcessorParser._register_iteration_references(
                name,
                parsed_select,
                iteration_sources,
                iteration_map)

            types = [_.strip() for _ in a['proctypes'].split(',')]
            ProcessorParser._register_input_types(types, inputs_by_type, name)

            resources = a.get('resources', [])
            artefact_required = False
            for r in resources:
                r['required'] = r.get('required', True)
            artefact_required = artefact_required or r['required']

            inputs[name] = {
                'types': types,
                'select': parsed_select,
                'artefact_type': 'assessor',
                'needs_qc': a.get('needs_qc', False),
                'resources': a.get('resources', []),
                'required': artefact_required
            }

        return inputs, inputs_by_type, iteration_sources, iteration_map


    @staticmethod
    def parse_variables(inputs):
        variables_to_inputs = {}
        for ik, iv in inputs.iteritems():
            for r in iv['resources']:
                v = r.get('varname', '')
                if v is not None and len(v) > 0:
                    variables_to_inputs[v] =\
                        {'input': ik, 'resource': r['resource']}

        return variables_to_inputs


    @staticmethod
    def parse_artefacts(csess):
        def parse(carts, arts):
            for cart in carts:
                resources = {}
                for cres in cart.resources():
                    resources[cres.label()] = cres
                full_path = cart.full_path()
                arts[full_path] = ParserArtefact(full_path,
                                                 resources,
                                                 cart)

        artefacts = {}
        parse(csess.scans(), artefacts)
        parse(csess.assessors(), artefacts)
        return artefacts


    @staticmethod
    def map_artefact_to_inputs(artefact,
                               inputs_by_type,
                               artefacts_by_input):
        artefact_type = artefact.type()
        inputs_of_type = inputs_by_type.get(artefact_type, set())
        if len(inputs_of_type) > 0:
            # this artefact type is relevant to the assessor
            for i in inputs_of_type:
                artefacts = artefacts_by_input.get(i, [])
                artefacts.append(artefact.full_path())
                artefacts_by_input[i] = artefacts


    @staticmethod
    def map_artefacts_to_inputs(csess, inputs_by_type):

        # a dictionary of input names to artefacts
        artefacts_by_input = {}

        for cscan in csess.scans():
            ProcessorParser.map_artefact_to_inputs(cscan,
                                                   inputs_by_type,
                                                   artefacts_by_input)

        for cassr in csess.assessors():
            ProcessorParser.map_artefact_to_inputs(cassr,
                                                   inputs_by_type,
                                                   artefacts_by_input)

        return artefacts_by_input


    def has_inputs(self, assr):

        input_artefacts = utilities.decode_url_json_string(
            assr.attrs.get(self.xsitype.lower() + '/inputs'))
        errors = []
        for artefact_input_k, artefact_input_path\
            in input_artefacts.iteritems():
            xsitype = assr.attrs.get('xsiType')
            # check whether any inputs are missing, unusable or lacking the
            # required resource files
            input_entry = self.inputs[artefact_input_k]
            artefact = assr._intf.select(artefact_input_path)

            # check for existence. Note, an assessor is created if the
            # appropriate combination of inputs is present. If one or more of
            # those inputs is subsequently removed from the session, the
            # assessor now has a missing input
            if not artefact.exists():
                errors.append(
                    (
                        artefact_input_k,
                        'Artefact {} does not exist'.format(
                            artefact_input_path)
                    )
                )
                continue

            artefact_type = assr._intf.object_type_from_path(
                artefact_input_path)
            if artefact_type not in ['scan', 'assessor']:
                errors.append(
                    (
                        artefact_input_k,
                        'Artefact {} must be a scan or assessor'.format(
                            artefact_input_path))
                    )
                continue

            if input_entry['needs_qc'] == True:
                if artefact_type == 'scan':
                    usable =\
                        artefact.attrs.get('quality') == 'usable'
                else:
                    status =\
                        artefact.attrs.get(xsitype + '/validation/status')
                    usable = XnatUtils.is_bad_qa(status) == 1

                if not usable:
                    errors.append(
                        (
                            artefact_input_k,
                            'Artefact {} is not usable'.format(
                                artefact_input_path)
                        )
                    )

            resource_dict = {}

            for robj in artefact.resources():
                resource_dict[robj.label()] = len(list(robj.files()))

            for r in input_entry['resources']:
                if r['resource'] not in resource_dict:
                    errors.append(
                        (
                            artefact_input_k,
                            'Artefact {} is missing {} resource'.format(
                                artefact_input_path, r['resource'])
                        )
                    )
                elif resource_dict[r['resource']] < 1:
                    errors.append(
                        (
                            artefact_input_k,
                            'Artefact {} is missing files from resource {}'
                            .format(artefact_input_path, r['resource'])
                        )
                    )

        return 1 if len(errors) == 0 else 0, errors


    # TODO: BenM/assessor_of_assessors/improve name of generate_parameter_matrix
    # TODO: BenM/assessor_of_assessors/handle multiple args disallowed / allowed
    # scenarios
    @staticmethod
    def generate_parameter_matrix(inputs,
                                  iteration_sources,
                                  iteration_map,
                                  artefacts,
                                  artefacts_by_input):

        # generate n dimensional input matrix based on iteration sources
        all_inputs = []
        input_dimension_map = []

        # check whether all inputs are present
        for i, iv in inputs.iteritems():
            if i not in artefacts_by_input and iv['required'] == True:
                return []

        # add in None for optional inputs so that the matrix can be generated
        # without artefacts present for those inputs
        sanitised_inputs = {}
        for i, iv in inputs.iteritems():
            if i not in artefacts_by_input:
                sanitised_inputs[i] = [[None]]
            else:
                sanitised_inputs[i] = artefacts_by_input[i]

        for i in iteration_sources:
            # find other inputs that map to this iteration source
            mapped_inputs = [i]
            mapped_input_vector = []
            select_fn = inputs[i]['select'][0]

            if select_fn == 'foreach':
                min_artefact_count = len(sanitised_inputs[i])
                for k, v in iteration_map.iteritems():
                    if v == i:
                        min_artefact_count = min(min_artefact_count,
                                                 sanitised_inputs[k])
                        mapped_inputs.append(k)

                if inputs[k]['select'][0] == 'foreach':
                    if min_artefact_count > 0:
                        for ind in range(min_artefact_count):
                            cur = []
                            for m in mapped_inputs:
                                cur.append(sanitised_inputs[m][ind])
                            mapped_input_vector.append(cur)
                else:
                    from_artefacts = artefacts_by_input[v]
                    for fa in from_artefacts:
                        cur = [fa]
                        # get the named input from each assessor
                        a = artefacts[fa]
                        from_inputs = a.entity.get_inputs()
                        for m in mapped_inputs[1:]:
                            cur.append(from_inputs[m])
                        mapped_input_vector.append(cur)

            elif select_fn == 'all':
                mapped_input_vector = [[sanitised_inputs[i][:]]]

            elif select_fn == 'some':
                input_count = min(len(sanitised_inputs[i]),
                                  inputs[i]['select'][1])
                mapped_input_vector = [[sanitised_inputs[i][input_count:]]]

            elif select_fn == 'one':
                mapped_input_vector = [sanitised_inputs[i][0]]

            all_inputs.append(mapped_inputs)
            input_dimension_map.append(mapped_input_vector)

        # perform a cartesian product of the dimension map entries to get the
        # final input combinations
        matrix = map(lambda x: list(itertools.chain.from_iterable(x)),
                     itertools.product(*input_dimension_map))

        matrix_headers = list(itertools.chain.from_iterable(all_inputs))

        # rebuild the matrix to order the inputs consistently
        final_matrix = []
        for r in matrix:
            row = dict()
            for i in range(len(matrix_headers)):
                row[matrix_headers[i]] = r[i]
            final_matrix.append(row)

        return final_matrix


    @staticmethod
    def compare_to_existing(csess, processor_type, parameter_matrix):

        assessors = [[] for _ in range(len(parameter_matrix))]
        for casr in filter(lambda a: a.type() == processor_type,
                           csess.assessors()):
            inputs = casr.get_inputs()

            for pi, p in enumerate(parameter_matrix):
                if inputs == p:
                    assessors[pi].append(casr)

        return zip(copy.deepcopy(parameter_matrix), assessors)


    @staticmethod
    def generate_commands(csess,
                          inputs,
                          variables_to_inputs,
                          parameter_matrix):
        # map from parameters to input resources

        path_elements = [
            csess.project_id(),
            csess.subject_id(),
            csess.session_id(),
            None,
            None]

        command_sets = []
        for p in parameter_matrix:
            command_set = dict()
            for k, v in variables_to_inputs.iteritems():
                inp = inputs[v['input']]
                artefact_type = inp['artefact_type']
                resource = v['resource']

                path_elements = [p[v['input']], resource]

                # command_set[k] =\
                #     artefact_paths[artefact_type].format(*path_elements)
                command_set[k] =\
                    resource_paths[artefact_type].format(*path_elements)

            command_sets.append(command_set)

        return command_sets
