FROM python:3.10-slim

WORKDIR /app

# Evita conflictos con caché de pip
ENV PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1

# Instala dependencias del sistema (si necesitas compiladores para algunas dependencias de Pip)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala requirements primero (aprovecha caché de Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de la aplicación
COPY . .

# Cambia a usuario no root
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 3000

CMD ["python", "run.py"]