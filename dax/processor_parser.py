
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


def _get_args(statement):
    leftindex = statement.find('(')
    rightindex = statement.find(')')
    if leftindex == -1 and rightindex == -1:
        return [statement]
    elif leftindex != -1 and rightindex != -1:
        return [statement[:leftindex]] +\
               [s.strip() for s in statement[leftindex+1:rightindex].split(',')]
    else:
        raise ValueError('statement is malformed')


def _parse_select(statement):
    if statement is None:
        statement = 'foreach'
    statement = statement.strip()
    return _get_args(statement)


def _register_iteration_references(name, iteration_args, iteration_sources,
                                   iteration_map):
    if iteration_args[0] == 'foreach':
        if len(iteration_args) == 1:
            iteration_sources.add(name)
        else:
            iteration_map[name] = iteration_args[1]


def _register_input_types(input_types, inputs_by_type, name):
    for t in input_types:
        ts = inputs_by_type.get(t, set())
        ts.add(name)
        inputs_by_type[t] = ts


# TODO: BenM/general refactor/update yaml schema so scan name is an explicit
# field
def _input_name(scan):
    candidates = list(filter(lambda v: v[1] is None, scan.iteritems()))
    if len(candidates) != 1:
        raise ValueError(
            "invalid scan entry format; scan name cannot be determined")
    return candidates[0][0]


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
        name = _input_name(s)
        select = s.get('select', None)

        _register_iteration_references(name, _parse_select(select),
                                       iteration_sources, iteration_map)

        types = [_.strip() for _ in s['types'].split(',')]
        _register_input_types(types, inputs_by_type, name)

        inputs[name] = {
            'types': types,
            'artefact_type': 'scan',
            'needs_qc': s.get('needs_qc', False),
            'resources': s.get('resources', [])
        }

    # get assessors
    asrs = xnat.get('assessors', list())
    for a in asrs:
        name = _input_name(a)
        select = a.get('select', None)

        _register_iteration_references(name, _parse_select(select),
                                       iteration_sources, iteration_map)

        types = [_.strip() for _ in a['proctypes'].split(',')]
        _register_input_types(types, inputs_by_type, name)

        inputs[name] = {
            'types': types,
            'artefact_type': 'assessor',
            'needs_qc': s.get('needs_qc', False),
            'resources': s.get('resources', [])
        }

    return inputs, inputs_by_type, iteration_sources, iteration_map


def parse_artefacts(csess):
    def parse(carts, arts):
        for cart in carts:
            artefact = {}
            resources = {}
            artefact['entity'] = cart
            artefact['resources'] = resources
            for cres in cart.get_resources():
                resources[cres.label()] = cres
            arts[cart.id()] = artefact

    artefacts = {}
    parse(csess.scans(), artefacts)
    parse(csess.assessors(), artefacts)
    return artefacts


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
                artefacts.append(artefact.id())
                artefacts_by_input[i] = artefacts


def map_artefacts_to_inputs(csess, inputs, inputs_by_type):

    # a dictionary of input names to artefacts
    artefacts_by_input = {}

    for cscan in csess.scans():
        map_artefact_to_inputs(cscan,
                               inputs,
                               inputs_by_type,
                               artefacts_by_input)

    for cassr in csess.assessors():
        map_artefact_to_inputs(cassr,
                               inputs,
                               inputs_by_type,
                               artefacts_by_input)

    return artefacts_by_input


def filter_artefacts_by_quality(inputs, artefacts, artefacts_by_input):

    filtered_artefacts_by_input = {}

    for k, v in inputs.iteritems():
        filtered_artefacts = []
        for a in artefacts_by_input.get(k, {}):
            artefact = artefacts[a]
            if not artefact['entity'].unusable() or v['needs_qc'] is False:
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


# TODO: BenM/assessor_of_assessors/improve name of generate_parameter_matrix
# TODO: BenM/assessor_of_assessors/handle multiple args disallowed / allowed
# scenarios
def generate_parameter_matrix(iteration_sources,
                              iteration_map,
                              artefacts_by_input):

    # generate n dimensional input matrix based on iteration sources
    input_dimension_map = {}
    for i in iteration_sources:
        # find other inputs that map to this iteration source
        mapped_inputs = []
        mapped_input_vector = []
        if len(artefacts_by_input.get(i, [])) > 0:
            mapped_inputs.append(i)
            for k, v in iteration_map.iteritems():
                if v == i and len(artefacts_by_input.get(k, [])) > 0:
                    mapped_inputs.append(k)

            print "mapped_inputs =", mapped_inputs

            # generate 'zip' of inputs that are all attached to iteration source

            for ind in range(len(artefacts_by_input[i])):
                cur = []
                for m in mapped_inputs:
                    cur.append(
                        artefacts_by_input[m][ind % len(artefacts_by_input[m])]
                    )
                mapped_input_vector.append(cur)

        input_dimension_map[i] = (mapped_inputs, mapped_input_vector)

    print input_dimension_map


def generate_commands(command_template, artefacts, input_dimension_map):
    pass