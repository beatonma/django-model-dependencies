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

    def one_to_one_fields(self) -> List[Field]:
        if self.is_model:
            return [x for x in self.fields if x.type == 'models.OneToOneField']
        return []

    def many_to_many_fields(self) -> List[Field]:
        if self.is_model:
            return [x for x in self.fields if x.type == 'models.ManyToManyField']
        return []

    def foreign_key_models(self) -> List[str]:
        """Return the list of names of models that this model references by ForeignKey."""
        return [x.args[0] for x in self.foreign_key_fields()]

    def one_to_one_models(self) -> List[str]:
        """Return the list of names of models that this model references by OneToOneField."""
        return [x.args[0] for x in self.one_to_one_fields()]

    def many_to_many_models(self) -> List[str]:
        """Return the list of names of models that this model references by ManyToManyField."""
        return [x.args[0] for x in self.many_to_many_fields()]

    def related_models(self) -> List[str]:
        """Return the list of names of models that this model references by
        any of ForeignKey, OneToOneFIeld, ManyToManyField."""
        return self.foreign_key_models() + self.one_to_one_models() + self.many_to_many_models()


def _flatten(lst):
    return [item for sub in lst for item in sub]


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
        for_models=None,  # Prune any nodes/edges that are not connected to a model with this name.
        abstract_enabled=True,
        related_field_enabled=True,
        subclass_enabled=True,
) -> Tuple[nx.Graph, Dict, Dict]:
    def filter_edge_for_model(output_list: List, self_name: str, foreign_name: str):
        """If for_model is defined, only add the edge to output_list if it matches
        either self_name or foreign_name.
        If for_model is not defined then just add the edge."""
        if not for_models:
            # print('NOT FOR_MODELS')
            output_list.append((self_name, foreign_name))
        elif for_models and (self_name in for_models or foreign_name in for_models):
            # print(self_name, foreign_name, 'in', for_models)
            output_list.append((self_name, foreign_name))
        # else:
        #     print('X', self_name, foreign_name, 'not in', for_models)

    graph = nx.MultiDiGraph(format='png', directed=True)

    foreign_key_relations = []
    one_to_one_relations = []
    many_to_many_relations = []
    subclass_relations = []

    # Classify edges and add them to graph
    for model in models.values():
        for fk in model.foreign_key_models():
            filter_edge_for_model(foreign_key_relations, model.name, fk)
        for oto in model.one_to_one_models():
            filter_edge_for_model(one_to_one_relations, model.name, oto)
        for mtm in model.many_to_many_models():
            filter_edge_for_model(many_to_many_relations, model.name, mtm)

        for dep in model.class_dependencies:
            filter_edge_for_model(subclass_relations, model.name, dep)

    # Classify nodes and add them to graph
    abstract_models = [models[a].name for a in models.keys() if models[a].abstract]
    concrete_models = [x.name for x in models.values() if x.name not in abstract_models]

    if for_models:
        # Remove any nodes that are not connected by edges filtered by for_model
        filtered_edges = (foreign_key_relations + one_to_one_relations
                          + many_to_many_relations + subclass_relations)
        filtered_nodes = _flatten(filtered_edges)

        abstract_models = [m for m in abstract_models if m in filtered_nodes]
        concrete_models = [m for m in concrete_models if m in filtered_nodes]

    # Add nodes to graph
    if abstract_enabled:
        graph.add_nodes_from(abstract_models)

    graph.add_nodes_from(concrete_models)

    # Add edges to graph
    if related_field_enabled:
        graph.add_edges_from(foreign_key_relations + one_to_one_relations + many_to_many_relations)
    if subclass_enabled:
        graph.add_edges_from(subclass_relations)

    nodes = {
        'abstract': abstract_models,
        'concrete': concrete_models,
    }

    edges = {
        'foreignkey': foreign_key_relations,
        'onetoone': one_to_one_relations,
        'manytomany': many_to_many_relations,
        'subclass': subclass_relations,
    }

    return graph, nodes, edges


def show_graph(
        graph: nx.Graph, nodes: Dict, edges: Dict,
        show=True,
        layout_fn=nx.circular_layout,
        saveas=None,
        abstract_enabled=True,
        related_field_enabled=True,
        subclass_enabled=True,
):
    fig = plt.figure(1, figsize=(28, 28))
    ax = fig.add_subplot(1, 1, 1)
    ax.set_facecolor('#333333')

    layout = layout_fn(graph)

    if related_field_enabled:
        nx.draw_networkx_edges(
            graph, layout,
            edgelist=edges.get('foreignkey'),
            edge_color='#4f9bd1',
            alpha=.9,
            connectionstyle='arc3, rad=.2'
        )

        nx.draw_networkx_edges(
            graph, layout,
            edgelist=edges.get('onetoone'),
            edge_color='#9bd14f',
            alpha=.9,
            connectionstyle='arc3, rad=.2'
        )

        nx.draw_networkx_edges(
            graph, layout,
            edgelist=edges.get('manytomany'),
            edge_color='#d14f9b',
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

    if abstract_enabled:
        nx.draw_networkx_nodes(
            graph, layout,
            nodelist=nodes.get('abstract'),
            node_color='#555555',
            node_shape='o',
            node_size=200,
            alpha=.7,
        )

    nx.draw_networkx_nodes(
        graph, layout,
        nodelist=nodes.get('concrete'),
        node_color='#244461',
        node_shape='o',
        node_size=200,
        alpha=1.0,
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


def get_models_for_directory(directory: str) -> Dict[str, PyClass]:
    classes = parse_classes_from_directory(directory)
    filter_models(classes)
    inherit_mixin_fields(classes)
    return classes


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
        '-nofields',
        dest='related_fields',
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
        '-fieldsonly',
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

    parser.add_argument(
        '--models',
        default=None,
        nargs='+',
        help='List of model names that you are interested in. '
             'The resulting graph will only show these models and those '
             'that share a direct relationship with them (in either direction).',
    )

    parsed = parser.parse_args()

    if parsed.cwd == '.':
        parsed.cwd = os.getcwd()

    if parsed.fieldsonly:
        parsed.abstract = False
        parsed.subclasses = False

    if parsed.subclassonly:
        parsed.related_fields = False

    if not parsed.abstract:
        log.info('Abstract classes hidden')
    if not parsed.related_fields:
        log.info('Field relations (ForeignKey, OneToOneField, ManyToManyField) hidden')
    if not parsed.subclasses:
        log.info('Subclass relations hidden')

    return parsed


def main():
    clargs = _parse_args()

    enabled_entities = {
        'related_field_enabled': clargs.related_fields,
        'subclass_enabled': clargs.subclasses,
        'abstract_enabled': clargs.abstract,
    }

    models = get_models_for_directory(clargs.cwd)

    graph, nodes, edges = generate_graph(
        models,
        for_models=clargs.models,
        **enabled_entities,
    )

    show_graph(
        graph, nodes, edges,
        saveas=clargs.saveas,
        show=clargs.show,
        **enabled_entities,
    )


if __name__ == '__main__':
    main()
