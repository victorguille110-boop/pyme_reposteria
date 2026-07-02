from django import template

register = template.Library()

@register.filter
def pesos(valor):
    try:
        return f"${int(valor):,}".replace(",", ".")
    except:
        return valor