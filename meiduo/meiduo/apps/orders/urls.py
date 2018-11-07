
from django.conf.urls import url

from orders.views import *

urlpatterns = [
    url(r'^orders/settlement/$', OrderView.as_view()),
    url(r'^orders/$', SaveOrderView.as_view()),
]
