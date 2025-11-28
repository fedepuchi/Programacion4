import redis
import json
import os
from dotenv import load_dotenv

# --- Configuración y Conexión ---

# Cargar variables de entorno del archivo .env
load_dotenv()

# Variables de conexión a KeyDB
KEYDB_HOST = os.getenv("KEYDB_HOST", "localhost")
KEYDB_PORT = int(os.getenv("KEYDB_PORT", 6379))
KEYDB_PASSWORD = os.getenv("KEYDB_PASSWORD") # Será None si no está definida

try:
    # Conexión a KeyDB
    # Se utiliza la clase Redis de redis-py, ya que KeyDB es compatible con el protocolo Redis
    r = redis.Redis(
        host=KEYDB_HOST,
        port=KEYDB_PORT,
        password=KEYDB_PASSWORD,
        decode_responses=True  # Decodifica las respuestas a string de Python automáticamente
    )
    r.ping()
    print("Conexión a KeyDB establecida con éxito.")
except redis.exceptions.ConnectionError as e:
    print(f"ERROR: No se pudo conectar a KeyDB en {KEYDB_HOST}:{KEYDB_PORT}. Asegúrate de que KeyDB esté corriendo.")
    print(e)
    exit(1)
except Exception as e:
    print(f"Ocurrió un error inesperado al conectar a KeyDB: {e}")
    exit(1)

# --- Funciones de la Lógica de la Aplicación (CRUD) ---

def generar_id_unico():
    # Incrementa un contador global en KeyDB y lo usa como ID
    return r.incr('libro:next_id')

def agregar_libro(titulo, autor, genero, estado):
    libro_id = generar_id_unico()
    libro = {
        "id": libro_id,
        "titulo": titulo,
        "autor": autor,
        "genero": genero,
        "estado": estado
    }
    # Serializar el objeto a JSON
    libro_json = json.dumps(libro)
    # Usar el comando SET para almacenar el string JSON con una clave única
    clave = f"libro:{libro_id}"
    r.set(clave, libro_json)
    print(f"\nLibro agregado: {titulo} con ID: {libro_id}")

def obtener_libro_por_id(libro_id):
    clave = f"libro:{libro_id}"
    libro_json = r.get(clave)
    if libro_json:
        return json.loads(libro_json)
    return None

def actualizar_libro(libro_id, nuevo_titulo, nuevo_autor, nuevo_genero, nuevo_estado):
    libro = obtener_libro_por_id(libro_id)
    if not libro:
        print(f"\nERROR: No se encontró el libro con ID {libro_id}.")
        return

    # Actualizar campos
    libro["titulo"] = nuevo_titulo
    libro["autor"] = nuevo_autor
    libro["genero"] = nuevo_genero
    libro["estado"] = nuevo_estado

    # Serializar y almacenar de nuevo
    clave = f"libro:{libro_id}"
    r.set(clave, json.dumps(libro))
    print(f"\nLibro con ID {libro_id} actualizado con éxito.")

def eliminar_libro(libro_id):
    clave = f"libro:{libro_id}"
    # Usar el comando DEL
    if r.delete(clave) == 1:
        print(f"\nLibro con ID {libro_id} eliminado con éxito.")
    else:
        print(f"\nERROR: No se encontró el libro con ID {libro_id}.")

def obtener_todos_los_libros():
    # Usar SCAN para buscar todas las claves que coincidan con el patrón "libro:*"
    claves = r.keys("libro:[0-9]*")
    libros = []
    if not claves:
        return libros

    # Usar MGET para obtener los valores de múltiples claves de forma eficiente
    libros_json = r.mget(claves)
    for libro_json in libros_json:
        if libro_json:
            libros.append(json.loads(libro_json))

    return sorted(libros, key=lambda l: l['id'])

def buscar_libros(termino):
    libros_encontrados = []
    # Obtener todos los libros para realizar la búsqueda en la aplicación
    # Una solución más escalable podría usar Redis Search (KeyDB soporta RediSearch)
    todos_los_libros = obtener_todos_los_libros()
    termino = termino.lower()

    for libro in todos_los_libros:
        if (termino in libro['titulo'].lower() or
            termino in libro['autor'].lower() or
            termino in libro['genero'].lower()):
            libros_encontrados.append(libro)
    
    return libros_encontrados

# --- Interfaz de Usuario (CLI) ---

def mostrar_menu():
    print("\n--- Menú de la Biblioteca Personal (KeyDB) ---")
    print("1. Agregar nuevo libro")
    print("2. Actualizar información de un libro")
    print("3. Eliminar libro existente")
    print("4. Ver listado de libros")
    print("5. Buscar libros")
    print("6. Salir")
    return input("Selecciona una opción: ")

def obtener_datos_libro():
    titulo = input("Título: ")
    autor = input("Autor: ")
    genero = input("Género: ")
    estado = input("Estado de lectura (por ejemplo, 'Leído', 'Pendiente', 'En curso'): ")
    return titulo, autor, genero, estado

def mostrar_libro(libro):
    print(f"  ID: {libro['id']}")
    print(f"  Título: {libro['titulo']}")
    print(f"  Autor: {libro['autor']}")
    print(f"  Género: {libro['genero']}")
    print(f"  Estado: {libro['estado']}")

def manejar_opcion(opcion):
    if opcion == '1':
        print("\n--- Agregar Nuevo Libro ---")
        titulo, autor, genero, estado = obtener_datos_libro()
        agregar_libro(titulo, autor, genero, estado)
    
    elif opcion == '2':
        print("\n--- Actualizar Libro ---")
        try:
            libro_id = int(input("ID del libro a actualizar: "))
            libro_existente = obtener_libro_por_id(libro_id)
            if libro_existente:
                print(f"Datos actuales del libro (ID {libro_id}):")
                mostrar_libro(libro_existente)
                print("\nIngresa los nuevos datos:")
                titulo, autor, genero, estado = obtener_datos_libro()
                actualizar_libro(libro_id, titulo, autor, genero, estado)
            else:
                print(f"No se encontró un libro con ID {libro_id}.")
        except ValueError:
            print("ERROR: El ID debe ser un número entero.")

    elif opcion == '3':
        print("\n--- Eliminar Libro ---")
        try:
            libro_id = int(input("ID del libro a eliminar: "))
            eliminar_libro(libro_id)
        except ValueError:
            print("ERROR: El ID debe ser un número entero.")

    elif opcion == '4':
        print("\n--- Listado de Libros ---")
        libros = obtener_todos_los_libros()
        if libros:
            for libro in libros:
                print("-" * 25)
                mostrar_libro(libro)
            print("-" * 25)
            print(f"Total de libros: {len(libros)}")
        else:
            print("No hay libros registrados.")

    elif opcion == '5':
        print("\n--- Buscar Libros ---")
        termino = input("Introduce el título, autor o género a buscar: ")
        libros_encontrados = buscar_libros(termino)
        if libros_encontrados:
            print(f"\nLibros encontrados para '{termino}':")
            for libro in libros_encontrados:
                print("-" * 25)
                mostrar_libro(libro)
            print("-" * 25)
        else:
            print(f"\nNo se encontraron libros que coincidan con '{termino}'.")

    elif opcion == '6':
        print("Saliendo de la aplicación. ¡Adiós!")
        return False
    
    else:
        print("Opción no válida. Inténtalo de nuevo.")
    
    return True

# --- Bucle Principal ---

if __name__ == "__main__":
    ejecutando = True
    while ejecutando:
        ejecutando = manejar_opcion(mostrar_menu())