from decimal import Decimal

from django.db import models
from django_enumfield import enum
from enum import Enum
from enumfields import EnumField


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


class PopulationGroupType(Enum):
    # From Canadian Census definitions http://www12.statcan.ca/census-recensement/2006/ref/
    # rp-guides/visible_minority-minorites_visibles-eng.cfm
    # For persons living in private households on Indian reserves, Indian settlements and in remote
    # areas, data were collected using the 2006 Census Form 2D questionnaire.
    # Response categories in the population group question included 11 mark-in circles and
    # one write-in space. Respondents were asked 'Is this person:' and were instructed to mark more
    # than one of the following response categories, or to specify another group, if applicable:
    #     White
    #     Chinese
    #     South Asian (e.g., East Indian, Pakistani, Sri Lankan, etc.)
    #     Black
    #     Filipino
    #     Latin American
    #     Southeast Asian (e.g., Vietnamese, Cambodian, Malaysian, Laotian, etc.)
    #     Arab
    #     West Asian (e.g., Iranian, Afghan, etc.)
    #     Korean
    #     Japanese
    #     Other -- Specify

    INDIGENOUS = 'Indigenous'
    WHITE = 'White'
    CHINESE = 'Chinese'
    SOUTH_ASIAN = 'South Asian'
    BLACK = 'Black'
    FILIPINO = 'Filipino'
    LATIN_AMERICAN = 'Latin American'
    SOUTHEAST_ASIAN = 'Southeast Asian'
    ARAB = 'Arab'
    WEST_ASIAN = 'West Asian'
    KOREAN = 'Korean'
    JAPANESE = 'Japanese'
    OTHER = 'Other'


class PopulationGroup(models.Model):
    name = EnumField(PopulationGroupType, max_length=20)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name.value


class Client(models.Model):
    name = models.CharField(max_length=100)
    started_at = models.DateTimeField(null=True, blank=True)
    continent = enum.EnumField(ContinentType, null=True, blank=True, default=None)
    gender = enum.EnumField(GenderType, null=True, blank=True, default=None)
    population_groups = models.ManyToManyField(PopulationGroup, blank=True, default=None)

    class Meta:
        ordering = ['name']

    @property
    def population_group_list(self):
        population_group_names = []
        for population_group in self.population_groups.all():
            population_group_names.append(population_group.name.value)
        return ', '.join(population_group_names)

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
