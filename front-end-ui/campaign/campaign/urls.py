from django.contrib import admin
from django.urls import path

from django.conf.urls import url

from .views import homepage
from .views import about
from .views import action

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^$', homepage),
    url(r'^about$', about),
    url(r'^action/$', action),
]
