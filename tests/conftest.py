import pytest

from grapresso.backend.file import PickleFileBackend
from grapresso.backend.memory import InMemoryBackend, Trait
from grapresso_cli.importer.mmi_importer import MmiImporter

ALL_BACKENDS = ('InMemory-OptimizeMemory', 'InMemory-OptimizePerformance', 'PickleFile')
ENABLED_BACKENDS = ('InMemory-OptimizePerformance', 'InMemory-OptimizeMemory')


@pytest.fixture(params=ENABLED_BACKENDS)
def create_backend(request, tmp_path):
    def _create_backend():
        return {'InMemory-OptimizeMemory': InMemoryBackend(Trait.OPTIMIZE_MEMORY),
                'InMemory-OptimizePerformance': InMemoryBackend(Trait.OPTIMIZE_PERFORMANCE),
                'PickleFile': PickleFileBackend(str(tmp_path))}[request.param]

    return _create_backend


@pytest.fixture
def importer():
    return MmiImporter("../grapresso_cli/res/example-graphs/")


@pytest.fixture
def create_graph(importer, create_backend):
    def _graph(name, directed=False):
        return importer.read_graph(create_backend(), name, directed)

    return _graph