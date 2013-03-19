from django.conf import settings
from django.template.loader import render_to_string
from .unsubscribe import unsubscribe_url


def render_newsletter(newsletter, user):
    url = hasattr(user, 'email') and unsubscribe_url(user.email) or ''
    return render_to_string('newsletter/%s.html' % newsletter.template, {
        'user': user,
        'obj': newsletter,
        'SITE': settings.SITE_DOMAIN,
        'unsubscribe_url': url
    })
