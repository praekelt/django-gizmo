from django import template

register = template.Library()


@register.simple_tag
def test_simple_tag():
    return 'test simple tag result'
