"""

"""

import logging

from django.db import models

from repository.models.mixins import (
    BaseModel,
    PeriodMixin,
    PersonMixin,
)

log = logging.getLogger(__name__)


HOUSE_OF_COMMONS = 'Commons'
HOUSE_OF_LORDS = 'Lords'


class House(BaseModel):
    name = models.CharField(
        max_length=16,
        unique=True,
    )

    def __str__(self):
        return self.name


class HouseMembership(PersonMixin, PeriodMixin, BaseModel):
    house = models.ForeignKey(
        'House',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'{self.house}: {self.person}'

    class Meta:
        unique_together = [
            ['start', 'house', 'person'],
        ]
