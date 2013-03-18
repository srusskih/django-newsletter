from django.core.management.base import BaseCommand
from newsletter.models import Newsletter
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from datetime import datetime
from accounts.models import Account
from newsletter.unsubscribe import unsubscribe_url
from newsletter.models import ExternalSubscriber


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        now = datetime.now()
        self.site = settings.SITE_DOMAIN

        external = list(ExternalSubscriber.objects.filter(is_subscribed=True, email__contains="@"))
        internal = list(Account.objects.filter(is_subscribed=True, email__contains="@"))

        for obj in Newsletter.objects.filter(status=Newsletter.QUEUED, publication_date__lt=now):
            obj.status = Newsletter.SENT
            obj.save()

            user_list = []
            if obj.send_to == Newsletter.ALL:
                user_list = internal + external
            elif obj.send_to == Newsletter.ONLY_INTERNAL:
                user_list = internal
            elif obj.send_to == Newsletter.ONLY_EXTERNAL:
                user_list = external

            for i, user in enumerate(user_list):
                try:
                    self.do_send(obj, user)
                except Exception, e:
                    print e
            if i:
                message = 'er zijn %s nieuwsbrieven is verzonden %s' %\
                    (i, datetime.now().strftime('%H:%m %d %m %Y'))
                admin_email = EmailMessage(
                    '[123FEELFREE NEWSLETTER NOTE]',
                    message,
                    settings.FROM_NEWSLETTER,
                    ['onno@code-on.be']
                )
                try:
                    admin_email.send()
                except Exception:
                    pass

    def do_send(self, obj, user):
        print user.email
        context = {
            'obj': obj,
            'unsubscribe_url': unsubscribe_url(user.email),
            'SITE': 'http://%s' % self.site
        }
        message = render_to_string('newsletter/%s.html' % obj.template, context)
        email = EmailMessage(obj.subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
        email.content_subtype = 'html'
        try:
            email.send()
        except Exception, e:
            print e
