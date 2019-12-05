import grapresso_cli.mmi_cli as cli


class TestCLI:
    def test_cli(self):
        results = cli.run("G_1_2.mmiw G_1_20.mmiw --symmetric "
                          "--backends memory --methods prim kruskal".split())
        assert round(results['G_1_2.mmiw']['memory']['prim']['return'], 3) == 286.711
        assert round(results['G_1_2.mmiw']['memory']['kruskal']['return'], 3) == 286.711
