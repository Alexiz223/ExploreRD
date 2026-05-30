import reflex as rx

# 1. Importamos las funciones de cada página de forma consistente
from explorerd.pages.inicio import inicio
from explorerd.pages.descripcion import descripcion
from explorerd.pages.reservas import reservas
from explorerd.pages.admin import admin  # <-- ¡Esta era la que te faltaba!

# 2. Inicializamos la App
app = rx.App(
    theme=rx.theme(
        appearance="light",
        has_background=True,
    )
)

# 3. [OPCIONAL] Si por algún motivo el decorador @rx.page se pone de caprichoso,
# aseguras la ruta al 100% agregándola manualmente aquí abajo:
app.add_page(admin, route="/admin")