from django import template

register = template.Library()

@register.filter(name='before_colon')
def before_colon(value):
    """Return the substring before the first colon."""
    if isinstance(value, str):
        return value.split(':', 1)[0]
    return value
