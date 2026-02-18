from django.db import models

from dashboard.models import BasePairStats


class PairStats(BasePairStats):

    pair = models.CharField(max_length=32)
    refdate = models.DateField()

    class Meta:
        unique_together = ['pair', 'refdate']
