from decimal import Decimal

from django.db import models
from django_enumfield import enum


class ContinentType(enum.Enum):
    AFRICA = 0
    ANTARCTICA = 1
    ASIA = 2
    AUSTRALIA = 3
    EUROPE = 4
    NORTH_AMERICA = 5
    SOUTH_AMERICA = 6


class GenderType(enum.Enum):
    CIS_FEMALE = 0
    CIS_MALE = 1
    TRANS_FEMALE = 2
    TRANS_MALE = 3
    AGENDER = 4


class RaceType(enum.Enum):
    AMERICAN_NATIVE = 0
    AUSTRALIAN_NATIVE = 1
    BLACK = 2
    EAST_ASIAN = 3
    SOUTH_ASIAN = 4
    WHITE = 5


class Race(models.Model):
    name = enum.EnumField(RaceType, default=RaceType.WHITE)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return RaceType.get(self.name).label


class Client(models.Model):
    name = models.CharField(max_length=100)
    started_at = models.DateTimeField(null=True, blank=True)
    continent = enum.EnumField(ContinentType, null=True, blank=True, default=None)
    gender = enum.EnumField(GenderType, null=True, blank=True, default=None)
    races = models.ManyToManyField(Race, blank=True, default=None)

    class Meta:
        ordering = ['name']

    @property
    def race_list(self):
        race_names = []
        for race in self.races.values_list('name', flat=True):
            race_names.append(RaceType.get(race).label)
        return ', '.join(race_names)

    def __str__(self):
        return self.name


class Review(models.Model):
    reviewer = models.ForeignKey(Client, related_name='reviews')
    date = models.DateTimeField()
    content = models.TextField()

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.content


class PayoutMethod(enum.Enum):
    PAYPAL = 0

    labels = {
        PAYPAL: 'PayPal',
    }


class Payout(models.Model):
    date = models.DateTimeField()
    method = enum.EnumField(PayoutMethod, default=PayoutMethod.PAYPAL)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return '%s (%s)' % (self.amount, self.date.date())


class Session(models.Model):
    client = models.ForeignKey(Client, related_name='sessions')
    started_at = models.DateTimeField()
    length = models.IntegerField(null=True, blank=True)  # in minutes
    review = models.OneToOneField(Review, null=True, blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return '%s (%s)' % (self.client, self.length)


class PaymentType(enum.Enum):
    SESSION = 0
    OFFLINE_HELP = 1
    MONTHLY = 2

    labels = {
        SESSION: 'Session',
        OFFLINE_HELP: 'Offline Help',
        MONTHLY: 'Codementor Monthly',
    }


class Payment(models.Model):
    client = models.ForeignKey(Client, related_name='payments')
    payout = models.ForeignKey(Payout, null=True, blank=True, related_name='payments')
    type = enum.EnumField(PaymentType, default=PaymentType.SESSION)
    date = models.DateTimeField()
    session = models.OneToOneField(Session, null=True, blank=True)
    free_preview = models.BooleanField(default=False)
    earnings = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return '%s (%s) - %s - %s' % (self.earnings, self.length,
                                      self.date, self.client)
