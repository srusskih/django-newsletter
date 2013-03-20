import mock
from datetime import datetime
from django.test import TestCase
from django.core import mail
from django.core.management import call_command
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from django.conf import settings

from .unsubscribe import generate_code, check_code
from .models import Newsletter, NewsletterItem, ExternalSubscriber
from .shortcuts import get_current_site_domain, get_intenal_user_model
from .conf import INTERNAL_USER_MODEL


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
        letter = create_newsletter()
        create_newsletter_item(letter)
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


class TestSendLettersCommand(TestCase):

    @mock.patch('newsletter.models.INTERNAL_USER_MODEL.objects.filter')
    def test_basic(self, mocked_user_manager):
        """ get newletter from queue to send
            and to subscriberds depends on newsletter settings
        """

        letter = create_newsletter()
        letter.status = Newsletter.NEW
        letter.save()
        create_newsletter_item(letter)
        ExternalSubscriber.objects.create(email='external@test.com')
        mocked_user_manager.return_value = INTERNAL_USER_MODEL.objects.all()
        # 1 internal user from initial_data.json

        # SEND only if in Queue
        mail.outbox = []
        call_command('send_letters')
        self.assertEquals(len(mail.outbox), len(settings.ADMINS))  # mail to admins

        # TO ALL
        mail.outbox = []
        letter.status = Newsletter.QUEUED
        letter.send_to = Newsletter.ALL
        letter.save()
        call_command('send_letters')
        self.assertEquals(len(mail.outbox), 2 + len(settings.ADMINS))

        # TO INTERNAL
        mail.outbox = []
        letter.send_to = Newsletter.ONLY_INTERNAL
        letter.save()
        call_command('send_letters')
        self.assertEquals(len(mail.outbox), 1 + len(settings.ADMINS))

        # TO EXTERNAL
        mail.outbox = []
        letter.send_to = Newsletter.ONLY_EXTERNAL
        letter.save()
        call_command('send_letters')
        self.assertEquals(len(mail.outbox), 1 + len(settings.ADMINS))


# image for tests
image_data = '\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00\tpHYs\x00\x00\x0b\x13\x00\x00\x0b\x13\x01\x00\x9a\x9c\x18\x00\x00\x00\x07tIME\x07\xdb\x0c\x17\x020;\xd1\xda\xcf\xd2\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xdc\xccY\xe7\x00\x00\x00\x00IEND\xaeB`\x82'


def create_newsletter():
    letter = Newsletter.objects.create(
        template='standaard',
        subject='test',
        intro='intro',
        publication_date=datetime.now()
    )
    return letter


def create_newsletter_item(letter):
    item = NewsletterItem.objects.create(
        newsletter=letter,
        order=0,
        title='item',
        body='body',
        url='http://google.com',
        picture=None
    )
    item.picture.save(content=ContentFile(image_data), name='1px.png')
    return item
