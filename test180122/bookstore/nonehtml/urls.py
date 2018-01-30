from django.conf.urls import url
from nonehtml import views

urlpatterns = [
    url(r'^test/$',views.test)
]
