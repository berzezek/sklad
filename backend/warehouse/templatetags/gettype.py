from django import template

register = template.Library()


def gettype(value):
    return value.__class__.__name__

register.filter('gettype', gettype)