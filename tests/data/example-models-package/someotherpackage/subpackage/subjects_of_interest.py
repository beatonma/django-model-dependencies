"""

"""

import logging

from django.db import models

from repository.models.mixins import (
    PersonMixin,
    BaseModel,
)

log = logging.getLogger(__name__)


class SubjectOfInterestCategory(BaseModel):
    title = models.CharField(max_length=128)


class SubjectOfInterest(PersonMixin, BaseModel):
    """A subject that a person is particularly interested in.
    This is distinct from """
    category = models.ForeignKey(
        'SubjectOfInterestCategory',
        on_delete=models.CASCADE
    )

    subject = models.CharField(max_length=512)
