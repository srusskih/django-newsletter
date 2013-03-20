from django.test import TestCase
from django.utils import timezone

from .unsubscribe import unsubscribe_url, generate_code, check_code
from .models import Newsletter, NewsletterItem, ExternalSubscriber


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
        print unsubscribe_url('admin@admin.com')


class TestNewsletterRendering(TestCase):
    """ testing newsletter rendering """
    def test_basic(self):
        letter = Newsletter.objects.create(
            template='standaard',
            subject='test',
            intro='intro',
            publication_date=timezone.now()
        )
        NewsletterItem.objects.create(
            newsletter=letter,
            order=0,
            title='item',
            body='body',
            url='http://google.com',
            picture=None
        )
        user = ExternalSubscriber(email='test@test.com')
        html = letter.render_for()
        self.assertIn(generate_code(user.email), html)
