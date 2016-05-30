from collections import OrderedDict
import pytz

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Avg, Sum
from django.shortcuts import render

from codementor import models as codementor_models


DATE_FORMAT = "%Y-%m-%d"
TIMEZONE = pytz.timezone(settings.LOCAL_TIME_ZONE)


@login_required
def payout_history(request):
    payouts = codementor_models.Payout.objects.all().order_by('date')
    data = {}
    if payouts:
        payout_values = payouts.values_list('date', 'amount', 'total_earnings')

        amounts = []
        earnings = []
        for [date, amount, earning] in payout_values:
            date_str = date.astimezone(TIMEZONE).strftime(DATE_FORMAT)
            amounts.append([date_str, float(amount)])
            earnings.append([date_str, float(earning)])

        data = {
            'amounts': amounts,
            'earnings': earnings
        }
    return JsonResponse(data)


@login_required
def payment_history(request):
    payments = codementor_models.Payment.objects.all().order_by('date')
    data = {}
    if payments:
        payment_values = payments.values_list('date').annotate(total_earnings=Sum('earnings'))
        # Payments don't have a specific time, so we converting to timezone after grouping works
        data = {
            'payments': [[d.astimezone(TIMEZONE).strftime(DATE_FORMAT), float(t)]
                         for [d, t] in payment_values],
        }
    return JsonResponse(data)


def _format_hours_worked_row(work_date, minutes):
    total_hours = round(minutes / 60.0, 1)
    return [work_date.astimezone(TIMEZONE).strftime(DATE_FORMAT), total_hours]


@login_required
def hours_worked(request):
    sessions = codementor_models.Session.objects.all().order_by('started_at')
    data = {}
    if sessions:
        payment_values = sessions.values_list('started_at').annotate(minutes=Sum('length'))

        hours = []
        last_date = None
        total_minutes = 0
        for [started_at, minutes] in payment_values:
            started_date = started_at.astimezone(TIMEZONE)
            if last_date and last_date.date() != started_date.date():
                if last_date:
                    hours.append(_format_hours_worked_row(last_date, total_minutes))
                total_minutes = 0
            if minutes:
                total_minutes += minutes
            last_date = started_date
        if total_minutes:
            hours.append(_format_hours_worked_row(last_date, total_minutes))

        data = {
            'hours': hours,
        }
    return JsonResponse(data)


@login_required
def session_lengths(request):
    sessions = codementor_models.Session.objects.all().order_by('length')
    data = {}
    if sessions:
        # Bucket by 15 minute increments
        bucket_size = 15

        buckets = OrderedDict()

        bucket_min = 0
        bucket_max = 15
        session_count = 0
        for session in sessions:
            if session.length > bucket_max:
                buckets[bucket_min] = session_count
                session_count = 0
                bucket_min += bucket_size
                bucket_max += bucket_size
            else:
                session_count += 1

        sessions = []
        for key, value in buckets.iteritems():
            # sessions.append(['%s-%s' % (key, key+bucket_size), value])
            sessions.append([key, value])

        data = {
            'sessions': sessions,
        }
    return JsonResponse(data)


@login_required
def statistics(request):
    payouts = codementor_models.Payout.objects.all()
    total_payouts = payouts.count()
    payouts_by_total_earnings = payouts.order_by('-total_earnings')

    payments = codementor_models.Payment.objects.all()
    number_of_payments = payments.count()
    pending_total = payments.filter(payout__isnull=True).aggregate(Sum('earnings'))['earnings__sum']
    session_payments = payments.filter(type=codementor_models.PaymentType.SESSION)
    offline_payments = payments.filter(type=codementor_models.PaymentType.OFFLINE_HELP)
    monthly_payments = payments.filter(type=codementor_models.PaymentType.MONTHLY)

    sessions = codementor_models.Session.objects.all()

    total_hours_worked = (sessions.aggregate(Sum('length'))['length__sum'])/60,

    graph_types = [
        ['payout_history', 'Payout History'],
        ['payment_history', 'Payment History'],
        ['hours_worked', 'Hours Worked'],
        ['session_lengths', 'Session Lengths'],
    ]

    context = {
        'timezone': TIMEZONE,
        'total_payouts': total_payouts,
        'payout_total': payouts.aggregate(Sum('amount'))['amount__sum'],
        'earnings_total': payouts.aggregate(Sum('total_earnings'))['total_earnings__sum'],
        'average_payout': payouts.aggregate(Avg('amount'))['amount__avg'],
        'first_payout': payouts[total_payouts - 1],
        'last_payout': payouts[0],
        'highest_payout': payouts_by_total_earnings[0],
        'lowest_payout': payouts_by_total_earnings[total_payouts - 1],
        'number_of_payments': number_of_payments,
        'number_of_sessions': sessions.count(),
        'session_total': session_payments.aggregate(Sum('earnings'))['earnings__sum'],
        'offline_payment_total': offline_payments.aggregate(Sum('earnings'))['earnings__sum'],
        'monthly_payment_total': monthly_payments.aggregate(Sum('earnings'))['earnings__sum'],
        'average_payment': payments.aggregate(Avg('earnings'))['earnings__avg'],
        'total_session_length': int(round((sessions.aggregate(Sum('length'))['length__sum']) / 60)),
        'average_session_length': int(round(sessions.aggregate(Avg('length'))['length__avg'])),
        'hours_worked': total_hours_worked,
        'sessions_per_client': (sessions.count()/codementor_models.Client.objects.count()),
        'pending_total': pending_total,
        'graph_types': graph_types
    }

    return render(request, 'codementor/statistics.html', context)
