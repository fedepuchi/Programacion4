from flask import Flask, jsonify, abort
import json
import os

DATA_FILE = "datos.json"

app = Flask(__name__)




def cargar_datos():
    """Carga los datos históricos de vacunación desde un archivo JSON."""
    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


datos = cargar_datos()




@app.get("/vacunas")
def obtener_todos():
    """Devuelve todos los registros disponibles."""
    return jsonify(datos)


@app.get("/vacunas/<int:anio>")
def obtener_por_anio(anio):
    """Devuelve el registro del año especificado."""
    registro = next((item for item in datos if item["year"] == anio), None)

    if not registro:
        abort(404, description="No hay datos para ese año.")

    return jsonify(registro)




@app.get("/vacunas/provincia/<nombre>")
def datos_por_provincia(nombre):
    """
    Devuelve datos simulados por provincia basados en promedio del país.
    Se usa solo si no existen datos regionales reales.
    """

    provincias = [
        "bocas del toro", "cocle", "colon", "chiriqui", "darien",
        "herrera", "los santos", "panama", "panama oeste", "veraguas",
        "ngabe bugle", "guna yala", "embera"
    ]

    nombre = nombre.lower()

    if nombre not in provincias:
        abort(404, description="Provincia no válida.")

    # Simulación simple basada en variación porcentual sobre los datos nacionales
    simulacion = []
    variacion = hash(nombre) % 6 - 3  # varía entre -3% y +2%

    for registro in datos:
        nuevo = registro.copy()
        nuevo["provincia"] = nombre
        nuevo["value"] = max(0, min(100, registro["value"] + variacion))
        simulacion.append(nuevo)

    return jsonify(simulacion)




if __name__ == "__main__":
    app.run(debug=True)
