from contextlib import contextmanager

from django.contrib import messages


class InvalidInput(Exception):
    pass


@contextmanager
def exception_to_message(request):
    try:
        yield None
    except InvalidInput as exception:
        messages.error(request, str(exception))
