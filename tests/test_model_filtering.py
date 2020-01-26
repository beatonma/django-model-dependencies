"""

"""

import logging
import os
from typing import Dict
from unittest import TestCase

from model_class_dependencies import (
    PyClass,
    filter_models,
    parse_classes_from_directory,
)

log = logging.getLogger(__name__)


class ModelFilteringTests(TestCase):
    """Tests for ensuring that models are filtered from classes correctly."""

    def test_filter_models(self):
        directory = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'tests/data/example-models-package/someotherpackage/'
        )
        self.assertTrue(os.path.exists(directory))

        expected_models = [
            'BaseModel',
            'BasePost',
            'BasePostMember',
            'ContestedElection',
            'DeclaredInterest',
            'DeclaredInterestCategory',
            'Election',
            'ElectionNationalResult',
            'ElectionType',
            'GovernmentPost',
            'GovernmentPostMember',
            'OppositionPost',
            'OppositionPostMember',
            'ParliamentDotUkMixin',
            'ParliamentaryPost',
            'ParliamentaryPostMember',
            'ParliamentarySession',
            'Party',
            'PartyAssociation',
            'PartyTheme',
            'PeriodMixin',
            'Person',
            'PersonMixin',
            'SubjectOfInterest',
            'SubjectOfInterestCategory',
            'TheyWorkForYouMixin',
            'WikipediaMixin',
        ]

        classes: Dict[str, PyClass] = parse_classes_from_directory(directory)

        filter_models(classes, search_iter=2)

        actual_models = list(classes.keys())

        self.assertCountEqual(
            expected_models,
            actual_models
        )
