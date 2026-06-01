import reflex as rx
import httpx
from typing import Any
from explorerd.components.layout import navbar, footer

API_URL = "http://localhost:8000"


class DescripcionState(rx.State):
    todas_las_ofertas: list[dict[str, Any]] = []
    ofertas: list[dict[str, Any]] = []
    idx_activo: int = 0
    loading: bool = False
    buscar_texto: str = ""

    @rx.var
    def oferta_activa(self) -> dict[str, Any]:
        if len(self.ofertas) == 0 or self.idx_activo >= len(self.ofertas):
            return {
                "nombre": "",
                "imagen_url": "",
                "duracion": "",
                "precio": "",
                "cupos_disponibles": 0,
                "descripcion_larga": "",
                "itinerario": "",
                "ubicacion": "",
            }
        return self.ofertas[self.idx_activo]

    @rx.var
    def descripcion_larga_texto(self) -> str:
        val = self.oferta_activa.get("descripcion_larga", "")
        if not val:
            return "Descripción detallada no disponible aún. Edita esta oferta desde el panel de administración para agregar una descripción."
        return str(val)

    @rx.var
    def itinerario_texto(self) -> str:
        val = self.oferta_activa.get("itinerario", "")
        if not val:
            return "Itinerario no disponible aún. Edita esta oferta desde el panel de administración para agregar el itinerario."
        return str(val)

    async def cargar_ofertas(self):
        self.loading = True
        self.buscar_texto = ""
        self.idx_activo = 0
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(f"{API_URL}/ofertas/")
                if r.status_code == 200:
                    datos = r.json()
                    self.todas_las_ofertas = datos
                    self.ofertas = datos
                else:
                    self.ofertas = []
                    self.todas_las_ofertas = []
        except Exception:
            self.ofertas = []
            self.todas_las_ofertas = []
        self.loading = False

    def filtrar_ofertas(self, valor: str):
        self.buscar_texto = valor
        query = valor.lower().strip()
        self.idx_activo = 0
        if not query:
            self.ofertas = self.todas_las_ofertas
        else:
            self.ofertas = [
                o for o in self.todas_las_ofertas
                if query in str(o.get("nombre", "")).lower()
                or query in str(o.get("ubicacion", "")).lower()
                or query in str(o.get("descripcion", "")).lower()
            ]

    def seleccionar(self, idx: int):
        self.idx_activo = idx


def tab_oferta(oferta: dict, index: int) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.image(
                src=oferta["imagen_url"],
                width="56px",
                height="48px",
                object_fit="cover",
                border_radius="6px",
                fallback="🏝️",
            ),
            rx.vstack(
                rx.text(oferta["nombre"], font_weight="600", color="#111111"),
                rx.text(oferta["ubicacion"], font_size="0.85rem", color="#666666"),
                align_items="start",
                spacing="0",
            ),
            spacing="3",
            align_items="center",
        ),
        cursor="pointer",
        padding="0.75rem",
        border="1px solid #eeeeee",
        border_radius="8px",
        width="100%",
        _hover={"background": "#f4f9f6", "border_color": "#1a5c3a"},
        on_click=DescripcionState.seleccionar(index),
    )


@rx.page(route="/descripcion", title="Destinos - ExploreRD")
def descripcion() -> rx.Component:
    return rx.box(
        navbar(),

        rx.box(
            rx.vstack(
                rx.text("Nuestros Destinos", font_size="1.8rem", font_weight="700", color="#111111"),
                rx.text("Selecciona un destino para ver todos los detalles de la ruta", font_size="0.9rem", color="#666666"),
                rx.hstack(
                    rx.text("🔍", font_size="1rem", color="#777777"),
                    rx.input(
                        placeholder="Filtrar por provincia, hotel o palabras clave...",
                        value=DescripcionState.buscar_texto,
                        on_change=DescripcionState.filtrar_ofertas,
                        border="none",
                        background="transparent",
                        color="#111111",
                        width=["100%", "360px"],
                        _focus={"outline": "none"},
                        font_size="0.9rem",
                    ),
                    background="#f5f5f5",
                    padding="0.4rem 1.1rem",
                    border_radius="30px",
                    border="1px solid #e0e0e0",
                    margin_top="0.75rem",
                    align_items="center",
                ),
                spacing="1",
                align="center",
                margin_bottom="2.5rem",
            ),

            rx.cond(
                DescripcionState.loading,
                rx.center(rx.spinner(color="#1a5c3a", size="3"), padding="3rem"),

                rx.cond(
                    DescripcionState.ofertas.length() == 0,
                    rx.center(
                        rx.vstack(
                            rx.text("🔍 No se encontraron destinos.", color="#888888", font_weight="600"),
                            rx.text("Intenta con otra palabra clave.", color="#aaaaaa", font_size="0.85rem"),
                            spacing="1", align="center",
                        ),
                        padding="4rem", width="100%",
                    ),

                    rx.hstack(
                        # COLUMNA IZQUIERDA: lista de destinos
                        rx.vstack(
                            rx.foreach(
                                DescripcionState.ofertas,
                                lambda oferta, i: tab_oferta(oferta, i),
                            ),
                            spacing="3",
                            min_width="260px",
                            max_width="300px",
                            height="700px",
                            overflow_y="auto",
                            padding_right="0.5rem",
                        ),

                        # COLUMNA DERECHA: detalle del destino
                        rx.vstack(
                            # Imagen
                            rx.image(
                                src=DescripcionState.oferta_activa["imagen_url"],
                                width="100%",
                                height="280px",
                                object_fit="cover",
                                border_radius="10px",
                            ),

                            # Nombre
                            rx.text(
                                DescripcionState.oferta_activa["nombre"],
                                font_size="1.7rem",
                                font_weight="700",
                                color="#1a5c3a",
                                margin_top="0.5rem",
                            ),

                            # Badges: duración, precio, cupos
                            rx.hstack(
                                rx.box(
                                    rx.text("⏱ ", DescripcionState.oferta_activa["duracion"]),
                                    background="#e8f4ee",
                                    padding="0.3rem 0.75rem",
                                    border_radius="4px",
                                    font_size="0.85rem",
                                    font_weight="600",
                                    color="#1a5c3a",
                                ),
                                rx.box(
                                    rx.text("💰 RD$ ", DescripcionState.oferta_activa["precio"].to_string()),
                                    background="#fdf3e3",
                                    padding="0.3rem 0.75rem",
                                    border_radius="4px",
                                    font_size="0.85rem",
                                    font_weight="600",
                                    color="#c8962a",
                                ),
                                rx.box(
                                    rx.text("👥 ", DescripcionState.oferta_activa["cupos_disponibles"].to_string(), " cupos"),
                                    background="#f5f5f5",
                                    padding="0.3rem 0.75rem",
                                    border_radius="4px",
                                    font_size="0.85rem",
                                    font_weight="600",
                                    color="#555555",
                                ),
                                spacing="2",
                                flex_wrap="wrap",
                            ),

                            rx.divider(margin_y="0.75rem"),

                            # Descripción General
                            rx.vstack(
                                rx.hstack(
                                    rx.text("📋", font_size="1.1rem"),
                                    rx.text("Descripción General", font_weight="700", font_size="1.1rem", color="#111111"),
                                    spacing="2", align_items="center",
                                ),
                                rx.box(
                                    rx.text(
                                        DescripcionState.descripcion_larga_texto,
                                        color="#444444",
                                        line_height="1.8",
                                        font_size="0.92rem",
                                        white_space="pre-line",
                                    ),
                                    background="#f8fafc",
                                    border_left="3px solid #1a5c3a",
                                    padding="1rem 1.2rem",
                                    border_radius="0 8px 8px 0",
                                    width="100%",
                                ),
                                align_items="start",
                                width="100%",
                                spacing="2",
                            ),

                            rx.divider(margin_y="0.75rem"),

                            # Itinerario
                            rx.vstack(
                                rx.hstack(
                                    rx.text("🗓️", font_size="1.1rem"),
                                    rx.text("Itinerario de Actividades", font_weight="700", font_size="1.1rem", color="#111111"),
                                    spacing="2", align_items="center",
                                ),
                                rx.box(
                                    rx.text(
                                        DescripcionState.itinerario_texto,
                                        color="#444444",
                                        line_height="1.8",
                                        font_size="0.92rem",
                                        white_space="pre-line",
                                    ),
                                    background="#fffbf0",
                                    border_left="3px solid #c8962a",
                                    padding="1rem 1.2rem",
                                    border_radius="0 8px 8px 0",
                                    width="100%",
                                ),
                                align_items="start",
                                width="100%",
                                spacing="2",
                            ),

                            rx.box(margin_top="1rem"),

                            rx.link(
                                rx.button(
                                    "Reservar este destino →",
                                    background="#1a5c3a",
                                    color="white",
                                    border_radius="6px",
                                    padding="0.7rem 1.8rem",
                                    font_weight="600",
                                    font_size="0.95rem",
                                    cursor="pointer",
                                    _hover={"background": "#c8962a"},
                                ),
                                href="/reservas",
                            ),

                            spacing="3",
                            align_items="start",
                            flex="1",
                            padding_left="1.5rem",
                            overflow_y="auto",
                            height="700px",
                        ),

                        spacing="6",
                        width="100%",
                        align_items="start",
                    ),
                ),
            ),
            padding="2rem 2rem 4rem 2rem",
            max_width="1150px",
            margin="0 auto",
        ),

        footer(),
        background="white",
        font_family="system-ui, sans-serif",
        on_mount=DescripcionState.cargar_ofertas,
    )