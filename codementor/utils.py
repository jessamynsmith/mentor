from decimal import Decimal, ROUND_DOWN

from django.db.models import Sum

from codementor import models as codementor_models


def format_status():
    separator = '------------------------------'
    payments = codementor_models.Payment.objects.all()
    pending_total = payments.filter(payout__isnull=True).aggregate(Sum('earnings'))['earnings__sum']
    if pending_total is None:
        pending_total = Decimal('0')
    payments_to_date = 'Payments to date: ${}'.format(pending_total)
    weekly_rating = codementor_models.WeeklyRating.objects.all().order_by('-week_end').first()
    payment_increase = pending_total * Decimal("0.025")
    payment_increase = payment_increase.quantize(Decimal('.01'), rounding=ROUND_DOWN)
    amount_gained = 'Amount gained from next level: ${}'.format(payment_increase)
    status = '\n'.join([separator, payments_to_date, str(weekly_rating), amount_gained, separator])
    return status
