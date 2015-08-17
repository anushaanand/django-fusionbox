import urls
#AGS:20150816: Django 1.4 to 1.8 migration
#from django.conf.urls.defaults import patterns, include
from django.conf.urls import patterns, url, include

from fusionbox.panels.user_panel.urls import urlpatterns

urls.urlpatterns += patterns('',
    ('', include(urlpatterns)),
)
