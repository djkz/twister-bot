from django.conf.urls.defaults import include, patterns


urlpatterns = patterns('views',
    (r"""(?iux)^\!test""",'test') ,
)