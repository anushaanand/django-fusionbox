#AGS:20150816: Django 1.4 to 1.8 migration
#from django.conf.urls.defaults import patterns, url
from django.conf.urls import patterns, url, include

#from debug_toolbar.urls import _PREFIX
_PREFIX = '__debug__'

urlpatterns = patterns('fusionbox.panels.user_panel.views',
    url(r'^%s/users/$' % _PREFIX, 'content',
        name='debug-userpanel'),
    url(r'^%s/users/login/$' % _PREFIX, 'login',
        name='debug-userpanel-login'),
    url(r'^%s/users/login/(?P<pk>-?\d+)$' % _PREFIX, 'login',
        name='debug-userpanel-login'),
)
