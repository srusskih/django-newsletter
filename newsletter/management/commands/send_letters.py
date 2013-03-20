from datetime import datetime

from django.core.mail import EmailMessage
from django.core.management.base import BaseCommand

from newsletter.conf import SITE_DOMAIN, FROM_NEWSLETTER, INTERNAL_USER_MODEL
from newsletter.models import Newsletter, ExternalSubscriber


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        now = datetime.now()
        self.site = SITE_DOMAIN
        Account = INTERNAL_USER_MODEL

        external = list(ExternalSubscriber.objects.
                        filter(is_subscribed=True, email__contains="@"))
        internal = list(Account.objects.
                        filter(is_subscribed=True, email__contains="@"))
        newsletters_to_send = list(
            Newsletter.objects.filter(status=Newsletter.QUEUED,
                                      publication_date__lt=now)
        )

        for obj in newsletters_to_send:
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
                    FROM_NEWSLETTER,
                    ['onno@code-on.be']
                )
                try:
                    admin_email.send()
                except Exception:
                    pass

    def do_send(self, obj, user):
        message = obj.render_for(user)
        email = EmailMessage(
            subject=obj.subject,
            body=message,
            to=[user.email]
        )
        email.content_subtype = 'html'
        try:
            email.send()
        except Exception, e:
            print e
