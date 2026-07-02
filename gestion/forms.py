from django import forms
from .models import Pedido
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


# =========================
# REGISTRO
# =========================
class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


# =========================
# CHECKOUT
# =========================
class CheckoutForm(forms.ModelForm):

    class Meta:
        model = Pedido

        fields = [
            "nombre_cliente",
            "correo",
            "telefono",
            "direccion",
            "comuna",
            "referencia",
            "observaciones",
        ]

        widgets = {

            "nombre_cliente": forms.TextInput(
                attrs={
                    "class": "w-full rounded-lg border border-outline-variant bg-white px-4 py-3 focus:border-primary focus:ring-primary",
                    "placeholder": "Nombre completo",
                }
            ),

            "correo": forms.EmailInput(
                attrs={
                    "class": "w-full rounded-lg border border-outline-variant bg-white px-4 py-3 focus:border-primary focus:ring-primary",
                    "placeholder": "Correo electrónico",
                }
            ),

            "telefono": forms.TextInput(
                attrs={
                    "class": "w-full rounded-lg border border-outline-variant bg-white px-4 py-3 focus:border-primary focus:ring-primary",
                    "placeholder": "Ej: +56 9 1234 5678",
                }
            ),

            "direccion": forms.TextInput(
                attrs={
                    "class": "w-full rounded-lg border border-outline-variant bg-white px-4 py-3 focus:border-primary focus:ring-primary",
                    "placeholder": "Ej: Av. Providencia 1234",
                }
            ),

            "comuna": forms.TextInput(
                attrs={
                    "class": "w-full rounded-lg border border-outline-variant bg-white px-4 py-3 focus:border-primary focus:ring-primary",
                    "placeholder": "Ej: Providencia",
                }
            ),

            "referencia": forms.Textarea(
                attrs={
                    "rows": 2,
                    "class": "w-full rounded-lg border border-outline-variant bg-white px-4 py-3 focus:border-primary focus:ring-primary",
                    "placeholder": "Ej: Casa blanca con portón negro (opcional)",
                }
            ),

            "observaciones": forms.Textarea(
                attrs={
                    "rows": 3,
                    "class": "w-full rounded-lg border border-outline-variant bg-white px-4 py-3 focus:border-primary focus:ring-primary",
                    "placeholder": "Indicaciones adicionales para el pedido (opcional)",
                }
            ),
        }


# =========================
# COMPROBANTE
# =========================
class ComprobanteForm(forms.ModelForm):

    class Meta:
        model = Pedido
        fields = ["comprobante"]