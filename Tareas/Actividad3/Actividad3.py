import sys
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from Basededatos import Libro, SessionLocal, init_db

# 1. Inicializar la base de datos (crear tablas)
init_db()

# --- Funciones de Acceso a la Base de Datos (CRUD) ---

def agregar_libro(titulo, autor, genero, leido_str):
    """Agrega un nuevo libro a la base de datos usando el ORM."""
    session = SessionLocal()
    leido = leido_str.lower() in ['si', 's', 'true', '1']
    nuevo_libro = Libro(titulo=titulo, autor=autor, genero=genero, leido=leido)

    try:
        session.add(nuevo_libro)
        session.commit()
        print(f"\n Libro '{titulo}' de {autor} agregado con éxito.")
    except IntegrityError:
        session.rollback()
        print(f"\n ERROR: Ya existe un libro con el título '{titulo}'.")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"\n ERROR de base de datos al agregar: {e}")
    finally:
        session.close()

def ver_libros():
    """Muestra el listado completo de libros."""
    session = SessionLocal()
    try:
        libros = session.query(Libro).all()
        if not libros:
            print("\n📚 La biblioteca está vacía.")
            return

        print("\n--- Listado de Libros ---")
        for libro in libros:
            estado = "Leído" if libro.leido else "Pendiente"
            print(f"ID: {libro.id} | Título: {libro.titulo} | Autor: {libro.autor} | Género: {libro.genero} | Estado: {estado}")
        print("--------------------------")

    except SQLAlchemyError as e:
        print(f"\n ERROR de base de datos al listar: {e}")
    finally:
        session.close()

def actualizar_libro(libro_id, **kwargs):
    """Modifica la información de un libro por su ID."""
    session = SessionLocal()
    try:
        libro = session.query(Libro).filter(Libro.id == libro_id).first()
        if not libro:
            print(f"\n Libro con ID {libro_id} no encontrado.")
            return

        # Aplicar las actualizaciones
        if 'titulo' in kwargs:
            libro.titulo = kwargs['titulo']
        # ... (otras actualizaciones como autor, genero, estado) ...
        if 'leido' in kwargs:
            leido = kwargs['leido'].lower() in ['si', 's', 'true', '1']
            libro.leido = leido

        session.commit()
        print(f"\n Libro con ID {libro_id} actualizado con éxito.")

    except IntegrityError:
        session.rollback()
        print(f"\n ERROR: Ya existe un libro con ese título.")
    except SQLAlchemyError as e:
        session.rollback()
        print(f"\n ERROR de base de datos al actualizar: {e}")
    finally:
        session.close()

def buscar_libros(termino):
    """Busca libros por título, autor o género."""
    session = SessionLocal()
    try:
        # Uso de .ilike() para búsqueda insensible a mayúsculas/minúsculas y 'OR'
        criterio = f"%{termino}%"
        libros = session.query(Libro).filter(
            (Libro.titulo.ilike(criterio)) | 
            (Libro.autor.ilike(criterio)) | 
            (Libro.genero.ilike(criterio))
        ).all()

        if not libros:
            print(f"\n No se encontraron libros con el término '{termino}'.")
            return

        print(f"\n--- Resultados de Búsqueda para '{termino}' ---")
        for libro in libros:
            estado = "Leído" if libro.leido else "Pendiente"
            print(f"ID: {libro.id} | Título: {libro.titulo} | Autor: {libro.autor} | Género: {libro.genero} | Estado: {estado}")
        print("-------------------------------------------------")
    
    except SQLAlchemyError as e:
        print(f"\n ERROR de base de datos al buscar: {e}")
    finally:
        session.close()

