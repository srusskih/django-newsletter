from datetime import datetime
from django.core.mail import EmailMessage
from django.db import models
from django.utils.translation import ugettext_lazy as _
from .conf import INTERNAL_USER_MODEL


class Newsletter(models.Model):
    ALL, ONLY_INTERNAL, ONLY_EXTERNAL = range(3)
    SEND_TYPES = (
        (ALL, _('all users')),  # send to internal and external subscribers
        (ONLY_INTERNAL, _('only internal')),
        (ONLY_EXTERNAL, _('only external')),
    )
    NEW, QUEUED, SENT = xrange(3)
    STATUS_CHOICES = (
        (NEW, _('New')),  # just recreated
        (QUEUED, _('Queued')),  # ready to send
        (SENT, _('Sent'))  # was sent
    )

    # select group of subscribers
    send_to = models.PositiveSmallIntegerField(
        _('send to'),
        choices=SEND_TYPES, default=ALL
    )

    # newsletter template
    template = models.CharField(
        _('template'),
        max_length=50,
        choices=(
            ('standaard', 'standaard'),
        )
    )

    # header image
    header = models.ImageField(
        _('header'),
        upload_to='uploads/newsletter/header/%Y/%m',
        blank=True
    )

    # footer image
    footer = models.ImageField(
        _('footer'),
        upload_to='uploads/newsletter/footer/%Y/%m',
        blank=True
    )

    # newsletter email message subject
    subject = models.CharField(_('subject'), max_length=200)
    intro = models.TextField(_('intro'), help_text=_('for internal use'))

    # when newsletter should be sent
    publication_date = models.DateTimeField(_('publication_date'))

    # sending status
    status = models.IntegerField(default=NEW, choices=STATUS_CHOICES)

    def __unicode__(self):
        return self.subject

    class Meta:
        ordering = ['-publication_date']
        verbose_name = _('newsletter')
        verbose_name_plural = _('newsletters')

    @models.permalink
    def get_absolute_url(self):
        return 'newsletter:newsletter', (), {'pk': self.pk}

    def render_for(self, user):
        """ render newsmail for **user** """
        from .shortcuts import render_newsletter
        return render_newsletter(self, user)

    def get_subscribers(self):
        subscribers = []

        if self.send_to == self.ONLY_EXTERNAL or\
                self.send_to == Newsletter.ALL:
            subscribers.extend(
                list(
                    ExternalSubscriber.objects.
                    filter(is_subscribed=True, email__contains="@")
                )
            )

        if INTERNAL_USER_MODEL:
            if self.send_to == self.ONLY_INTERNAL or\
                    self.send_to == Newsletter.ALL:
                subscribers.extend(
                    list(
                        INTERNAL_USER_MODEL.objects.
                        filter(is_subscribed=True, email__contains="@")
                    )
                )
        return subscribers

    @classmethod
    def get_queue(cls):
        return cls.objects.filter(
            status=Newsletter.QUEUED,
            publication_date__lt=datetime.now()
        )

    def send(self, user):
        message = self.render_for(user)
        email = EmailMessage(
            subject=self.subject,
            body=message,
            to=[user.email]
        )
        email.content_subtype = 'html'
        email.send()
        return email


class ExternalSubscriber(models.Model):
    email = models.EmailField()
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    is_subscribed = models.BooleanField(default=True)

    class Meta:
        ordering = ('email',)
        verbose_name = _("External Subscriber")
        verbose_name_plural = _("External Subscribers")


class NewsletterItem(models.Model):
    """ Newslatter content object """
    newsletter = models.ForeignKey(Newsletter)
    order = models.IntegerField(_('order'))
    title = models.CharField(_('title'), max_length=120)
    body = models.TextField(_('body'))
    url = models.URLField(_('url'))
    url_display_name = models.CharField(
        _('url display name'),
        max_length=80,
        default="lees meer"
    )
    picture = models.ImageField(
        _('picture'),
        upload_to='uploads/newsletter/picture/%Y/%m/'
    )

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['order']
        verbose_name = _('Newsletter item')
        verbose_name_plural = _('Newsletter items')


class NewsletterAdd(models.Model):
    """ Newslatter content add """
    newsletter = models.ForeignKey(Newsletter)
    order = models.IntegerField(_('order'))
    adds = models.ImageField(
        _('picture'),
        upload_to='uploads/newsletter/picture/%Y/%m/'
    )
    url = models.URLField(_('url'))

    def __unicode__(self):
        return self.url

    class Meta:
        ordering = ['order']
        verbose_name = _('Newsletter add')
        verbose_name_plural = _('Newsletter adds')
