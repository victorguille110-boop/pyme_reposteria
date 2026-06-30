from django.urls import path
from . import views

urlpatterns = [

    path('', views.inicio),

    path('agregar/<int:producto_id>/', views.agregar_carrito),

    path('carrito/', views.ver_carrito),

    path('checkout/', views.checkout, name='checkout'),

    path('transferencia/', views.transferencia, name='transferencia'),

    # NUEVA PÁGINA DE ESPERA
    path('espera/', views.espera, name='espera'),

    path('aumentar/<int:producto_id>/', views.aumentar_producto),

    path('disminuir/<int:producto_id>/', views.disminuir_producto),

    path('eliminar/<int:producto_id>/', views.eliminar_producto),

    path('finalizar/', views.finalizar_compra, name='finalizar_compra'),
]