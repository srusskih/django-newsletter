import hashlib
from django.conf import settings
from django.core.urlresolvers import reverse
from .models import ExternalSubscriber
from .conf import INTERNAL_USER_MODEL, SITE_DOMAIN


class InvalidCode(Exception):
    pass


def generate_code(email):
    return hashlib.sha1(settings.SECRET_KEY+email).hexdigest()


def check_code(code, email):
    return generate_code(email) == code


def unsubscribe_url(email):
    code = generate_code(email)
    domain = SITE_DOMAIN
    path = reverse('newsletter:unsubscribe', args=[code, email])
    return u'http://%s%s' % (domain, path)


def unsubscribe(code, email):
    Account = INTERNAL_USER_MODEL

    if not check_code(code, email):
        raise InvalidCode('Envalid unsubscribe code')

    Account.objects.filter(email=email).update(is_subscribed=False)
    ExternalSubscriber.objects.filter(email=email).update(is_subscribed=False)
