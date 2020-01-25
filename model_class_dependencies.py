"""
Parse project files and build a dependency diagram between Django models,
including class inheritance and foreign key/m2m/121 relationships.
"""
import argparse
import logging
import re
from dataclasses import dataclass
from typing import (
    Dict,
    List,
    Tuple,
)

log = logging.getLogger(__name__)

DIRECTORY_BLACKLIST = [
    '__pycache__',
    '.git',
    '.idea',
    'env',
    'migrations',
]


@dataclass
class Field:
    name: str
    type: str
    args: List
    kwargs: Dict


@dataclass
class Model:
    name: str
    class_dependencies: List[str]
    fields: List[Field]
    abstract: bool = False

    def foreign_key_fields(self) -> List[Field]:
        return [x for x in self.fields if x.type == 'models.ForeignKey']

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
    print(f)
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


def parse_models(text: str) -> List[Model]:
    models = []
    matches = MODEL_REGEX.findall(text)
    for m in matches:
        model_name = m[0]
        class_dependencies = [x.strip() for x in m[1].split(',')]
        fields = parse_fields(m[2])
        abstract = ABSTRACT_MODEL_REGEX.match(m[2]) is not None
        models.append(
            Model(
                name=model_name,
                class_dependencies=class_dependencies,
                fields=fields,
                abstract=abstract
            ))
    return models


def _build_model_dictionary(models: List[Model]) -> Dict[str, Model]:
    d = {}
    for model in models:
        d[model.name] = model

    return d


def build_model_references(models: List[Model]):
    as_dict = _build_model_dictionary(models)

    for model in models:
        for dep in model.class_dependencies:
            if dep in as_dict:
                model.fields += as_dict[dep].fields


def _parse_args():
    parser = argparse.ArgumentParser()
    return parser.parse_args()


def main(clargs):
    # TODO
    pass


if __name__ == '__main__':
    _args = _parse_args()
    main(_args)
