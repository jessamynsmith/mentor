from django.db.models import Sum

from codementor import models as codementor_models


def format_status():
    separator = '------------------------------'
    payments = codementor_models.Payment.objects.all()
    pending_total = payments.filter(payout__isnull=True).aggregate(Sum('earnings'))['earnings__sum']
    payments_to_date = 'Payments to date: $%s' % pending_total
    weekly_rating = codementor_models.WeeklyRating.objects.all().order_by('-week_end').first()
    status = '\n'.join(['', separator, payments_to_date, str(weekly_rating), separator])
    return status
