import pytest

from grapresso.backend.memory import InMemoryBackend, Trait
from grapresso.components.graph import BiGraph


class TestAlgorithmIntegration:
    """ This class performs integration tests.
    It proves that the modules work well together when using the graph algorithms.
    """

    def test_connected_components(self, create_graph):
        components = create_graph("big.mmi").count_connected_components()
        assert 222 == components

    def test_build_mst(self, create_graph, create_backend):
        mst_graph = BiGraph(create_backend())
        mst_result = create_graph("G_1_2.mmiw").build_mst(mst_graph)
        assert 286.711 == round(mst_result.costs, 3)

    @pytest.fixture(params=[BiGraph.perform_kruskal, BiGraph.perform_prim])
    def mst_alg(self, request):
        return request.param

    def test_prim_kruskal(self, create_graph, mst_alg):
        mst_weights = mst_alg(create_graph("G_1_2.mmiw"))
        assert 286.711 == round(mst_weights, 3)

        mst_weights = mst_alg(create_graph("G_1_20.mmiw"))
        assert 29.5493 == round(mst_weights, 4)

        mst_weights = mst_alg(create_graph("G_1_200.mmiw"))
        assert 3.0228 == round(mst_weights, 4)

        mst_weights = mst_alg(create_graph("G_10_20.mmiw"))
        assert 2775.44 == round(mst_weights, 2)

        mst_weights = mst_alg(create_graph("G_10_200.mmiw"))
        assert 301.552 == round(mst_weights, 3)

        mst_weights = mst_alg(create_graph("G_100_200.mmiw"))
        assert 27450.6 == round(mst_weights, 1)

    def test_nearest_neighbour(self, create_graph):
        for x in range(0, 10):
            tour = create_graph("K_10.mmiw").perform_nearest_neighbour_tour(x)
            assert tour.edges[-1].to_node == tour.start_node  # start and end node are the same
            assert tour.cost >= 38.41

        for x in range(0, 100):
            tour = create_graph("K_100.mmiw").perform_nearest_neighbour_tour(x)
            assert tour.edges[-1].to_node == tour.start_node  # start and end node are the same

    def test_double_tree(self, create_graph):
        tour = create_graph("K_10.mmiw").double_tree_tour()
        assert tour.edges[-1].to_node == tour.start_node  # start and end node are the same
        assert tour.cost >= 38.41

        tour = create_graph("K_100.mmiw").double_tree_tour()
        assert tour.edges[-1].to_node == tour.start_node  # start and end node are the same

    def test_full_enumeration(self, create_graph):
        tracker = create_graph("K_10.mmiw").enumerate()
        assert tracker.cheapest_tour.cost == 38.41

    def test_branch_and_bound(self, create_graph):
        cheapest_tour = create_graph("K_10.mmiw").enumerate_bnb()
        assert cheapest_tour.cost == 38.41

    def test_moore_bellman_ford(self, create_graph):
        start_node = 2
        target_node = 0
        graph = create_graph("paths1.mmiw", True)
        result = graph.perform_bellman_ford(start_node)
        assert 6 == result.dist_table[graph.node_by_name(target_node)].dist

        graph = create_graph("paths2.mmiw", True)
        result = graph.perform_bellman_ford(start_node)
        assert 2 == result.dist_table[graph.node_by_name(target_node)].dist

        graph = create_graph("paths3.mmiw", True)
        result = graph.perform_bellman_ford(start_node)
        assert result.is_cycle_detected

        graph = create_graph("negative-cycle.mmiw", True)
        result = graph.perform_bellman_ford(0)
        assert result.is_cycle_detected

        start_node = 0
        target_node = 1
        graph = create_graph("G_1_2.mmiw", True)
        result = graph.perform_bellman_ford(0)
        assert 5.54417 == round(result.dist_table[graph.node_by_name(1)].dist, 5)

        graph = create_graph("G_1_2.mmiw", False)
        result = graph.perform_bellman_ford(start_node)
        assert 2.36796 == round(result.dist_table[graph.node_by_name(target_node)].dist, 5)

    def test_dijkstra(self, create_graph):
        graph = create_graph("paths1.mmiw", True)
        table = graph.perform_dijkstra(2)
        assert 6 == table[graph.node_by_name(0)].dist

        graph = create_graph("paths2.mmiw", True)
        table = graph.perform_dijkstra(2)
        assert 2 == table[graph.node_by_name(0)].dist

        graph = create_graph("G_1_2.mmiw", True)
        table = graph.perform_dijkstra(0)
        assert 5.54417 == round(table[graph.node_by_name(1)].dist, 5)

        graph = create_graph("G_1_2.mmiw")
        table = graph.perform_dijkstra(0)
        assert 2.36796 == round(table[graph.node_by_name(1)].dist, 5)

    def test_edmonds_karp(self, create_graph):
        graph = create_graph("flow-small.mmic", True)
        flow = graph.perform_edmonds_karp(0, 3)
        assert flow.max_flow == 6.0

        graph = create_graph("flow.mmic", True)
        flow = graph.perform_edmonds_karp(0, 7)
        assert flow.max_flow == 4.0

        graph = create_graph("flow2.mmic", True)
        flow = graph.perform_edmonds_karp(0, 7)
        assert flow.max_flow == 5.0

        graph = create_graph("G_1_2.mmic", True)
        flow = graph.perform_edmonds_karp(0, 7)
        assert flow.max_flow == 0.73580156

    def test_cycle_cancelling(self, create_graph):
        graph = create_graph("negative-cycle.mmibwc", True)
        flow = graph.perform_cycle_cancelling()
        assert flow.cost == -4

        graph = create_graph("costminflow1.mmibwc", True)
        flow = graph.perform_cycle_cancelling()
        assert flow.cost == 3

        try:
            graph = create_graph("costminflow2-impossible.mmibwc", True)
            flow = graph.perform_cycle_cancelling()
        except ValueError as e:
            assert "No balanced flow" in str(e)

        graph = create_graph("costminflow3.mmibwc", True)
        flow = graph.perform_cycle_cancelling()
        assert flow.cost == 1537

        graph = create_graph("costminflow4.mmibwc", True)
        flow = graph.perform_cycle_cancelling()
        assert flow.cost == 0

    def test_successive_shortest_path(self, create_graph):
        graph = create_graph("negative-cycle.mmibwc", True)
        flow = graph.perform_successive_shortest_path()
        assert flow.cost == -4

        graph = create_graph("costminflow1.mmibwc", True)
        flow = graph.perform_successive_shortest_path()
        assert flow.cost == 3

        try:
            graph = create_graph("costminflow2-impossible.mmibwc", True)
            flow = graph.perform_successive_shortest_path()
        except ValueError as e:
            assert "No balanced flow" in str(e)

        graph = create_graph("costminflow3.mmibwc", True)
        flow = graph.perform_successive_shortest_path()
        assert flow.cost == 1537

        graph = create_graph("costminflow4.mmibwc", True)
        flow = graph.perform_successive_shortest_path()
        assert flow.cost == 0

    def test_matching(self, importer, create_backend):
        graph = importer.read_graph(create_backend(), "Matching_100_100.mmim", False)
        set_a = {i for i in range(importer.last_import_metainfo.matching_group_no)}
        set_b = {i for i in range(importer.last_import_metainfo.matching_group_no, len(graph))}
        assert len(graph.max_matchings(set_a, set_b)) == 100

        graph = importer.read_graph(create_backend(), "Matching2_100_100.mmim", False)
        set_a = {i for i in range(importer.last_import_metainfo.matching_group_no)}
        set_b = {i for i in range(importer.last_import_metainfo.matching_group_no, len(graph))}
        assert len(graph.max_matchings(set_a, set_b)) == 99
