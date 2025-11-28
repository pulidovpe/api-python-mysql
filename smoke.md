# Smoke test (AWS Fargate)

Propósito
-------
Guía rápida para levantar la imagen de `api-python-mysql` sin depender de la base de datos, validar que el contenedor y el endpoint de salud funcionan y realizar un despliegue mínimo en AWS Fargate para smoke-tests.

1) Prueba rápida local (sin BD)
--------------------------------
- Copia `EXAMPLE.env` a `.env` y añade:

```env
SKIP_DB_CHECKS=true
FLASK_ENV=production
# (opcional) APP_PORT=3000
```

- Construir y ejecutar localmente:

```bash
docker build -t api-python-mysql:latest .
docker run --rm -p 3000:3000 --env-file .env api-python-mysql:latest
```

- Verifica `/health` y `/`:

```bash
curl -i http://localhost:3000/health
curl -i http://localhost:3000/
```

La respuesta de `/health` debería devolver HTTP 200 y JSON con `"database": "skipped"` cuando `SKIP_DB_CHECKS=true`.

2) Preparar imagen para ECS/Fargate
----------------------------------
- Etiqueta la imagen para tu repositorio ECR (reemplaza `<aws_account>` y `<region>` y `<repo>`):

```bash
docker tag api-python-mysql:latest <aws_account>.dkr.ecr.<region>.amazonaws.com/<repo>:latest

# Login (ejemplo con AWS CLI v2)
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <aws_account>.dkr.ecr.<region>.amazonaws.com
docker push <aws_account>.dkr.ecr.<region>.amazonaws.com/<repo>:latest
```

- Alternativa rápida: usa una imagen pública en Docker Hub para pruebas.

3) Desplegar en Fargate (smoke test)
-----------------------------------

Recomendaciones mínimas para la Task Definition / Service:

- Container port: `3000` (el `Dockerfile` expone este puerto).
- Environment variables (Task/Container overrides):
  - `SKIP_DB_CHECKS=true`
  - `FLASK_ENV=production`
  - (opcional) `APP_PORT=3000`
- Task networking: choose a subnet + security group that allows outbound HTTP (para la prueba no se requiere inbound a la BD).
- ALB / Target Group:
  - Health check path: `/health`
  - Healthy: HTTP 200
  - Interval/Timeout: keep defaults; si necesitas más rapidez, reduce `interval` y `healthy threshold`.

Flujo rápido (Console / CloudFormation / Terraform / CDK):

- Crear Task Definition (Fargate) apuntando a la imagen ECR y los env vars anteriores.
- Crear Service (desired count = 1) en un cluster y asociarlo a un ALB Target Group configurado con path `/health`.

4) Notas y troubleshooting
--------------------------
- `SKIP_DB_CHECKS=true` hace que `/health` devuelva `database: skipped` y que el `before_request` no ejecute la comprobación de BD, por lo tanto el ALB marcará la tarea como sana.
- Si ves `WORKER TIMEOUT` en logs:
  - Asegúrate de que la imagen no esté bloqueada por operaciones lentas en startup. Ejecuta con `FLASK_ENV=production` para evitar que `db.create_all()` se ejecute en arranque.
  - Ajusta el timeout de Gunicorn si necesitas (archivo `Dockerfile` o configuración de entrada). Para smoke-tests no es recomendable reducir demasiado.
- Si planeas que la tarea de Fargate acceda a una RDS posteriormente:
  - Añade las variables `DB_HOST`, `DB_USERNAME`, `DB_PASSWORD`, `DB_DATABASE`, `DB_CONNECT_TIMEOUT` y configura Security Groups para permitir la conexión.

5) Siguientes pasos opcionales
-----------------------------
- Puedo generar una `task-definition.json` de ejemplo con los campos mínimos y plantillas de Terraform/ECS.
- Puedo añadir un `github-actions` workflow para construir la imagen y publicarla en ECR automáticamente.

Archivo relacionado: `EXAMPLE.env` (ejemplo de variables de entorno y nota sobre `SKIP_DB_CHECKS`).

Si quieres, creo también la `task-definition.json` y un ejemplo de `aws ecs run-task` para que ejecutes el smoke-test desde CLI.
