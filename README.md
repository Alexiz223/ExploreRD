# ExploreRD 🌴
**Plataforma de Reservas y Ofertas Turísticas – República Dominicana**

Página web responsive desarrollada con **Reflex** (frontend) y **FastAPI** (backend), conectada a una base de datos **MySQL** en Aiven. Permite consultar ofertas turísticas, ver descripciones detalladas y registrar reservas.

---

## Estructura del Proyecto

```
explorerd/
├── frontend/               # Aplicación Reflex (UI)
│   ├── explorerd/
│   │   ├── pages/
│   │   │   ├── inicio.py       # Página principal (hero, ofertas, contacto)
│   │   │   ├── descripcion.py  # Página de destinos con detalle e itinerario
│   │   │   └── reservas.py     # Formulario de reservas
│   │   ├── components/
│   │   │   └── layout.py       # Navbar y Footer compartidos
│   │   └── explorerd.py        # Punto de entrada de la app
│   ├── rxconfig.py             # Configuración de Reflex
│   └── requirements.txt
│
├── backend/                # API REST con FastAPI
│   ├── routes/
│   │   ├── ofertas.py      # GET /ofertas/
│   │   ├── reservas.py     # POST /reservas/ · GET /reservas/
│   │   └── contacto.py     # POST /contacto/
│   ├── main.py             # App FastAPI + CORS
│   ├── models.py           # Modelos SQLAlchemy
│   ├── schemas.py          # Schemas Pydantic
│   ├── database.py         # Conexión MySQL
│   ├── .env                # Variables de entorno (no subir a GitHub)
│   └── requirements.txt
│
├── assets/
│   └── favicon.ico
├── setup_db.py             # Script para crear tablas e insertar datos
├── .gitignore
└── README.md
```

---

## Instalación y Ejecución

### Requisitos
- Python 3.10+
- Node.js 18+ (para Reflex)
- Acceso a la base de datos MySQL (Aiven)

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/explorerd.git
cd explorerd
```

### 2. Configurar el Backend
```bash
cd backend
pip install -r requirements.txt
```

Crea o edita el archivo `.env` con tus credenciales:
```
DB_HOST=tu-host.aivencloud.com
DB_PORT=12975
DB_USER=avnadmin
DB_PASSWORD=tu_password
DB_NAME=defaultdb
DB_SSL_CA=fastapi
```

Inicializar la base de datos (solo la primera vez):
```bash
cd ..
python setup_db.py
```

Ejecutar el servidor:
```bash
cd backend
uvicorn main:app --reload --port 8000
```

La API estará disponible en: `http://localhost:8000`
Documentación automática: `http://localhost:8000/docs`

### 3. Configurar el Frontend
```bash
cd frontend
pip install -r requirements.txt
reflex run
```

El frontend estará disponible en: `http://localhost:3000`

---

## Endpoints de la API

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/ofertas/` | Lista todas las ofertas activas |
| GET | `/ofertas/{id}` | Detalle de una oferta |
| POST | `/reservas/` | Crear una nueva reserva |
| GET | `/reservas/` | Ver todas las reservas |
| GET | `/reservas/{id}` | Detalle de una reserva |
| POST | `/contacto/` | Enviar mensaje de contacto |

---

## Páginas

- **`/`** – Inicio: buscador, tarjetas de ofertas, formulario de contacto
- **`/descripcion`** – Destinos: descripción detallada, detalles e itinerario
- **`/reservas`** – Reservas: formulario completo con resumen y confirmación

---

## Despliegue

El proyecto está configurado para desplegarse en **Render**:

- **Backend**: Web Service con `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Frontend**: Static Site o Web Service con `reflex run --env prod`

Ramas GitFlow:
- `main` – producción
- `develop` – desarrollo activo
- `feature/*` – nuevas funcionalidades

---

## Créditos

- Desarrollado con [Reflex](https://reflex.dev) y [FastAPI](https://fastapi.tiangolo.com)
- Base de datos MySQL en [Aiven](https://aiven.io)
- Imágenes de [Unsplash](https://unsplash.com)
- Tipografías: Playfair Display + DM Sans vía Google Fonts
