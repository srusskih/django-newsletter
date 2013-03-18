import xlrd
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.core import validators

from utils.views import render_to
from accounts.models import Account

from .models import ExternalSubscriber
from .forms import ExternalSubscriberUpload

def validate_email(value, row_number):
    error_message = _(u'Invalid e-mail address on "%d" line.')
    return validators.EmailValidator(
        validators.email_re,
        unicode(error_message % row_number),
        'invalid'
    )(value)

def upload_handler(file_obj, path_to_save):
    destination = open(path_to_save, 'wb+')
    for chunk in file_obj.chunks():
        destination.write(chunk)
    destination.close()

def get_externalsubscribers(file_obj):
    pass_count = 0
    fail_count = 0
    PATH = '/tmp/import_subscribers.xls'
    upload_handler(file_obj, PATH)
    sheet = xlrd.open_workbook(PATH).sheet_by_index(0)
    for i in range(1,sheet.nrows):
        row = sheet.row(i)
        if not row[0].value:
            continue
        subscriber = {}
        subscriber['email'] = row[0].value
        try:
            validate_email(subscriber['email'].strip(), i)
            pass_count+=1
        except Exception as e:
            fail_count+=1
            #print e, u'"%s"' % subscriber['email']
            continue

        try:
            subscriber['first_name'] = row[1].value
        except IndexError:
            pass

        try:
            subscriber['last_name'] = row[2].value
        except IndexError:
            pass

        if not bool(Account.objects.filter(email=subscriber['email']).only('id')):
            obj, created = ExternalSubscriber.objects.get_or_create(
                email=subscriber['email'],
                defaults={
                    'first_name': subscriber.get('first_name'),
                    'last_name': subscriber.get('last_name'),
                }
            )
            if not created:
                for field in ['first_name', 'last_name']:
                    if subscriber.get(field) and\
                       getattr(obj, field) != subscriber.get(field):
                        setattr(obj, field, subscriber.get(field))
                obj.save()

    return pass_count, fail_count

@render_to('newsletter/import_subscribers_form.html')
def import_subscribers(request):
    if request.method == 'POST':
        form = ExternalSubscriberUpload(request.POST, request.FILES)
        if form.is_valid():
            passed, failed  = get_externalsubscribers(form.cleaned_data['xls'])
            messages.add_message(request, messages.INFO, _('Subscribers successfuly imported. %(passed)d added and %(failed)d failed ') % {'passed':passed, 'failed': failed})

            return redirect('admin:newsletter_externalsubscriber_changelist')
    else:
        form = ExternalSubscriberUpload()
    return {'form': form}

