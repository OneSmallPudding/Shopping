from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r"^categories/(?P<pk>\d+)/skus/$", SKUListView.as_view()),
    url(r"^categories/(?P<pk>\d+)/$", GoodCategorieView.as_view()),
]
