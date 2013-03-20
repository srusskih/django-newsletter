import mock
from django.test import TestCase
from django.utils import timezone
from django.core.files.base import ContentFile
from django.contrib.auth.models import User

from .unsubscribe import generate_code, check_code
from .models import Newsletter, NewsletterItem, ExternalSubscriber
from .shortcuts import get_current_site_domain, get_intenal_user_model


class TestUnsubscribeUrl(TestCase):
    def test_code(self):
        self.assert_(check_code(
            generate_code('email@emalil.com'),
            'email@emalil.com'
        ))
        self.assertFalse(check_code(
            generate_code('email@emalil.com'),
            'email@emalil2.com'
        ))


class TestNewsletterRendering(TestCase):
    """ testing newsletter rendering """

    def test_basic(self):
        letter = Newsletter.objects.create(
            template='standaard',
            subject='test',
            intro='intro',
            publication_date=timezone.now()
        )
        item = NewsletterItem.objects.create(
            newsletter=letter,
            order=0,
            title='item',
            body='body',
            url='http://google.com',
            picture=None
        )
        item.picture.save(content=ContentFile(image_data), name="1px.png")
        user = ExternalSubscriber(email='test@test.com')
        html = letter.render_for(user)
        self.assertIn(generate_code(user.email), html)


class TestGetCurrentSiteDomain(TestCase):
    """ testing gettings current site domain """

    @mock.patch('newsletter.shortcuts.settings', SITE_DOMAIN='testserver')
    def test_domain_in_django_settings(self, settings):
        self.assertEquals('testserver', get_current_site_domain())

    @mock.patch('newsletter.shortcuts.Site.objects', get_current=mock.Mock())
    def test_domain_not_in_settings(self, objects):
        site_obj = mock.Mock()
        site_obj.domain = 'testserver'
        objects.get_current.return_value = site_obj
        self.assertEquals('testserver', get_current_site_domain())


class TestGetInternalUsserModel(TestCase):
    """ testing gettings internal user model """
    def test_get_default_django_model(self):
        UserModel = get_intenal_user_model()
        self.assertIs(UserModel, User)

    @mock.patch(
        'newsletter.shortcuts.settings',
        AUTH_USER_MODEL="newsletter.ExternalSubscriber"
    )
    def test_get_custom_suer_model(self, settings):
        UserModel = get_intenal_user_model()
        self.assertIs(UserModel, ExternalSubscriber)


# image for tests
image_data = '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x07tIME\x07\xdb\x0c\x17\x020;\xd1\xda\xcf\xd2\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xdc\xccY\xe7\x00\x00\x00\x00IEND\xaeB`\x82'
