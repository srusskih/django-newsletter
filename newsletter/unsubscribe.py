import hashlib
from django.conf import settings
from accounts.models import Account
from django.core.urlresolvers import reverse
from newsletter.models import ExternalSubscriber


def generate_code(email):
    return hashlib.sha1(settings.SECRET_KEY+email).hexdigest()


def check_code(code, email):
    return generate_code(email) == code


def unsubscribe_url(email):
    code = generate_code(email)
    domain = settings.SITE_DOMAIN
    path = reverse('newsletter:unsubscribe', args=[code, email])
    return u'http://%s%s' % (domain, path)


class InvalidCode(Exception):
    pass


def unsubscribe(code, email):
    if not check_code(code, email):
        raise InvalidCode('Envalid unsubscribe code')
    Account.objects.filter(email=email).update(is_subscribed=False)
    ExternalSubscriber.objects.filter(email=email).update(is_subscribed=False)
