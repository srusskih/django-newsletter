from django.conf import settings
from django.conf.urls.defaults import patterns, url
from django.contrib import admin
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.http import Http404
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils.functional import update_wrapper
from django.utils.translation import ugettext_lazy as _
from models import (Newsletter, NewsletterItem, NewsletterAdd,
                    ExternalSubscriber)


class NewsletterItemInline(admin.StackedInline):
    model = NewsletterItem


class NewsletterAddInline(admin.StackedInline):
    model = NewsletterAdd


def copy_newsletter(modeladmin, request, queryset):
    newsletter_fields = Newsletter._meta.get_all_field_names()
    newsletter_fields.remove('id')
    newsletter_fields.remove('status')
    newsletter_fields.remove('newsletteradd')
    newsletter_fields.remove('newsletteritem')

    for i in queryset:
        newsletter = Newsletter()
        for field in newsletter_fields:
            setattr(newsletter, field, getattr(i, field))
        newsletter.subject = newsletter.subject + " (copy)"
        newsletter.save()

        for item in i.newsletteritem_set.all():
            NewsletterItem.objects.create(
                newsletter=newsletter,
                order=item.order,
                category=item.category,
                title=item.title,
                body=item.body,
                url=item.url,
                url_display_name=item.url_display_name,
                picture=item.picture
            )

        for add_ in i.newsletteradd_set.all():
            NewsletterAdd.objects.create(
                newsletter=newsletter,
                order=add_.order,
                adds=add_.adds,
                url=add_.url
            )
copy_newsletter.short_description = "Make a copy"


class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['subject', 'send_to', 'publication_date', 'status',
                    'send', 'test_send']
    list_filter = ['status']
    inlines = (NewsletterItemInline, NewsletterAddInline)
    actions = [copy_newsletter]

    def test_send(self, obj):
        url = reverse('admin:send_admin', args=[obj.pk])
        return u'<a href="%s">%s</a>' % (url, _('Send admin'))
    test_send.allow_tags = True
    test_send.short_description = _("Sent Mail to Admin")

    def send(self, obj):
        if obj.status == Newsletter.NEW:
            url = reverse('admin:add_to_queue', args=[obj.pk])
            return u'<a href="%s">%s</a>' % (url, _('Send'))
        return ""
    send.allow_tags = True
    send.short_description = _("Add to Queue")

    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)
        urlpatterns = super(NewsletterAdmin, self).get_urls()
        urlpatterns = patterns('',
            url(r'^(.+)/send_admin/$',
                wrap(self.send_admin),
                name='send_admin'),
            url(r'^(.+)/add_to_queue/$',
                wrap(self.add_to_queue),
                name='add_to_queue'),
        ) + urlpatterns
        return urlpatterns

    def send_admin(self, request, object_id):
        opts = self.model._meta
        user = request.user
        letter = self._get_object(request, object_id)
        context = {
            'user': user,
            'obj': letter,
            'SITE': 'http://%s' % request.get_host()
        }
        message = render_to_string('newsletter/%s.html' % letter.template,
                                   context)
        email = EmailMessage(letter.subject, message,
                             settings.DEFAULT_FROM_EMAIL, [user.email])
        email.content_subtype = 'html'
        email.send()
        return redirect('admin:%s_%s_changelist' % (opts.app_label, opts.module_name))

    def add_to_queue(self, request, object_id):
        opts = self.model._meta
        self.model.objects.filter(id=object_id).update(status=Newsletter.QUEUED)
        return redirect('admin:%s_%s_changelist' % (opts.app_label, opts.module_name))

    def _get_object(self, request, object_id):
        try:
            obj = self.queryset(request).get(pk=object_id)
        except self.model.DoesNotExist:
            obj = None
        if not self.has_change_permission(request, obj):
            raise Http404('No permission')
        if obj is None:
            raise Http404(
                '%(name)s object with primary key %(key)r does not exist.' %
                {'name': self.model._meta.verbose_name, 'key': object_id}
            )
        return obj


class ExternalSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'is_subscribed']
    list_filter = ['is_subscribed',]
    search_fields = ['email', 'first_name', 'last_name']

    def get_urls(self):
        from admin_views import import_subscribers

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)
        urlpatterns = super(ExternalSubscriberAdmin, self).get_urls()
        urlpatterns = patterns('',
            url(r'^import/$',
                wrap(import_subscribers),
                name='externalsubscriber_import'),
        ) + urlpatterns
        return urlpatterns


admin.site.register(Newsletter, NewsletterAdmin)
admin.site.register(ExternalSubscriber, ExternalSubscriberAdmin)
