"""

"""

import logging

from django.db import models

from repository.models.mixins import BaseModel

log = logging.getLogger(__name__)


class Town(BaseModel):
    name = models.CharField(max_length=64)
    country = models.ForeignKey(
        'Country',
        on_delete=models.SET_NULL,
        null=True
    )

    def __str__(self):
        return f'{self.name}, {self.country}'

    class Meta:
        unique_together = [
            ['name', 'country'],
        ]


class Country(BaseModel):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Countries'
