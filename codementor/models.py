from decimal import Decimal

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from enum import Enum
from enumfields import EnumField


class Continent(Enum):
    AFRICA = 'Africa'
    ANTARCTICA = 'Antarctica'
    ASIA = 'Asia'
    AUSTRALIA = 'Australia'
    EUROPE = 'Europe'
    NORTH_AMERICA = 'North America'
    SOUTH_AMERICA = 'South America'
    UNKNOWN = 'Unknown'


class Gender(Enum):
    AGENDER = 'Agender'
    CIS_FEMALE = 'Cis Female'
    CIS_MALE = 'Cis Male'
    TRANS_FEMALE = 'Trans Female'
    TRANS_MALE = 'Trans Male'
    UNKNOWN = 'Unknown'


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
    username = models.CharField(max_length=100, blank=True, null=True)
    # Add client timezone and other info from client page?
    started_at = models.DateTimeField(null=True, blank=True)
    continent = EnumField(Continent, max_length=20, default=Continent.UNKNOWN)
    gender = EnumField(Gender, max_length=20, default=Gender.UNKNOWN)
    population_groups = models.ManyToManyField(PopulationGroup, blank=True, default=None)

    class Meta:
        ordering = ['name']

    @property
    def population_group_list(self):
        population_group_names = []
        for population_group in self.population_groups.all():
            population_group_names.append(population_group.name.value)
        return ', '.join(population_group_names)

    def user_external_link(self):
        return ('<a href="%s%s" target="_blank">%s</a>'
                % (settings.SOURCE_URL, self.username, self.username))

    user_external_link.allow_tags = True

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


class PayoutMethod(Enum):
    PAYPAL = 'PayPal'


class Payout(models.Model):
    date = models.DateTimeField()
    method = EnumField(PayoutMethod, default=PayoutMethod.PAYPAL)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0'))

    class Meta:
        ordering = ['-date']

    def payments_link(self):
        return ('<a href="%s?payout__id__exact=%s" target="_blank">Payments</a>'
                % (reverse('admin:codementor_payment_changelist'), self.pk))

    payments_link.allow_tags = True

    def __str__(self):
        return '%s (%s)' % (self.amount, self.date.date())


class Session(models.Model):
    session_id = models.CharField(max_length=12)
    client = models.ForeignKey(Client, related_name='sessions')
    started_at = models.DateTimeField()
    length = models.IntegerField(null=True, blank=True)  # in minutes
    review = models.OneToOneField(Review, null=True, blank=True)

    class Meta:
        ordering = ['-started_at']

    def session_external_link(self):
        return ('<a href="%s#/finished-sessions/%s" target="_blank">%s</a>'
                % (settings.SOURCE_URL, self.session_id, self.session_id))

    session_external_link.allow_tags = True

    def __str__(self):
        return '%s - %s (%s)' % (self.client, self.length, self.started_at)


class PaymentType(Enum):
    SESSION = 'Session'
    OFFLINE_HELP = 'Offline Help'
    MONTHLY = 'Codementor Monthly'


class Payment(models.Model):
    client = models.ForeignKey(Client, related_name='payments')
    payout = models.ForeignKey(Payout, null=True, blank=True, related_name='payments')
    type = EnumField(PaymentType, max_length=30, default=PaymentType.SESSION)
    date = models.DateTimeField()
    session = models.OneToOneField(Session, null=True, blank=True)
    free_preview = models.BooleanField(default=False)
    earnings = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['-date']

    def payout_link(self):
        return ('<a href="%s" target="_blank">Payout</a>'
                % (reverse('admin:codementor_payout_change', args=(self.payout.pk,))))

    payout_link.allow_tags = True

    def session_link(self):
        if not self.session_id:
            return ''
        return ('<a href="%s" target="_blank">Session</a>'
                % (reverse('admin:codementor_session_change', args=(self.session.pk,))))

    session_link.allow_tags = True

    def __str__(self):
        return '%s (%s) - %s' % (self.earnings, self.date, self.client)
