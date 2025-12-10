import json
import os

FILE_NAME = "articulos.json"




def cargar_datos():
    """Carga los artículos desde el archivo JSON. Si el archivo no existe o está vacío, devuelve una lista vacía."""
    if not os.path.exists(FILE_NAME):
        return []
    try:
        with open(FILE_NAME, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []


def guardar_datos(articulos):
    """Guarda la lista de artículos en el archivo JSON con formato legible."""
    with open(FILE_NAME, "w", encoding="utf-8") as file:
        json.dump(articulos, file, indent=4, ensure_ascii=False)




def registrar_articulo(articulos):
    """Registra un nuevo artículo solicitando sus datos al usuario."""
    print("\n--- Registrar Nuevo Artículo ---")

    nombre = input("Nombre del artículo: ").strip()
    categoria = input("Categoría: ").strip()

    # Validación de cantidad
    while True:
        try:
            cantidad = int(input("Cantidad: "))
            if cantidad < 0:
                raise ValueError
            break
        except ValueError:
            print("Cantidad inválida. Ingrese un número entero positivo.")

    # Validación de precio unitario
    while True:
        try:
            precio = float(input("Precio unitario: "))
            if precio < 0:
                raise ValueError
            break
        except ValueError:
            print("Precio inválido. Ingrese un número positivo.")

    descripcion = input("Descripción (opcional): ").strip()

    articulo = {
        "id": len(articulos) + 1,
        "nombre": nombre,
        "categoria": categoria,
        "cantidad": cantidad,
        "precio_unitario": precio,
        "descripcion": descripcion
    }

    articulos.append(articulo)
    guardar_datos(articulos)
    print("Artículo registrado correctamente.\n")


def buscar_articulos(articulos):
    """Busca artículos por nombre o categoría."""
    print("\n--- Buscar Artículos ---")
    criterio = input("Buscar por nombre o categoría: ").strip().lower()

    resultados = [
        art for art in articulos
        if criterio in art["nombre"].lower() or criterio in art["categoria"].lower()
    ]

    if not resultados:
        print("No se encontraron artículos.\n")
    else:
        imprimir_tabla(resultados)


def editar_articulo(articulos):
    """Permite editar los datos de un artículo existente mediante su ID."""
    print("\n--- Editar Artículo ---")
    identificador = input("Ingrese el ID del artículo: ")

    try:
        identificador = int(identificador)
    except ValueError:
        print("El ID debe ser numérico.\n")
        return

    articulo = next((a for a in articulos if a["id"] == identificador), None)

    if not articulo:
        print("No existe un artículo con ese ID.\n")
        return

    print("Dejar un campo vacío mantiene el valor original.\n")

    nuevo_nombre = input(f"Nombre [{articulo['nombre']}]: ").strip()
    nueva_categoria = input(f"Categoría [{articulo['categoria']}]: ").strip()

    nueva_cantidad = input(f"Cantidad [{articulo['cantidad']}]: ").strip()
    if nueva_cantidad:
        try:
            articulo["cantidad"] = int(nueva_cantidad)
        except ValueError:
            print("Cantidad inválida. No se aplicó el cambio.")

    nuevo_precio = input(f"Precio unitario [{articulo['precio_unitario']}]: ").strip()
    if nuevo_precio:
        try:
            articulo["precio_unitario"] = float(nuevo_precio)
        except ValueError:
            print("Precio inválido. No se aplicó el cambio.")

    nueva_descripcion = input(f"Descripción [{articulo['descripcion']}]: ").strip()

    if nuevo_nombre:
        articulo["nombre"] = nuevo_nombre
    if nueva_categoria:
        articulo["categoria"] = nueva_categoria
    if nueva_descripcion:
        articulo["descripcion"] = nueva_descripcion

    guardar_datos(articulos)
    print("Artículo editado correctamente.\n")


def eliminar_articulo(articulos):
    """Elimina un artículo por ID o nombre exacto."""
    print("\n--- Eliminar Artículo ---")
    criterio = input("Ingrese el ID o nombre del artículo: ").strip()

    articulo = None

    if criterio.isdigit():
        articulo = next((a for a in articulos if a["id"] == int(criterio)), None)
    else:
        articulo = next((a for a in articulos if a["nombre"].lower() == criterio.lower()), None)

    if not articulo:
        print("No existe el artículo.\n")
        return

    articulos.remove(articulo)
    guardar_datos(articulos)
    print("Artículo eliminado correctamente.\n")


def listar_articulos(articulos):
    """Lista todos los artículos registrados."""
    print("\n--- Lista de Artículos Registrados ---")

    if not articulos:
        print("No hay artículos registrados.\n")
    else:
        imprimir_tabla(articulos)




def imprimir_tabla(lista):
    """Imprime los artículos en formato tabulado para lectura clara."""
    print("{:<4} {:<20} {:<15} {:<8} {:<12} {}".format(
        "ID", "Nombre", "Categoría", "Cant.", "Precio", "Descripción"
    ))
    print("-" * 80)

    for art in lista:
        print("{:<4} {:<20} {:<15} {:<8} {:<12} {}".format(
            art["id"],
            art["nombre"],
            art["categoria"],
            art["cantidad"],
            art["precio_unitario"],
            art["descripcion"]
        ))

    print()




def menu():

    articulos = cargar_datos()

    while True:
        print("===== SISTEMA DE PRESUPUESTOS =====")
        print("1. Registrar artículo")
        print("2. Buscar artículos")
        print("3. Editar artículo")
        print("4. Eliminar artículo")
        print("5. Listar todos los artículos")
        print("6. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            registrar_articulo(articulos)
        elif opcion == "2":
            buscar_articulos(articulos)
        elif opcion == "3":
            editar_articulo(articulos)
        elif opcion == "4":
            eliminar_articulo(articulos)
        elif opcion == "5":
            listar_articulos(articulos)
        elif opcion == "6":
            print("Saliendo del sistema...")
            break
        else:
            print("Opción no válida. Intente nuevamente.\n")




if __name__ == "__main__":
    menu()
