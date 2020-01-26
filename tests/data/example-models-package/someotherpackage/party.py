from django.db import models
from django.db.models import DO_NOTHING

from repository.models.mixins import (
    WikipediaMixin,
    BaseModel,
    PeriodMixin,
)


class Party(WikipediaMixin, BaseModel):
    name = models.CharField(max_length=64, unique=True)
    short_name = models.CharField(
        max_length=16,
        unique=True,
        null=True,
        blank=True,
        default=None,
    )
    long_name = models.CharField(
        max_length=128,
        unique=True,
        null=True,
        blank=True,
        help_text='Official name',
        default=None,
    )
    homepage = models.URLField(null=True, blank=True)
    year_founded = models.PositiveSmallIntegerField(default=0)

    @property
    def mp_population(self) -> int:
        """Returns number of MPs associated with this party"""
        return self.objects.count()

    class Meta:
        verbose_name_plural = 'Parties'

    def __str__(self):
        return self.name


class PartyAssociation(PeriodMixin, BaseModel):
    """Allow tracking of people that have moved between different parties."""
    party = models.ForeignKey(
        'Party',
        on_delete=models.CASCADE,
    )

    person = models.ForeignKey(
        'Person',
        on_delete=models.CASCADE,
        related_name='parties',
    )

    def __str__(self):
        return f'{self.person}: {self.party}'

    class Meta:
        unique_together = [
            ['start', 'person'],
        ]


class PartyTheme(BaseModel):
    TEXT_COLOR_OPTIONS = [
        ('light', 'light'),
        ('dark', 'dark'),
    ]

    party = models.OneToOneField(
        Party,
        on_delete=DO_NOTHING,
        null=True,
        blank=True,
        related_name='theme',
    )

    primary_color = models.CharField(max_length=6, help_text='Hex color code')
    accent_color = models.CharField(max_length=6, help_text='Hex color code')
    primary_text_color = models.CharField(
        max_length=5,
        choices=TEXT_COLOR_OPTIONS,
        help_text='Color for text that overlays primary_color',
    )
    accent_text_color = models.CharField(
        max_length=5,
        choices=TEXT_COLOR_OPTIONS,
        help_text='Color for text that overlays accent_color',
    )

    def __str__(self):
        return f'Theme: {self.party}'
