from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
import sms_app

import object_tools
object_tools.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^contact/$', 'sms_survey.views.contact', name='contact'),
    url(r'^(SMS|sms)/', include('sms_app.urls')), 
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^object-tools/', include(object_tools.tools.urls)),
)
