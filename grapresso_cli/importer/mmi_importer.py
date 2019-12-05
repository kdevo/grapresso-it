import os
from typing import NamedTuple

from grapresso.backend.api import DataBackend
from grapresso.components.graph import UndirectedGraph, DirectedGraph

MetaInfo = NamedTuple('MetaInfo', [('matching_group_no', int),
                                   ('weighted', bool), ('capacity', bool), ('matching', bool), ('balanced', bool)])


class MmiImporter:
    def __init__(self, relative_dir=None):
        self._relative_dir = relative_dir
        self._meta_info = None

    def read_graph(self, backend: DataBackend, file_path, is_directed=False):
        if self._relative_dir:
            file_path = os.path.join(self._relative_dir, file_path)

        weighted = file_path.endswith('w') or file_path.endswith('wc')
        capacity = file_path.endswith('c') or file_path.endswith('wc')
        matching = file_path.endswith('m')
        balanced = file_path.endswith('bwc')

        last_import_group_no = 0
        graph = DirectedGraph(backend) if is_directed else UndirectedGraph(backend)
        with open(file_path, 'rt', buffering=1, encoding='ascii') as file:
            node_count = int(file.readline().strip())
            if matching:
                last_import_group_no = int(file.readline().strip())
            for i in range(node_count):
                graph.add_node(i, balance=float(file.readline().strip()) if balanced else 0.0)

            for line in file:
                edge = line.strip().split()
                graph.add_edge(int(edge[0]), int(edge[1]),
                               cost=float(edge[2]) if weighted else 0.0,
                               capacity=float(edge[2 + file_path.endswith('wc')]) if capacity else 0.0)
        self._meta_info = MetaInfo(last_import_group_no, weighted, capacity, matching, balanced)
        return graph

    def scan_dir(self, directory='', ext=('mmi', 'mmiw', 'mmic', 'mmiwc')):
        return [fn for fn in os.listdir(os.path.join(self._relative_dir, directory))
                if (fn.endswith(e) for e in ext)]  # Only allow files ending with ext

    @property
    def last_import_metainfo(self) -> MetaInfo:
        return self._meta_info
