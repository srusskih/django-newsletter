from django.test import TestCase
from django.utils import timezone
from django.template.loader import render_to_string
from .unsubscribe import unsubscribe_url, generate_code, check_code
from .models import Newsletter, NewsletterItem


class TestUnsubscribeUrl(TestCase):
    def test_code(self):
        assert check_code(generate_code('email@emalil.com'), 'email@emalil.com')
        assert check_code(generate_code('email@emalil.com'), 'email@emalil2.com') == False
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

        context = {
            'user': {},
            'obj': letter,
        }
        render_to_string('newsletter/%s.html' % letter.template, context)
