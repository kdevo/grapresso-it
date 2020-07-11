""" Just an example:
Implementation of a CLI that can handle the supplied .mmi files in the `res/example-graphs` directory.

Example arguments:
- `K_12.mmiw G_10_20.mmiw --methods 2*kruskal 2*prim --backend memory --graph-size`
WIll
"""

import argparse
import os
import sys

LIB_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..")
sys.path.insert(1, LIB_DIR)

from grapresso.tools.memory import getsize
from grapresso.tools.performance import timeit
from grapresso.backends.memory import InMemoryBackend, Trait
from grapresso.backends.networkx import NetworkXBackend
from grapresso.components.graph import UnDiGraph, DiGraph
from grapresso_cli.importer.mmi_importer import MmiImporter

BACKEND_DISPATCH = {'mem-optper': lambda: InMemoryBackend(Trait.OPTIMIZE_PERFORMANCE),
                    'mem-optmem': lambda: InMemoryBackend(Trait.OPTIMIZE_PERFORMANCE),
                    'mem': lambda: InMemoryBackend(),
                    'nx ': NetworkXBackend()}

METHOD_DISPATCH = {'count-components': UnDiGraph.count_connected_components,
                   'kruskal': UnDiGraph.perform_kruskal,
                   'prim': UnDiGraph.perform_prim,
                   'nearest-neighbour': UnDiGraph.perform_nearest_neighbour_tour,
                   'enumerate': UnDiGraph.enumerate,
                   'enumerate-bb': UnDiGraph.enumerate_bnb,
                   'double-tree': UnDiGraph.double_tree_tour,
                   'dijkstra': UnDiGraph.perform_dijkstra,
                   'mbf': UnDiGraph.perform_bellman_ford}

parser = argparse.ArgumentParser(description='Process MMI graph.')
parser.add_argument('files', metavar='file', type=str, nargs='+',
                    help='MMI files to process.')
parser.add_argument('--symmetric', action='store_const', const=True, default=False)
parser.add_argument('--backends', nargs='+', choices=BACKEND_DISPATCH.keys(), default='mmi',
                    help="Backend for storing the graph's data structure.")
parser.add_argument('--base-dir', type=str,
                    default=os.path.abspath(os.path.join(os.path.dirname(__file__), "./res/example-graphs/")))
parser.add_argument('--methods', type=str, nargs='+',
                    help="Methods to execute (you can even say that you want to execute a method n-times:\n"
                         "\t Simply pass <n>*<method>, e.g. 3*count-components. "
                         "If the value before * is omitted, it will simply execute it once ('1*').")
parser.add_argument('--graph-size', action='store_const', const=True, default=False)


def run(arguments):
    passed_values = parser.parse_args(arguments)

    print("Arguments:", passed_values, "\n")

    importer = MmiImporter(passed_values.base_dir)
    file_names = passed_values.files
    results = {}
    for file_name in file_names:
        results[file_name] = {}
        for backend in passed_values.backends:
            results[file_name][backend] = {}
            print("↓ Importing graph '{}' using '{}' backend...".format(file_name, backend), end=" ", flush=True)

            def import_graph():
                if backend == 'file':
                    directory = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                             "./res/example-graphs/serialized/" + file_name))
                    if os.path.exists(directory):
                        print("Info: Graph already exists in a serialized form (dir: {}).".format(directory))
                        if passed_values.symmetric:
                            return UnDiGraph(BACKEND_DISPATCH[backend]())
                        else:
                            return DiGraph(BACKEND_DISPATCH[backend]())
                    else:
                        return importer.read_graph(BACKEND_DISPATCH[backend](), file_name,
                                                   not passed_values.symmetric)
                else:
                    return importer.read_graph(BACKEND_DISPATCH[backend](), file_name, not passed_values.symmetric)

            timeit_result = timeit(import_graph, status_fn=lambda n, t: print("Took", t, "ms."), cleanup_fn=None)
            graph = timeit_result['return']
            if passed_values.graph_size:
                size = getsize(graph)
                print("\t💾 Backend: {} - recursively measuring graph size...".format(backend), end="", flush=True)
                print("\r\t💾 Backend: {} - approximated graph size:".format(backend),
                      getsize(graph), "Byte |", size / 1000 ** 2, "Megabyte")

            for n_method in passed_values.methods:
                n, method = (n_method if '*' in n_method else '1*' + n_method).strip().split('*')
                print("\t➤ Performing {method} {n} time(s).".format(method=method, n=n), flush=True)

                timeit_result = timeit(lambda: METHOD_DISPATCH[method](graph), int(n),
                                       lambda n, t: print("\r\t\t🏃 Run #", n + 1, "took", t, "ms.", end="",
                                                          flush=True),
                                       lambda r: print("\r\t\t⌛ Timings (ms): "
                                                       "[o] {avg} | [+] {fastest} | [-] {slowest}".format(**r)))
                viewable_result = str(timeit_result['return'])
                if len(viewable_result) > 1000:
                    viewable_result = viewable_result.splitlines()[0] + " (...OUTPUT HAS BEEN TRUNCATED!)"
                print("\t\t∑ Result:", viewable_result)
                results[file_name][backend][method] = timeit_result
        print()
    methods = ""
    for m in passed_values.methods:
        methods += m.ljust(26)
    print("Timing tables:")
    for file_name in results:
        print(file_name.ljust(25), '/', methods)
        for be in results[file_name]:
            print(be.ljust(26), end='| ')
            for method in results[file_name][be]:
                print(str(round(results[file_name][be][method]['avg'], 3)).ljust(25), end=' ')
            print()
        print()
    return results


if __name__ == "__main__":
    run(sys.argv[1:])
