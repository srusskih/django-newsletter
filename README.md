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

3. add `is_subscribed = models.BooleanField()` to your intenal user model


4. Create tables with django `syncdb` command (and create and rub migrations for internal user's model if required)


5. Done!


License
-------

GNU GPL v3
