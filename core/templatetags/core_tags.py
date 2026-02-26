# core/templatetags/core_tags.py

from django import template
register = template.Library()

@register.filter
def get_historial(mapa, clave_compuesta):
    """
    Busca una serie en el mapa de historial usando una clave 'ejercicio_id-numero_serie'.
    Uso: mapa_historial|get_historial:'12-1'
    """
    if not mapa:
        return None
    return mapa.get(clave_compuesta)

@register.simple_tag
def make_history_key(ejercicio_id, numero_serie):
    """
    Genera la clave para buscar en el diccionario.
    """
    return (ejercicio_id, numero_serie) # Tu clave en la vista era una tupla (id, num)