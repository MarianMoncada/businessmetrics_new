# 📊 BusinessMetrics - Proyecto final de Administración de Base de Datos

[![Python](https://img.shields.io/badge/Python-99.5%25-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Sistema integral de administración de bases de datos empresariales que implementa las prácticas aprendidas de gestión, monitoreo, respaldo y seguridad de datos.

---

## 📋 Tabla de Contenidos

- [Descripción del Proyecto](#-descripción-del-proyecto)
- [Características Principales](#-características-principales)
- [Arquitectura del Sistema](#-arquitectura-del-sistema)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Scripts Disponibles](#-scripts-disponibles)
- [Monitoreo y Seguridad](#-monitoreo-y-seguridad)
- [Respaldo y Recuperación](#-respaldo-y-recuperación)
- [Contribución](#-contribución)
- [Licencia](#-licencia)

---

## 🎯 Descripción del Proyecto

**BusinessMetrics** es un proyecto académico de Administración de Bases de Datos (ABD) que demuestra la implementación práctica de conceptos fundamentales en la gestión de sistemas de bases de datos empresariales. El proyecto integra herramientas modernas como Docker, PostgreSQL y Apache Airflow para crear un entorno completo de administración de datos.

### Objetivos del Proyecto

- Implementar administradores y manejadores de bases de datos
- Gestionar espacios lógicos y físicos de almacenamiento
- Aplicar técnicas de respaldo y recuperación
- Configurar monitoreo y seguridad de la base de datos
- Optimizar el rendimiento mediante afinación de consultas
- Desarrollar scripts y consultas funcionales

---

## ✨ Características Principales

| Característica | Descripción |
|----------------|-------------|
| **Orquestación** | Despliegue automatizado con Docker Compose |
| **Respaldos Automatizados** | Sistema de backups programados con retención configurable |
| **Monitoreo** | Dashboard de métricas y alertas en tiempo real |
| **Seguridad** | Gestión de usuarios, roles y permisos |
| **ETL/Pipelines** | Flujos de datos automatizados con Apache Airflow |
| **Afinación** | Herramientas de análisis y optimización de consultas |

---

## 🏗 Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Compose Network                    │
├─────────────┬─────────────┬─────────────┬──────────────────┤
│  PostgreSQL │   Airflow   │  Monitoring │    Backups       │
│   Database  │  Scheduler  │   Service   │    Service       │
│   :5432     │   :8080     │   :9090     │   Scheduled      │
└─────────────┴─────────────┴─────────────┴──────────────────┘
```

---

## 📦 Requisitos Previos

Antes de instalar el proyecto, asegúrate de tener instalado:

- **Docker Desktop** v20.10 o superior
- **Docker Compose** v2.0 o superior
- **Git** v2.30 o superior
- **Python** 3.9+ (opcional, para desarrollo local)

### Verificar instalación

```bash
docker --version
docker-compose --version
git --version
```

---

## 🚀 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/MarianMoncada/businessmetrics_new.git
cd businessmetrics_new
```

### 2. Configurar variables de entorno

Copia el archivo de ejemplo y edita las variables según tu entorno:

```bash
cp .env.example .env
```

Edita el archivo `.env` con tus configuraciones:

```env
# Base de Datos
POSTGRES_USER=admin
POSTGRES_PASSWORD=tu_password_seguro
POSTGRES_DB=businessmetrics
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Airflow
AIRFLOW_ADMIN_USER=airflow
AIRFLOW_ADMIN_PASSWORD=airflow_password

# Backup
BACKUP_RETENTION_DAYS=7
BACKUP_SCHEDULE="0 2 * * *"
```

### 3. Iniciar los servicios

```bash
docker-compose up -d
```

### 4. Verificar el estado de los contenedores

```bash
docker-compose ps
```

Deberías ver todos los servicios en estado "running".

---

## ⚙️ Configuración

### Configuración de la Base de Datos

1. **Acceder a PostgreSQL:**
   ```bash
   docker exec -it businessmetrics_postgres psql -U admin -d businessmetrics
   ```

2. **Crear esquemas y tablas:**
   ```bash
   docker exec -it businessmetrics_postgres psql -U admin -d businessmetrics -f /scripts/init_schema.sql
   ```

### Configuración de Airflow

1. **Acceder al panel web:** `http://localhost:8080`
2. **Credenciales por defecto:** Usuario y contraseña configurados en `.env`
3. **Activar DAGs:** Navegar a la lista de DAGs y activar los pipelines necesarios

---

## 📖 Uso

### Comandos Principales

| Comando | Descripción |
|---------|-------------|
| `docker-compose up -d` | Iniciar todos los servicios |
| `docker-compose down` | Detener todos los servicios |
| `docker-compose logs -f` | Ver logs en tiempo real |
| `docker-compose restart` | Reiniciar servicios |

### Ejecutar Scripts

```bash
# Ejecutar script de respaldo manual
docker exec -it businessmetrics_postgres /scripts/backup.sh

# Ejecutar script de monitoreo
docker exec -it businessmetrics_postgres /scripts/monitor.sh

# Ejecutar consultas de afinación
docker exec -it businessmetrics_postgres /scripts/tuning_queries.sql
```

### Acceso a Servicios

| Servicio | URL | Descripción |
|----------|-----|-------------|
| PostgreSQL | `localhost:5432` | Base de datos principal |
| Airflow | `http://localhost:8080` | Orquestador de pipelines |
| Monitoring | `http://localhost:9090` | Dashboard de monitoreo |

---

## 📁 Estructura del Proyecto

```
businessmetrics_new/
│
├── 📂 backups/              # Respaldos automáticos y manuales
│   ├── daily/               # Backups diarios
│   ├── weekly/              # Backups semanales
│   └── scripts/             # Scripts de backup
│
├── 📂 dags/                 # DAGs de Apache Airflow
│   ├── etl_pipeline.py      # Pipeline principal de ETL
│   └── maintenance_dag.py   # Tareas de mantenimiento
│
├── 📂 data/                 # Datos y datasets
│   ├── raw/                 # Datos sin procesar
│   ├── processed/           # Datos procesados
│   └── seeds/               # Datos iniciales
│
├── 📂 monitoring/           # Configuración de monitoreo
│   ├── alerts/              # Reglas de alertas
│   ├── dashboards/          # Configuración de dashboards
│   └── metrics/             # Definición de métricas
│
├── 📂 scripts/              # Scripts SQL y Shell
│   ├── init_schema.sql      # Creación de esquemas
│   ├── procedures.sql       # Procedimientos almacenados
│   ├── backup.sh            # Script de respaldo
│   ├── restore.sh           # Script de restauración
│   └── tuning_queries.sql   # Consultas de afinación
│
├── 📄 .env                  # Variables de entorno
├── 📄 docker-compose.yaml   # Orquestación de contenedores
└── 📄 README.md             # Documentación del proyecto
```

---

## 📜 Scripts Disponibles

### Scripts SQL

| Script | Descripción |
|--------|-------------|
| `init_schema.sql` | Inicialización de esquemas y tablas |
| `procedures.sql` | Procedimientos almacenados y funciones |
| `tuning_queries.sql` | Consultas de análisis de rendimiento |
| `security_setup.sql` | Configuración de roles y permisos |

### Scripts Shell

| Script | Descripción |
|--------|-------------|
| `backup.sh` | Realiza backup completo de la base de datos |
| `restore.sh` | Restaura desde un archivo de backup |
| `monitor.sh` | Muestra estadísticas del sistema |
| `maintenance.sh` | Ejecuta tareas de mantenimiento |

---

## 🔒 Monitoreo y Seguridad

### Sistema de Monitoreo

El proyecto incluye un sistema de monitoreo que supervisa:

- Uso de CPU y memoria del servidor de base de datos
- Conexiones activas y en espera
- Tamaño de tablas e índices
- Tiempos de respuesta de consultas
- Bloqueos y deadlocks

### Configuración de Seguridad

1. **Gestión de Usuarios:**
   ```sql
   -- Crear usuario con permisos específicos
   CREATE USER app_user WITH PASSWORD 'secure_password';
   GRANT SELECT, INSERT ON ALL TABLES IN SCHEMA public TO app_user;
   ```

2. **Auditoría:** Logs de acceso y modificaciones habilitados
3. **Encriptación:** Conexiones SSL configuradas

---

## 💾 Respaldo y Recuperación

### Estrategia de Respaldo

| Tipo | Frecuencia | Retención |
|------|------------|-----------|
| Completo | Diario (2:00 AM) | 7 días |
| Incremental | Cada 6 horas | 2 días |
| Semanal | Domingo | 4 semanas |

### Realizar Backup Manual

```bash
# Backup completo
./scripts/backup.sh full

# Backup de esquema específico
./scripts/backup.sh schema public
```

### Restaurar desde Backup

```bash
# Restaurar último backup
./scripts/restore.sh latest

# Restaurar backup específico
./scripts/restore.sh backups/daily/backup_2024-01-15.sql
```

---

## 🤝 Contribución

Las contribuciones son bienvenidas. Para contribuir:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request


---

## 👥 Autores

- **Fajardo Barraza Ana Paloma**
- **Goudge Moncada Marian** 
- **Falcón Díaz Ricardo**

---

<p align="center">
  <i>Proyecto desarrollado como parte del curso de Administración de Bases de Datos</i>
</p>
