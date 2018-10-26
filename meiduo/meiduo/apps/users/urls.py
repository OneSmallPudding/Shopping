from django.conf.urls import url

from users.views import SMSCodeView, UserNameCountView, MobileCountView, UserView

urlpatterns = [
    url(r"^sms_codes/(?P<mobile>1[3-9]\d{9})/$", SMSCodeView.as_view()),
    url(r"^usernames/(?P<username>\w+)/count/$", UserNameCountView.as_view()),
    url(r"^mobiles/(?P<mobile>1[3-9]\d{9})/count/$", MobileCountView.as_view()),
    url(r"^users/$", UserView.as_view()),
]
