from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()


def just_raise(request):
    def f():
        def g():
            raise ValueError("We've run out of Venezuelan Beaver Cheese.")
        g()
    return f()

class ClassBasedView(object):

    def method(self, request):
        raise TypeError("Something happened inside a method.")

    def __call__(self, request):
        raise TypeError("Something happened inside a class.")


urlpatterns = patterns('',
    # Example:
    # (r'^example/', include('example.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
    (r'^$', just_raise),
    (r'^class/$', ClassBasedView()),
    (r'^method/$', ClassBasedView().method),
)
