from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker


DB_USER = "tu_usuario_mariadb"
DB_PASSWORD = "tu_password_mariadb"
DB_HOST = "localhost"
DB_NAME = "biblioteca_db"


DATABASE_URL = f"mariadb+mysqlclient://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"


try:
    engine = create_engine(DATABASE_URL)
    # Probar la conexión inmediatamente
    with engine.connect() as connection:
        print(" Conexión a MariaDB exitosa.")
except Exception as e:
    print(f" Error al conectar a la base de datos: {e}")

Base = declarative_base()

class Libro(Base):
    """
    Modelo ORM para la tabla 'libros'.
    Cada instancia de esta clase representa una fila en la tabla.
    """
    __tablename__ = 'libros'

    id = Column(Integer, primary_key=True)
    titulo = Column(String(255), nullable=False, unique=True) # Título debe ser único
    autor = Column(String(255), nullable=False)
    genero = Column(String(100))
    leido = Column(Boolean, default=False) # Estado de lectura (True/False)

    def __repr__(self):
        return f"Libro(id={self.id}, titulo='{self.titulo}', autor='{self.autor}', leido={self.leido})"

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    Crea las tablas definidas en los modelos (Libro) si aún no existen
    en la base de datos conectada.
    """
    Base.metadata.create_all(bind=engine)
    print(" Tablas de la base de datos inicializadas (si no existían).")