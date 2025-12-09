from celery import Celery
from flask import Flask
from flask_mail import Message, Mail
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# --- Configuración Base de Celery ---
# Es crucial crear la instancia de Celery por separado
celery_app = Celery(
    'tasks',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/1')
)

# Configuración del contexto de Flask
def create_app_context():
    """Crea una aplicación Flask mínima para el contexto del worker."""
    app = Flask(__name__)
    app.config.update(
        MAIL_SERVER=os.getenv('MAIL_SERVER'),
        MAIL_PORT=int(os.getenv('MAIL_PORT', 587)),
        MAIL_USE_TLS=os.getenv('MAIL_USE_TLS') == 'True',
        MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
        MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
        MAIL_DEFAULT_SENDER=os.getenv('MAIL_DEFAULT_SENDER'),
        SECRET_KEY=os.getenv('FLASK_SECRET_KEY')
    )
    return app

# Inicializar Flask-Mail
mail = Mail()

# Carga la configuración de Flask en Celery
@celery_app.task(bind=True)
def send_async_email(self, recipient, subject, body):
    """Tarea Celery para enviar un correo electrónico de forma asíncrona."""
    # Necesitamos el contexto de la aplicación para que Flask-Mail funcione
    app = create_app_context()
    with app.app_context():
        # Inicializar mail DENTRO del contexto para evitar errores de aplicación no registrada
        mail.init_app(app) 
        
        msg = Message(
            subject=subject,
            recipients=[recipient],
            body=body
        )
        try:
            mail.send(msg)
            print(f"Correo enviado a {recipient} para la tarea: {subject}")
        except Exception as e:
            # En caso de fallo de SMTP, reintenta la tarea después de un tiempo
            raise self.retry(exc=e, countdown=60)