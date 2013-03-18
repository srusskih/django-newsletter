from django.conf import settings
from django.conf.urls import patterns, url
from django.contrib import admin
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils.functional import update_wrapper
from django.utils.translation import ugettext_lazy as _

from .models import (Newsletter, NewsletterItem, NewsletterAdd,
                     ExternalSubscriber)


class NewsletterItemInline(admin.StackedInline):
    model = NewsletterItem


class NewsletterAddInline(admin.StackedInline):
    model = NewsletterAdd


def copy_newsletter(modeladmin, request, queryset):
    """ create copy of selected newsletters """
    for original_newsletter in queryset:
        newsletter = original_newsletter
        newsletter.id = None
        newsletter.status = Newsletter.NEW
        newsletter.subject += " (copy)"
        newsletter.save()

        for item in original_newsletter.newsletteritem_set.all():
            item.id = None
            item.newsletter = newsletter
            item.save()

        for _add in original_newsletter.newsletteradd_set.all():
            _add.id = None
            _add.newsletter = newsletter
            _add.save()

copy_newsletter.short_description = _("Make a copy")


class SendingMixin(object):
    def test_send(self, obj):
        url = reverse('admin:send_admin', args=[obj.pk])
        return u'<a href="%s">%s</a>' % (url, _('Send admin'))

    test_send.allow_tags = True
    test_send.short_description = _("Sent Mail to Admin")

    def send(self, obj):
        if obj.status == self.model.NEW:
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

        urlpatterns = super(SendingMixin, self).get_urls()
        urlpatterns = patterns('',
                               url(r'^(.+)/send_admin/$', wrap(self.send_admin),
                                   name='send_admin'),
                               url(r'^(.+)/add_to_queue/$',
                                   wrap(self.add_to_queue),
                                   name='add_to_queue'),
        ) + urlpatterns
        return urlpatterns

    def send_admin(self, request, object_id):
        opts = self.model._meta
        user = request.user
        letter = get_object_or_404(self.queryset(request), id=object_id)
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
        return redirect(
            'admin:%s_%s_changelist' % (opts.app_label, opts.module_name)
        )

    def add_to_queue(self, request, object_id):
        """ push newsletters to queue """
        # change object permissions required
        if not self.has_change_permission(request):
            return HttpResponseForbidden("Not enough permissions")

        opts = self.model._meta
        self.queryset(request).filter(id=object_id). \
            update(status=Newsletter.QUEUED)
        return redirect(
            'admin:%s_%s_changelist' % (opts.app_label, opts.module_name)
        )


class NewsletterAdmin(SendingMixin, admin.ModelAdmin):
    list_display = ['subject', 'send_to', 'publication_date', 'status',
                    'send', 'test_send']
    list_filter = ['status']
    inlines = (NewsletterItemInline, NewsletterAddInline)
    actions = [copy_newsletter]


class ExternalSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name', 'last_name', 'is_subscribed']
    list_filter = ['is_subscribed']
    search_fields = ['email', 'first_name', 'last_name']
    #
    # def get_urls(self):
    #     from admin_views import import_subscribers
    #
    #
    #     def wrap(view):
    #         def wrapper(*args, **kwargs):
    #             return self.admin_site.admin_view(view)(*args, **kwargs)
    #
    #         return update_wrapper(wrapper, view)
    #
    #     urlpatterns = super(ExternalSubscriberAdmin, self).get_urls()
    #     urlpatterns = patterns('',
    #                            url(r'^import/$',
    #                                wrap(import_subscribers),
    #                                name='externalsubscriber_import'),
    #     ) + urlpatterns
    #     return urlpatterns


admin.site.register(Newsletter, NewsletterAdmin)
admin.site.register(ExternalSubscriber, ExternalSubscriberAdmin)
