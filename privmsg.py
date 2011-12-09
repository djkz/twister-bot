from django.conf.urls.defaults import include, patterns


urlpatterns = patterns('views',
    (r"""(?iux)^\!test$""",'test') ,
    (r"""(?iux)^\!more$""",'more') ,
    # definitions
    (r"""(?iux)^\!learn \s (?P<tag>\S+) \s (?P<definition>.+$)""",'learn') ,
    (r"""(?iux)^\?\? \s (?P<tag>\S+)$""",'show_definition') ,
    (r"""(?iux)^\?\? \s (?P<tag>\S+)\s(?P<index>\d+?)$""",'show_definition') ,
    (r"""(?iux)^\!whoset \s (?P<tag>\S+)$""",'who_set') ,
    (r"""(?iux)^\!whoset \s (?P<tag>\S+) \s(?P<index>\d+?)$""",'who_set') ,
    (r"""(?iux)^\!forget \s (?P<tag>\S+)$""",'forget') ,
    (r"""(?iux)^\!forget \s (?P<tag>\S+) \s(?P<index>\d+?)$""",'forget') ,
    (r"""(?iux)^\!search \s (?P<search_str>.+?)$""",'search') ,
    (r"""(?iux)^\!search \s (?P<search_str>.+?)\s by \s (?P<nick>\w+?)$""",'search') ,
    
    #quotes
    (r"""(?iux)^\!quote$""",'get_quote') ,
    (r"""(?iux)^\!quote \s (?P<quote_id>\d+?)$""",'get_quote') ,
    (r"""(?iux)^\!quote \s (?P<quote>.+?)$""",'add_quote') ,
    (r"""(?iux)^\!unquote \s (?P<quote_id>\d+?)$""",'del_quote') ,
    
    #dict
    (r"""(?iux)^\!dict \s (?P<word>\S+)$""",'dict') ,
    
    # package tracking
    (r"""(?iux)^\!track \s (?P<tracking_number>.+?)$""",'track') ,
    
    # misc commands
    (r"""(?iux)^\!weather \s (?P<location>.+?)$""",'get_weather') ,
    (r"""(?iux)^\!map \s (?P<location>.+?)$""",'map') ,
    (r"""(?iux)^\!google \s (?P<query>.+?)$""",'google') ,
    (r"""(?iux)^\!magic \s (?P<query>.+?)$""",'magic') ,
)

