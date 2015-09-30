from django.contrib import admin

from codementor import models


class ReviewAdmin(admin.ModelAdmin):
    list_display = ['reviewer', 'date', 'content']
    list_filter = ['date', 'reviewer']
    search_fields = ['reviewer__name', 'content']


class PayoutAdmin(admin.ModelAdmin):
    list_display = ['date', 'method', 'amount', 'total_earnings']
    list_filter = ['method']


class PaymentAdmin(admin.ModelAdmin):
    list_display = ['client', 'payout', 'date', 'type', 'length', 'free_preview', 'earnings']
    list_filter = ['payout', 'date', 'type', 'free_preview']
    search_fields = ['client__name']


admin.site.register(models.Client)
admin.site.register(models.Review, ReviewAdmin)
admin.site.register(models.Payout, PayoutAdmin)
admin.site.register(models.Payment, PaymentAdmin)
