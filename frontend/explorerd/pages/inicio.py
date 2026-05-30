import reflex as rx
import httpx
from explorerd.components.layout import navbar, footer

# El URL de la API de FastAPI
API_URL = "http://localhost:8000"

class InicioState(rx.State):
    todas_las_ofertas: list[dict] = []  # Copia de seguridad con los datos originales
    ofertas: list[dict] = []            # Lista filtrada que se muestra en pantalla
    loading: bool = False
    buscar_texto: str = ""              # Guarda lo que escribe el usuario
    
    # Campos del formulario de contacto
    nombre_contacto: str = ""
    email_contacto: str = ""
    mensaje_contacto: str = ""
    contacto_enviado: bool = False

    async def cargar_ofertas(self):
        self.contacto_enviado = False
        self.nombre_contacto = ""
        self.email_contacto = ""
        self.mensaje_contacto = ""
        self.buscar_texto = ""
        
        self.loading = True
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                r = await client.get(f"{API_URL}/ofertas/")
                if r.status_code == 200:
                    datos = r.json()
                    self.todas_las_ofertas = datos  # Guardamos los originales
                    self.ofertas = datos            # Inicialmente mostramos todos
        except Exception:
            self.ofertas = []
            self.todas_las_ofertas = []
        finally:
            self.loading = False

    # LÓGICA DE BÚSQUEDA EN TIEMPO REAL
    def filtrar_ofertas(self, valor: str):
        self.buscar_texto = valor
        query = valor.lower().strip()
        
        if not query:
            # Si borra lo que escribió, se muestran todas otra vez
            self.ofertas = self.todas_las_ofertas
        else:
            # Filtra si la palabra clave coincide con el Nombre, Ubicación o Descripción
            self.ofertas = [
                o for o in self.todas_las_ofertas
                if query in str(o.get("nombre", "")).lower() 
                or query in str(o.get("ubicacion", "")).lower()
                or query in str(o.get("descripcion", "")).lower()
            ]

    def set_nombre(self, v): self.nombre_contacto = v
    def set_email(self, v): self.email_contacto = v
    def set_mensaje(self, v): self.mensaje_contacto = v

    async def enviar_contacto(self):
        if not self.nombre_contacto or not self.email_contacto or not self.mensaje_contacto:
            return rx.toast.error("Por favor, llena todos los campos antes de enviar.")
            
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                r = await client.post(
                    f"{API_URL}/contacto/", 
                    json={
                        "nombre": self.nombre_contacto,
                        "email": self.email_contacto,
                        "mensaje": self.mensaje_contacto,
                    }
                )
                
                if r.status_code in [200, 201]:
                    self.contacto_enviado = True
                    self.nombre_contacto = ""
                    self.email_contacto = ""
                    self.mensaje_contacto = ""
                    return rx.toast.success("¡Mensaje enviado correctamente!")
                else:
                    return rx.toast.error(f"Error del servidor ({r.status_code}).")
        except Exception as e:
            print(f"Error enviando contacto: {e}")
            return rx.toast.error("No se pudo conectar con el servidor.")


# Componente de tarjeta para las ofertas
def oferta_card(oferta: rx.Var, index: rx.Var) -> rx.Component:
    return rx.box(
        rx.image(
            src=oferta["imagen_url"],
            width="100%",
            height="200px",
            object_fit="cover",
        ),
        rx.box(
            rx.text(
                oferta["nombre"],
                font_weight="700",
                font_size="1rem",
                color="#111111",
                margin_bottom="0.4rem",
            ),
            rx.text(
                oferta["descripcion"],
                font_size="0.83rem",
                color="#444444",
                line_height="1.5",
                margin_bottom="0.75rem",
            ),
            rx.hstack(
                rx.box(
                    rx.text(oferta["ubicacion"], font_size="0.78rem", color="#1a5c3a", font_weight="600"),
                    background="#e8f4ee",
                    padding="0.2rem 0.6rem",
                    border_radius="4px",
                ),
                rx.spacer(),
                rx.text(oferta["duracion"], font_size="0.78rem", color="#666666"),
                width="100%",
                align="center",
            ),
            rx.hstack(
                rx.text(
                    "RD$ ", oferta["precio"].to_string(),
                    font_size="1.15rem",
                    font_weight="800",
                    color="#1a5c3a",
                ),
                rx.spacer(),
                rx.hstack(
                    rx.link(
                        rx.button(
                            "Ver más",
                            background="white",
                            color="#1a5c3a",
                            border="1px solid #1a5c3a",
                            border_radius="4px",
                            padding="0.3rem 0.8rem",
                            font_size="0.82rem",
                            font_weight="600",
                            cursor="pointer",
                            _hover={"background": "#e8f4ee"},
                        ),
                        href="/descripcion",
                    ),
                    rx.link(
                        rx.button(
                            "Reservar",
                            background="#1a5c3a",
                            color="white",
                            border="none",
                            border_radius="4px",
                            padding="0.3rem 0.8rem",
                            font_size="0.82rem",
                            font_weight="600",
                            cursor="pointer",
                            _hover={"background": "#c8962a"},
                        ),
                        href="/reservas",
                    ),
                    spacing="2",
                ),
                width="100%",
                align="center",
                margin_top="0.75rem",
            ),
            padding="1rem",
        ),
        background="white",
        border="1px solid #e0e0e0",
        border_radius="8px",
        overflow="hidden",
        _hover={"box_shadow": "0 4px 16px rgba(0,0,0,0.10)"},
        transition="box-shadow 0.2s",
    )


def input_style():
    return {
        "border": "1px solid #ccc",
        "border_radius": "6px",
        "padding": "0.65rem 1rem",
        "width": "100%",
        "font_size": "0.9rem",
        "color": "#111111",
        "background": "white",
        "_focus": {"border_color": "#1a5c3a", "outline": "none"},
        "_placeholder": {"color": "#777777"}, 
    }


@rx.page(route="/", title="ExploreRD - Turismo en República Dominicana", on_load=InicioState.cargar_ofertas)
def inicio() -> rx.Component:
    return rx.box(
        navbar(),

        # Hero Section con el Formulario de Búsqueda integrado
        rx.box(
            rx.vstack(
                rx.text(
                    "Descubre la República Dominicana",
                    font_size="2.4rem",
                    font_weight="700",
                    color="white",
                    text_align="center",
                    line_height="1.2",
                ),
                rx.text(
                    "Experiencias turísticas únicas en el Caribe",
                    color="rgba(255,255,255,0.85)",
                    font_size="1.05rem",
                    text_align="center",
                ),
                
                # BARRA DE BÚSQUEDA ESTILO AIRBNB
                rx.hstack(
                    rx.text("🔍", font_size="1.1rem"),
                    rx.input(
                        placeholder="¿A dónde quieres ir? (Ej: Samaná, Jarabacoa, Hotel...)",
                        value=InicioState.buscar_texto,
                        on_change=InicioState.filtrar_ofertas,  # Dispara la función al escribir
                        border="none",
                        background="transparent",
                        color="#111111",
                        width=["100%", "380px"],
                        _focus={"outline": "none", "border": "none"},
                        font_size="0.95rem",
                    ),
                    background="white",
                    padding="0.5rem 1.2rem",
                    border_radius="50px",
                    box_shadow="0 4px 15px rgba(0,0,0,0.25)",
                    margin_top="1rem",
                    align_items="center",
                    width=["90%", "auto"],
                ),
                
                spacing="4",
                align="center",
            ),
            background="linear-gradient(rgba(0,0,0,0.55),rgba(0,0,0,0.60)), url('https://upload.wikimedia.org/wikipedia/commons/thumb/7/70/Punta_Cana%2C_Dominican_Republic.jpg/1200px-Punta_Cana%2C_Dominican_Republic.jpg')",
            background_size="cover",
            background_position="center",
            padding="7rem 2rem",
            display="flex",
            align_items="center",
            justify_content="center",
        ),

        # Seccion de Ofertas
        rx.box(
            rx.vstack(
                rx.text("Ofertas Turísticas", font_size="1.6rem", font_weight="700", color="#111111"),
                rx.text("Explora nuestros destinos disponibles", font_size="0.9rem", color="#666666"),
                spacing="1",
                align="center",
                margin_bottom="2rem",
            ),
            rx.cond(
                InicioState.loading,
                rx.center(rx.spinner(color="#1a5c3a", size="3"), padding="3rem"),
                rx.cond(
                    InicioState.ofertas.length() == 0,
                    rx.center(
                        rx.vstack(
                            rx.text("🔍 No se encontraron ofertas que coincidan con tu búsqueda.", color="#888", font_size="0.9rem"),
                            spacing="2",
                            align="center",
                        ),
                        padding="3rem",
                    ),
                    rx.grid(
                        rx.foreach(InicioState.ofertas, lambda o, i: oferta_card(o, i)),
                        columns="3",
                        spacing="5",
                        width="100%",
                    ),
                ),
            ),
            id="ofertas",
            padding="3rem 2rem",
            max_width="1100px",
            margin="0 auto",
        ),

        # Seccion de Contacto
        rx.box(
            rx.hstack(
                rx.vstack(
                    rx.text("Información de la Empresa", font_size="1.2rem", font_weight="700", color="#111111"),
                    rx.text(
                        "Somos la plataforma líder de turismo en República Dominicana. Te ayudamos a descubrir los mejores destinos del Caribe con guías expertos y precios accesibles.",
                        font_size="0.9rem",
                        color="#444444",
                        line_height="1.7",
                        max_width="360px",
                    ),
                    rx.vstack(
                        rx.hstack(rx.text("📍"), rx.text("Santo Domingo, República Dominicana", font_size="0.88rem", color="#333333"), align="center", spacing="2"),
                        rx.hstack(rx.text("📞"), rx.text("+1 (849) 555-0100 (Emilio)", font_size="0.88rem", color="#333333"), align="center", spacing="2"),
                        rx.hstack(rx.text("✉️"), rx.text("emilioavaldezrossis@gmail.com", font_size="0.88rem", color="#333333"), align="center", spacing="2"),
                        rx.hstack(rx.text("📞"), rx.text("+1 (829) 555-0199 (Alejandro)", font_size="0.88rem", color="#333333"), align="center", spacing="2"),
                        rx.hstack(rx.text("✉️"), rx.text("alejandrojimenez0304@gmail.com", font_size="0.88rem", color="#333333"), align="center", spacing="2"),
                        rx.hstack(rx.text("🕐"), rx.text("Lun–Vie 8am–6pm", font_size="0.88rem", color="#333333"), align="center", spacing="2"),
                        spacing="3",
                        align="start",
                        margin_top="0.5rem",
                    ),
                    spacing="4",
                    align="start",
                    flex="1",
                ),
                rx.cond(
                    InicioState.contacto_enviado,
                    rx.vstack(
                        rx.text("✅", font_size="2.5rem"),
                        rx.text("¡Mensaje enviado!", font_size="1.1rem", font_weight="700", color="#1a5c3a"),
                        rx.text("Te contactaremos pronto.", color="#555555", font_size="0.9rem"),
                        spacing="3",
                        align="center",
                        background="white",
                        border="1px solid #e0e0e0",
                        border_radius="8px",
                        padding="2rem",
                        min_width="300px",
                    ),
                    rx.vstack(
                        rx.text("Contáctanos", font_size="1.1rem", font_weight="700", color="#111111"),
                        rx.input(
                            placeholder="Tu nombre",
                            value=InicioState.nombre_contacto,
                            on_change=InicioState.set_nombre,
                            **input_style(),
                        ),
                        rx.input(
                            placeholder="Tu email",
                            value=InicioState.email_contacto,
                            on_change=InicioState.set_email,
                            type="email",
                            **input_style(),
                        ),
                        rx.text_area(
                            placeholder="¿En qué podemos ayudarte?",
                            value=InicioState.mensaje_contacto,
                            on_change=InicioState.set_mensaje,
                            rows="4",
                            **input_style(),
                        ),
                        rx.button(
                            "Enviar mensaje",
                            on_click=InicioState.enviar_contacto,
                            background="#1a5c3a",
                            color="white",
                            border="none",
                            border_radius="6px",
                            padding="0.65rem 1.5rem",
                            font_weight="600",
                            width="100%",
                            cursor="pointer",
                            _hover={"background": "#c8962a"},
                        ),
                        spacing="3",
                        background="white",
                        border="1px solid #e0e0e0",
                        border_radius="8px",
                        padding="1.5rem",
                        min_width="300px",
                        width=["100%", "340px"],
                    ),
                ),
                spacing="8",
                flex_wrap="wrap",
                align="start",
            ),
            background="#f5f5f5",
            padding="3rem 2rem",
            max_width="1100px",
            margin="0 auto",
        ),

        footer(),
    )