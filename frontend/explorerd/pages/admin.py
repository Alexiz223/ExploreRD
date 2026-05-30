import reflex as rx
import httpx
from typing import Any, List, Dict
from explorerd.components.layout import navbar, footer

API_URL = "http://localhost:8000"

class AdminState(rx.State):
    reservas: List[Dict[str, Any]] = []
    mensajes: List[Dict[str, Any]] = []
    ofertas: List[Dict[str, Any]] = []
    tab_actual: str = "reservas"
    cargando: bool = False
    error_msg: str = ""
    exito_msg: str = ""

    # Formulario oferta
    form_id: int = 0
    form_nombre: str = ""
    form_descripcion: str = ""
    form_precio: str = ""
    form_duracion: str = ""
    form_ubicacion: str = ""
    form_imagen: str = ""
    form_cupos: str = "10"
    dialog_abierto: bool = False
    modo_edicion: bool = False

    # Formulario editar cupos de reserva
    reserva_edit_id: int = 0
    reserva_edit_cupos: str = ""
    dialog_cupos_abierto: bool = False

    def set_form_nombre(self, v: str): self.form_nombre = v
    def set_form_descripcion(self, v: str): self.form_descripcion = v
    def set_form_precio(self, v: str): self.form_precio = v
    def set_form_duracion(self, v: str): self.form_duracion = v
    def set_form_ubicacion(self, v: str): self.form_ubicacion = v
    def set_form_imagen(self, v: str): self.form_imagen = v
    def set_form_cupos(self, v: str): self.form_cupos = v
    def set_dialog_abierto(self, v: bool): self.dialog_abierto = v
    def set_dialog_cupos_abierto(self, v: bool): self.dialog_cupos_abierto = v
    def set_reserva_edit_cupos(self, v: str): self.reserva_edit_cupos = v
    def cambiar_tab(self, tab: str): self.tab_actual = tab

    async def cargar_datos(self):
        self.cargando = True
        self.error_msg = ""
        self.exito_msg = ""
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                r_res = await client.get(f"{API_URL}/reservas/")
                r_of  = await client.get(f"{API_URL}/ofertas/")
                r_msg = await client.get(f"{API_URL}/contacto/")
                self.reservas = r_res.json() if r_res.status_code == 200 else []
                self.ofertas  = r_of.json()  if r_of.status_code  == 200 else []
                self.mensajes = r_msg.json() if r_msg.status_code == 200 else []
        except Exception as e:
            self.error_msg = "⚠️ No se pudo conectar al servidor."
        self.cargando = False

    # ── RESERVAS ──────────────────────────────────────────
    async def confirmar_reserva(self, reserva_id: int):
        try:
            async with httpx.AsyncClient() as client:
                r = await client.put(
                    f"{API_URL}/reservas/{reserva_id}/estado",
                    params={"estado": "confirmada"}
                )
            if r.status_code == 200:
                self.exito_msg = f"Reserva #{reserva_id} confirmada."
            else:
                self.error_msg = f"Error: {r.text}"
            await self.cargar_datos()
        except Exception:
            self.error_msg = "Error al confirmar la reserva."

    async def cancelar_reserva(self, reserva_id: int):
        try:
            async with httpx.AsyncClient() as client:
                r = await client.put(
                    f"{API_URL}/reservas/{reserva_id}/estado",
                    params={"estado": "cancelada"}
                )
            if r.status_code == 200:
                self.exito_msg = f"Reserva #{reserva_id} cancelada."
            else:
                self.error_msg = f"Error: {r.text}"
            await self.cargar_datos()
        except Exception:
            self.error_msg = "Error al cancelar la reserva."

    async def eliminar_reserva(self, reserva_id: int):
        try:
            async with httpx.AsyncClient() as client:
                await client.delete(f"{API_URL}/reservas/{reserva_id}")
            self.exito_msg = f"Reserva #{reserva_id} eliminada."
            await self.cargar_datos()
        except Exception:
            self.error_msg = "Error al eliminar la reserva."

    def abrir_modal_cupos(self, reserva_id: int, cupos_actuales: int):
        self.reserva_edit_id = reserva_id
        self.reserva_edit_cupos = str(cupos_actuales)
        self.dialog_cupos_abierto = True

    async def guardar_cupos(self):
        try:
            nuevos_cupos = int(self.reserva_edit_cupos or 0)
            async with httpx.AsyncClient() as client:
                r = await client.patch(
                    f"{API_URL}/reservas/{self.reserva_edit_id}/cupos",
                    params={"cupos": nuevos_cupos}
                )
            if r.status_code == 200:
                self.exito_msg = f"Cupos de reserva #{self.reserva_edit_id} actualizados."
            else:
                self.error_msg = f"Error: {r.text}"
            self.dialog_cupos_abierto = False
            await self.cargar_datos()
        except Exception:
            self.error_msg = "Error al actualizar cupos."

    # ── MENSAJES ──────────────────────────────────────────
    async def eliminar_mensaje(self, mensaje_id: int):
        try:
            async with httpx.AsyncClient() as client:
                await client.delete(f"{API_URL}/contacto/{mensaje_id}")
            self.exito_msg = "Mensaje eliminado."
            await self.cargar_datos()
        except Exception:
            self.error_msg = "Error al eliminar el mensaje."

    # ── OFERTAS ───────────────────────────────────────────
    def abrir_modal_nueva(self):
        self.form_id = 0
        self.form_nombre = ""
        self.form_descripcion = ""
        self.form_precio = ""
        self.form_duracion = ""
        self.form_ubicacion = ""
        self.form_imagen = ""
        self.form_cupos = "10"
        self.modo_edicion = False
        self.dialog_abierto = True

    def abrir_modal_editar(self, oferta: Dict[str, Any]):
        self.form_id         = int(oferta.get("id", 0))
        self.form_nombre     = str(oferta.get("nombre", ""))
        self.form_descripcion= str(oferta.get("descripcion", ""))
        self.form_precio     = str(oferta.get("precio", ""))
        self.form_duracion   = str(oferta.get("duracion", "") or "")
        self.form_ubicacion  = str(oferta.get("ubicacion", "") or "")
        self.form_imagen     = str(oferta.get("imagen_url", "") or "")
        self.form_cupos      = str(oferta.get("cupos_disponibles", 10))
        self.modo_edicion    = True
        self.dialog_abierto  = True

    async def guardar_oferta(self):
        if not self.form_nombre or not self.form_precio:
            self.error_msg = "Nombre y precio son obligatorios."
            return
        payload = {
            "nombre": self.form_nombre,
            "descripcion": self.form_descripcion or "Sin descripción",
            "precio": float(self.form_precio),
            "duracion": self.form_duracion or None,
            "ubicacion": self.form_ubicacion or None,
            "imagen_url": self.form_imagen or None,
            "cupos_disponibles": int(self.form_cupos or 10),
        }
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                if self.modo_edicion:
                    r = await client.put(f"{API_URL}/ofertas/{self.form_id}", json=payload)
                else:
                    r = await client.post(f"{API_URL}/ofertas/", json=payload)
            if r.status_code in (200, 201):
                self.exito_msg = "Oferta guardada correctamente."
                self.dialog_abierto = False
                await self.cargar_datos()
            else:
                self.error_msg = f"Error del servidor: {r.text}"
        except Exception as e:
            self.error_msg = f"Error de conexión: {str(e)}"

    async def eliminar_oferta(self, oferta_id: int):
        try:
            async with httpx.AsyncClient() as client:
                await client.delete(f"{API_URL}/ofertas/{oferta_id}")
            self.exito_msg = f"Oferta #{oferta_id} eliminada."
            await self.cargar_datos()
        except Exception:
            self.error_msg = "Error al eliminar la oferta."


# ── COMPONENTES ───────────────────────────────────────────

def tarjeta_metrica(titulo: str, valor, icono: str, color: str) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.vstack(
                rx.text(titulo.upper(), font_size="0.72rem", font_weight="700", color="#718096"),
                rx.text(valor, font_size="2rem", font_weight="800", color="#1a202c"),
                align_items="start", spacing="1"
            ),
            rx.spacer(),
            rx.text(icono, font_size="2rem"),
        ),
        padding="1.5rem", background="white", border_radius="12px",
        border_left=f"4px solid {color}",
        box_shadow="0 4px 6px -1px rgba(0,0,0,0.05)", width="100%"
    )

def badge_estado(estado: rx.Var) -> rx.Component:
    return rx.badge(
        estado,
        color_scheme=rx.cond(
            estado == "confirmada", "green",
            rx.cond(estado == "cancelada", "red", "yellow")
        ),
        variant="soft"
    )

def fila_reserva(reserva: rx.Var) -> rx.Component:
    return rx.table.row(
        rx.table.cell(reserva["id"].to_string()),
        rx.table.cell(rx.text(reserva["nombre_cliente"], " ", reserva["apellido_cliente"])),
        rx.table.cell(reserva["email"]),
        rx.table.cell(reserva["telefono"]),
        rx.table.cell(reserva["fecha_reserva"]),
        rx.table.cell(reserva["num_personas"].to_string()),
        rx.table.cell(badge_estado(reserva["estado"])),
        rx.table.cell(
            rx.hstack(
                rx.button(
                    "✔", size="1", color_scheme="green", variant="soft",
                    on_click=AdminState.confirmar_reserva(reserva["id"].to(int)),
                ),
                rx.button(
                    "✖", size="1", color_scheme="yellow", variant="soft",
                    on_click=AdminState.cancelar_reserva(reserva["id"].to(int)),
                ),
                rx.button(
                    "🗑️", size="1", color_scheme="red", variant="ghost",
                    on_click=AdminState.eliminar_reserva(reserva["id"].to(int)),
                ),
                spacing="1"
            )
        ),
    )

def tarjeta_mensaje(msg: rx.Var) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text(msg["nombre"], font_weight="700", color="#1a202c"),
                rx.spacer(),
                rx.text(msg["email"], font_size="0.8rem", color="#718096"),
            ),
            rx.text(msg["mensaje"], font_size="0.9rem", color="#4a5568"),
            rx.hstack(
                rx.spacer(),
                rx.button(
                    "🗑️ Eliminar", size="1", color_scheme="red", variant="soft",
                    on_click=AdminState.eliminar_mensaje(msg["id"].to(int)),
                ),
            ),
            align_items="start", spacing="2", width="100%"
        ),
        background="white", border="1px solid #e2e8f0",
        border_radius="10px", padding="1rem 1.2rem", width="100%",
    )

def tarjeta_oferta(oferta: rx.Var) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.image(
                src=oferta["imagen_url"], width="100%", height="130px",
                object_fit="cover", border_radius="10px 10px 0 0"
            ),
            rx.vstack(
                rx.text(oferta["nombre"], font_weight="700", color="#1a202c"),
                rx.hstack(
                    rx.badge(oferta["ubicacion"], color_scheme="blue", variant="surface"),
                    rx.badge(oferta["duracion"], color_scheme="orange", variant="surface"),
                ),
                rx.text("RD$ ", oferta["precio"].to_string(), font_size="1.1rem", font_weight="800", color="#1a5c3a"),
                rx.text("Cupos: ", oferta["cupos_disponibles"].to_string(), font_size="0.85rem", color="#718096"),
                rx.hstack(
                    rx.button(
                        "✏️ Editar", size="1", color_scheme="blue", variant="soft",
                        on_click=AdminState.abrir_modal_editar(oferta),
                    ),
                    rx.button(
                        "🗑️ Eliminar", size="1", color_scheme="red", variant="soft",
                        on_click=AdminState.eliminar_oferta(oferta["id"].to(int)),
                    ),
                    justify="between", width="100%"
                ),
                padding="1rem", spacing="2", align_items="start", width="100%"
            ),
            spacing="0"
        ),
        border="1px solid #e2e8f0", border_radius="12px",
        background="white", width="100%",
        box_shadow="0 2px 4px rgba(0,0,0,0.04)"
    )


# ── PÁGINA ────────────────────────────────────────────────

@rx.page(route="/admin", title="Panel Admin - ExploreRD", on_load=AdminState.cargar_datos)
def admin() -> rx.Component:
    return rx.box(
        navbar(),

        rx.box(
            rx.vstack(
                rx.badge("🔒 Panel de Control Seguro", color_scheme="yellow", variant="surface"),
                rx.heading("Administración ExploreRD", size="8", color="white", font_weight="bold", text_align="center"),
                rx.text("Gestiona reservas, sugerencias de clientes y ofertas turísticas.", color="#e2e8f0", text_align="center"),
                spacing="2", align_items="center", padding="3rem 2rem",
            ),
            background="linear-gradient(135deg, #1a5c3a 0%, #14452b 100%)", width="100%",
        ),

        rx.center(
            rx.vstack(

                # Alertas
                rx.cond(
                    AdminState.error_msg != "",
                    rx.box(rx.text(AdminState.error_msg, color="#c53030", font_weight="600"),
                        background="#fff5f5", border="1px solid #fed7d7",
                        border_radius="8px", padding="1rem", width="100%"),
                    rx.box()
                ),
                rx.cond(
                    AdminState.exito_msg != "",
                    rx.box(rx.text(AdminState.exito_msg, color="#276749", font_weight="600"),
                        background="#f0fff4", border="1px solid #c6f6d5",
                        border_radius="8px", padding="1rem", width="100%"),
                    rx.box()
                ),

                # Métricas
                rx.grid(
                    tarjeta_metrica("Total Reservas", AdminState.reservas.length().to_string(), "📅", "#3182ce"),
                    tarjeta_metrica("Sugerencias",    AdminState.mensajes.length().to_string(), "📩", "#805ad5"),
                    tarjeta_metrica("Ofertas Activas",AdminState.ofertas.length().to_string(),  "🗺️", "#dd6b20"),
                    columns={"sm": "1", "md": "3"}, spacing="4", width="100%"
                ),

                # Tabs
                rx.hstack(
                    rx.button("📅 Reservas",   color_scheme="green",
                        variant=rx.cond(AdminState.tab_actual == "reservas", "solid", "outline"),
                        on_click=AdminState.cambiar_tab("reservas")),
                    rx.button("📩 Sugerencias", color_scheme="purple",
                        variant=rx.cond(AdminState.tab_actual == "mensajes", "solid", "outline"),
                        on_click=AdminState.cambiar_tab("mensajes")),
                    rx.button("🗺️ Ofertas",    color_scheme="orange",
                        variant=rx.cond(AdminState.tab_actual == "ofertas",  "solid", "outline"),
                        on_click=AdminState.cambiar_tab("ofertas")),
                    spacing="3", width="100%"
                ),

                # Tab: Reservas
                rx.cond(
                    AdminState.tab_actual == "reservas",
                    rx.cond(
                        AdminState.reservas.length() > 0,
                        rx.box(
                            rx.table.root(
                                rx.table.header(
                                    rx.table.row(
                                        rx.table.column_header_cell("ID"),
                                        rx.table.column_header_cell("Cliente"),
                                        rx.table.column_header_cell("Email"),
                                        rx.table.column_header_cell("Teléfono"),
                                        rx.table.column_header_cell("Fecha"),
                                        rx.table.column_header_cell("Pers."),
                                        rx.table.column_header_cell("Estado"),
                                        rx.table.column_header_cell("Acciones"),
                                    )
                                ),
                                rx.table.body(rx.foreach(AdminState.reservas, fila_reserva)),
                                variant="surface", width="100%"
                            ),
                            overflow_x="auto", width="100%"
                        ),
                        rx.center(rx.text("No hay reservas registradas aún.", color="#718096", padding="3rem"))
                    )
                ),

                # Tab: Sugerencias
                rx.cond(
                    AdminState.tab_actual == "mensajes",
                    rx.cond(
                        AdminState.mensajes.length() > 0,
                        rx.vstack(rx.foreach(AdminState.mensajes, tarjeta_mensaje), width="100%", spacing="3"),
                        rx.center(rx.text("No hay sugerencias aún.", color="#718096", padding="3rem"))
                    )
                ),

                # Tab: Ofertas
                rx.cond(
                    AdminState.tab_actual == "ofertas",
                    rx.vstack(
                        rx.hstack(
                            rx.button("➕ Nueva Oferta", color_scheme="green", on_click=AdminState.abrir_modal_nueva),
                            width="100%", justify="end"
                        ),
                        rx.cond(
                            AdminState.ofertas.length() > 0,
                            rx.grid(
                                rx.foreach(AdminState.ofertas, tarjeta_oferta),
                                columns={"sm": "1", "md": "2", "lg": "3"}, spacing="4", width="100%"
                            ),
                            rx.center(rx.text("No hay ofertas activas.", color="#718096", padding="3rem"))
                        ),
                        width="100%", spacing="4"
                    )
                ),

                max_width="1200px", width="100%", padding="2rem", spacing="5"
            ),
            width="100%"
        ),

        # Modal: Crear / Editar Oferta
        rx.dialog.root(
            rx.dialog.content(
                rx.dialog.title(rx.cond(AdminState.modo_edicion, "Editar Oferta", "Nueva Oferta")),
                rx.vstack(
                    rx.text("Nombre *", font_weight="600"),
                    rx.input(value=AdminState.form_nombre, on_change=AdminState.set_form_nombre, width="100%", color="black"),
                    rx.text("Descripción *", font_weight="600"),
                    rx.text_area(value=AdminState.form_descripcion, on_change=AdminState.set_form_descripcion, width="100%", rows="3"),
                    rx.grid(
                        rx.vstack(
                            rx.text("Precio (RD$) *", font_weight="600"),
                            rx.input(value=AdminState.form_precio, on_change=AdminState.set_form_precio, type="number", width="100%"),
                        ),
                        rx.vstack(
                            rx.text("Duración", font_weight="600"),
                            rx.input(value=AdminState.form_duracion, on_change=AdminState.set_form_duracion, placeholder="Ej: 3 días", width="100%"),
                        ),
                        columns="2", spacing="4", width="100%"
                    ),
                    rx.grid(
                        rx.vstack(
                            rx.text("Ubicación", font_weight="600"),
                            rx.input(value=AdminState.form_ubicacion, on_change=AdminState.set_form_ubicacion, width="100%"),
                        ),
                        rx.vstack(
                            rx.text("Cupos disponibles", font_weight="600"),
                            rx.input(value=AdminState.form_cupos, on_change=AdminState.set_form_cupos, type="number", width="100%"),
                        ),
                        columns="2", spacing="4", width="100%"
                    ),
                    rx.text("URL de Imagen", font_weight="600"),
                    rx.input(value=AdminState.form_imagen, on_change=AdminState.set_form_imagen, placeholder="https://...", width="100%"),
                    rx.cond(
                        AdminState.error_msg != "",
                        rx.text(AdminState.error_msg, color="red", font_size="0.85rem"),
                        rx.box()
                    ),
                    rx.hstack(
                        rx.dialog.close(rx.button("Cancelar", variant="soft", color_scheme="gray")),
                        rx.button(
                            rx.cond(AdminState.modo_edicion, "Guardar Cambios", "Crear Oferta"),
                            color_scheme="green", on_click=AdminState.guardar_oferta
                        ),
                        justify="end", width="100%", padding_top="1rem"
                    ),
                    align_items="start", spacing="3"
                )
            ),
            open=AdminState.dialog_abierto,
            on_open_change=AdminState.set_dialog_abierto
        ),

        footer(),
        background="#f8fafc",
        font_family="system-ui, -apple-system, sans-serif",
        min_height="100vh"
    )