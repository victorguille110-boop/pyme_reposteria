from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail

from .models import Producto, Categoria, Pedido, DetallePedido
from .forms import CheckoutForm

from django.contrib.auth import login as auth_login, logout as auth_logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistroForm

from django.contrib.auth.decorators import login_required

@login_required
def panel(request):
    pedidos = Pedido.objects.filter(usuario=request.user)[:1]  # el más reciente
    pedido_actual = pedidos.first() if pedidos else None
    historial = Pedido.objects.filter(usuario=request.user)

    return render(request, "gestion/panel.html", {
        "pedido_actual": pedido_actual,
        "total_pedidos": historial.count(),
    })

def registro(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "Cuenta creada correctamente.")
            return redirect("/")
    else:
        form = RegistroForm()
    return render(request, "gestion/registro.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect("/")
    else:
        form = AuthenticationForm()
    return render(request, "gestion/login.html", {"form": form})


def logout_view(request):
    auth_logout(request)
    return redirect("/")

# =========================
# HOME
# =========================
def inicio(request):
    busqueda = request.GET.get('buscar')
    categoria_id = request.GET.get('categoria')

    productos = Producto.objects.select_related('id_categoria').all()

    if busqueda:
        productos = productos.filter(nombre__icontains=busqueda)

    if categoria_id:
        try:
            categoria_id = int(categoria_id)
            productos = productos.filter(id_categoria=categoria_id)
        except:
            categoria_id = None

    carrito = request.session.get('carrito', {})
    cantidad_carrito = sum(carrito.values())
    categorias = Categoria.objects.all()

    return render(request, 'gestion/index.html', {
        'productos': productos,
        'cantidad_carrito': cantidad_carrito,
        'categorias': categorias,
        'categoria_activa': categoria_id,
    })


# =========================
# AGREGAR CARRITO
# =========================
def agregar_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})

    producto_id = str(producto_id)
    producto = get_object_or_404(Producto, id_producto=producto_id)

    if producto.stock_actual > 0:
        producto.stock_actual -= 1
        producto.save()

        carrito[producto_id] = carrito.get(producto_id, 0) + 1
        request.session['carrito'] = carrito

    return redirect('/')


# =========================
# VER CARRITO
# =========================
def ver_carrito(request):
    carrito = request.session.get('carrito', {})

    productos = []
    subtotal = 0
    cantidad_carrito = 0

    for producto_id, cantidad in carrito.items():
        producto = Producto.objects.get(id_producto=producto_id)

        item_subtotal = producto.precio_base * cantidad
        subtotal += item_subtotal
        cantidad_carrito += cantidad

        productos.append({
            "producto": producto,
            "cantidad": cantidad,
            "subtotal": item_subtotal,
        })

    despacho = 5000
    total = subtotal + despacho

    return render(request, "gestion/carrito.html", {
        "productos": productos,
        "subtotal": subtotal,
        "despacho": despacho,
        "total": total,
        "cantidad_carrito": cantidad_carrito,
    })


# =========================
# CHECKOUT
# =========================
def checkout(request):
    carrito = request.session.get("carrito", {})

    if not carrito:
        return redirect("/carrito/")

    productos = []
    subtotal = 0

    for producto_id, cantidad in carrito.items():
        producto = Producto.objects.get(id_producto=producto_id)

        item_subtotal = producto.precio_base * cantidad
        subtotal += item_subtotal

        productos.append({
            "producto": producto,
            "cantidad": cantidad,
            "subtotal": item_subtotal,
        })

    despacho = 5000
    total_final = subtotal + despacho

    if request.method == "POST":

        form = CheckoutForm(request.POST, request.FILES)

        if form.is_valid():
            if request.user.is_authenticated:
                pedido.usuario = request.user
            pedido = form.save(commit=False)
            pedido.total = total_final
            pedido.estado = "Pendiente"
            pedido.metodo_pago = "Transferencia"
            pedido.save()

            # Guardar detalles
            for item in productos:
                DetallePedido.objects.create(
                    pedido=pedido,
                    producto=item["producto"],
                    cantidad=item["cantidad"],
                    precio=item["producto"].precio_base,
                    subtotal=item["subtotal"],
                )

            # Enviar correo
            send_mail(
                subject="Pedido recibido - Marcelavovo",
                message=f"""
Hola {pedido.nombre_cliente},

Tu pedido {pedido.numero_pedido} fue recibido correctamente.

Total: ${pedido.total}

Estado: En revisión de pago.

Gracias por tu compra.
""",
                from_email=None,
                recipient_list=[pedido.correo],
                fail_silently=False,
            )

            # Limpiar carrito
            request.session["carrito"] = {}

            # Guardar pedido
            request.session["pedido_id"] = pedido.id

            return redirect("transferencia")

    else:
        form = CheckoutForm()

    return render(request, "gestion/checkout.html", {
        "form": form,
        "productos": productos,
        "subtotal": subtotal,
        "despacho": despacho,
        "total": total_final,
    })


# =========================
# TRANSFERENCIA
# =========================
def transferencia(request):

    pedido_id = request.session.get("pedido_id")

    if not pedido_id:
        return redirect("/")

    pedido = get_object_or_404(Pedido, pk=pedido_id)

    if request.method == "POST":
        archivo = request.FILES.get("comprobante")

        if archivo:
            pedido.comprobante = archivo
            pedido.estado = "Revisando"
            pedido.save()

            return redirect("espera")

    return render(request, "gestion/transferencia.html", {
        "pedido": pedido
    })


# =========================
# FINALIZAR COMPRA
# =========================
def finalizar_compra(request):
    request.session['carrito'] = {}
    request.session['datos_cliente'] = {}
    return render(request, "gestion/confirmacion.html")

# =========================
# ESPERA CONFIRMACIÓN
# =========================
def espera(request):

    pedido_id = request.session.get("pedido_id")

    if not pedido_id:
        return redirect("/")

    pedido = get_object_or_404(Pedido, pk=pedido_id)

    return render(request, "gestion/espera.html", {
        "pedido": pedido
    })


# =========================
# AUMENTAR PRODUCTO
# =========================
def aumentar_producto(request, producto_id):

    carrito = request.session.get("carrito", {})
    producto_id = str(producto_id)

    producto = get_object_or_404(Producto, id_producto=producto_id)

    if producto.stock_actual > 0:
        producto.stock_actual -= 1
        producto.save()

        carrito[producto_id] = carrito.get(producto_id, 0) + 1
        request.session["carrito"] = carrito

    return redirect("/carrito/")


# =========================
# DISMINUIR PRODUCTO
# =========================
def disminuir_producto(request, producto_id):

    carrito = request.session.get("carrito", {})
    producto_id = str(producto_id)

    if producto_id in carrito:

        producto = Producto.objects.get(id_producto=producto_id)

        producto.stock_actual += 1
        producto.save()

        carrito[producto_id] -= 1

        if carrito[producto_id] <= 0:
            del carrito[producto_id]

        request.session["carrito"] = carrito

    return redirect("/carrito/")


# =========================
# ELIMINAR PRODUCTO
# =========================
def eliminar_producto(request, producto_id):

    carrito = request.session.get("carrito", {})
    producto_id = str(producto_id)

    if producto_id in carrito:

        cantidad = carrito[producto_id]

        producto = Producto.objects.get(id_producto=producto_id)

        producto.stock_actual += cantidad
        producto.save()

        del carrito[producto_id]

        request.session["carrito"] = carrito

    return redirect("/carrito/")

@login_required
def historial(request):
    pedidos = Pedido.objects.filter(usuario=request.user)
    return render(request, "gestion/historial.html", {"pedidos": pedidos})


@login_required
def detalle_pedido(request, pedido_id):
    pedido = get_object_or_404(Pedido, id_pedido=pedido_id, usuario=request.user)
    return render(request, "gestion/detalle_pedido.html", {"pedido": pedido})