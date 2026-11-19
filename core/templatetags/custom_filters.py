from django import template

register = template.Library()

@register.filter(name='split')
def split(value, arg=','):
    """Split string by delimiter."""
    if not value:
        return []
    return [item.strip() for item in str(value).split(arg)]

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Retrieve value from dictionary safely."""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None
