from django.conf import settings
from django.contrib.sites.models import Site
from django.db.models import get_model
from django.template.loader import render_to_string


def render_newsletter(newsletter, user):
    from .unsubscribe import unsubscribe_url
    url = hasattr(user, 'email') and unsubscribe_url(user.email) or ''
    return render_to_string('newsletter/%s.html' % newsletter.template, {
        'user': user,
        'obj': newsletter,
        'SITE': get_current_site_domain(),
        'unsubscribe_url': url
    })


def get_current_site_domain():
    """ Get project site domain

        :return: settings.SITE_DOMAIN value if exists or
                 current site of Django Site contrib app
    """
    site_domain = getattr(settings, 'SITE_DOMAIN', None)
    if not site_domain:
        site_domain = Site.objects.get_current().domain
    return site_domain


def get_intenal_user_model():
    """ Get internal user model class

        :return: django.contrib.auth.models.User or
                 model in settings.AUTH_USER_MODEL
    """
    User = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')
    return get_model(*User.split('.'))
