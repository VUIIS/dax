
import logging
LOGGER = logging.getLogger('dax')

# TODO: BenM/asr_of_asr/should detect / report cycles
# TODO: BenM/asr_of_asr/needs proper unittesting


class ProcessorGraph:

    @staticmethod
    def processor_inputs_from_sources(yaml_sources):
        sources = dict()
        for name, source in yaml_sources:
            xnat = source.contents.get('inputs', {}).get('xnat', {})

            asrs = xnat.get('assessors', {})
            inputs = set()
            for a in asrs:
                types = a.get('types', '').split(',')

                inputs = inputs.union(types)
            sources[name] = list(inputs)
        return sources

    @staticmethod
    def get_forward_edges(nodes_to_src_edges):
        sink_edges = dict()
        # calculate a list of nodes to sink edges
        for k, v in list(nodes_to_src_edges.items()):
            if k not in sink_edges:
                sink_edges[k] = []
            for src in v:
                if src not in sink_edges:
                    sink_edges[src] = []
                sink_edges[src].append(k)
        for v in sink_edges:
            sink_edges[v] = sorted(sink_edges[v])

        return sink_edges

    @staticmethod
    def order_processors(processors, log=None):
        """
        Order a list of processors in dependency order.
        This method takes a list of processors and orders them so that:
        . if processor type b takes an input of processor type a, processor a
          appears in the list before processor b
        . processors without a well-formed name are placed at the end of the
          list in no particular order


        :param processors:
        :return:
        """
        processor_map = dict([(p.get_proctype(), p) for p in processors])
        named_processors = []
        unnamed_processors = []
        assessor_inputs = {}
        for p in processors:
            proctype = p.get_proctype()
            if not proctype:
                unnamed_processors.append(p)
            else:
                assessor_inputs[p.get_proctype()] =\
                    p.get_assessor_input_types()

        ordered_names = ProcessorGraph.order_from_inputs(assessor_inputs, log)
        for n in ordered_names:
            named_processors.append(processor_map[n])
        return named_processors + unnamed_processors

    # TODO: BenM/assessor_of_assessor/ideally, this would operate on a list of
    # processors rather than a list of yaml_sources, but this would require a
    # refactor of existing processors
    @staticmethod
    def order_from_inputs(artefacts_to_inputs, log=None):
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
        ordered = list()
        fwd_edges = ProcessorGraph.get_forward_edges(artefacts_to_inputs)

        # calculate the 'in-degree' (number of incoming edges) for each
        # node; this is more easily done using the mapping of nodes to inputs.
        # if a node has an in-degree of zero then it can go onto the satisfied
        # list
        for k, v in list(artefacts_to_inputs.items()):
            open_nodes[k] = len(v)
            if len(v) == 0:
                satisfied.append(k)

        # keep picking nodes from the front of the satisfied list until there
        # are no more. each follow the sink edges for that node and reduce the
        # sink node in-degrees by 1. Any node whose in-degree falls to 0 is
        # added to the end of the satisfied list
        while len(satisfied) > 0:
            cur = satisfied[0]
            ordered.append(cur)
            satisfied = satisfied[1:]
            for sink in fwd_edges[cur]:
                open_nodes[sink] -= 1
                if open_nodes[sink] == 0:
                    satisfied.append(sink)

        unordered = list()
        for k, v in list(open_nodes.items()):
            if v > 0:
                unordered.append(k)
        unordered = sorted(unordered)

        if len(unordered) > 0 and log is not None:
            log.warning('Unable to order all processors:')
            log.warning('  Unordered: ' + ', '.join(unordered))
            regions = ProcessorGraph.tarjan(fwd_edges)
            if len(regions) < len(artefacts_to_inputs):
                log.warning('Cyclic processor dependencies detected:')
            regions.reverse()
            for r in [x for x in regions if len(x) > 1]:
                log.warning('  Cycle: ' + ', '.join(r))

        return ordered + unordered

    @staticmethod
    def tarjan(graph):

        class Vertex:
            def __init__(self, v, e):
                self.v = v
                self.e = e
                self.index = None
                self.onstack = False
                self.lowLink = None

        class TarjanImpl:
            """
            Expecting graph to be in the form of:
            {
                a: [b, c],
                b: [d],
                c: [e],
                d: [f],
                e: [f],
                f: []
            }
            :param graph:
            :return:
            """

            def __init__(self):
                self.V = dict()
                self.S = list()
                self.index = 0
                self.scrs = list()

            def go(self, graph):
                self.V = dict()
                self.S = list()
                self.index = 0
                self.scrs = list()
                self.V = {v: Vertex(v, w) for (v, w) in list(graph.items())}

                self.index = 0
                self.S = list()

                for v in self.V.values():
                    if v.index is None:
                        self.strongconnect(v)

                return self.scrs

            def strongconnect(self, v):
                v.index = self.index
                v.lowlink = self.index
                self.index += 1
                self.S.append(v)
                v.onstack = True

                for d in v.e:
                    w = self.V[d]
                    if w.index is None:
                        self.strongconnect(w)
                        v.lowlink = min(v.lowlink, w.lowlink)
                    elif w.onstack is True:
                        v.lowlink = min(v.lowlink, w.index)

                if v.lowlink == v.index:
                    scr = []
                    while True:
                        w = self.S.pop()
                        w.onstack = False
                        scr.append(w.v)
                        if w is v:
                            break
                    self.scrs.append(scr)

        t = TarjanImpl()
        results = t.go(graph)
        # print results, len(results) < len(graph)
        return results
