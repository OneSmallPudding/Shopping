from django.conf.urls import url
from rest_framework_jwt.views import obtain_jwt_token

from users.views import SMSCodeView, UserNameCountView, MobileCountView, UserView, UserDetailView, EmailView

urlpatterns = [
    url(r"^sms_codes/(?P<mobile>1[3-9]\d{9})/$", SMSCodeView.as_view()),
    url(r"^usernames/(?P<username>\w+)/count/$", UserNameCountView.as_view()),
    url(r"^mobiles/(?P<mobile>1[3-9]\d{9})/count/$", MobileCountView.as_view()),
    url(r"^users/$", UserView.as_view()),
    url(r'^authorizations/$', obtain_jwt_token),  # POST email=email&password=password
    url(r"^user/$", UserDetailView.as_view()),
    url(r"^emails/$", EmailView.as_view()),
]
