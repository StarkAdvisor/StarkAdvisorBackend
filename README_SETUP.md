# StarkAdvisor - Setup Local

## 🚀 Configuración para Desarrollo Local

### Prerrequisitos
- Python 3.11+
- Docker Desktop
- Git

### 1. Clonar el Repositorio
```bash
git clone https://github.com/StarkAdvisor/StarkAdvisorBackend.git
cd StarkAdvisorBackend
```

### 2. Crear y Activar Entorno Virtual
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Base de Datos y Redis
```bash
# Iniciar contenedores Docker
docker-compose -f docker-compose.local.yml up -d

# Verificar que estén corriendo
docker ps
```

### 5. Configurar Django
```bash
# Aplicar migraciones
python manage.py migrate

# Crear superusuario (opcional)
python manage.py createsuperuser
```

### 6. Ejecutar Servidor de Desarrollo
```bash
python manage.py runserver
```

### 7. Probar la API
El servidor estará disponible en: `http://127.0.0.1:8000`

#### Endpoints Principales:
- **POST** `/api/auth/register/` - Registro de usuarios
- **POST** `/api/auth/login/` - Login
- **POST** `/api/auth/logout/` - Logout
- **GET** `/api/auth/session-status/` - Estado de sesión

#### Ejemplo de Registro:
```json
{
  "email": "usuario@example.com",
  "password": "password123",
  "first_name": "Juan",
  "last_name": "Pérez",
  "risk_profile": "Conservative"
}
```

#### Ejemplo de Login:
```json
{
  "email": "usuario@example.com",
  "password": "password123"
}
```

### 🔧 Configuración de Entorno

El proyecto utiliza configuraciones separadas:
- **Desarrollo**: `settings_local.py` - SQLite + Redis local
- **Producción**: `settings_production.py` - PostgreSQL + Redis

### 📊 Herramientas de Monitoreo

#### DataGrip (Recomendado)
1. Conectar a PostgreSQL:
   - Host: `localhost`
   - Port: `5432`
   - Database: `starkadvisor`
   - User: `starkadvisor_user`
   - Password: `starkadvisor_password`

2. Conectar a Redis:
   - Host: `localhost`
   - Port: `6379`

### 🐛 Troubleshooting

#### Error de CSRF
El proyecto incluye middleware personalizado que deshabilita CSRF para endpoints `/api/`

#### Error de Conexión Redis
```bash
# Verificar que Redis esté corriendo
docker exec -it redis-server redis-cli ping
```

#### Error de Base de Datos
```bash
# Reiniciar contenedores
docker-compose -f docker-compose.local.yml down
docker-compose -f docker-compose.local.yml up -d
```

### 📝 Arquitectura

- **Backend**: Django 5.2.5 + Django REST Framework
- **Base de Datos**: PostgreSQL 15 (Producción) / SQLite (Desarrollo)
- **Cache**: Redis 7
- **Autenticación**: Token-based + Redis Sessions
- **Perfiles de Riesgo**: Conservative, Moderate, Aggressive

### 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request
