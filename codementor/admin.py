from daterange_filter.filter import DateRangeFilter
from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.db.models import Avg, Sum

from codementor import models


class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'started_at', 'continent', 'gender', 'race_list']
    list_filter = ['continent', 'gender', 'races__name', ('started_at', DateRangeFilter)]
    search_fields = ['name']


class ReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer', 'date', 'content']
    list_filter = [('date', DateRangeFilter), 'reviewer']
    search_fields = ['reviewer__name', 'content']


class SumAverageChangeList(ChangeList):
    """Custom total rows at bottom of changelist"""

    NUMERIC_FIELDS = ('Integer', 'Decimal number')

    def get_field(self, field_name):
        for field in self.model._meta.fields:
            if field_name == field.attname:
                return field
        return None

    def get_aggregate(self, queryset, title, aggregate_function):
        """ Get aggregate data for changelist"""
        total = self.model()
        total.__unicode__ = lambda: title
        for field_name in self.list_display:
            field = self.get_field(field_name)
            if field and not field.primary_key:
                if field.choices:
                    setattr(total, field_name, None)
                elif str(field.description) in self.NUMERIC_FIELDS:
                    result_data = queryset.aggregate(aggregate_function(field_name))
                    setattr(total, field_name, result_data.items()[0][1])
        return total

    def get_results(self, request):
        super(SumAverageChangeList, self).get_results(request)
        queryset = self.get_queryset(request)
        total = self.get_aggregate(queryset, u"Totals", Sum)
        average = self.get_aggregate(queryset, u"Averages", Avg)
        # HACK: in order to get the objects loaded we need to call for
        # queryset results once so simple len function does it
        len(self.result_list)
        self.result_list._result_cache.append(total)
        self.result_list._result_cache.append(average)


class PayoutAdmin(admin.ModelAdmin):
    list_display = ['date', 'method', 'amount', 'total_earnings']
    list_filter = ['method', ('date', DateRangeFilter)]

    def get_changelist(self, request, **kwargs):
        """Override the default changelist"""
        return SumAverageChangeList


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['client', 'payout', 'date', 'type', 'free_preview', 'earnings']
    list_filter = ['type', ('date', DateRangeFilter), 'free_preview', 'payout']
    search_fields = ['client__name']

    def get_changelist(self, request, **kwargs):
        """Override the default changelist"""
        return SumAverageChangeList


class SessionAdmin(admin.ModelAdmin):
    list_display = ['client', 'started_at', 'length', 'review']
    list_filter = [('started_at', DateRangeFilter), 'client']
    search_fields = ['client__name']


admin.site.register(models.Client, ClientAdmin)
admin.site.register(models.Payment, PaymentAdmin)
admin.site.register(models.Payout, PayoutAdmin)
admin.site.register(models.Race)
admin.site.register(models.Review, ReviewAdmin)
admin.site.register(models.Session, SessionAdmin)
