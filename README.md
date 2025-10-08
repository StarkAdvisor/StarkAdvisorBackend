# StarkAdvisor
# StarkAdvisor Backend

Este README describe cómo instalar y configurar el backend Django `StarkAdvisorBackend` en entorno de desarrollo y producción, teniendo en cuenta la estructura de configuraciones en `starkadvisorbackend/settings/`.

## Resumen rápido
- Proyecto: Django (estructura multi-settings: `base.py`, `local.py`, `production.py`).
- Configuración por defecto en `manage.py` apunta a `starkadvisorbackend.settings.local`.
- El proyecto usa variables de entorno gestionadas con `django-environ`.
- Hay un `Pipfile`/`Pipfile.lock` en el repositorio; también puedes usar `requirements.txt`.

## Prerrequisitos
- Python 3.11+
- Git
- (Opcional) Docker / Docker Compose para servicios como PostgreSQL y Redis

## Archivos de configuración
- `starkadvisorbackend/settings/base.py` — configuración común (env, MONGO, DRF, apps, etc.).
- `starkadvisorbackend/settings/local.py` — configuración para desarrollo (DEBUG=True, DB local por defecto, CORS abierto, middleware de desarrollo).
- `starkadvisorbackend/settings/production.py` — configuración para producción (DEBUG=False, HTTPS, PostgreSQL, Redis, logs, `STATIC_ROOT`, `MEDIA_ROOT`).

Las configuraciones leen variables de entorno mediante `environ.Env()`.
Variables importantes (defínelas en un `.env` o en el entorno):
- `SECRET_KEY` (obligatoria en producción)
- `DEBUG` (True/False)
- `ALLOWED_HOSTS` (coma-separados)
- DB (Postgres): `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- Redis: `REDIS_URL` o `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`
- Mongo: `MONGO_URI` o `MONGO_NAME`, `MONGO_HOST`, `MONGO_PORT` (el `MONGO_URI` tiene precedencia si está presente)
- Opcionales chatbot: `FAQ_PATH`, `FAQ_MODEL_PATH`, `FINANCIAL_NEWS_SOURCES`

## Instalación (Desarrollo - opción A: Pipenv)
Si usas Pipenv (hay `Pipfile`):

```powershell
# Instala pipenv (si no lo tienes)
pip install --user pipenv

# Desde la raíz del repo
cd C:\Users\ASUS\Desktop\X\StarkAdvisorBackend
pipenv install --dev

# Activar shell de pipenv
pipenv shell
```

Generar `requirements.txt` desde `Pipfile.lock` (si necesitas):

```powershell
pipenv lock -r > requirements.txt
pipenv lock -r -d > requirements-dev.txt
```

## Instalación (Desarrollo - opción B: venv y pip)
```powershell
cd C:\Users\ASUS\Desktop\X\StarkAdvisorBackend
python -m venv .venv
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## Variables de entorno (.env)
Crea un archivo `.env` en la raíz con, como mínimo, las variables necesarias. Ejemplo mínimo para desarrollo (ajusta valores):

```
# .env
SECRET_KEY=django-insecure-dev-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=starkadvisorbd
DB_USER=postgres
DB_PASSWORD=root
DB_HOST=localhost
DB_PORT=5432
REDIS_URL=redis://localhost:6379/0
# Mongo (elige MONGO_URI o las variables individuales)
MONGO_URI=
# o
MONGO_NAME=starkadvisor
MONGO_HOST=localhost
MONGO_PORT=27017
```

El proyecto usa `environ.Env.read_env()` en `base.py`, así que si `.env` está en la raíz será cargado automáticamente.

## Arrancar servicios (con Docker Compose local)
Si prefieres usar Docker para Postgres y Redis, hay un `docker-compose.local.yml`.

```powershell
# Levantar servicios
docker-compose -f docker-compose.local.yml up -d

# Verificar contenedores
docker ps
```

## Migraciones, superusuario y pruebas
```powershell
# Activar virtualenv/pipenv si aplica
. .\.venv\Scripts\Activate.ps1
# o pipenv shell

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Ejecutar tests
python manage.py test
```

## Ejecutar servidor (desarrollo)
Por defecto `manage.py` carga `starkadvisorbackend.settings.local`.

```powershell
python manage.py runserver
```

## Recolectar estáticos y despliegue básico (producción)
En producción asegúrate de definir `DJANGO_SETTINGS_MODULE=starkadvisorbackend.settings.production` y de configurar un WSGI server (gunicorn/uWSGI) y un proxy reverso (nginx).

```powershell
# Ejemplo de variables de entorno (PowerShell)
$env:DJANGO_SETTINGS_MODULE = "starkadvisorbackend.settings.production"
$env:SECRET_KEY = "<tu-secret>"
# Resto de variables DB y Redis...

# Recolectar estáticos
python manage.py collectstatic --noinput

# Ejecutar con gunicorn (instálalo primero)
gunicorn starkadvisorbackend.wsgi:application --bind 0.0.0.0:8000
```

## Logs, Static y Media
- `STATIC_ROOT` en producción apunta a `<BASE_DIR>/staticfiles`.
- `MEDIA_ROOT` apunta a `<BASE_DIR>/media`.
- Los logs (errores) se guardan en `logs/django_errors.log` según `production.py`.

Asegúrate de que el usuario del proceso tenga permisos de escritura a esos directorios.

## Recomendaciones
- Versiona `Pipfile.lock` o `requirements.txt` para que otros reproductores obtengan las mismas versiones.
- No subas tu `.env` al repositorio.
- Usa `pip-tools` (`pip-compile`) si quieres separar `requirements.in` (top-level) y `requirements.txt` (locked).

## Cómo generar `requirements.txt` rápidamente
- Desde el entorno activo:

```powershell
pip freeze > requirements.txt
```

- O, si usas pip-tools:

```powershell
pip install --user pip-tools
pip-compile --output-file=requirements.txt requirements.in
```

## Notas específicas sobre la carpeta `starkadvisorbackend/settings`
- `local.py` inserta un middleware `starkadvisorbackend.middleware.DisableCSRFMiddleware` para desarrollo (verifica si necesitas habilitar CSRF en entornos abiertos).
- `production.py` fuerza HTTPS (`SECURE_SSL_REDIRECT = True`) y cookies seguras; completa todas las variables de entorno antes de activar producción.
- Mongo se configura desde `base.py` vía `MONGO_DB` / `MONGO_URI`.
- FAQ y modelos de chatbot se refieren a rutas relativas, controla `FAQ_PATH` y `FAQ_MODEL_PATH` si modificas la estructura de carpetas.

### Cambiar qué settings usa Django (manage.py / wsgi / asgi)
En este proyecto `manage.py`, `wsgi.py` y `asgi.py` por defecto usan `starkadvisorbackend.settings.local`.
Si quieres cambiar a producción u otro archivo de settings debes ajustar la variable de entorno `DJANGO_SETTINGS_MODULE` en los tres lugares donde corresponda (o definirla globalmente en el entorno del proceso).

Ejemplos:

```powershell
# Definir para la sesión actual (PowerShell)
$env:DJANGO_SETTINGS_MODULE = "starkadvisorbackend.settings.production"

# Para WSGI/ASGI en despliegue (ejemplo systemd) exporta la variable en el servicio que arranca gunicorn/uvicorn
```

También puedes editar directamente `wsgi.py` y `asgi.py` si necesitas un valor por defecto distinto al momento de deploy (no recomendado — mejor definir `DJANGO_SETTINGS_MODULE` desde el entorno del sistema):

```python
# ejemplo en wsgi.py/asgi.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'starkadvisorbackend.settings.production')
```

### Mongo y Redis: `*_URI` vs variables individuales (precedencia)
Las settings para Mongo y Redis en este proyecto aceptan dos estilos:

- URI completa (p. ej. `MONGO_URI`, `REDIS_URL`) — forma compacta que incluye esquema, host, puerto, base y credenciales.
- Variables individuales (p. ej. `MONGO_HOST`, `MONGO_PORT`, `MONGO_NAME` o `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`).

Comportamiento y recomendación:

- Si se provee `MONGO_URI` en el entorno (no-nulo), el proyecto usará esa URI para conectar a Mongo y las variables individuales de Mongo serán ignoradas.
- De forma similar, si `REDIS_URL` está presente, se usará esa URL y las variables `REDIS_HOST`/`REDIS_PORT`/`REDIS_DB` no serán tenidas en cuenta.
- Esto permite flexibilidad: en local puedes usar variables individuales, y en producción usar una única URI gestionada por tu proveedor (p. ej. `mongodb+srv://...` o `rediss://...`).

Ejemplos de `.env` con URI completa:

```
MONGO_URI=mongodb://user:pass@mongo-host:27017/starkadvisor
REDIS_URL=redis://:password@redis-host:6379/0
```

Si no usas las URIs, define las variables individuales que están documentadas en `starkadvisorbackend/settings/base.py` y `local.py`.

## Contribuir
1. Fork y crea una rama feature
2. Ejecuta pruebas localmente
3. Haz PR hacia `main` con una descripción clara

---

Si quieres, puedo:
- Crear un `.env.example` con las variables más importantes.
- Actualizar `requirements.txt` automáticamente desde tu entorno actual (vi que ejecutaste `pip freeze > requirements.txt`).
- Añadir instrucciones específicas de Docker/Nginx para producción.

Dime qué prefieres y lo hago.

## Comandos útiles y recomendaciones de ejecución periódica
A continuación se listan los scripts CLI que existen en el proyecto y recomendaciones para ejecutarlos periódicamente (crontab). Todos los comandos asumen que estás en la raíz del repo y tienes el entorno virtual activado o usas pipenv.

- Actualizar "Trade of the Day":

```powershell
python -m stocks.scripts.update_trade_of_the_day_data
```

Descripción: trae la información de los trades del día y guarda/actualiza el documento correspondiente en Mongo (colección `trade_of_the_day`).
Recomendación: programar en cron cada 8 horas (por ejemplo: 0 */8 * * *), para mantener la información reciente sin sobrecargar las APIs.

- Scraping de noticias:

```powershell
python -m news.scripts.scraping_job
```

Descripción: ejecuta el scraper de noticias por categorías, realiza análisis de sentimiento y persiste los resultados en la base de datos.
Recomendación: ejecutar una vez cada dos días (por ejemplo en cron: 0 3 */2 * *). Este job puede consumir rate limits de fuentes externas, por eso una frecuencia baja es recomendable.

- Pipeline de mercado (todo en uno):

```powershell
python -m stocks.scripts.market_pipeline_cli run_all --period 5d --interval 1d
```

Descripción: `run_all` descarga y actualiza métricas y series temporales para acciones, ETFs y divisas. Incluye tanto time series históricos como métricas calculadas.
Recomendaciones:

- Primera ejecución: si es la primera vez que lo ejecutas, trae los últimos 5 años (`--period 5y`) con `--interval 1d` para poblar la base histórica completa.
- Ejecución diaria: para mantenimiento, programa un cron diario que actualice las métricas y series de los últimos 3 días a intervalo de 1 día (p. ej. `--period 3d --interval 1d`).

Ejemplos de crontab (edítalos con `crontab -e` en Linux; en Windows usa el Programador de tareas):

```cron
# Cada 8 horas -> update_trade_of_the_day_data
0 */8 * * * cd /path/to/StarkAdvisorBackend && . .venv/bin/activate && python -m stocks.scripts.update_trade_of_the_day_data

# Cada 2 días a las 03:00 -> scraping_job
0 3 */2 * * cd /path/to/StarkAdvisorBackend && . .venv/bin/activate && python -m news.scripts.scraping_job

# Diario a las 02:00 -> pipeline de mercado (actualizar últimos 3 días)
0 2 * * * cd /path/to/StarkAdvisorBackend && . .venv/bin/activate && python -m stocks.scripts.market_pipeline_cli run_all --period 3d --interval 1d
```

Notas:
- Ajusta rutas y el comando de activación del virtualenv según tu OS (Windows PowerShell usa `. .\.venv\Scripts\Activate.ps1` o `venv\Scripts\activate`).
- Si ejecutas dentro de contenedores (Docker), adapta los comandos para ejecutarlos dentro del contenedor o usa tareas programadas en el orquestador.
- Revisa logs y límites de API externos (rate limits). Para scraping heavy, considera usar backoff y retries (el job ya implementa retries básicos).
