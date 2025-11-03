# core/templatetags/core_tags.py

from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Permite acceder a un valor de diccionario por clave en plantillas."""
    return dictionary.get(key)