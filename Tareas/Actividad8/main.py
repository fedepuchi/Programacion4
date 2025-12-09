from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mail import Mail
from tasks import celery_app, send_async_email
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde .env
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# --- Configuración de Flask-Mail ---
app.config.update(
    MAIL_SERVER=os.getenv('MAIL_SERVER'),
    MAIL_PORT=int(os.getenv('MAIL_PORT', 587)),
    MAIL_USE_TLS=os.getenv('MAIL_USE_TLS') == 'True',
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_DEFAULT_SENDER=os.getenv('MAIL_DEFAULT_SENDER')
)
mail = Mail(app)

# --- Configuración de Celery ---
# Esto es necesario para que Celery herede la configuración de la aplicación Flask
celery_app.conf.update(app.config)

# 📚 Simulación de Base de Datos
books = [
    {'id': 1, 'title': 'Cien años de soledad', 'author': 'Gabriel García Márquez', 'year': 1967},
    {'id': 2, 'title': 'Don Quijote de la Mancha', 'author': 'Miguel de Cervantes', 'year': 1605},
]
next_id = 3
DEFAULT_RECIPIENT = "usuario@ejemplo.com" # Dirección de correo del destinatario

# Función de utilidad para encontrar un libro por ID
def find_book(book_id):
    return next((book for book in books if book['id'] == book_id), None)

# --- RUTAS DE LA APLICACIÓN ---

@app.route('/')
def book_list():
    return render_template('book_list.html', books=books)

## ➡️ Agregar/Actualizar libro
@app.route('/add', methods=['GET', 'POST'])
@app.route('/edit/<int:book_id>', methods=['GET', 'POST'])
def book_form(book_id=None):
    book = find_book(book_id) if book_id else {'id': None, 'title': '', 'author': '', 'year': ''}
    
    if request.method == 'POST':
        global next_id
        
        new_data = {
            'title': request.form['title'],
            'author': request.form['author'],
            'year': int(request.form['year'])
        }

        if book_id: # Lógica de Actualización
            book.update(new_data)
            flash(f'Libro "{book["title"]}" actualizado con éxito.', 'success')
            
            # Tarea Asíncrona de Correo
            send_async_email.delay(
                recipient=DEFAULT_RECIPIENT, 
                subject=f'Libro Actualizado: {book["title"]}', 
                body=f'La información del libro "{book["title"]}" de {book["author"]} ha sido actualizada.'
            )
            
        else: # Lógica de Creación
            new_book = {'id': next_id, **new_data}
            books.append(new_book)
            next_id += 1
            flash(f'Libro "{new_book["title"]}" agregado con éxito.', 'success')

            # Tarea Asíncrona de Correo
            send_async_email.delay(
                recipient=DEFAULT_RECIPIENT, 
                subject=f'Nuevo Libro Agregado: {new_book["title"]}', 
                body=f'Se ha añadido un nuevo libro: "{new_book["title"]}" de {new_book["author"]} ({new_book["year"]}).'
            )
            
        return redirect(url_for('book_list'))
        
    return render_template('book_form.html', book=book)

## ➡️ Eliminar libro (Confirmación)
@app.route('/delete/<int:book_id>', methods=['GET', 'POST'])
def confirm_delete(book_id):
    book = find_book(book_id)
    if not book:
        flash('Libro no encontrado.', 'error')
        return redirect(url_for('book_list'))
    
    if request.method == 'POST':
        book_title = book["title"]
        book_author = book["author"]
        books.remove(book)
        
        flash(f'Libro "{book_title}" eliminado con éxito.', 'success')
        
        # Tarea Asíncrona de Correo
        send_async_email.delay(
            recipient=DEFAULT_RECIPIENT, 
            subject=f'Libro Eliminado: {book_title}', 
            body=f'El libro "{book_title}" de {book_author} ha sido eliminado permanentemente de la biblioteca.'
        )
        
        return redirect(url_for('book_list'))
        
    return render_template('confirm_delete.html', book=book)

## ➡️ Buscar libros
@app.route('/search', methods=['GET'])
def search_books():
    query = request.args.get('query', '').lower()
    
    if query:
        search_results = [
            book for book in books 
            if query in book['title'].lower() or query in book['author'].lower()
        ]
        message = f"Resultados para: **{request.args['query']}**"
    else:
        search_results = []
        message = "Ingresa un término de búsqueda."
        
    return render_template('book_list.html', books=search_results, message=message, query=request.args.get('query', ''))

if __name__ == '__main__':
    # Esto es solo para el desarrollo local; en producción se usaría Gunicorn/Nginx
    app.run(debug=True)