# Dockerfile - version web de Enseñando (servidor siempre encendido, p. ej. Koyeb).
# La plataforma construye esta imagen y la publica con HTTPS (necesario para la camara).
# Los usuarios se guardan en MongoDB Atlas: definir la variable de entorno MONGO_URI.

FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    WEB_DEPLOYMENT=1 \
    PORT=8000

# Librerias de sistema que necesitan OpenCV y MediaPipe (libegl1/libgles2: detector de manos).
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 libgomp1 libegl1 libgles2 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user PATH=/home/user/.local/bin:$PATH
WORKDIR /home/user/app

COPY --chown=user requirements-web.txt .
RUN pip install --no-cache-dir --user -r requirements-web.txt

COPY --chown=user . .

EXPOSE 8000
# Un solo proceso: cada sesion guarda su estado (letra, reto, evaluacion) en memoria.
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT} --workers 1 --threads 16 --timeout 120 web_server:app"]
