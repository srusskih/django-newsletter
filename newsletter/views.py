from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from .models import Newsletter
from .unsubscribe import unsubscribe as do_unsubscribe, InvalidCode
from .shortcuts import render_newsletter


def detail(request, pk):
    newsletter = get_object_or_404(Newsletter, pk=pk)
    return HttpResponse(render_newsletter(newsletter, request.user))


def unsubscribe(request, code, email):
    try:
        do_unsubscribe(code, email)
    except InvalidCode:
        return HttpResponse('Invalid code')
    return render(request, 'newsletter/unsubscribe.html', {})
