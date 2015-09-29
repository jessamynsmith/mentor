from django.contrib import admin

from codementor import models


admin.site.register(models.Client)
admin.site.register(models.Review)
admin.site.register(models.Payout)
admin.site.register(models.Payment)
