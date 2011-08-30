from django.conf.urls.defaults import patterns, url


def some_method(request):
    pass

urlpatterns = patterns(
    '',
    url(r'^$', some_method, name='url_name'),
)
