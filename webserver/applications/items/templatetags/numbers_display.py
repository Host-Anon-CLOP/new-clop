from django import template
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.safestring import mark_safe

register = template.Library()


def format_number(value: int, show_sign: bool = False, invert: bool = False):
    value = int(value)
    if invert:
        value = -value

    sign = '+' if show_sign and value > 0 else ''

    if value == 0:
        number_class = 'text-secondary'
    elif value > 0:
        number_class = 'text-success'
    else:
        number_class = 'text-danger'

    return mark_safe(f'<span class="{number_class} font-monospace">{sign}{intcomma(value)}</span>')


@register.filter()
def absolute_number(value: int, invert: bool = False):
    return format_number(value, show_sign=False, invert=invert)


@register.filter()
def delta_number(value, invert: bool = False):
    return format_number(value, show_sign=True, invert=invert)


@register.filter()
def number(value: int):
    return mark_safe(f'<span class="font-monospace fw-bold">{intcomma(value)}</span>')


@register.filter
def multiply(value, arg):
    return value * arg


@register.filter
def check_float(value):
    return isinstance(value, float)
