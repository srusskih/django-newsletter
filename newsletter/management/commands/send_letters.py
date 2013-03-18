from datetime import datetime
from django.db.models import get_model
from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage
from django.conf import settings

from accounts.models import Account


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        now = datetime.now()
        self.site = settings.SITE_DOMAIN
        ExternalSubscriber = get_model('newsletters', 'ExternalSubscriber')
        Newsletter = get_model('newsletters', 'Newsletter')

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
