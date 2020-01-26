"""
Parse project files and build a dependency diagram between Django models,
including class inheritance and foreign key/m2m/121 relationships.
"""
import argparse
import logging
import os
import re
from dataclasses import dataclass
from typing import (
    Dict,
    List,
    Tuple,
)

import matplotlib.pyplot as plt
import networkx as nx

log = logging.getLogger(__name__)
log.addHandler(logging.StreamHandler())
log.setLevel(logging.INFO)

DIRECTORY_BLACKLIST = [
    '__pycache__',
    '.git',
    '.idea',
    'env',
    'venv',
    'migrations',
    'static',
    'templates',
    'tests',
]


@dataclass
class Field:
    name: str
    type: str
    args: List
    kwargs: Dict


@dataclass
class PyClass:
    name: str
    class_dependencies: List[str]
    fields: List[Field]
    abstract: bool = False
    is_model = False

    def foreign_key_fields(self) -> List[Field]:
        if self.is_model:
            return [x for x in self.fields if x.type == 'models.ForeignKey']
        return []

    def fk_models(self) -> List[str]:
        return [x.args[0] for x in self.foreign_key_fields()]


FIELD_REGEX = re.compile(
    r'\s+([^\s]+) = ([^(]+?)\(([^)]*?)\)',
    re.DOTALL
)
ABSTRACT_MODEL_REGEX = re.compile(
    r'.*class Meta:.*abstract = True',
    re.DOTALL
)
MODEL_REGEX = re.compile(
    r'^class ([\S]+)\(([^)]*?)\):\n(.*?)(\Z|(?=^[\S]))',
    re.DOTALL | re.MULTILINE
)


def parse_field_params(text: str) -> Tuple[List, Dict]:
    args: List = []
    kwargs = {}
    for param in text.split(','):
        if param.strip() == '':
            continue

        if '=' in param:
            name, value = param.split('=')
            kwargs[name.strip(' \n\'"')] = value.strip(' \n\'"')
        else:
            args.append(param.strip(' \n\'"'))

    return args, kwargs


def parse_field(text: str) -> Field:
    match = FIELD_REGEX.match(text)
    field_args, field_kwargs = parse_field_params(match.group(3))
    f = Field(
        match.group(1),
        match.group(2),
        field_args,
        field_kwargs
    )
    return f


def parse_fields(text: str) -> List[Field]:
    fields = []

    matches = FIELD_REGEX.findall(text)
    for m in matches:
        field_args, field_kwargs = parse_field_params(m[2])
        fields.append(Field(
            m[0],
            m[1],
            field_args,
            field_kwargs
        ))

    return fields


def parse_classes(text: str) -> Dict[str, PyClass]:
    classes = {}
    matches = MODEL_REGEX.findall(text)
    for m in matches:
        model_name = m[0]
        class_dependencies = [x.strip() for x in m[1].split(',')]
        fields = parse_fields(m[2])
        abstract = ABSTRACT_MODEL_REGEX.match(m[2]) is not None
        classes[model_name] = PyClass(
            name=model_name,
            class_dependencies=class_dependencies,
            fields=fields,
            abstract=abstract
        )
    return classes


def filter_models(classes: Dict[str, PyClass], search_iter=2):
    for iteration in range(0, search_iter):
        # is_model status will 'trickle down' to models that are `search_iter`
        # subclasses away from models.Model
        for cls in classes.values():
            if cls.is_model:
                continue

            for dep in cls.class_dependencies:
                if dep == 'models.Model':
                    cls.is_model = True
                    break

                if dep in classes and classes[dep].is_model:
                    cls.is_model = True
                    break

    non_models = [c for c in classes.values() if not c.is_model]
    for c in non_models:
        del classes[c.name]


def inherit_mixin_fields(models: Dict[str, PyClass]):
    """Cross-reference models to check for subclasses that inherit fields from
    parent.
    """
    for model in models.values():
        for dep in model.class_dependencies:
            if dep in models:
                model.fields += models[dep].fields


def generate_graph(
        models: Dict[str, PyClass],
        abstract_enabled=True,
        concrete_enabled=True,
        fk_enabled=True,
        subclass_enabled=True,
) -> Tuple[nx.Graph, Dict, Dict]:
    graph = nx.MultiDiGraph(format='png', directed=True)

    # Classify nodes and add them to graph
    abstract_models = [models[a].name for a in models.keys() if models[a].abstract]
    concrete_models = [x.name for x in models.values() if x.name not in abstract_models]

    if abstract_enabled:
        graph.add_nodes_from(abstract_models)

    if concrete_enabled:
        graph.add_nodes_from(concrete_models)

    nodes = {
        'abstract': abstract_models,
        'concrete': concrete_models,
    }

    fk_relations = []
    subclass_relations = []

    # Classify edges and add them to graph
    for model in models.values():
        for fk in model.fk_models():
            fk_relations.append((model.name, fk))

        for dep in model.class_dependencies:
            subclass_relations.append((model.name, dep))

    if fk_enabled:
        graph.add_edges_from(fk_relations)
    if subclass_enabled:
        graph.add_edges_from(subclass_relations)

    edges = {
        'fk': fk_relations,
        'subclass': subclass_relations,
    }

    return graph, nodes, edges


def show_graph(
        graph: nx.Graph, nodes: Dict, edges: Dict,
        show=True,
        layout_fn=nx.circular_layout,
        saveas=None,
        abstract_enabled=True,
        concrete_enabled=True,
        fk_enabled=True,
        subclass_enabled=True,
):
    fig = plt.figure(1, figsize=(28, 28))
    ax = fig.add_subplot(1, 1, 1)
    ax.set_facecolor('#333333')

    layout = layout_fn(graph)

    if fk_enabled:
        nx.draw_networkx_edges(
            graph, layout,
            edgelist=edges.get('fk'),
            edge_color='#4f9bd1',
            alpha=.9,
            connectionstyle='arc3, rad=.2'
        )

    if subclass_enabled:
        nx.draw_networkx_edges(
            graph, layout,
            edgelist=edges.get('subclass'),
            edge_color='#d68bb6',
            alpha=.3,
            connectionstyle='arc3, rad=.05'
        )

    if concrete_enabled:
        nx.draw_networkx_nodes(
            graph, layout,
            nodelist=nodes.get('concrete'),
            node_color='#244461',
            node_shape='o',
            node_size=200,
            alpha=1.0,
        )

    if abstract_enabled:
        nx.draw_networkx_nodes(
            graph, layout,
            nodelist=nodes.get('abstract'),
            node_color='#555555',
            node_shape='o',
            node_size=200,
            alpha=.7,
        )

    nx.draw_networkx_labels(
        graph, layout,
        font_size=8,
        font_color='#eeeeee',
    )

    if saveas:
        plt.savefig(saveas)

    if show:
        plt.show()


def parse_classes_from_directory(directory: str) -> Dict[str, PyClass]:
    models = {}

    for cwd, dirs, files in os.walk(directory):
        for d in DIRECTORY_BLACKLIST:
            if d in dirs:
                dirs.remove(d)

        dotpy = [f for f in files if f.endswith('.py')]

        for filename in dotpy:
            filepath = os.path.join(cwd, filename)
            with open(filepath, 'r') as f:
                models.update(parse_classes(f.read()))

    return models


def _parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'cwd',
        type=str,
        default='.',
        help='Base project directory. PyClasss will be discovered in any '
             'subdirectory not included in DIRECTORY_BLACKLIST',
    )

    parser.add_argument(
        '--saveas',
        default=None,
    )

    parser.add_argument(
        '-nosubclass',
        dest='subclasses',
        default=True,
        action='store_false',
    )

    parser.add_argument(
        '-nofk',
        dest='fk',
        default=True,
        action='store_false',
    )

    parser.add_argument(
        '-noabstract',
        dest='abstract',
        default=True,
        action='store_false',
    )

    parser.add_argument(
        '-noconcrete',
        dest='concrete',
        default=True,
        action='store_false',
    )

    parser.add_argument(
        '-fkonly',
        default=False,
        action='store_true',
    )

    parser.add_argument(
        '-subclassonly',
        default=False,
        action='store_true',
    )

    parser.add_argument(
        '-noshow',
        dest='show',
        default=True,
        action='store_false',
    )

    parsed = parser.parse_args()

    if parsed.cwd == '.':
        parsed.cwd = os.getcwd()

    if parsed.fkonly:
        parsed.abstract = False
        parsed.subclasses = False

    if parsed.subclassonly:
        parsed.fk = False

    if not parsed.abstract:
        log.info('Abstract classes hidden')
    if not parsed.concrete:
        log.info('Concrete classes hidden')
    if not parsed.fk:
        log.info('Foreign Key relations hidden')
    if not parsed.subclasses:
        log.info('Subclass relations hidden')

    return parsed


def main(clargs):
    enabled_entities = {
        'fk_enabled': clargs.fk,
        'subclass_enabled': clargs.subclasses,
        'abstract_enabled': clargs.abstract,
        'concrete_enabled': clargs.concrete,
    }

    classes = parse_classes_from_directory(clargs.cwd)
    inherit_mixin_fields(classes)
    filter_models(classes)

    graph, nodes, edges = generate_graph(classes, **enabled_entities)

    show_graph(
        graph, nodes, edges,
        saveas=clargs.saveas,
        show=clargs.show,
        **enabled_entities,
    )


if __name__ == '__main__':
    _args = _parse_args()

    main(_args)
