"""

"""

import logging

from django.db import models

from repository.models.mixins import (
    BaseModel,
    ParliamentDotUkMixin,
    PeriodMixin,
    PersonMixin,
)

log = logging.getLogger(__name__)


class BasePost(ParliamentDotUkMixin, BaseModel):
    name = models.CharField(max_length=512)
    hansard_name = models.CharField(
        max_length=512,
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class GovernmentPost(BasePost):
    pass


class ParliamentaryPost(BasePost):
    pass


class OppositionPost(BasePost):
    pass


class BasePostMember(PersonMixin, PeriodMixin, BaseModel):
    class Meta:
        abstract = True


class GovernmentPostMember(BasePostMember):
    post = models.ForeignKey(
        'GovernmentPost',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'{self.person}: {self.post}'


class ParliamentaryPostMember(BasePostMember):
    post = models.ForeignKey(
        'ParliamentaryPost',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'{self.person}: {self.post}'


class OppositionPostMember(BasePostMember):
    post = models.ForeignKey(
        'OppositionPost',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'{self.person}: {self.post}'
