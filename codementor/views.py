from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Avg, Sum
from django.shortcuts import render

from codementor import models as codementor_models


DATE_FORMAT = "%Y-%m-%d"


@login_required
def payout_history(request):
    payouts = codementor_models.Payout.objects.all().order_by('date')
    data = {}
    if payouts:
        payout_values = payouts.values_list('date', 'amount', 'total_earnings')

        amounts = []
        earnings = []
        for [date, amount, earning] in payout_values:
            date_str = date.strftime(DATE_FORMAT)
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
        data = {
            'payments': [[d.strftime(DATE_FORMAT), float(t)] for [d, t] in payment_values],
        }
    return JsonResponse(data)


@login_required
def hours_worked(request):
    payments = codementor_models.Payment.objects.all().order_by('date')
    data = {}
    if payments:
        payment_values = payments.values_list('date').annotate(total_minutes=Sum('length'))

        hours = []
        for [date, minutes] in payment_values:
            total_hours = 0
            if minutes:
                total_hours = round(minutes / 60.0, 1)
            hours.append([date.strftime(DATE_FORMAT), total_hours])

        data = {
            'hours': hours,
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
    sessions = payments.filter(type=codementor_models.PaymentType.SESSION)
    offline_payments = payments.filter(type=codementor_models.PaymentType.OFFLINE_HELP)
    monthly_payments = payments.filter(type=codementor_models.PaymentType.MONTHLY)

    graph_types = [
        ['payout_history', 'Payout History'],
        ['payment_history', 'Payment History'],
        ['hours_worked', 'Hours Worked']
    ]

    context = {
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
        'session_total': sessions.aggregate(Sum('earnings'))['earnings__sum'],
        'offline_payment_total': offline_payments.aggregate(Sum('earnings'))['earnings__sum'],
        'monthly_payment_total': monthly_payments.aggregate(Sum('earnings'))['earnings__sum'],
        'average_payment': payments.aggregate(Avg('earnings'))['earnings__avg'],
        'average_session_length': int(round(payments.aggregate(Avg('length'))['length__avg'])),
        'hours_worked': (payments.aggregate(Sum('length'))['length__sum'])/60,
        'pending_total': pending_total,
        'graph_types': graph_types
    }

    return render(request, 'codementor/statistics.html', context)
