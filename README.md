
Django-Newsletter
=================

Yeat another newsletter app to create and send mails to subscribers


Installation
-----------

1. Add `'newsletter', to `INSTALLED_APPS`

	INSTALLED_APPS = (
		# ...
		'newsletter',
		# ...
	)

2. Insert `url(r'^newsletter/', include(namespace="newsletter")),`, to `urls.py`

	urlpatterns = patterns('',
		# ..
		url(r'^newsletter/', include(namespace="newsletter")),
		# ..
	)


3. Create tables with django `syncdb` command.


4. Done!


License
-------

GNU GPL v3
