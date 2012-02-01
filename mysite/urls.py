# -*- encoding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from mysite.users import views

urlpatterns = patterns('',

    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.index),
    url(r'^admin_tools/', include('admin_tools.urls')),
)
