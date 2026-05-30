import reflex as rx
import httpx
from datetime import datetime
from typing import Any
from explorerd.components.layout import navbar, footer

API_URL = "http://localhost:8000"


class ReservasState(rx.State):
    ofertas: list[dict[str, Any]] = []
    oferta_idx: int = 0
    nombre: str = ""
    apellido: str = ""
    email: str = ""
    telefono: str = ""
    fecha_reserva: str = ""       
    fecha_checkin: str = ""       
    fecha_checkout: str = ""      
    num_personas: int = 1
    metodo_pago: str = "tarjeta"
    notas: str = ""
    reserva_exitosa: bool = False
    reserva_id: int = 0
    error: str = ""
    loading: bool = False

    async def cargar_ofertas(self):
        # 🔄 REINICIO AUTOMÁTICO AL REFRESCAR LA PÁGINA
        self.reserva_exitosa = False
        self.error = ""
        self.loading = False
        
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(f"{API_URL}/ofertas/")
                if r.status_code == 200:
                    self.ofertas = r.json()
        except Exception:
            self.ofertas = []

    @rx.var
    def nombres_ofertas(self) -> list[str]:
        return [o["nombre"] for o in self.ofertas]

    @rx.var
    def precio_unitario(self) -> float:
        if not self.ofertas or self.oferta_idx >= len(self.ofertas):
            return 0.0
        return float(self.ofertas[self.oferta_idx]["precio"])

    @rx.var
    def num_noches(self) -> int:
        if not self.fecha_checkin or not self.fecha_checkout:
            return 1
        try:
            d1 = datetime.strptime(self.fecha_checkin, "%Y-%m-%d")
            d2 = datetime.strptime(self.fecha_checkout, "%Y-%m-%d")
            noches = (d2 - d1).days
            return noches if noches > 0 else 1
        except Exception:
            return 1

    @rx.var
    def total_calculado(self) -> float:
        return self.precio_unitario * self.num_personas * self.num_noches

    # 💰 STRINGS FORMATEADOS DESDE EL BACKEND PARA EVITAR ERRORES EN EL FRONTEND
    @rx.var
    def precio_unitario_str(self) -> str:
        return f"RD$ {self.precio_unitario:,.2f}"

    @rx.var
    def total_calculado_str(self) -> str:
        return f"RD$ {self.total_calculado:,.2f}"

    @rx.var
    def oferta_id_actual(self) -> int:
        if not self.ofertas or self.oferta_idx >= len(self.ofertas):
            return 1
        return int(self.ofertas[self.oferta_idx]["id"])

    def set_oferta(self, nombre: str):
        for i, o in enumerate(self.ofertas):
            if o["nombre"] == nombre:
                self.oferta_idx = i
                break

    def set_nombre(self, v): self.nombre = v
    def set_apellido(self, v): self.apellido = v
    def set_email(self, v): self.email = v
    def set_telefono(self, v): self.telefono = v
    
    def set_checkin(self, v): 
        self.fecha_checkin = v
        self.fecha_reserva = v  
        
    def set_checkout(self, v): 
        self.fecha_checkout = v
        
    def set_notas(self, v): self.notas = v
    def set_pago(self, v): self.metodo_pago = v

    def set_personas(self, v: str):
        try:
            n = int(v)
            if n > 0:
                self.num_personas = n
        except Exception:
            pass

    async def enviar(self):
        if not self.nombre or not self.apellido or not self.email or not self.fecha_checkin or not self.fecha_checkout:
            self.error = "Completa todos los campos obligatorios (*)."
            return
        if self.num_noches <= 0:
            self.error = "La fecha de Check-out debe ser posterior al Check-in."
            return
            
        self.error = ""
        self.loading = True
        
        detalles_estadia = f"\n\n--- DETALLES DE ESTADÍA AUTOMÁTICOS ---\n• Check-in: {self.fecha_checkin}\n• Check-out: {self.fecha_checkout}\n• Total de noches: {self.num_noches}"
        notas_finales = self.notas + detalles_estadia

        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "oferta_id": self.oferta_id_actual,
                    "nombre_cliente": self.nombre,
                    "apellido_cliente": self.apellido,
                    "email": self.email,
                    "telefono": self.telefono,
                    "fecha_reserva": self.fecha_reserva,
                    "num_personas": self.num_personas,
                    "metodo_pago": self.metodo_pago,
                    "notas": notas_finales,
                }
                r = await client.post(f"{API_URL}/reservas/", json=payload)
                if r.status_code == 200:
                    self.reserva_id = r.json()["id"]
                    self.reserva_exitosa = True
                else:
                    self.error = r.json().get("detail", "Error al procesar la reserva.")
        except Exception:
            self.error = "Error de conexión con el servidor FastAPI."
        self.loading = False


def inp(label, placeholder, value, on_change, tipo="text", req=True):
    return rx.vstack(
        rx.text(
            label + (" *" if req else ""),
            font_size="0.85rem",
            font_weight="600",
            color="#2d3748",
        ),
        rx.input(
            placeholder=placeholder,
            value=value,
            on_change=on_change,
            type=tipo,
            border="1px solid #cbd5e1",
            border_radius="8px",
            padding="0.65rem 1rem",
            width="100%",
            font_size="0.9rem",
            style={
                "color": "#1a202c",
                "backgroundColor": "white",
                "boxShadow": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
                "&::placeholder": {
                    "color": "#a0aec0",
                },
            },
            _focus={
                "border_color": "#1a5c3a", 
                "outline": "none",
                "box_shadow": "0 0 0 3px rgba(26, 92, 58, 0.15)"
            },
        ),
        spacing="1",
        align_items="start",
        width="100%",
    )


def pago_btn(label, valor):
    return rx.box(
        label,
        on_click=ReservasState.set_pago(valor),
        padding="0.6rem 1.2rem",
        border_radius="8px",
        cursor="pointer",
        background=rx.cond(ReservasState.metodo_pago == valor, "#1a5c3a", "white"),
        color=rx.cond(ReservasState.metodo_pago == valor, "white", "#4a5568"),
        border=rx.cond(ReservasState.metodo_pago == valor, "1px solid #1a5c3a", "1px solid #cbd5e1"),
        font_size="0.88rem",
        font_weight="600",
        box_shadow="0 1px 2px 0 rgba(0, 0, 0, 0.05)",
        transition="all 0.2s ease",
        _hover={"transform": "translateY(-1px)", "box_shadow": "0 4px 6px -1px rgba(0,0,0,0.1)"}
    )


@rx.page(route="/reservas", title="Reservas - ExploreRD")
def reservas() -> rx.Component:
    return rx.box(
        navbar(),
        # 🎯 HERO BANNER COMPLETAMENTE CENTRADO EN LA PÁGINA
        rx.box(
            rx.center(
                rx.vstack(
                    rx.text("Reserva tu aventura", font_size="2.4rem", font_weight="800", color="white", letter_spacing="-0.025em"),
                    rx.text(
                        "Completa tus datos de estadía y calcula tu presupuesto en tiempo real de forma automática.",
                        color="rgba(255,255,255,0.9)",
                        font_size="1rem",
                        max_width="600px",
                        text_align="center",
                    ),
                    spacing="2",
                    align_items="center",
                ),
                width="100%",
            ),
            background="linear-gradient(135deg, #14452b 0%, #1a5c3a 100%)",
            padding="4rem 2rem",
        ),

        rx.cond(
            ReservasState.reserva_exitosa,
            # ✨ VENTANA DE ÉXITO PERFECTAMENTE CENTRADA
            rx.center(
                rx.box(
                    rx.vstack(
                        rx.text("🎉", font_size="4rem", margin_bottom="0.5rem"),
                        rx.text("¡Reserva Confirmada Exitosamente!", font_size="1.7rem", font_weight="800", color="#1a5c3a", text_align="center"),
                        rx.text("Tu solicitud ha sido procesada por el sistema.", color="#718096", font_size="0.95rem", text_align="center"),
                        rx.box(
                            rx.text(
                                "Código identificador: #", ReservasState.reserva_id,
                                font_size="1.1rem",
                                color="#14452b",
                                font_weight="700",
                                text_align="center"
                            ),
                            background="#e6fffa",
                            border="1px solid #b2f5ea",
                            border_radius="8px",
                            padding="0.8rem 2rem",
                            margin_top="1rem",
                            margin_bottom="1rem",
                        ),
                        rx.link(
                            rx.button(
                                "← Volver al inicio",
                                background="#1a5c3a",
                                color="white",
                                border_radius="8px",
                                padding="0.7rem 2rem",
                                font_weight="700",
                                cursor="pointer",
                                _hover={"background": "#c8962a", "transform": "translateY(-1px)"},
                                transition="all 0.2s",
                            ),
                            href="/",
                        ),
                        spacing="3",
                        align="center",
                    ),
                    background="white",
                    border_radius="16px",
                    box_shadow="0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)",
                    padding="3rem",
                    max_width="500px",
                    width="100%",
                ),
                padding="4rem 2rem",
                width="100%",
            ),

            # 📦 CUERPO PRINCIPAL DEL FORMULARIO Y COTIZACIÓN ALINEADOS AL MEDIO
            rx.center(
                rx.box(
                    rx.hstack(
                        # COLUMNA IZQUIERDA: FORMULARIO
                        rx.vstack(
                            rx.text("Información Personal", font_size="1.25rem", font_weight="700", color="#1a202c"),
                            rx.grid(
                                inp("Nombre", "Ej. Alejandro", ReservasState.nombre, ReservasState.set_nombre),
                                inp("Apellido", "Ej. Jimenez", ReservasState.apellido, ReservasState.set_apellido),
                                columns="2",
                                spacing="4",
                                width="100%",
                            ),
                            rx.grid(
                                inp("Correo Electrónico", "tu@correo.com", ReservasState.email, ReservasState.set_email, tipo="email"),
                                inp("Teléfono de Contacto", "Ej. 809-555-0199", ReservasState.telefono, ReservasState.set_telefono, req=False),
                                columns="2",
                                spacing="4",
                                width="100%",
                            ),

                            rx.divider(border_color="#e2e8f0", margin_top="0.5rem", margin_bottom="0.5rem"),
                            rx.text("Detalles de Estadía y Planificación", font_size="1.25rem", font_weight="700", color="#1a202c"),

                            rx.vstack(
                                rx.text("Destino Seleccionado *", font_size="0.85rem", font_weight="600", color="#2d3748"),
                                rx.select(
                                    ReservasState.nombres_ofertas,
                                    on_change=ReservasState.set_oferta,
                                    border="1px solid #cbd5e1",
                                    border_radius="8px",
                                    width="100%",
                                    padding="0.4rem",
                                    font_size="0.9rem",
                                    color="#1a202c",
                                    background="white",
                                    box_shadow="0 1px 2px 0 rgba(0, 0, 0, 0.05)",
                                ),
                                spacing="1",
                                align_items="start",
                                width="100%",
                            ),
                            
                            rx.grid(
                                inp("Fecha Entrada 🛫", "", ReservasState.fecha_checkin, ReservasState.set_checkin, tipo="date"),
                                inp("Fecha Salida 🛬", "", ReservasState.fecha_checkout, ReservasState.set_checkout, tipo="date"),
                                inp("N° Personas 👥", "1", ReservasState.num_personas.to_string(), ReservasState.set_personas, tipo="number"),
                                columns="3",
                                spacing="4",
                                width="100%",
                            ),

                            rx.divider(border_color="#e2e8f0", margin_top="0.5rem", margin_bottom="0.5rem"),
                            rx.vstack(
                                rx.text("Método de Pago Preferido *", font_size="0.85rem", font_weight="600", color="#2d3748"),
                                rx.hstack(
                                    pago_btn("💳 Tarjeta de Crédito", "tarjeta"),
                                    pago_btn("🏦 Transferencia", "transferencia"),
                                    pago_btn("💵 Efectivo", "efectivo"),
                                    flex_wrap="wrap",
                                    spacing="3",
                                ),
                                align_items="start",
                                width="100%",
                            ),

                            rx.divider(border_color="#e2e8f0", margin_top="0.5rem", margin_bottom="0.5rem"),
                            rx.vstack(
                                rx.text("Notas Especiales", font_size="0.85rem", font_weight="600", color="#2d3748"),
                                rx.text_area(
                                    placeholder="Especificaciones de habitaciones, requerimientos alimenticios o asistencia...",
                                    value=ReservasState.notas,
                                    on_change=ReservasState.set_notas,
                                    border="1px solid #cbd5e1",
                                    border_radius="8px",
                                    padding="0.7rem 1rem",
                                    width="100%",
                                    rows="3",
                                    font_size="0.9rem",
                                    color="#1a202c",
                                    background="white",
                                    box_shadow="0 1px 2px 0 rgba(0, 0, 0, 0.05)",
                                    _focus={"border_color": "#1a5c3a", "outline": "none"},
                                ),
                                spacing="1",
                                align_items="start",
                                width="100%",
                            ),

                            rx.cond(
                                ReservasState.error != "",
                                rx.box(
                                    rx.text("⚠️ ", ReservasState.error, color="#c53030", font_size="0.88rem", font_weight="600"),
                                    background="#fff5f5",
                                    border="1px solid #fed7d7",
                                    border_radius="8px",
                                    padding="0.75rem 1.2rem",
                                    width="100%",
                                ),
                                rx.box(),
                            ),

                            spacing="5",
                            align_items="start",
                            flex="2",
                            min_width="320px",
                        ),

                        # COLUMNA DERECHA: RESUMEN DE COMPRA (FLOTANTE ELEGANTE)
                        rx.vstack(
                            rx.box(
                                rx.vstack(
                                    rx.text("Resumen de Cotización", font_size="1.2rem", font_weight="700", color="#1a202c"),
                                    rx.divider(border_color="#e2e8f0"),
                                    
                                    rx.hstack(
                                        rx.text("Precio base:", font_size="0.9rem", color="#4a5568"),
                                        rx.spacer(),
                                        rx.text(ReservasState.precio_unitario_str, font_size="0.9rem", font_weight="700", color="#1a202c"),
                                        width="100%",
                                    ),
                                    rx.hstack(
                                        rx.text("Cantidad personas:", font_size="0.9rem", color="#4a5568"),
                                        rx.spacer(),
                                        rx.text(ReservasState.num_personas.to_string(), font_size="0.9rem", font_weight="700", color="#1a202c"),
                                        width="100%",
                                    ),
                                    rx.hstack(
                                        rx.text("Noches calculadas:", font_size="0.9rem", color="#4a5568"),
                                        rx.spacer(),
                                        rx.text(ReservasState.num_noches.to_string(), font_size="0.9rem", font_weight="700", color="#1a5c3a"),
                                        width="100%",
                                    ),
                                    rx.hstack(
                                        rx.text("Vía de pago:", font_size="0.9rem", color="#4a5568"),
                                        rx.spacer(),
                                        rx.text(ReservasState.metodo_pago.upper(), font_size="0.85rem", font_weight="700", color="#718096"),
                                        width="100%",
                                    ),
                                    
                                    rx.divider(border_color="#e2e8f0"),
                                    rx.hstack(
                                        rx.text("Total Neto:", font_size="1rem", font_weight="700", color="#1a202c"),
                                        rx.spacer(),
                                        rx.text(
                                            ReservasState.total_calculado_str,
                                            font_size="1.4rem",
                                            font_weight="800",
                                            color="#c8962a",
                                        ),
                                        width="100%",
                                    ),
                                    rx.divider(border_color="#e2e8f0"),
                                    
                                    rx.vstack(
                                        rx.text("Servicios Incluidos de Origen:", font_size="0.78rem", color="#718096", font_weight="700", text_transform="uppercase"),
                                        rx.text("• Asistencia y guías certificados Mitur", font_size="0.82rem", color="#4a5568"),
                                        rx.text("• Logística de transporte completa", font_size="0.82rem", color="#4a5568"),
                                        rx.text("• Póliza de seguro médico básica", font_size="0.82rem", color="#4a5568"),
                                        spacing="1",
                                        align_items="start",
                                    ),
                                    spacing="3",
                                    align_items="start",
                                    width="100%",
                                ),
                                background="#f8fafc",
                                border="1px solid #e2e8f0",
                                border_radius="12px",
                                box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
                                padding="1.75rem",
                                width="100%",
                            ),
                            
                            rx.button(
                                rx.cond(
                                    ReservasState.loading,
                                    rx.spinner(color="white", size="2"),
                                    rx.text("Procesar Reserva de Viaje →"),
                                ),
                                on_click=ReservasState.enviar,
                                background="#1a5c3a",
                                color="white",
                                border="none",
                                border_radius="8px",
                                padding="0.9rem 1.5rem",
                                font_weight="700",
                                font_size="0.95rem",
                                width="100%",
                                cursor="pointer",
                                box_shadow="0 4px 6px -1px rgba(26, 92, 58, 0.2)",
                                _hover={"background": "#14452b", "transform": "translateY(-1px)", "box_shadow": "0 10px 15px -3px rgba(26, 92, 58, 0.3)"},
                                transition="all 0.2s",
                                disabled=ReservasState.loading,
                            ),
                            rx.text("🔒 Transacción segura y verificada.", font_size="0.75rem", color="#a0aec0", text_align="center", width="100%"),
                            spacing="4",
                            min_width="290px",
                            width="320px",
                        ),
                        spacing="8",
                        align_items="start",
                        flex_wrap="wrap",
                        width="100%",
                    ),
                    max_width="1140px",
                    width="100%",
                ),
                padding="4rem 2rem",
                width="100%",
            ),
        ),
        footer(),
        background="#ffffff",
        font_family="system-ui, -apple-system, sans-serif",
        on_mount=ReservasState.cargar_ofertas,
    )