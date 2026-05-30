import reflex as rx

def navbar() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.link(
                rx.hstack(
                    rx.text("Explore", font_weight="700", font_size="1.3rem", color="#1a5c3a"),
                    rx.text("RD", font_weight="700", font_size="1.3rem", color="#c8962a"),
                    spacing="0",
                ),
                href="/",
            ),
            rx.hstack(
                rx.link("Inicio", href="/", color="#333", font_size="0.9rem", _hover={"color": "#1a5c3a"}),
                rx.link("Destinos", href="/descripcion", color="#333", font_size="0.9rem", _hover={"color": "#1a5c3a"}),
                rx.link("Reservar", href="/reservas", color="white", background="#1a5c3a", padding="0.4rem 1rem", border_radius="6px", font_size="0.9rem", _hover={"background": "#c8962a"}),
                spacing="5",
                align="center",
            ),
            justify="between",
            align="center",
            width="100%",
        ),
        background="white",
        padding="1rem 2rem",
        border_bottom="1px solid #e5e5e5",
        position="sticky",
        top="0",
        z_index="100",
    )

def footer() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.hstack(
                        rx.text("Explore", font_weight="700", color="white"),
                        rx.text("RD", font_weight="700", color="#c8962a"),
                        spacing="0",
                    ),
                    rx.text("Turismo en República Dominicana", color="#aaa", font_size="0.85rem"),
                    align="start", spacing="2",
                ),
                rx.vstack(
                    rx.text("Páginas", color="white", font_weight="600", font_size="0.85rem"),
                    rx.link("Inicio", href="/", color="#aaa", font_size="0.85rem"),
                    rx.link("Destinos", href="/descripcion", color="#aaa", font_size="0.85rem"),
                    rx.link("Reservas", href="/reservas", color="#aaa", font_size="0.85rem"),
                    align="start", spacing="2",
                ),
                rx.vstack(
                    rx.text("Contacto", color="white", font_weight="600", font_size="0.85rem"),
                    rx.text("Santo Domingo, RD", color="#aaa", font_size="0.85rem"),
                    
                    # Contacto de Emilio
                    rx.text("+1 (849) 555-0100 (Emilio)", color="#aaa", font_size="0.85rem"),
                    rx.text("emilioavaldezrossis@gmail.com", color="#aaa", font_size="0.85rem"),
                    
                    # Tu contacto actualizado
                    rx.text("+1 (829) 555-0199 (Alejandro)", color="#aaa", font_size="0.85rem"),
                    rx.text("alejandrojimenez0304@gmail.com", color="#aaa", font_size="0.85rem"),
                    
                    align="start", spacing="2",
                ),
                justify="between",
                width="100%",
                flex_wrap="wrap",
                spacing="8",
            ),
            rx.divider(border_color="#333"),
            rx.text("© 2026 ExploreRD. Todos los derechos reservados.", color="#666", font_size="0.8rem"),
            spacing="5",
            width="100%",
        ),
        background="#111",
        padding="2.5rem 2rem",
    )