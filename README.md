# API Python MySQL

API RESTful usando Python, Flask y SQLAlchemy con una base MySQL (o SQLite en modo testing).

## 🚀 Tecnologías

- Python 3.9+
- Flask
- SQLAlchemy + PyMySQL
- Flask-JWT-Extended
- pytest (tests)
- python-dotenv (lectura de `.env`)

## 🛠 Instalación rápida

1. Clona el repositorio:

```bash
git clone <repo-url> api-python-mysql
cd api-python-mysql
```

# API Python MySQL

API RESTful usando Python, Flask y SQLAlchemy con soporte para MySQL (y SQLite en modo testing).

## Tecnologías

- Python 3.9+
- Flask
- SQLAlchemy + PyMySQL
- Flask-JWT-Extended
- pytest
- python-dotenv

## Instalación rápida

1. Clona el repo:

```bash
git clone <repo-url> api-python-mysql
cd api-python-mysql
```

2. Crea y activa un virtualenv (recomendado):

```bash
python -m venv .venv
source .venv/bin/activate
```

3. Instala dependencias:

```bash
pip install -r requirements.txt
```

## Configurar `.env`

Usa `EXAMPLE.env` como plantilla:

```bash
cp EXAMPLE.env .env
# editar .env con tus credenciales
```

Variables importantes (en `.env`):

- `APP_PORT` (por defecto 3000)
- `APP_SECRET`
- `DB_HOST`, `DB_PORT`, `DB_DATABASE`, `DB_USERNAME`, `DB_PASSWORD`

La aplicación carga `.env` automáticamente con `python-dotenv`.

## Ejecutar la aplicación

Desarrollo:

```bash
python run.py
```

Testing (usa SQLite en memoria — no necesita MySQL):

```bash
FLASK_ENV=testing python run.py
```

Producción (asegúrate de definir variables en el entorno o en `.env`):

```bash
FLASK_ENV=production python run.py
```

## Endpoint de Health

Se añadió `GET /health` como endpoint público para health checks.

Comportamiento:
- Respuesta 200 cuando el servicio y la base de datos responden: `{ "service": "ok", "database": "ok" }`.
- Respuesta 503 cuando la comprobación de BD falla: `{ "service": "ok", "database": "unreachable", "error": "..." }`.

Implementación:
- La comprobación de BD ejecuta un `SELECT 1` usando `db.engine.connect()` para evitar efectos secundarios en la sesión.

Uso con AWS Application Load Balancer (Target Group):

- Path: `/health`
- Protocol: `HTTP` (o `HTTPS` si tu listener es HTTPS)
- Port: el puerto del listener (ejemplo `80`/`443`) o `traffic port`
- Matcher / Success codes: `200` (o `200-399` si prefieres aceptar redirecciones)
- Interval: `30` seconds (recomendado)
- Timeout: `5` seconds
- Healthy threshold: `2`
- Unhealthy threshold: `2`

Notas para ALB:
- Si la BD está inaccesible el endpoint devuelve 503 y el ALB marcará el target como unhealthy — esto es útil para evitar enviar tráfico a instancias con problemas de persistencia.
- Asegúrate de que las reglas de seguridad (Security Groups) permiten al ALB realizar las comprobaciones hacia las instancias en el puerto correcto.

Ejemplo rápido (comprobar desde una máquina local o desde dentro de la VPC):

```bash
curl -i http://<instance-or-lb-dns>:3000/health
```

## Tests

```bash
pytest -q
```

Los tests usan `sqlite:///:memory:` y no requieren MySQL.

## Buenas prácticas

- No subir `.env` a repositorios públicos.
- En producción considerar separar la comprobación de salud en dos endpoints si prefieren que el ALB solo verifique que el proceso está vivo (sin comprobar la BD). Por ejemplo:
  - `/health` → comprobación completa (incluye BD)
  - `/ready`  → readiness check más ligera (proc up, se usa para readiness probes)
