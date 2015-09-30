from django.db import models
from django_enumfield import enum


class Client(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Review(models.Model):
    reviewer = models.ForeignKey(Client, related_name='reviews')
    date = models.DateField()
    content = models.TextField()

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return '%s (%s)' % (self.reviewer.name, self.date)


class PayoutMethod(enum.Enum):
    PAYPAL = 0

    labels = {
        PAYPAL: 'PayPal',
    }


class Payout(models.Model):
    date = models.DateField()
    method = enum.EnumField(PayoutMethod, default=PayoutMethod.PAYPAL)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['-date']

    @property
    def total_earnings(self):
        total_earnings = self.payments.all().aggregate(models.Sum('earnings'))
        return total_earnings['earnings__sum']

    def __str__(self):
        return '%s (%s)' % (self.amount, self.date)


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
    date = models.DateField()
    length = models.IntegerField(null=True, blank=True)  # in seconds
    free_preview = models.BooleanField(default=False)
    earnings = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['-date']

    def length_minutes(self):
        if not self.length:
            return PaymentType.get(self.type).label
        return '%s min' % int(round(self.length/60.0))

    def __str__(self):
        return '%s (%s) - %s - %s' % (self.earnings, self.length_minutes(),
                                          self.date, self.client)
