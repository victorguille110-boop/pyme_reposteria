from django import forms
from .models import Pedido
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

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
                    "class": "form-control",
                    "placeholder": "Nombre completo",
                }
            ),

            "correo": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Correo electrónico",
                }
            ),

            "telefono": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Teléfono",
                }
            ),

            "direccion": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Dirección de despacho",
                }
            ),

            "comuna": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Comuna",
                }
            ),

            "referencia": forms.Textarea(
                attrs={
                    "rows": 2,
                    "placeholder": "Referencia para encontrar el domicilio (opcional)",
                }
            ),

            "observaciones": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Observaciones del pedido (opcional)",
                }
            ),

        }
        # =========================
# FORMULARIO COMPROBANTE
# =========================

class ComprobanteForm(forms.ModelForm):

    class Meta:
        model = Pedido
        fields = ["comprobante"]