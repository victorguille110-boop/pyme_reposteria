from django.contrib import admin
from django.core.mail import send_mail

from .models import Producto, Categoria, Pedido, DetallePedido


# =========================
# PRODUCTOS
# =========================
admin.site.register(Producto)
admin.site.register(Categoria)


# =========================
# DETALLE PEDIDO
# =========================
class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0


# =========================
# PEDIDOS (REPOSTERA)
# =========================
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):

    list_display = (
        "numero_pedido",
        "nombre_cliente",
        "estado",
        "total",
        "fecha",
        "estado_visual",
        "tiene_comprobante"
    )

    list_filter = ("estado",)

    search_fields = (
        "numero_pedido",
        "nombre_cliente",
        "correo"
    )

    inlines = [DetallePedidoInline]

    # =========================
    # ESTADO VISUAL
    # =========================
    def estado_visual(self, obj):
        if obj.estado == "Pendiente":
            return "❌ Pendiente"
        elif obj.estado == "Revisando":
            return "⏳ En revisión"
        elif obj.estado == "Pagado":
            return "✅ Pagado"
        elif obj.estado == "Preparacion":
            return "🍰 En preparación"
        elif obj.estado == "Despacho":
            return "🚚 En despacho"
        elif obj.estado == "Entregado":
            return "📦 Entregado"
        return obj.estado

    estado_visual.short_description = "Estado"

    # =========================
    # COMPROBANTE
    # =========================
    def tiene_comprobante(self, obj):
        return bool(obj.comprobante)

    tiene_comprobante.boolean = True
    tiene_comprobante.short_description = "Comprobante"

    # =========================
    # ACCIONES ADMIN
    # =========================
    actions = ["marcar_pagado", "marcar_revisando"]

    def marcar_pagado(self, request, queryset):

        for pedido in queryset:

            # descontar stock
            for detalle in pedido.detalles.all():
                producto = detalle.producto
                producto.stock_actual -= detalle.cantidad
                producto.save()

            pedido.estado = "Pagado"
            pedido.save()

            # =========================
            # EMAIL REAL AL CLIENTE
            # =========================
            send_mail(
                subject="Pago aprobado - Marcelavovo",
                message=f"""
Hola {pedido.nombre_cliente},

Tu pago del pedido {pedido.numero_pedido} fue aprobado.

Ya estamos preparando tu pedido 🍰

Gracias por tu compra.
""",
                from_email=None,
                recipient_list=[pedido.correo],
                fail_silently=False,     # IMPORTANTE para ver errores reales
            )

        self.message_user(request, "Pedidos marcados como PAGADOS + email enviado.")

    def marcar_revisando(self, request, queryset):
        queryset.update(estado="Revisando")
        self.message_user(request, "Pedidos marcados como EN REVISIÓN.")

    marcar_pagado.short_description = "✅ Marcar como Pagado"
    marcar_revisando.short_description = "⏳ Marcar como En Revisión"