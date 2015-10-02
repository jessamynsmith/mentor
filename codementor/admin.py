from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.db.models import Avg, Sum

from codementor import models


class ReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer', 'date', 'content']
    list_filter = ['date', 'reviewer']
    search_fields = ['reviewer__name', 'content']


class PayoutAdmin(admin.ModelAdmin):
    list_display = ['date', 'method', 'amount', 'total_earnings']
    list_filter = ['method']


class PaymentChangeList(ChangeList):
    """Custom total rows at bottom of changlist"""

    def get_total_payments(self, queryset):
        """ Payment total for changelist"""
        total = models.Payment()
        total.__unicode__ = lambda: u"Total Payments"
        earning_dict = queryset.aggregate(Sum('earnings'))
        total.earnings = earning_dict.items()[0][1]
        return total

    def get_average_payment(self, queryset):
        """ Average payment for changelist"""
        avg = models.Payment()
        avg.__unicode__ = lambda: u"Average cost"
        earning_dict = queryset.aggregate(Avg('earnings'))
        avg.earnings = earning_dict.items()[0][1]
        return avg

    def get_results(self, request):
        super(PaymentChangeList, self).get_results(request)
        queryset = self.get_queryset(request)
        total_payments = self.get_total_payments(queryset)
        average_payment = self.get_average_payment(queryset)
        # HACK: in order to get the objects loaded we need to call for
        # queryset results once so simple len function does it
        len(self.result_list)
        self.result_list._result_cache.append(total_payments)
        self.result_list._result_cache.append(average_payment)


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['client', 'payout', 'date', 'type', 'length', 'free_preview', 'earnings']
    list_filter = ['type', 'date', 'free_preview', 'payout']
    search_fields = ['client__name']

    def get_changelist(self, request, **kwargs):
        """Override the default changelist"""
        return PaymentChangeList


admin.site.register(models.Client)
admin.site.register(models.Review, ReviewAdmin)
admin.site.register(models.Payout, PayoutAdmin)
admin.site.register(models.Payment, PaymentAdmin)
