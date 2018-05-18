
import copy
import itertools

from . import utilities
from . import XnatUtils
from .XnatUtils import InterfaceTemp


# TODO: BenM/assessor_of_assessor/
# support lack of input field on old assessors
# support lack of schema number & schema number (maybe on processor)
# support the ability to fix broken inputs
# support partial node ordering of processor dependencies

session_namespace = {
    'foreach': {'args': [{'optional': True, 'type': str}]},
    'one': {'args': []},
    'some': {'args': [{'optional': False, 'type': int}]},
    'all': {'args': []}
}


no_scans_error = 'No scan of the required type/s ({}) found for input {}'
no_asrs_error = 'No assessors of the require type/s ({}) found for input {}'
scan_unusable_error = 'Scan {} is unusable for input {}'
asr_unusable_error = 'Assessor {} is unusable for input {}'

base_path = '/project/{0}/subject/{1}/experiment/{2}/'
assr_path = base_path + 'assessor/{3}/out/resource/{4}'
scan_path = base_path + 'scan/{3}/resource/{4}'
artefact_paths = {'assessor': assr_path, 'scan': scan_path}

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


    def parse_session(self, csess):
        self.csess = None
        self.artefacts = None
        self.artefacts_by_input = None
        self.parameter_matrix = None
        self.assessor_parameter_map = None
        self.command_params = None

        artefacts = ProcessorParser.parse_artefacts(csess)

        artefacts_by_input = \
            ProcessorParser.map_artefacts_to_inputs(csess,
                                                    self.inputs,
                                                    self.inputs_by_type)

        filtered_artefacts_by_input = \
            ProcessorParser.filter_artefacts_by_quality(self.inputs,
                                                        artefacts,
                                                        artefacts_by_input)

        parameter_matrix = \
            ProcessorParser.generate_parameter_matrix(
                self.iteration_sources,
                self.iteration_map,
                filtered_artefacts_by_input)

        assessor_parameter_map = \
            ProcessorParser.compare_to_existing(csess, 'proc2',
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
        #elif iteration_args[0] = 'one':



    @staticmethod
    def _register_input_types(input_types, inputs_by_type, name):
        for t in input_types:
            ts = inputs_by_type.get(t, set())
            ts.add(name)
            inputs_by_type[t] = ts


    # TODO: BenM/general refactor/update yaml schema so scan name is an explicit
    # field
    @staticmethod
    def _input_name(scan):
        candidates = list(filter(lambda v: v[1] is None, scan.iteritems()))
        if len(candidates) != 1:
            raise ValueError(
                "invalid scan entry format; scan name cannot be determined")
        return candidates[0][0]


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
        print 'xnat =', xnat

        inputs = {}
        # get scans
        scans = xnat.get('scans', list())
        for s in scans:
            name = ProcessorParser._input_name(s)
            select = s.get('select', None)

            ProcessorParser._register_iteration_references(
                name,
                ProcessorParser._parse_select(select),
                iteration_sources,
                iteration_map)

            types = [_.strip() for _ in s['types'].split(',')]
            ProcessorParser._register_input_types(types, inputs_by_type, name)

            inputs[name] = {
                'types': types,
                'artefact_type': 'scan',
                'needs_qc': s.get('needs_qc', False),
                'resources': s.get('resources', [])
            }

        # get assessors
        asrs = xnat.get('assessors', list())
        for a in asrs:
            name = ProcessorParser._input_name(a)
            select = a.get('select', None)

            ProcessorParser._register_iteration_references(
                name,
                ProcessorParser._parse_select(select),
                iteration_sources,
                iteration_map)

            types = [_.strip() for _ in a['proctypes'].split(',')]
            ProcessorParser._register_input_types(types, inputs_by_type, name)

            inputs[name] = {
                'types': types,
                'artefact_type': 'assessor',
                'needs_qc': a.get('needs_qc', False),
                'resources': a.get('resources', [])
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
                # artefact = {}
                resources = {}
                # artefact['entity'] = cart
                # artefact['resources'] = resources
                for cres in cart.get_resources():
                    resources[cres.label()] = cres
                full_path = cart.full_path()
                arts[full_path] = ParserArtefact(full_path,
                                                 resources,
                                                 cart)
                # arts[cart.label()] = artefact

        artefacts = {}
        parse(csess.scans(), artefacts)
        parse(csess.assessors(), artefacts)
        return artefacts


    @staticmethod
    def map_artefact_to_inputs(artefact,
                               inputs,
                               inputs_by_type,
                               artefacts_by_input):
        artefact_type = artefact.type()
        inputs_of_type = inputs_by_type.get(artefact_type, set())
        if len(inputs_of_type) > 0:
            # this artefact type is relevant to the assessor
            for i in inputs_of_type:
                artefacts = artefacts_by_input.get(i, [])
                matched = 0
                for ir in (r['resource'] for r in inputs[i]['resources']):
                    for ar in artefact.get_resources():
                        if ir == ar.label():
                            matched += 1
                            break
                if matched == len(inputs[i]['resources']):
                    artefacts.append(artefact.full_path())
                    artefacts_by_input[i] = artefacts


    @staticmethod
    def map_artefacts_to_inputs(csess, inputs, inputs_by_type):

        # a dictionary of input names to artefacts
        artefacts_by_input = {}

        for cscan in csess.scans():
            ProcessorParser.map_artefact_to_inputs(cscan,
                                                   inputs,
                                                   inputs_by_type,
                                                   artefacts_by_input)

        for cassr in csess.assessors():
            ProcessorParser.map_artefact_to_inputs(cassr,
                                                   inputs,
                                                   inputs_by_type,
                                                   artefacts_by_input)

        return artefacts_by_input


    @staticmethod
    def filter_artefacts_by_quality(inputs, artefacts, artefacts_by_input):

        filtered_artefacts_by_input = {}

        for k, v in inputs.iteritems():
            filtered_artefacts = []
            for a in artefacts_by_input.get(k, {}):
                artefact = artefacts[a]
                if not artefact.entity.unusable() or v['needs_qc'] is False:
                    filtered_artefacts.append(a)

            if len(filtered_artefacts) > 0:
                filtered_artefacts_by_input[k] = filtered_artefacts

        return filtered_artefacts_by_input


    # TODO: BenM/assessor_of_assessor/has_inputs needs to be run on a particular
    # combination of inputs; this method isn't doing that!
    # This method really should just be checking if there are inputs of the proper
    # type in the first place; another method should check the status of individual
    # combinations of inputs. Remember, we always create an assessor if a given
    # combination if inputs is present, even if it can't yet run
    # def has_inputs(inputs, artefacts, artefacts_by_input):
    #     errors = []
    #     for k, v in inputs.iteritems():
    #         print "k, v =", k, v
    #         is_scan = v['artefact_type'] == 'scan'
    #         if k not in artefacts_by_input:
    #             # there are no available artefacts of this input type
    #             error_msg = no_scans_error if is_scan else no_asrs_error
    #             errors.append(error_msg.format(','.join(v['types']), k))
    #         elif artefacts[k]['entity'].unusable() and v['needs_qc']:
    #             error_msg = scan_unusable_error if is_scan else asr_unusable_error
    #             errors.append(error_msg.format(','.join(k)))
    #         else:
    #             print k, 'can use',
    #
    #     return len(errors) == 0, errors


    def has_inputs(self, cassr):
        assr = cassr.full_object()
        intf = cassr.intf
        input_artefacts = utilities.decode_url_json_string(
            assr.attrs.get(self.xsitype + '/inputs'))
        errors = []
        for artefact_input_k, artefact_input_path\
            in input_artefacts.iteritems():
            xsitype = assr.attrs.get('xsiType')
            # check whether any inputs are missing, unusable or lacking the
            # required resource files
            input_entry = self.inputs[artefact_input_k]
            artefact = intf.select(artefact_input_path)

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

            artefact_type = intf.object_type_from_path(
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
                                artefact_input_path, r.label())
                        )
                    )
                elif resource_dict[r['resource']] < 1:
                    errors.append(
                        (
                            artefact_input_k,
                            'Artefact {} is missing files from resource {}'
                            .format(artefact_input_path, r.label())
                        )
                    )

        return 1 if len(errors) == 0 else 0, errors


    # TODO: BenM/assessor_of_assessors/improve name of generate_parameter_matrix
    # TODO: BenM/assessor_of_assessors/handle multiple args disallowed / allowed
    # scenarios
    @staticmethod
    def generate_parameter_matrix(iteration_sources,
                                  iteration_map,
                                  artefacts_by_input):

        # generate n dimensional input matrix based on iteration sources
        all_inputs = []
        input_dimension_map = [] #{}
        for i in iteration_sources:
            # find other inputs that map to this iteration source
            mapped_inputs = []
            mapped_input_vector = []
            if len(artefacts_by_input.get(i, [])) > 0:
                mapped_inputs.append(i)
                for k, v in iteration_map.iteritems():
                    if v == i and len(artefacts_by_input.get(k, [])) > 0:
                        mapped_inputs.append(k)

                # generate 'zip' of inputs that are all attached to iteration
                # source

                for ind in range(len(artefacts_by_input[i])):
                    cur = []
                    for m in mapped_inputs:
                        cur.append(
                            artefacts_by_input[m][ind % len(artefacts_by_input[m])]
                        )
                    mapped_input_vector.append(cur)

            # input_dimension_map[i] = (mapped_inputs, mapped_input_vector)
            all_inputs.append(mapped_inputs)
            input_dimension_map.append(mapped_input_vector)

        # perform a cartesian product of the dimension map entries to get the
        # final input combinations

        matrix = map(lambda x: list(itertools.chain.from_iterable(x)),
                     itertools.product(*input_dimension_map))
        return list(itertools.chain.from_iterable(all_inputs)), matrix


    @staticmethod
    def compare_to_existing(csess, processor_type, parameter_matrix):

        assessors = [[] for _ in range(len(parameter_matrix[1]))]
        for casr in filter(lambda a: a.type() == processor_type, csess.assessors()):
            inputs = casr.get_inputs()

            #get an index map from the inputs to the parameter matrix
            index_map = {}
            for index, input in enumerate(parameter_matrix[0]):
                index_map[input] = index
            indices = []
            for i in inputs:
                indices.append(index_map[i])

            # for each entry in the parameter matrix, see if it matches with
            # an existing assessor in terms of inputs
            asr_artefacts =\
                map(lambda v: v[1].split('/')[-1], inputs.iteritems())
            asr_artefacts = [v for _, v in inputs.iteritems()]
            print 'asr_artefacts =', asr_artefacts

            for pi, p in enumerate(parameter_matrix[1]):
                # ia[0] is an index, ia[1] is the artefact name; artefact names in
                # p are in a different order to artefact names in the inputs, so use
                # 'indices' to find the index of the ith input artefact in the
                # parameter map and then perform the comparison. If all match, p
                # matches the current assessor
                if all((p[indices[ia[0]]] == ia[1]
                        for ia in enumerate(asr_artefacts))):
                    assessors[pi].append(casr)
                    break

            # TODO: BenM/assessor_of_assessor/handle multiple assessors associated
            # with a given set of inputs

        return (parameter_matrix[0],
                zip(copy.deepcopy(parameter_matrix[1]), assessors))


    @staticmethod
    def generate_commands(csess,
                          inputs,
                          variables_to_inputs,
                          parameter_matrix):
        # map from parameters to input resources

        parameter_matrix_indices = {}
        for k, v in variables_to_inputs.iteritems():
            index = None
            for i, p in enumerate(parameter_matrix[0]):
                if p == v['input']:
                    index = i
                    break
            parameter_matrix_indices[k] = index
        print "parameter_matrix_indices =", parameter_matrix_indices

        path_elements = [
            csess.project_id(),
            csess.subject_id(),
            csess.session_id(),
            None,
            None]

        command_sets = []
        for p in parameter_matrix[1]:
            command_set = {}
            for k, v in variables_to_inputs.iteritems():
                parameter_index = parameter_matrix_indices[k]
                inp = inputs[parameter_matrix[0][parameter_index]]
                artefact_type = inp['artefact_type']
                resource = v['resource']

                path_elements[-2] = parameter_matrix[0][parameter_index]
                path_elements[-1] = resource

                command_set[k] =\
                    artefact_paths[artefact_type].format(*path_elements)

            command_sets.append(command_set)

        return command_sets

