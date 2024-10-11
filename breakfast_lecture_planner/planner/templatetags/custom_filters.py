from django import template


register = template.Library()


@register.filter
def get_item_by_index(sequence, index):
    try:
        return sequence[int(index)]
    except (IndexError, ValueError):
        return None
