from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
	url(r'^$', 'controller.views.index', name='index'),
    url(r'^search/(?P<hashcode>\w+)/(?P<filesize>([0-9]+)+)/?$', 'controller.views.search', name='search'),
    # Examples:
    # url(r'^$', 'dsproject.views.home', name='home'),
    # url(r'^dsproject/', include('dsproject.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
