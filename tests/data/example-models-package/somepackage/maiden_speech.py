"""

"""

import logging

from django.db import models

from repository.models.mixins import (
    BaseModel,
    PersonMixin,
)

log = logging.getLogger(__name__)


class MaidenSpeech(PersonMixin, BaseModel):
    date = models.DateField()
    house = models.ForeignKey(
        'House',
        on_delete=models.CASCADE,
    )
    subject = models.CharField(
        max_length=512,
        blank=True,
        null=True,
    )
    hansard = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        help_text='Hansard ID',
    )

    def __str__(self):
        return f'{self.person}: {self.house}'

    class Meta:
        verbose_name_plural = 'Maiden Speeches'
