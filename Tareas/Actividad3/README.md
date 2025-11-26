#  Biblioteca Personal (MariaDB + SQLAlchemy ORM)

Esta aplicación es una adaptación del proyecto original de biblioteca, migrado de SQLite a **MariaDB** como motor de base de datos y utilizando **SQLAlchemy** como Object-Relational Mapper (ORM).

##  Requisitos

Necesitas tener instalado:

1.  **Python 3.x**
2.  **MariaDB Server** (o MySQL, ya que el conector es compatible)

##  Instalación y Configuración

### 1. Instalar MariaDB

Las instrucciones varían según el sistema operativo:

* **Linux (Debian/Ubuntu):**
    ```bash
    sudo apt update
    sudo apt install mariadb-server
    sudo systemctl start mariadb
    sudo mysql_secure_installation # Para configurar la contraseña de root
    ```
* **macOS (Homebrew):**
    ```bash
    brew install mariadb
    brew services start mariadb
    ```
* **Windows:** Descargar el instalador oficial de MariaDB.

### 2. Crear la Base de Datos

Accede al cliente de MariaDB (usualmente con `mysql -u root -p`) y ejecuta el siguiente comando SQL:

```sql
CREATE DATABASE biblioteca_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
-- Opcional: Crear un usuario dedicado para la aplicación
CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'tu_password_segura';
GRANT ALL PRIVILEGES ON biblioteca_db.* TO 'app_user'@'localhost';
FLUSH PRIVILEGES;