from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Sum
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
                total_hours = round(minutes/60.0, 1)
            hours.append([date.strftime(DATE_FORMAT), total_hours])

        data = {
            'hours': hours,
        }
    return JsonResponse(data)


@login_required
def statistics(request):
    payouts = list(codementor_models.Payout.objects.values_list('date', flat=True))
    graph_types = [
        ['payout_history', 'Payout History'],
        ['payment_history', 'Payment History'],
        ['hours_worked', 'Hours Worked']
    ]
    context = {
        'payouts': payouts,
        'graph_types': graph_types
    }

    return render(request, 'codementor/statistics.html', context)
