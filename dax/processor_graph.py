

class ProcessorGraph:

    @staticmethod
    def processor_inputs_from_sources(yaml_sources):
        sources = dict()
        for name, source in yaml_sources:
            xnat = source.contents.get('inputs', {}).get('xnat', {})

            asrs = xnat.get('assessors', {})
            inputs = set()
            print 'asrs =', asrs
            for a in asrs:
                types = a.get('proctypes', '').split(',')

                inputs = inputs.union(types)
            sources[name] = list(inputs)
        print sources



    # TODO: BenM/assessor_of_assessor/ideally, this would operate on a list of
    # processors rather than a list of yaml_sources, but this would require a
    # refactor of existing processors
    @staticmethod
    def ordered_processors(artefact_type_map):
        print artefact_type_map
        # artefact_type_map is a list of artefacts to their *inputs*.
        # consider the following graph:
        # a --> b --> d
        #   \     \     \
        #    \     \     \
        #     > c --> e --> f
        # this function takes a mapping from a node to its inputs:
        # a -> [], b -> [a], c -> [a], d -> [b], e -> [b, c], f -> [d, e]
        #
        # the algorithm then proceeds as follows:
        # 1. calculate a list of nodes to sink edges (fwd_edges)
        # 2. calculate in-degrees for the nodes, adding any node with no
        #    inputs to the satisfied node list
        # 3. keep taking nodes from the satisfied node list, following their
        #    sink edges and lowering the in-degree of each sink node by 1.
        #    Nodes that hit zero in-degree are added to the satisfied list and
        #    the current node is added to the ordered list
        open_nodes = dict()
        satisfied = list()
        ordering = list()
        fwd_edges = dict()

        # calculate a list of nodes to sink edges
        for k, v in artefact_type_map.iteritems():
            if k not in fwd_edges:
                fwd_edges[k] = []
            for src in v:
                if src not in fwd_edges:
                    fwd_edges[src] = []
                fwd_edges[src].append(k)
        for v in fwd_edges:
            fwd_edges[v] = sorted(fwd_edges[v])

        # calculate the 'in-degree' (number of incoming edges) for each
        # node; this is more easily done using the mapping of nodes to inputs.
        # if a node has an in-degree of zero then it can go onto the satisfied
        # list
        for k, v in artefact_type_map.iteritems():
            open_nodes[k] = len(v)
            if len(v) == 0:
                satisfied.append(k)

        # keep picking nodes from the front of the satisfied list until there
        # are no more. each follow the sink edges for that node and reduce the
        # sink node in-degrees by 1. Any node whose in-degree falls to 0 is
        # added to the end of the satisfied list
        while len(satisfied) > 0:
            cur = satisfied[0]
            ordering.append(cur)
            satisfied = satisfied[1:]
            for sink in fwd_edges[cur]:
                open_nodes[sink] -= 1
                if open_nodes[sink] == 0:
                    satisfied.append(sink)

        for k, v in open_nodes.iteritems():
            if v > 0:
                ordering.append(k)

        return ordering