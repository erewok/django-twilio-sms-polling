# -*- coding: utf-8 -*- #

from django.conf.urls import patterns, include, url
import sms_app.views

urlpatterns = patterns('sms_app.views',
    url(r'^$', 'sms_main', name='sms_main'),
    url(r'^response/$', 'sms_response', name='sms_response'),
    url(r'^response_fallback/$', 'sms_fallback', name='sms_fallback'),
#    url(r'^status_callback/$', views.sms_status_callback),                      
)
