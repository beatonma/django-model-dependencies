import datetime
from typing import Optional

from django.db import models
from django.db.models import Q

from repository.models.mixins import (
    PeriodMixin,
    ParliamentDotUkMixin,
    BaseModel,
)


class Constituency(ParliamentDotUkMixin, PeriodMixin, BaseModel):
    name = models.CharField(max_length=64)
    mp = models.OneToOneField(
        'Person',
        on_delete=models.SET_NULL,
        related_name='+',
        null=True,
        help_text='Current representative',
    )

    ordinance_survey_name = models.CharField(max_length=64, null=True, blank=True)
    gss_code = models.CharField(
        max_length=12, null=True, blank=True,
        help_text='Government Statistical Service ID')
    constituency_type = models.CharField(
        max_length=10, null=True,
        choices=[
            ('county', 'County'),
            ('borough', 'Borough'),
        ],
        help_text='Borough, county...')

    @property
    def is_extant(self) -> bool:
        """Return True if this constituency still exists.
        i.e. It has not undergone boundary/name changes and is represented by
        an MP in parliament."""
        return self.end is None

    def __str__(self):
        return f'{self.name}: {self.mp if self.mp else "No MP"}'

    class Meta:
        verbose_name_plural = 'Constituencies'


class ConstituencyResult(PeriodMixin, BaseModel):
    election = models.ForeignKey(
        'Election',
        on_delete=models.CASCADE,
    )

    mp = models.ForeignKey(
        'Person',
        on_delete=models.CASCADE,
    )

    constituency = models.ForeignKey(
        'Constituency',
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f'{self.election}: {self.constituency}'

    class Meta:
        unique_together = [
            ['election', 'constituency'],
            ['election', 'mp'],
        ]


class UnlinkedConstituency(BaseModel):
    """A placeholder for a constituency which is known by name only.

    Contested Elections data sometimes list a constituency for which we have
    no data. In those cases, create an UnlinkedConstituency which can be checked
    manually."""

    name = models.CharField(max_length=64)
    election = models.ForeignKey(
        'Election',
        on_delete=models.CASCADE,
    )

    mp = models.ForeignKey(
        'Person',
        on_delete=models.CASCADE,
    )

    constituency = models.ForeignKey(
        'Constituency',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='Constituency which this is supposed to refer to.'
    )

    def __str__(self):
        return self.name


class ConstituencyBoundary(BaseModel):
    constituency = models.OneToOneField(
        Constituency,
        on_delete=models.DO_NOTHING,
    )
    boundary = models.TextField(help_text='KML file content')

    def __str__(self):
        return self.constituency

    class Meta:
        verbose_name_plural = 'Constituency Boundaries'


def get_constituency_for_date(name: str, date: datetime.date) -> Optional[Constituency]:
    c = Constituency.objects.filter(name=name)
    count = c.count()

    # Simple cases
    if count == 0:
        return None

    elif count == 1:
        return c.first()

    # More complicated
    with_start = c.exclude(start=None).order_by('start')

    filtered_by_date = with_start.filter(
        Q(start__lte=date) & (Q(end__gt=date) | Q(end__isnull=True))
    )

    if filtered_by_date:
        # Result was found that matches the date requirement
        return filtered_by_date.first()

    if with_start.count() == 0:
        # No useful date, just return the first result.
        return c.first()

    earliest = with_start.first()
    if earliest.start > date:
        # Date is before earliest result -> return earliest available result
        return earliest

    # All else fails, return the latest available result.
    return with_start.last()


def get_current_constituency(name: str) -> Optional[Constituency]:
    return get_constituency_for_date(name, datetime.date.today())
