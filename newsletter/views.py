from models import Newsletter
from utils.views import render_to
from newsletter.unsubscribe import unsubscribe as do_unsubscribe, unsubscribe_url, InvalidCode
from django.http import HttpResponse


@render_to('newsletter/standaard.html')
def detail(request, pk):
    url = ''
    if request.user.is_authenticated():
        url = unsubscribe_url(request.user.email)
    return {
        'user': request.user,
        'obj': Newsletter.objects.get(pk=pk), 'SITE':'',
        'unsubscribe_url': url
    }


@render_to('newsletter/unsubscribe.html')
def unsubscribe(request, code, email):
    try:
        do_unsubscribe(code, email)
    except InvalidCode:
        return HttpResponse('Invalid code')
    return {}
