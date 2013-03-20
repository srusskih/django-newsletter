import itertools
from datetime import datetime

from django.core.mail import mail_admins
from django.core.management.base import BaseCommand

from newsletter.conf import SITE_DOMAIN
from newsletter.models import Newsletter


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        self.site = SITE_DOMAIN
        newsletters_to_send = Newsletter.get_queue().iterator()

        for obj in newsletters_to_send:
            obj.status = Newsletter.SENT
            obj.save()

            user_list = iter(obj.get_subscribers())
            counter = itertools.count()
            for user in user_list:
                counter.next()
                try:
                    obj.send(user)
                except Exception, e:
                    print e

            send_report_to_admin(counter.next())


def send_report_to_admin(email_count):
    message = 'er zijn %s nieuwsbrieven is verzonden %s' % (
        email_count, datetime.now().strftime('%H:%m %d %m %Y')
    )
    try:
        mail_admins(
            subject='[123FEELFREE NEWSLETTER NOTE]',
            message=message,
        )
    except Exception, e:
        print "Report sent failed with error: %r" % e
