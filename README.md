# API Python MySQL

API RESTful usando Python, Flask, SQLAlchemy y MySQL con Pruebas Unitarias.

## 🚀 Tecnologías Usadas

- Python 3.9+
- Flask 2.0.1
- SQLAlchemy 1.4.22
- MySQL
- Flask-JWT-Extended 4.3.1
- pytest 6.2.5
- passlib (para hashing de contraseñas)

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
| `/register`      | POST   | Crear usuario        | fullname, email, password  | JSON {message, access_token}       |
| `/login`         | POST   | Autenticar usuario   | email, password            | JSON {access_token}                |
| `/update`        | PUT    | Actualizar usuario   | Bearer Token, fullname/email | JSON {dataUser, message}         |
| `/updatePassword`| PUT    | Actualizar contraseña| Bearer Token, newPassword  | JSON {message}                     |
| `/delete`        | DELETE | Eliminar usuario     | Bearer Token               | JSON {message}                     |

## 🔍 Pruebas

Ejecutar pruebas unitarias:
```
pytest
```

### Estado de los Tests ✅

Todos los tests están funcionando correctamente:

- ✅ **test_register**: Verifica la creación de usuarios
- ✅ **test_login**: Verifica la autenticación de usuarios  
- ✅ **test_update_user**: Verifica la actualización de datos de usuario
- ✅ **test_update_password**: Verifica la actualización de contraseñas
- ✅ **test_delete_user**: Verifica la eliminación de usuarios

## 🔧 Correcciones Recientes

### Problemas Solucionados:

1. **Importación del modelo User**: Se agregó `__init__.py` en `app/models/`
2. **Configuración duplicada**: Se eliminó la clase `TestingConfig` duplicada en `config.py`
3. **Hashing de contraseñas**: Se unificó el uso de `passlib` en lugar de `werkzeug.security`
4. **JWT Identity**: Se cambió de usar ID (entero) a email (string) como identity en JWT
5. **Contexto de aplicación**: Se corrigió el acceso a la base de datos en tests usando `app.app_context()`

### Cambios Técnicos:

- **Autenticación**: Ahora usa `passlib` para hashing consistente
- **JWT**: Usa email como identity en lugar de ID de usuario
- **Tests**: Todos los tests funcionan con contexto de aplicación apropiado
- **Base de datos**: Configuración SQLite en memoria para tests

## Licencia

Distribuido bajo la licencia MIT.