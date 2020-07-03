import grapresso_cli.mmi_cli as cli


class TestCLI:
    def test_cli(self):
        results = cli.run("G_1_2.mmiw G_1_20.mmiw --symmetric "
                          "--backends mem --methods 3*prim 3*kruskal".split())
        assert round(results['G_1_2.mmiw']['mem']['prim']['return'], 3) == 286.711
        assert round(results['G_1_2.mmiw']['mem']['kruskal']['return'], 3) == 286.711
