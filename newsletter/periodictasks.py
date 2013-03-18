from django.core.management import call_command
from periodically.decorators import every


@every(minutes=5)
def try_to_send_newsletters():
    call_command('send_letters')
