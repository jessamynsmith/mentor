from django.conf.urls import url
from django.views.generic import RedirectView

from codementor import views as codementor_views


urlpatterns = [
    url(r'^$', RedirectView.as_view(url='statistics/', permanent=True)),
    url(r'^statistics/$', codementor_views.statistics, name='statistics'),
    url(r'^statistics/payout_history$', codementor_views.payout_history),
    url(r'^statistics/payment_history$', codementor_views.payment_history),
    url(r'^statistics/hours_worked', codementor_views.hours_worked),
]
