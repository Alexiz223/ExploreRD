import reflex as rx
import httpx
from typing import Any
from explorerd.components.layout import navbar, footer

API_URL = "http://localhost:8000"


class DescripcionState(rx.State):
    todas_las_ofertas: list[dict[str, Any]] = []  # Copia original de la base de datos
    ofertas: list[dict[str, Any]] = []            # Lista filtrada que se muestra en pantalla
    idx_activo: int = 0
    loading: bool = False
    buscar_texto: str = ""                        # Texto del buscador

    @rx.var
    def oferta_activa(self) -> dict[str, Any]:
        if len(self.ofertas) == 0 or self.idx_activo >= len(self.ofertas):
            return {}
        return self.ofertas[self.idx_activo]

    async def cargar_ofertas(self):
        self.loading = True
        self.buscar_texto = ""
        self.idx_activo = 0

        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(f"{API_URL}/ofertas/")

                if r.status_code == 200:
                    datos = r.json()
                    
                    # 🔥 CONTROL DE IMÁGENES: Mantiene tus 3 fijas, y a los nuevos les pone "el cosa"
                    for index, oferta in enumerate(datos):
                        if index == 0:
                            oferta["imagen_url"] = "/punta_cana.jpg"
                        elif index == 1:
                            oferta["imagen_url"] = "/jarabacoa.jpg"
                        elif index == 2:
                            oferta["imagen_url"] = "/santo_domingo.jpg"
                        else:
                            # Marcador de posición temporal para los nuevos destinos que crees
                            oferta["imagen_url"] = "https://placehold.co/600x400?text=Nuevo+Destino"
                            
                    self.todas_las_ofertas = datos
                    self.ofertas = datos
                else:
                    self.ofertas = []
                    self.todas_las_ofertas = []

        except Exception:
            self.ofertas = []
            self.todas_las_ofertas = []

        self.loading = False

    # 🔍 FILTRADO EN TIEMPO REAL
    def filtrar_ofertas(self, valor: str):
        self.buscar_texto = valor
        query = valor.lower().strip()
        self.idx_activo = 0  # Reinicia la selección al primer resultado que encuentre
        
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
            ),
            rx.vstack(
                rx.text(
                    oferta["nombre"],
                    font_weight="600",
                    color="#111111",
                ),
                rx.text(
                    oferta["ubicacion"],
                    font_size="0.85rem",
                    color="#666666",
                ),
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
            # Cabecera de la página con buscador moderno
            rx.vstack(
                rx.text(
                    "Nuestros Destinos",
                    font_size="1.8rem",
                    font_weight="700",
                    color="#111111",
                ),
                rx.text(
                    "Selecciona un destino para ver todos los detalles de la ruta",
                    font_size="0.9rem",
                    color="#666666",
                ),
                
                # 🔍 BARRA DE BÚSQUEDA MEJORADA
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
                    _focus_within={"border_color": "#1a5c3a", "background": "white"},
                ),

                spacing="1",
                align="center",
                margin_bottom="2.5rem",
            ),

            rx.cond(
                DescripcionState.loading,
                rx.center(
                    rx.spinner(color="#1a5c3a", size="3"),
                    padding="3rem",
                ),

                rx.cond(
                    DescripcionState.ofertas.length() == 0,
                    rx.center(
                        rx.vstack(
                            rx.text("🔍 No se encontraron destinos que coincidan.", color="#888888", font_weight="600"),
                            rx.text("Intenta con otra palabra clave o verifica el servidor.", color="#aaaaaa", font_size="0.85rem"),
                            spacing="1",
                            align="center",
                        ),
                        padding="4rem",
                        width="100%",
                    ),

                    # Contenido normal cuando sí hay ofertas
                    rx.box(
                        rx.hstack(
                            # COLUMNA IZQUIERDA: LISTA DE DESTINOS (CON SCROLL INTERNO)
                            rx.vstack(
                                rx.foreach(
                                    DescripcionState.ofertas,
                                    lambda oferta, i: tab_oferta(oferta, i),
                                ),
                                spacing="3",
                                min_width="280px",
                                max_width="320px",
                                height="650px",
                                overflow_y="auto",  # Crea un scroll cómodo si metes 20 destinos
                                padding_right="0.5rem",
                            ),

                            # COLUMNA DERECHA: DETALLE COMPLETO DEL DESTINO SELECCIONADO
                            rx.vstack(
                                rx.image(
                                    src=DescripcionState.oferta_activa["imagen_url"],
                                    width="100%",
                                    height="280px",
                                    object_fit="cover",
                                    border_radius="8px",
                                ),

                                rx.text(
                                    DescripcionState.oferta_activa["nombre"],
                                    font_size="1.6rem",
                                    font_weight="700",
                                    color="#1a5c3a",
                                ),

                                # SOLUCIÓN AL ERROR: Comas en vez de "+" para evitar fallos de tipos de datos en Reflex
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
                                        rx.text("💰 RD$ ", DescripcionState.oferta_activa["precio"]),
                                        background="#fdf3e3",
                                        padding="0.3rem 0.75rem",
                                        border_radius="4px",
                                        font_size="0.85rem",
                                        font_weight="600",
                                        color="#c8962a",
                                    ),

                                    rx.box(
                                        rx.text("👥 ", DescripcionState.oferta_activa["cupos_disponibles"], " cupos"),
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

                                rx.divider(margin_top="0.5rem", margin_bottom="0.5rem"),

                                rx.vstack(
                                    rx.text("Descripción General", font_weight="700", font_size="1.1rem", color="#111111"),
                                    rx.text(
                                        DescripcionState.oferta_activa["descripcion_larga"],
                                        color="#444444",
                                        line_height="1.7",
                                        font_size="0.92rem",
                                    ),
                                    align_items="start",
                                    width="100%",
                                ),

                                rx.divider(margin_top="0.5rem", margin_bottom="0.5rem"),

                                rx.vstack(
                                    rx.text("Itinerario de Actividades", font_weight="700", font_size="1.1rem", color="#111111"),
                                    rx.text(
                                        DescripcionState.oferta_activa["itinerario"],
                                        color="#444444",
                                        line_height="1.7",
                                        font_size="0.92rem",
                                    ),
                                    align_items="start",
                                    width="100%",
                                ),

                                rx.box(margin_top="1rem"),

                                rx.link(
                                    rx.button(
                                        "Reservar este destino →",
                                        background="#1a5c3a",
                                        color="white",
                                        border_radius="6px",
                                        padding="0.6rem 1.5rem",
                                        font_weight="600",
                                        cursor="pointer",
                                        _hover={"background": "#c8962a"},
                                    ),
                                    href="/reservas",
                                    width="100%",
                                ),

                                spacing="4",
                                align_items="start",
                                flex="1",
                                padding_left="1rem",
                            ),

                            spacing="6",
                            width="100%",
                            align_items="start",
                        ),
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