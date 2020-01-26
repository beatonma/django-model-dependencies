"""

"""

import logging

from django.db import models

from repository.models.mixins import (
    BaseModel,
    ParliamentDotUkMixin,
    PersonMixin,
)

log = logging.getLogger(__name__)


class ElectionType(BaseModel):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


class Election(ParliamentDotUkMixin, BaseModel):
    name = models.CharField(
        max_length=128,
        unique=True,
    )
    date = models.DateField()
    election_type = models.ForeignKey(
        'ElectionType',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name


class ElectionNationalResult(ParliamentDotUkMixin, BaseModel):
    election = models.ForeignKey(
        'Election',
        on_delete=models.CASCADE,
    )

    winning_party = models.ForeignKey(
        'Party',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'{self.election}: {self.winning_party}'


class ContestedElection(PersonMixin, BaseModel):
    """Elections in which the person took part but did not win."""
    election = models.ForeignKey(
        'Election',
        on_delete=models.CASCADE,
    )

    constituency = models.ForeignKey(
        'Constituency',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'{self.election}: {self.constituency}'
