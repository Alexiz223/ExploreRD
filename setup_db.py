import pymysql

timeout = 10
connection = pymysql.connect(
  charset="utf8mb4",
  connect_timeout=timeout,
  cursorclass=pymysql.cursors.DictCursor,
  db="defaultdb",
  host="mysql-5cb43f0-paginawebhoteles-52d7.a.aivencloud.com",
  password="AVNS_2FTghz4Gv6SS7rMDHoc",
  read_timeout=timeout,
  port=12975,
  user="avnadmin",
  write_timeout=timeout,
)

sql_commands = [
    """CREATE TABLE IF NOT EXISTS ofertas (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(150) NOT NULL,
        descripcion TEXT NOT NULL,
        descripcion_larga TEXT,
        precio DECIMAL(10,2) NOT NULL,
        duracion VARCHAR(50),
        ubicacion VARCHAR(150),
        imagen_url VARCHAR(300),
        cupos_disponibles INT DEFAULT 10,
        itinerario TEXT,
        activo BOOLEAN DEFAULT TRUE,
        creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS reservas (
        id INT AUTO_INCREMENT PRIMARY KEY,
        oferta_id INT NOT NULL,
        nombre_cliente VARCHAR(100) NOT NULL,
        apellido_cliente VARCHAR(100) NOT NULL,
        email VARCHAR(150) NOT NULL,
        telefono VARCHAR(20),
        fecha_reserva DATE NOT NULL,
        num_personas INT NOT NULL DEFAULT 1,
        metodo_pago ENUM('tarjeta','transferencia','efectivo') NOT NULL,
        estado ENUM('pendiente','confirmada','cancelada') DEFAULT 'pendiente',
        total DECIMAL(10,2),
        notas TEXT,
        creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (oferta_id) REFERENCES ofertas(id) ON DELETE CASCADE
    )""",
    """CREATE TABLE IF NOT EXISTS contacto_mensajes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nombre VARCHAR(100) NOT NULL,
        email VARCHAR(150) NOT NULL,
        mensaje TEXT NOT NULL,
        creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )""",
    # Actualizar imágenes a URLs que siempre funcionan
    """UPDATE ofertas SET imagen_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/70/Punta_Cana%2C_Dominican_Republic.jpg/1200px-Punta_Cana%2C_Dominican_Republic.jpg' WHERE id = 1""",
    """UPDATE ofertas SET imagen_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Jarabacoa%2C_Dominican_Republic.jpg/1200px-Jarabacoa%2C_Dominican_Republic.jpg' WHERE id = 2""",
    """UPDATE ofertas SET imagen_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Zona_Colonial_de_Santo_Domingo.jpg/1200px-Zona_Colonial_de_Santo_Domingo.jpg' WHERE id = 3""",
]

# Insertar ofertas si no existen
insert_ofertas = """INSERT IGNORE INTO ofertas (id, nombre, descripcion, descripcion_larga, precio, duracion, ubicacion, imagen_url, cupos_disponibles, itinerario) VALUES
(1, 'Tour Punta Cana', 'Disfruta de las mejores playas del Caribe con guía experto y actividades acuáticas.', 'Una experiencia única recorriendo las playas más hermosas de Punta Cana con guía experto, transporte incluido y actividades acuáticas. Vivirás momentos inolvidables en las arenas blancas y aguas cristalinas del Caribe.', 4500.00, '3 días / 2 noches', 'Punta Cana, RD', 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/70/Punta_Cana%2C_Dominican_Republic.jpg/1200px-Punta_Cana%2C_Dominican_Republic.jpg', 15, 'Día 1: Llegada, check-in en hotel y tour por la playa. Día 2: Tour en catamarán, snorkeling en arrecifes de coral. Día 3: Visita a Isla Saona, almuerzo en la playa y regreso.'),
(2, 'Aventura en Jarabacoa', 'Rafting, cañones y montañas para los amantes de la aventura extrema.', 'Explora la naturaleza salvaje de Jarabacoa con actividades de adrenalina: rafting en el río Yaque del Norte, canyoning en cascadas naturales y senderismo por la montaña. Una experiencia única rodeada de verde y aventura.', 2800.00, '2 días / 1 noche', 'Jarabacoa, RD', 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Jarabacoa%2C_Dominican_Republic.jpg/1200px-Jarabacoa%2C_Dominican_Republic.jpg', 10, 'Día 1: Rafting en río Yaque del Norte, almuerzo en la montaña, caminata a cascada El Salto. Día 2: Canyoning, senderismo por Pico Duarte y regreso.'),
(3, 'Santo Domingo Colonial', 'Recorre la primera ciudad del Nuevo Mundo, Patrimonio de la Humanidad UNESCO.', 'Un recorrido cultural e histórico por la Zona Colonial de Santo Domingo, declarada Patrimonio de la Humanidad por la UNESCO. Con guía certificado visitarás los monumentos históricos más importantes del continente americano.', 1200.00, '1 día', 'Santo Domingo, RD', 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e3/Zona_Colonial_de_Santo_Domingo.jpg/1200px-Zona_Colonial_de_Santo_Domingo.jpg', 20, 'Mañana: Catedral Primada de América, Alcázar de Colón y Calle Las Damas. Tarde: Fortaleza Ozama, Museo de las Casas Reales y cena típica dominicana.')"""

try:
    cursor = connection.cursor()
    for cmd in sql_commands:
        try:
            cursor.execute(cmd)
            connection.commit()
            print(f"✅ Ejecutado correctamente")
        except Exception as e:
            print(f"⚠️  {e}")

    cursor.execute(insert_ofertas)
    connection.commit()
    print("✅ Ofertas insertadas/verificadas")

    cursor.execute("SELECT id, nombre, precio, imagen_url FROM ofertas")
    print("\n📋 Ofertas en la base de datos:")
    for row in cursor.fetchall():
        print(f"  → [{row['id']}] {row['nombre']} - RD${row['precio']}")
        print(f"       Imagen: {row['imagen_url'][:60]}...")

    print("\n🎉 Base de datos configurada exitosamente!")
finally:
    connection.close()
