"""

"""

import logging

from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from repository.models.mixins import (
    BaseModel,
    PersonMixin,
)

log = logging.getLogger(__name__)


PHONE_NUMBER_REGION = 'GB'


class PhysicalAddress(PersonMixin, BaseModel):
    description = models.CharField(
        max_length=128,
        help_text='What kind of address is this? e.g Parliamentary, Constituency...'
    )
    address = models.CharField(max_length=512)
    postcode = models.CharField(max_length=10, null=True, blank=True)
    phone = PhoneNumberField(null=True, blank=True)
    fax = PhoneNumberField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return f'{self.person} {self.description}'


class WebAddress(PersonMixin, BaseModel):
    description = models.CharField(
        max_length=128,
        help_text='What kind of address is this? e.g Twitter, personal site...'
    )

    url = models.URLField()

    def __str__(self):
        return f'{self.person} {self.description}'
