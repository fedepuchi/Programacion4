from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import os
from dotenv import load_dotenv

# Cargar variables de entorno del archivo .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24) # Necesario para flash messages

# Obtener la URL base de la API del archivo .env
API_BASE_URL = os.getenv("API_BASE_URL")

# --- Funciones de Interacción con la API (CRUD) ---

def api_request(method, endpoint, data=None):
    """Función genérica para hacer solicitudes a la API."""
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        if method == 'GET':
            response = requests.get(url)
        elif method == 'POST':
            response = requests.post(url, json=data)
        elif method == 'PUT':
            response = requests.put(url, json=data)
        elif method == 'DELETE':
            response = requests.delete(url)
        else:
            raise ValueError("Método HTTP no soportado")
        
        response.raise_for_status() # Lanza HTTPError si la respuesta es 4xx o 5xx
        return response.json(), response.status_code
        
    except requests.exceptions.RequestException as e:
        # Gestión de errores de red o errores HTTP de la API
        print(f"Error al conectar con la API: {e}")
        # Intentar obtener el JSON de error si es posible
        try:
            error_msg = response.json().get('message', 'Error desconocido de la API')
        except:
            error_msg = f"Error de red o conexión: {e}"
            
        # Devolver un diccionario de error y un código de estado de fallo (503 si es problema de conexión)
        return {"message": error_msg}, response.status_code if 'response' in locals() else 503

# --- Vistas de la Aplicación Cliente ---

@app.route('/')
def index():
    """Vista principal: Muestra todos los libros."""
    books, status = api_request('GET', 'books')
    
    if status == 200:
        return render_template('index.html', books=books)
    else:
        # Mostrar error si no se pueden cargar los libros
        flash(f"Error al cargar libros: {books.get('message', 'Servicio no disponible')}", 'error')
        return render_template('index.html', books=[])

@app.route('/add', methods=['GET', 'POST'])
def add_book():
    """Vista para agregar un nuevo libro."""
    if request.method == 'POST':
        book_data = {
            "title": request.form['title'],
            "author": request.form['author'],
            "year": int(request.form['year']) if request.form['year'] else None
        }
        
        response, status = api_request('POST', 'books', data=book_data)
        
        if status == 201:
            flash('Libro agregado con éxito.', 'success')
            return redirect(url_for('index'))
        else:
            flash(f"Error al agregar libro: {response.get('message', 'Error de la API')}", 'error')
            
    return render_template('add_book.html')

@app.route('/delete/<book_id>', methods=['POST'])
def delete_book(book_id):
    """Vista para eliminar un libro."""
    
    response, status = api_request('DELETE', f'books/{book_id}')
    
    if status == 200:
        flash(f"Libro {book_id} eliminado con éxito.", 'success')
    elif status == 404:
        flash("Error: Libro no encontrado para eliminar.", 'error')
    else:
        flash(f"Error al eliminar libro: {response.get('message', 'Error de la API')}", 'error')
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    # El cliente Flask se ejecuta por defecto en el puerto 5000
    app.run(debug=True)