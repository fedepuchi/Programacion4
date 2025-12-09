from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)

app.secret_key = 'super_secret_key' 


books = [
    {'id': 1, 'title': 'Cien años de soledad', 'author': 'Gabriel García Márquez', 'year': 1967},
    {'id': 2, 'title': 'Don Quijote de la Mancha', 'author': 'Miguel de Cervantes', 'year': 1605},
]
next_id = 3

def find_book(book_id):
    return next((book for book in books if book['id'] == book_id), None)


@app.route('/')
def book_list():
    return render_template('listalibros.html', books=books)

@app.route('/add', methods=['GET', 'POST'])
@app.route('/edit/<int:book_id>', methods=['GET', 'POST'])
def book_form(book_id=None):
    book = find_book(book_id) if book_id else {'id': None, 'title': '', 'author': '', 'year': ''}
    
    if request.method == 'POST':
        global next_id
        
        # Recolectar datos del formulario
        new_data = {
            'title': request.form['title'],
            'author': request.form['author'],
            'year': int(request.form['year'])
        }

        if book_id: # Lógica de Actualización
            book.update(new_data)
            flash(f'Libro "{book["title"]}" actualizado con éxito.', 'success')
        else: # Lógica de Creación
            new_book = {'id': next_id, **new_data}
            books.append(new_book)
            next_id += 1
            flash(f'Libro "{new_book["title"]}" agregado con éxito.', 'success')
            
        return redirect(url_for('book_list'))
        
    # Renderizar el formulario (GET)
    return render_template('libroformato.html', book=book)

@app.route('/delete/<int:book_id>', methods=['GET', 'POST'])
def confirm_delete(book_id):
    book = find_book(book_id)
    if not book:
        flash('Libro no encontrado.', 'error')
        return redirect(url_for('book_list'))
    
    if request.method == 'POST':
        books.remove(book)
        flash(f'Libro "{book["title"]}" eliminado con éxito.', 'success')
        return redirect(url_for('book_list'))
        
    # Renderizar la página de confirmación (GET)
    return render_template('eleminacion.html', book=book)

## ➡️ 4. Buscar libros
@app.route('/search', methods=['GET'])
def search_books():
    query = request.args.get('query', '').lower()
    
    if query:
        # Filtrar libros que coincidan en título o autor
        search_results = [
            book for book in books 
            if query in book['title'].lower() or query in book['author'].lower()
        ]
        message = f"Resultados para: **{request.args['query']}**"
    else:
        search_results = []
        message = "Ingresa un término de búsqueda."
        
    return render_template('listalibros.html', books=search_results, message=message, query=request.args.get('query', ''))

if __name__ == '__main__':
    app.run(debug=True)