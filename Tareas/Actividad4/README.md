# Biblioteca Personal (MongoDB NoSQL + PyMongo)

Esta aplicación es una adaptación del proyecto de biblioteca, migrado de un enfoque relacional (SQL) a una base de datos **NoSQL de documentos** utilizando **MongoDB** y el cliente oficial **PyMongo**.

## Estructura del Documento

Cada libro es almacenado como un documento JSON en la colección `libros` con la siguiente estructura:

```json
{
  "_id": ObjectId("..."),  // Identificador único generado por MongoDB
  "titulo": "Cien años de soledad",
  "autor": "Gabriel García Márquez",
  "genero": "Realismo Mágico",
  "leido": true
}