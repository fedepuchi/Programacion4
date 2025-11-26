import sys
from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError, WriteConcernError, OperationFailure
from Basededatos import libros_collection # Importamos la colección ya conectada


def agregar_libro(titulo, autor, genero, leido_str):
    """Agrega un nuevo documento (libro) a la colección."""
    
    # Adaptar el estado de lectura a un tipo de dato booleano
    leido = leido_str.lower() in ['si', 's', 'true', '1']
    
    # Estructura del documento (análoga a un registro/fila)
    nuevo_libro = {
        "titulo": titulo,
        "autor": autor,
        "genero": genero,
        "leido": leido
    }

    try:
        # Insertar el documento. MongoDB genera automáticamente el _id.
        resultado = libros_collection.insert_one(nuevo_libro)
        print(f"\n Libro '{titulo}' agregado con éxito. ID: {resultado.inserted_id}")
    except DuplicateKeyError:
        # Esta excepción ocurriría si se creara un índice único en 'titulo'
        print(f"\n ERROR: Ya existe un libro con el título '{titulo}'.")
    except OperationFailure as e:
        print(f"\n ERROR de MongoDB al insertar: {e}")

def ver_libros():
    """Muestra el listado completo de documentos (libros)."""
    try:
        # Usamos .find({}) para obtener todos los documentos
        libros = libros_collection.find({})
        
        if libros_collection.count_documents({}) == 0:
            print("\n La biblioteca está vacía.")
            return

        print("\n--- Listado de Libros ---")
        for libro in libros:
            estado = "Leído" if libro['leido'] else "Pendiente"
            # El ID en MongoDB es '_id' y es un objeto ObjectId
            print(f"ID: {libro['_id']} | Título: {libro['titulo']} | Autor: {libro['autor']} | Género: {libro['genero']} | Estado: {estado}")
        print("--------------------------")

    except OperationFailure as e:
        print(f"\n ERROR de MongoDB al listar: {e}")

def actualizar_libro(libro_id_str, campo, nuevo_valor):
    """Modifica un campo específico de un documento por su _id."""
    try:
        # Convertir el ID de string a ObjectId
        libro_id = ObjectId(libro_id_str)
    except Exception:
        print(f"\n ERROR: ID '{libro_id_str}' no es un formato válido de MongoDB ObjectId.")
        return

    # Preparar el filtro y la actualización
    filtro = {"_id": libro_id}
    
    # Manejar el campo 'leido' como caso especial (booleano)
    if campo.lower() == 'leido':
        set_value = nuevo_valor.lower() in ['si', 's', 'true', '1']
        actualizacion = {"$set": {campo: set_value}}
    else:
        actualizacion = {"$set": {campo: nuevo_valor}}

    try:
        # Ejecutar la actualización
        resultado = libros_collection.update_one(filtro, actualizacion)
        
        if resultado.matched_count == 0:
            print(f"\n Libro con ID {libro_id_str} no encontrado.")
        elif resultado.modified_count == 1:
            print(f"\n Libro con ID {libro_id_str} actualizado con éxito. Campo '{campo}' modificado.")
        else:
            print(f"\n Libro encontrado, pero no se realizó ninguna modificación (el valor ya era el mismo).")

    except OperationFailure as e:
        print(f"\n ERROR de MongoDB al actualizar: {e}")

def buscar_libros(termino):
    """Busca documentos por título, autor o género utilizando expresiones regulares."""
    
    # Expresión regular para búsqueda parcial e insensible a mayúsculas/minúsculas ($options: 'i')
    regex_pattern = {"$regex": termino, "$options": "i"}

    # Construir el filtro $or para buscar en múltiples campos
    filtro = {
        "$or": [
            {"titulo": regex_pattern},
            {"autor": regex_pattern},
            {"genero": regex_pattern}
        ]
    }
    
    try:
        # Ejecutar la búsqueda
        libros = libros_collection.find(filtro)
        
        # Contar resultados (una alternativa más eficiente sería .count_documents(filtro))
        resultados_encontrados = list(libros)
        
        if not resultados_encontrados:
            print(f"\n No se encontraron libros con el término '{termino}'.")
            return

        print(f"\n--- Resultados de Búsqueda para '{termino}' ---")
        for libro in resultados_encontrados:
            estado = "Leído" if libro.get('leido', False) else "Pendiente"
            print(f"ID: {libro['_id']} | Título: {libro['titulo']} | Autor: {libro['autor']} | Género: {libro['genero']} | Estado: {estado}")
        print("-------------------------------------------------")
    
    except OperationFailure as e:
        print(f"\n ERROR de MongoDB al buscar: {e}")

def eliminar_libro(libro_id_str):
    """Elimina un documento por su _id."""
    try:
        libro_id = ObjectId(libro_id_str)
    except Exception:
        print(f"\n ERROR: ID '{libro_id_str}' no es un formato válido de MongoDB ObjectId.")
        return

    try:

        resultado = libros_collection.delete_one({"_id": libro_id})
        
        if resultado.deleted_count == 1:
            print(f"\n Libro con ID {libro_id_str} eliminado con éxito.")
        else:
            print(f"\n Libro con ID {libro_id_str} no encontrado.")

    except OperationFailure as e:
        print(f"\n ERROR de MongoDB al eliminar: {e}")


