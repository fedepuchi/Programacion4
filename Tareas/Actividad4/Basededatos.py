from pymongo import MongoClient
from pymongo.errors import ConnectionError, ConfigurationError

# 1. Parámetros de Conexión a MongoDB
# Usar MongoDB Atlas o una instancia local.
# Ejemplo de conexión local: "mongodb://localhost:27017/"
# Ejemplo de conexión Atlas (reemplazar con su URL):
# MONGO_URI = "mongodb+srv://<usuario>:<password>@cluster0.abcde.mongodb.net/?retryWrites=true&w=majority"
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "biblioteca_nosql"
COLLECTION_NAME = "libros"

# 2. Inicialización del Cliente y Conexión
try:
    # Intentar establecer la conexión
    client = MongoClient(MONGO_URI)
    # Ping para verificar que la conexión está activa
    client.admin.command('ping')
    print("✅ Conexión a MongoDB exitosa.")

    # Acceder a la base de datos y la colección
    db = client[DB_NAME]
    libros_collection = db[COLLECTION_NAME]

except ConnectionError:
    print(f"\n❌ ERROR: No se pudo conectar a MongoDB en {MONGO_URI}.")
    print("Asegúrate de que MongoDB esté corriendo o que la cadena de conexión sea correcta.")
    # Usamos exit() para terminar el programa si la conexión falla
    import sys
    sys.exit(1)
except ConfigurationError as e:
    print(f"\n❌ ERROR de configuración de URI de MongoDB: {e}")
    import sys
    sys.exit(1)