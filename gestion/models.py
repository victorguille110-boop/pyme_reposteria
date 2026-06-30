from django.db import models
from django.conf import settings


class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre_categoria = models.CharField(max_length=50)

    class Meta:
        db_table = 'categorias'

    def __str__(self):
        return self.nombre_categoria


class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)

    id_categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='id_categoria'
    )

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    precio_base = models.DecimalField(max_digits=10, decimal_places=2)
    imagen_url = models.CharField(max_length=255, blank=True, null=True)
    stock_actual = models.IntegerField(default=0)

    class Meta:
        db_table = "productos"

    def __str__(self):
        return self.nombre

    @property
    def precio(self):
        return self.precio_base


# ======================================================
# PEDIDOS
# ======================================================

class Pedido(models.Model):

    ESTADOS = [
    ("Pendiente", "Pendiente de Revisión"),
    ("Revisando", "Pago en Revisión"),
    ("Pagado", "Pago Aprobado"),
    ("Preparacion", "En Preparación"),
    ("Despacho", "En Despacho"),
    ("Entregado", "Entregado"),
]
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pedidos")


    numero_pedido = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )

    nombre_cliente = models.CharField(max_length=100)

    correo = models.EmailField()

    telefono = models.CharField(max_length=20)

    direccion = models.CharField(
    max_length=250,
    default="Sin dirección"
)

    comuna = models.CharField(
    max_length=100,
    default="Sin comuna"
)

    referencia = models.TextField(
    blank=True,
    null=True,
    default=""
)

    observaciones = models.TextField(
        blank=True,
        null=True
    )

    fecha = models.DateTimeField(
        auto_now_add=True
    )

    metodo_pago = models.CharField(
        max_length=30,
        default="Transferencia Bancaria"
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="Pendiente"
    )

    total = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    comprobante = models.ImageField(
        upload_to="comprobantes/",
        blank=True,
        null=True
    )

    class Meta:
        db_table = "pedidos"
        ordering = ["-fecha"]

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

        if not self.numero_pedido:
            self.numero_pedido = f"MV-{self.id:05d}"
            super().save(update_fields=["numero_pedido"])

    def __str__(self):
        return f"{self.numero_pedido} - {self.nombre_cliente}"


# ======================================================
# DETALLE DEL PEDIDO
# ======================================================

class DetallePedido(models.Model):

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name="detalles"
    )

    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE
    )

    cantidad = models.PositiveIntegerField()

    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    class Meta:
        db_table = "detalle_pedidos_web"

    def __str__(self):
        return f"{self.pedido.numero_pedido} - {self.producto.nombre}"