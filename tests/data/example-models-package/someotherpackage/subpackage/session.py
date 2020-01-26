"""

"""

import logging

from repository.models.mixins import (
    PeriodMixin,
    BaseModel,
)

log = logging.getLogger(__name__)


class ParliamentarySession(PeriodMixin, BaseModel):
    """A legislative session, usually lasting about a year."""
    pass


class SomeNonModel(object):
    pass
