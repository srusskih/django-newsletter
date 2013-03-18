Django-Newsletter
=================

Yeat another newsletter app to create and send mails to subscribers


Installation
-----------

1. update `settings.py`

		INSTALLED_APPS = (
			# ...
			'newsletter',
			# ...
		)

2. update `urls.py`

		urlpatterns = patterns('',
			# ..
			url(r'^newsletter/', include('newsletter.urls', namespace="newsletter")),
			# ..
		)


3. Create tables with django `syncdb` command.


4. Done!


License
-------

GNU GPL v3
