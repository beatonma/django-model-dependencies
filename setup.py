"""

"""

import logging

from setuptools import setup

log = logging.getLogger(__name__)


setup(
    name='djmodgraph',
    version='0.1',
    scripts=[
        'model_class_dependencies.py',
    ],
    install_requires=[
        'matplotlib>=3.1.2',
        'networkx>=2.4',
    ],
    test_requires=[
        'nose>=1.3.7',
    ],
    url='https://github.com/beatonma/django-model-dependencies',
    entry_points={
        'console_scripts': [
            'djmodgraph = model_class_dependencies:main',
        ],
    },
)
