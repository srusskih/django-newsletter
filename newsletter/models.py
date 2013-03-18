from django.db import models
from django.utils.translation import ugettext_lazy as _


class Newsletter(models.Model):
    ALL, ONLY_INTERNAL, ONLY_EXTERNAL = range(3)
    SEND_TYPES = (
        (ALL, _('all users')),
        (ONLY_INTERNAL, _('only internal')),
        (ONLY_EXTERNAL, _('only external')),
    )
    NEW, QUEUED, SENT = xrange(3)
    STATUS_CHOICES = (
        (NEW, _('New')),
        (QUEUED, _('Queued')),
        (SENT, _('Sent'))
    )

    send_to = models.PositiveSmallIntegerField(_('send to'), choices=SEND_TYPES, default=ALL)
    template = models.CharField(_('template'), max_length=50, choices=(('standaard', 'standaard'), ('flash', 'flash')))
    header = models.ImageField(_('header'), upload_to='uploads/newsletter/header/%Y/%m', blank=True, null=True)
    footer = models.ImageField(_('footer'), upload_to='uploads/newsletter/footer/%Y/%m', blank=True, null=True)
    subject = models.CharField(_('subject'), max_length=200)
    intro = models.TextField(_('intro'), help_text=_('for internal use'))
    publication_date = models.DateTimeField(_('publication_date'))
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


class ExternalSubscriber(models.Model):
    email = models.EmailField()
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    is_subscribed = models.BooleanField(default=True)

    class Meta:
        ordering = ['email',]
        verbose_name = _("External Subscriber")
        verbose_name_plural = _("External Subscribers")


class NewsletterItem(models.Model):
    """ Newslatter  infrormation """
    newsletter = models.ForeignKey(Newsletter)
    order = models.IntegerField(_('order'))
    title = models.CharField(_('title'), max_length=120)
    body = models.TextField(_('body'))
    url = models.URLField(_('url'))
    url_display_name = models.CharField(_('url display name'), max_length=80, default="lees meer")
    picture = models.ImageField(_('picture'), upload_to='uploads/newsletter/picture/%Y/%m/')

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['order']
        verbose_name = _('Newsletter item')
        verbose_name_plural = _('Newsletter items')


class NewsletterAdd(models.Model):
    """ Newslatter attachment """
    newsletter = models.ForeignKey(Newsletter)
    order = models.IntegerField(_('order'))
    adds = models.ImageField(_('picture'), upload_to='uploads/newsletter/picture/%Y/%m/')
    url = models.URLField(_('url'))

    def __unicode__(self):
        return self.url

    class Meta:
        ordering = ['order']
        verbose_name = _('Newsletter add')
        verbose_name_plural = _('Newsletter adds')
