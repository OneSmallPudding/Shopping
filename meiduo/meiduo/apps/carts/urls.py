
from django.conf.urls import url

from carts.views import *

urlpatterns = [
    url(r'^cart/$',CartsView.as_view() ),
]
