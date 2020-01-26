"""

"""

import logging
import os
from typing import Dict
from unittest import TestCase

from model_class_dependencies import (
    parse_classes_from_directory,
    PyClass,
)

mpl_logger = logging.getLogger('matplotlib')
mpl_logger.setLevel(logging.WARNING)
log = logging.getLogger(__name__)


class FilesystemDiscoveryTests(TestCase):
    """Tests to ensure classes are found correctly in the filesystem."""

    def test_parse_classes_from_directory(self):
        expected_classes = [
            'CommitteeChair',
            'CommitteeMember',
            'Committee',
            'Constituency',
            'ConstituencyBoundary',
            'ConstituencyResult',
            'ContestedElection',
            'Country',
            'DeclaredInterestCategory',
            'DeclaredInterest',
            'ElectionNationalResult',
            'ElectionType',
            'Election',
            'ExperienceCategory',
            'Experience',
            'GovernmentPostMember',
            'GovernmentPost',
            'HouseMembership',
            'House',
            'MaidenSpeech',
            'OppositionPostMember',
            'OppositionPost',
            'ParliamentaryPostMember',
            'ParliamentaryPost',
            'ParliamentarySession',
            'Party',
            'PartyAssociation',
            'PartyTheme',
            'Person',
            'PhysicalAddress',
            'SubjectOfInterestCategory',
            'SubjectOfInterest',
            'Town',
            'UnlinkedConstituency',
            'WebAddress',

            'BaseModel',
            'PersonMixin',
            'PeriodMixin',
            'ParliamentDotUkMixin',
            'TheyWorkForYouMixin',
            'WikipediaMixin',

            'BasePost',
            'BasePostMember',

            'SomeNonModel',  # Should be detected as a class but filtered by filter_models() later
        ]

        directory = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'tests/data/example-models-package'
        )

        self.assertTrue(os.path.exists(directory))
        classes: Dict[str, PyClass] = parse_classes_from_directory(directory)

        actual_classes = list(classes.keys())

        self.assertCountEqual(
            expected_classes,
            actual_classes
        )
