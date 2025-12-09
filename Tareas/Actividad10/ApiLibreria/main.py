from flask import Flask, jsonify, request
import uuid

app = Flask(__name__)

# Simulación de una base de datos en memoria
books = [
    {"id": "a1b2c3d4", "title": "Cien años de soledad", "author": "Gabriel García Márquez", "year": 1967},
    {"id": "e5f6g7h8", "title": "Don Quijote de la Mancha", "author": "Miguel de Cervantes", "year": 1605},
]

# --- Helpers ---

def get_book_by_id(book_id):
    """Busca un libro por ID."""
    return next((book for book in books if book["id"] == book_id), None)

# --- Endpoints RESTful ---

@app.route('/books', methods=['GET'])
def get_books():
    """GET /books -> Obtener la lista de libros."""
    return jsonify(books), 200

@app.route('/books/<book_id>', methods=['GET'])
def get_book(book_id):
    """GET /books/<id> -> Obtener un libro específico."""
    book = get_book_by_id(book_id)
    if book:
        return jsonify(book), 200
    return jsonify({"message": "Libro no encontrado"}), 404

@app.route('/books', methods=['POST'])
def add_book():
    """POST /books -> Agregar un nuevo libro."""
    if not request.json or 'title' not in request.json or 'author' not in request.json:
        return jsonify({"message": "Datos de libro incompletos"}), 400
    
    new_book = {
        "id": str(uuid.uuid4())[:8],  # ID corto generado
        "title": request.json['title'],
        "author": request.json['author'],
        "year": request.json.get('year') # Año es opcional
    }
    books.append(new_book)
    return jsonify(new_book), 201  # 201 Created

@app.route('/books/<book_id>', methods=['PUT'])
def update_book(book_id):
    """PUT /books/<id> -> Actualizar la información de un libro."""
    book = get_book_by_id(book_id)
    if not book:
        return jsonify({"message": "Libro no encontrado"}), 404
    
    if not request.json:
        return jsonify({"message": "No hay datos para actualizar"}), 400

    # Actualizar solo los campos proporcionados
    book['title'] = request.json.get('title', book['title'])
    book['author'] = request.json.get('author', book['author'])
    book['year'] = request.json.get('year', book['year'])
    
    return jsonify(book), 200

@app.route('/books/<book_id>', methods=['DELETE'])
def delete_book(book_id):
    """DELETE /books/<id> -> Eliminar un libro."""
    global books
    initial_len = len(books)
    books = [book for book in books if book["id"] != book_id]
    
    if len(books) < initial_len:
        return jsonify({"message": "Libro eliminado con éxito"}), 200
    
    return jsonify({"message": "Libro no encontrado"}), 404

if __name__ == '__main__':
    # Ejecutar en el puerto 5001 por defecto para separarlo del cliente Flask (5000)
    app.run(debug=True, port=5001)
