from django.conf import settings
from django.utils.functional import SimpleLazyObject
from .shortcuts import get_current_site_domain, get_intenal_user_model

INTERNAL_USER_MODEL = SimpleLazyObject(get_intenal_user_model)

SITE_DOMAIN = SimpleLazyObject(get_current_site_domain)

FROM_NEWSLETTER = getattr(
    settings, 'FROM_NEWSLETTER',
    settings.DEFAULT_FROM_EMAIL
)
