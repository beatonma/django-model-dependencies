"""

"""

import logging
import os
from typing import Dict
from unittest import TestCase

from model_class_dependencies import (
    PyClass,
    generate_graph,
    _flatten,
    get_models_for_directory,
)

log = logging.getLogger(__name__)


class GraphGenerationTests(TestCase):
    def test_generate_graph(self):
        directory = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'tests/data/example-models-package'
        )

        classes: Dict[str, PyClass] = get_models_for_directory(directory)

        graph, nodes, edges = generate_graph(classes)

        all_nodes = _flatten(nodes.values())
        all_edges = _flatten(edges.values())

        for node in all_nodes:
            self.assertTrue(graph.has_node(node))

        for edge in all_edges:
            self.assertTrue(graph.has_edge(*edge))

    def test_generate_graph__with_for_models(self):
        directory = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'tests/data/example-models-package'
        )

        classes: Dict[str, PyClass] = get_models_for_directory(directory)

        graph, nodes, edges = generate_graph(
            classes,
            for_models=[
                'Party',
            ],
        )

        self.assertTrue(graph.has_node('Party'))
        self.assertTrue(graph.has_node('PartyAssociation'))
        self.assertTrue(graph.has_node('PartyTheme'))
        self.assertTrue(graph.has_node('Person'))
        self.assertTrue(graph.has_node('WikipediaMixin'))
        self.assertTrue(graph.has_node('ElectionNationalResult'))
        self.assertTrue(graph.has_node('BaseModel'))
        self.assertTrue(graph.has_edge('Person', 'Party'))

        self.assertFalse(graph.has_node('Constituency'))
        self.assertFalse(graph.has_node('DeclaredInterest'))
        self.assertFalse(graph.has_node('WebAddress'))

    def test_generate_graph__with_multiple_for_models(self):
        directory = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'tests/data/example-models-package'
        )

        classes: Dict[str, PyClass] = get_models_for_directory(directory)

        graph, nodes, edges = generate_graph(
            classes,
            for_models=[
                'Party',
                'Constituency',
            ],
        )

        self.assertTrue(graph.has_node('Party'))
        self.assertTrue(graph.has_node('PartyAssociation'))
        self.assertTrue(graph.has_node('PartyTheme'))
        self.assertTrue(graph.has_node('Person'))
        self.assertTrue(graph.has_node('WikipediaMixin'))
        self.assertTrue(graph.has_node('ElectionNationalResult'))
        self.assertTrue(graph.has_node('BaseModel'))

        self.assertTrue(graph.has_node('Constituency'))
        self.assertTrue(graph.has_node('ConstituencyResult'))
        self.assertTrue(graph.has_edge('Person', 'Constituency'))

        self.assertFalse(graph.has_node('DeclaredInterest'))
        self.assertFalse(graph.has_node('WebAddress'))
