# API Python MySQL

API RESTful usando Python, Flask, SQLAlchemy y MySQL con Pruebas Unitarias.

## 🚀 Tecnologías Usadas

- Python 3.9+
- Flask 2.0.1
- SQLAlchemy 1.4.22
- MySQL
- Flask-JWT-Extended 4.3.1
- pytest 6.2.5

## 🛠️ Instalación

1. Clonar el repositorio:
   ```
   git clone https://github.com/usuario/api-python-mysql.git
   ```
2. Instalar dependencias:
   ```
   pip install -r requirements.txt
   ```
3. Configurar variables de entorno en `.env`.
4. Correr la aplicación:
   ```
   python run.py
   ```

## 🔧 Variables de Entorno

Crear un archivo `.env` con:
```
APP_PORT=3000
APP_SECRET=your-secret-key-here
APP_HOST=localhost
DB_HOST=localhost
DB_CONNECTION=mysql
DB_PORT=3306
DB_DATABASE=api_python_mysql
DB_USERNAME=root
DB_PASSWORD=password
```

## 📋 Endpoints

| Endpoint         | Método | Descripción          | Requerido                  | Respuesta                          |
|------------------|--------|----------------------|----------------------------|------------------------------------|
| `/`              | GET    | Ruta principal       |                            | `{"response":"Flask RESTful API"}`|
| `/register`      | POST   | Crear usuario        | fullname, email, password  | JSON {dataUser, message}          |
| `/login`         | POST   | Autenticar usuario   | email, password            | JSON {auth, dataUser, access_token} |
| `/update`        | PUT    | Actualizar usuario   | accessToken, email, fullname | JSON {dataUser, auth, message} |
| `/updatePassword`| PUT    | Actualizar contraseña| accessToken, newPassword   | JSON {auth, message}              |
| `/delete`        | DELETE | Eliminar usuario     | accessToken                | JSON {message}                    |

## 🔍 Pruebas

Ejecutar pruebas unitarias:
```
pytest
```

## Licencia

Distribuido bajo la licencia MIT.