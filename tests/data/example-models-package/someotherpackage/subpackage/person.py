import logging
from typing import Optional

from django.db import models

from repository.models.houses import (
    HOUSE_OF_COMMONS,
    HOUSE_OF_LORDS,
)
from repository.models.mixins import (
    BaseModel,
    ParliamentDotUkMixin,
    TheyWorkForYouMixin,
)
from repository.models.util import time as timeutil

NAME_MAX_LENGTH = 128

log = logging.getLogger(__name__)


class Person(
    ParliamentDotUkMixin,
    TheyWorkForYouMixin,
    BaseModel,
):
    name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        help_text='Canonical name for this person.',
    )
    given_name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        help_text='First name',
        null=True,
        blank=True,
    )
    family_name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        help_text='Last name',
        null=True,
        blank=True,
    )
    additional_name = models.CharField(
        max_length=NAME_MAX_LENGTH,
        help_text='Middle name(s)',
        blank=True,
        null=True,
    )

    full_title = models.CharField(
        max_length=NAME_MAX_LENGTH,
        help_text='Official name with honorifics.',
        blank=True,
        null=True,
    )

    gender = models.CharField(
        max_length=16,
        default=None,
        null=True,
        blank=True,
    )

    date_of_birth = models.DateField(
        default=None,
        null=True,
        blank=True,
    )
    date_of_death = models.DateField(
        default=None,
        null=True,
        blank=True,
    )

    town_of_birth = models.ForeignKey(
        'Town',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    country_of_birth = models.ForeignKey(
        'Country',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    constituency = models.ForeignKey(
        'Constituency',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
    )

    party = models.ForeignKey(
        'Party',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='Current party membership. Historic memberships can be '
                  'retrieved via PartyAssociation model.',
    )

    house = models.ForeignKey(
        'House',
        on_delete=models.CASCADE
    )
    date_entered_house = models.DateField(
        default=None,
        null=True,
        blank=True,
    )
    date_left_house = models.DateField(
        default=None,
        null=True,
        blank=True,
    )
    active = models.BooleanField(
        help_text='Whether this person currently has a seat in parliament.',
    )

    @property
    def age(self) -> int:
        if self.date_of_death:
            return timeutil.years_between(self.date_of_birth, self.date_of_death)
        else:
            return timeutil.years_since(self.date_of_birth)

    @property
    def is_birthday(self) -> bool:
        return timeutil.is_anniversary(self.date_of_birth)

    @property
    def is_mp(self) -> bool:
        return self.active and self.house.name == HOUSE_OF_COMMONS

    @property
    def is_lord(self) -> bool:
        return self.active and self.house.name == HOUSE_OF_LORDS

    def __str__(self):
        return f'{self.name} [{self.parliamentdotuk}]'

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'People'
