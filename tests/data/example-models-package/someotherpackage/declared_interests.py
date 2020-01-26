from django.db import models

from repository.models.mixins import (
    BaseModel,
    PersonMixin,
    ParliamentDotUkMixin,
)


class DeclaredInterestCategory(ParliamentDotUkMixin, BaseModel):
    name = models.CharField(max_length=512)

    def __str__(self):
        return self.name


class DeclaredInterest(ParliamentDotUkMixin, PersonMixin, BaseModel):
    """Declared investments/involvements/relationships that a person has with
    organisations that could potentially influence their work in Parliament."""
    category = models.ForeignKey(
        'DeclaredInterestCategory',
        on_delete=models.CASCADE
    )
    description = models.CharField(max_length=1024)

    created = models.DateField(blank=True, null=True)
    amended = models.DateField(blank=True, null=True)
    deleted = models.DateField(blank=True, null=True)
    registered_late = models.BooleanField()

    def __str__(self):
        return f'{self.person}: {self.description}'
