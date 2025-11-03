from django import template

register = template.Library()

@register.filter(name='dict_by_detalle_id')
def dict_by_detalle_id(forms, detalle_id):
    """
    Filtra los formularios del formset para devolver solo aquellos 
    cuya instancia (SerieEjercicio) pertenece al DetalleEntrenamiento dado.
    """
    return [
        form 
        for form in forms 
        if form.instance.detalle_entrenamiento_id == detalle_id
    ]

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Permite acceder a elementos de un diccionario con clave dinámica"""
    if not dictionary:
        return None
    return dictionary.get(key)