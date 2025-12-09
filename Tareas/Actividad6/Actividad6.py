import redis
import json
import os
from dotenv import load_dotenv
from flask import Flask, render_template_string, request, redirect, url_for


load_dotenv()

KEYDB_HOST = os.getenv("KEYDB_HOST", "localhost")
KEYDB_PORT = int(os.getenv("KEYDB_PORT", 6379))
KEYDB_PASSWORD = os.getenv("KEYDB_PASSWORD")
KEYDB_PREFIX = "libro:"

try:
    r = redis.Redis(
        host=KEYDB_HOST,
        port=KEYDB_PORT,
        password=KEYDB_PASSWORD,
        decode_responses=True,
        socket_timeout=5
    )
    r.ping()
    print(f"INFO: Conexión a KeyDB establecida en {KEYDB_HOST}:{KEYDB_PORT}")
except redis.exceptions.ConnectionError as e:
    print(f"ERROR: No se pudo conectar a KeyDB. Asegúrate de que KeyDB esté corriendo. {e}")
    r = None # Establecer r como None si la conexión falla

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24) # Necesario para sesiones/mensajes flash si se usan



def generar_id_unico():
    if r is None: return None
    # Incrementa un contador global
    return r.incr(f'{KEYDB_PREFIX}next_id')

def obtener_todos_los_libros():
    if r is None: return []
    # Usar el patrón KEYDB_PREFIX más un patrón numérico para evitar el contador
    claves = r.keys(f"{KEYDB_PREFIX}[0-9]*")
    libros = []
    if not claves: return libros

    try:
        libros_json = r.mget(claves)
        for libro_json in libros_json:
            if libro_json:
                libros.append(json.loads(libro_json))
    except Exception as e:
        print(f"ERROR al obtener libros: {e}")
        return []

    # Se ordena en Python ya que Redis no garantiza el orden con KEYS o SCAN
    return sorted(libros, key=lambda l: int(l['id']))

def obtener_libro_por_id(libro_id):
    if r is None: return None
    clave = f"{KEYDB_PREFIX}{libro_id}"
    libro_json = r.get(clave)
    if libro_json:
        return json.loads(libro_json)
    return None

def agregar_libro_db(titulo, autor, genero, estado):
    if r is None: return False
    try:
        libro_id = generar_id_unico()
        if libro_id is None: return False
        libro = {
            "id": libro_id,
            "titulo": titulo,
            "autor": autor,
            "genero": genero,
            "estado": estado
        }
        clave = f"{KEYDB_PREFIX}{libro_id}"
        r.set(clave, json.dumps(libro))
        return True
    except Exception as e:
        print(f"ERROR al agregar libro: {e}")
        return False

def actualizar_libro_db(libro_id, titulo, autor, genero, estado):
    if r is None: return False
    libro = obtener_libro_por_id(libro_id)
    if not libro: return False

    try:
        libro["titulo"] = titulo
        libro["autor"] = autor
        libro["genero"] = genero
        libro["estado"] = estado
        
        clave = f"{KEYDB_PREFIX}{libro_id}"
        r.set(clave, json.dumps(libro))
        return True
    except Exception as e:
        print(f"ERROR al actualizar libro: {e}")
        return False

def eliminar_libro_db(libro_id):
    if r is None: return False
    clave = f"{KEYDB_PREFIX}{libro_id}"
    try:
        return r.delete(clave) == 1
    except Exception as e:
        print(f"ERROR al eliminar libro: {e}")
        return False

def buscar_libros_db(termino):
    todos_los_libros = obtener_todos_los_libros()
    if not todos_los_libros: return []

    libros_encontrados = []
    termino = termino.lower().strip()
    if not termino: return todos_los_libros # Si la búsqueda está vacía, mostrar todos

    for libro in todos_los_libros:
        if (termino in libro['titulo'].lower() or
            termino in libro['autor'].lower() or
            termino in libro['genero'].lower()):
            libros_encontrados.append(libro)
    
    return libros_encontrados

#  Plantilla Base HTML (Utilizando render_template_string para ser single-file) 

BASE_HTML = """
<!doctype html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>Biblioteca Personal KeyDB</title>
    <!-- Bootstrap CSS CDN -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" xintegrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
    <style>
        body { background-color: #f8f9fa; font-family: 'Inter', sans-serif; }
        .card { border-radius: 0.75rem; box-shadow: 0 4px 8px rgba(0,0,0,0.05); }
        .btn-custom { border-radius: 0.5rem; }
        .book-list-container { max-height: 70vh; overflow-y: auto; }
        .navbar { border-radius: 0 0 0.75rem 0.75rem; }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm mb-4">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('index') }}">📚 Mi Biblioteca KeyDB</a>
        </div>
    </nav>
    <div class="container py-4">
        {% if error %}
            <div class="alert alert-danger" role="alert">{{ error }}</div>
        {% elif mensaje %}
            <div class="alert alert-success" role="alert">{{ mensaje }}</div>
        {% endif %}
        
        <div class="row">
            <div class="col-12">
                {{ content }}
            </div>
        </div>
    </div>
    <!-- Bootstrap JS CDN (Bundle con Popper) -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" xintegrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
</body>
</html>
"""



@app.route('/', methods=['GET', 'POST'])
def index():
    if r is None:
        return render_template_string(BASE_HTML, content="""
            <div class="alert alert-danger" role="alert">
                Error de Conexión: La aplicación no puede conectarse a KeyDB. Por favor, verifica la configuración y el servicio.
            </div>
        """)

    libros = obtener_todos_los_libros()
    
    content = f"""
    <div class="d-flex justify-content-between align-items-center mb-3">
        <h2 class="h3">Listado de Libros ({len(libros)} encontrados)</h2>
        <a href="{url_for('agregar')}" class="btn btn-success btn-custom">Añadir Nuevo Libro</a>
    </div>

    <form method="POST" action="{url_for('buscar')}" class="mb-4">
        <div class="input-group">
            <input type="text" name="termino" class="form-control" placeholder="Buscar por título, autor o género..." required>
            <button class="btn btn-outline-primary btn-custom" type="submit">Buscar</button>
            <a href="{url_for('index')}" class="btn btn-outline-secondary btn-custom">Limpiar</a>
        </div>
    </form>
    
    <div class="book-list-container">
        <div class="list-group">
            { libros_html(libros) }
        </div>
    </div>
    """
    return render_template_string(BASE_HTML, content=content, mensaje=request.args.get('mensaje'))

@app.route('/search', methods=['POST'])
def buscar():
    termino = request.form.get('termino')
    libros = buscar_libros_db(termino)

    content = f"""
    <div class="d-flex justify-content-between align-items-center mb-3">
        <h2 class="h3">Resultados de Búsqueda para: "{termino}" ({len(libros)} encontrados)</h2>
        <a href="{url_for('agregar')}" class="btn btn-success btn-custom">Añadir Nuevo Libro</a>
    </div>

    <form method="POST" action="{url_for('buscar')}" class="mb-4">
        <div class="input-group">
            <input type="text" name="termino" class="form-control" placeholder="Buscar por título, autor o género..." value="{termino}" required>
            <button class="btn btn-outline-primary btn-custom" type="submit">Buscar</button>
            <a href="{url_for('index')}" class="btn btn-outline-secondary btn-custom">Limpiar</a>
        </div>
    </form>
    
    <div class="book-list-container">
        <div class="list-group">
            { libros_html(libros) }
        </div>
    </div>
    """
    return render_template_string(BASE_HTML, content=content)

@app.route('/add', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        autor = request.form.get('autor')
        genero = request.form.get('genero')
        estado = request.form.get('estado')
        
        if not all([titulo, autor, genero, estado]):
            return render_template_string(BASE_HTML, content=formulario_agregar_html(), error="Todos los campos son obligatorios.")

        if agregar_libro_db(titulo, autor, genero, estado):
            return redirect(url_for('index', mensaje=f"Libro '{titulo}' agregado con éxito."))
        else:
            return render_template_string(BASE_HTML, content=formulario_agregar_html(), error="Error al guardar el libro en KeyDB.")

    return render_template_string(BASE_HTML, content=formulario_agregar_html())

@app.route('/edit/<int:libro_id>', methods=['GET', 'POST'])
def editar(libro_id):
    libro = obtener_libro_por_id(libro_id)
    if not libro:
        return redirect(url_for('index', mensaje=f"ERROR: Libro con ID {libro_id} no encontrado."))

    if request.method == 'POST':
        titulo = request.form.get('titulo')
        autor = request.form.get('autor')
        genero = request.form.get('genero')
        estado = request.form.get('estado')

        if not all([titulo, autor, genero, estado]):
            return render_template_string(BASE_HTML, content=formulario_editar_html(libro), error="Todos los campos son obligatorios.")

        if actualizar_libro_db(libro_id, titulo, autor, genero, estado):
            return redirect(url_for('index', mensaje=f"Libro con ID {libro_id} actualizado con éxito."))
        else:
            return render_template_string(BASE_HTML, content=formulario_editar_html(libro), error="Error al actualizar el libro en KeyDB.")

    return render_template_string(BASE_HTML, content=formulario_editar_html(libro))

@app.route('/delete/<int:libro_id>')
def eliminar(libro_id):
    if eliminar_libro_db(libro_id):
        return redirect(url_for('index', mensaje=f"Libro con ID {libro_id} eliminado con éxito."))
    else:
        return redirect(url_for('index', mensaje=f"ERROR: No se pudo eliminar el libro con ID {libro_id} (posiblemente no existe)."))


# --- Funciones Auxiliares para HTML ---

def libros_html(libros):
    if not libros:
        return '<p class="text-muted text-center mt-5">No hay libros registrados en la biblioteca.</p>'
    
    html = ""
    for libro in libros:
        # Determinar color de estado
        badge_class = 'bg-secondary'
        if 'Leído' in libro['estado']: badge_class = 'bg-success'
        elif 'En curso' in libro['estado']: badge_class = 'bg-warning text-dark'
        elif 'Pendiente' in libro['estado']: badge_class = 'bg-info text-dark'

        html += f"""
        <div class="card mb-3">
            <div class="card-body">
                <div class="d-flex w-100 justify-content-between">
                    <h5 class="mb-1">{libro['titulo']} <span class="badge {badge_class}">{libro['estado']}</span></h5>
                    <small class="text-muted">ID: {libro['id']}</small>
                </div>
                <p class="mb-1"><strong>Autor:</strong> {libro['autor']}</p>
                <p class="mb-1"><strong>Género:</strong> {libro['genero']}</p>
                <div class="mt-2">
                    <a href="{url_for('editar', libro_id=libro['id'])}" class="btn btn-sm btn-primary btn-custom me-2">Editar</a>
                    <a href="{url_for('eliminar', libro_id=libro['id'])}" class="btn btn-sm btn-danger btn-custom" 
                       onclick="return confirm('¿Estás seguro de que quieres eliminar el libro \\'{libro['titulo']}\\'?');">Eliminar</a>
                </div>
            </div>
        </div>
        """
    return html

def formulario_agregar_html():
    return f"""
    <div class="card p-4">
        <h2 class="h3 card-title">Añadir Nuevo Libro</h2>
        <form method="POST" action="{url_for('agregar')}">
            <div class="mb-3">
                <label for="titulo" class="form-label">Título</label>
                <input type="text" class="form-control rounded-lg" id="titulo" name="titulo" required>
            </div>
            <div class="mb-3">
                <label for="autor" class="form-label">Autor</label>
                <input type="text" class="form-control rounded-lg" id="autor" name="autor" required>
            </div>
            <div class="mb-3">
                <label for="genero" class="form-label">Género</label>
                <input type="text" class="form-control rounded-lg" id="genero" name="genero" required>
            </div>
            <div class="mb-3">
                <label for="estado" class="form-label">Estado de Lectura</label>
                <select class="form-select rounded-lg" id="estado" name="estado" required>
                    <option value="Pendiente">Pendiente</option>
                    <option value="En curso">En curso</option>
                    <option value="Leído">Leído</option>
                </select>
            </div>
            <button type="submit" class="btn btn-success btn-custom">Guardar Libro</button>
            <a href="{url_for('index')}" class="btn btn-secondary btn-custom">Cancelar</a>
        </form>
    </div>
    """

def formulario_editar_html(libro):
    # Función auxiliar para manejar el estado seleccionado
    def is_selected(estado_opcion):
        return 'selected' if libro['estado'] == estado_opcion else ''

    return f"""
    <div class="card p-4">
        <h2 class="h3 card-title">Editar Libro (ID: {libro['id']})</h2>
        <form method="POST" action="{url_for('editar', libro_id=libro['id'])}">
            <div class="mb-3">
                <label for="titulo" class="form-label">Título</label>
                <input type="text" class="form-control rounded-lg" id="titulo" name="titulo" value="{libro['titulo']}" required>
            </div>
            <div class="mb-3">
                <label for="autor" class="form-label">Autor</label>
                <input type="text" class="form-control rounded-lg" id="autor" name="autor" value="{libro['autor']}" required>
            </div>
            <div class="mb-3">
                <label for="genero" class="form-label">Género</label>
                <input type="text" class="form-control rounded-lg" id="genero" name="genero" value="{libro['genero']}" required>
            </div>
            <div class="mb-3">
                <label for="estado" class="form-label">Estado de Lectura</label>
                <select class="form-select rounded-lg" id="estado" name="estado" required>
                    <option value="Pendiente" {is_selected('Pendiente')}>Pendiente</option>
                    <option value="En curso" {is_selected('En curso')}>En curso</option>
                    <option value="Leído" {is_selected('Leído')}>Leído</option>
                </select>
            </div>
            <button type="submit" class="btn btn-primary btn-custom">Guardar Cambios</button>
            <a href="{url_for('index')}" class="btn btn-secondary btn-custom">Cancelar</a>
        </form>
    </div>
    """

if __name__ == '__main__':
    # Flask necesita un host/puerto para que sea accesible dentro del entorno
    app.run(host='0.0.0.0', port=5000, debug=True)