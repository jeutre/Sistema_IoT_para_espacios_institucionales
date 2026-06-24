# Manual de Instalación y Despliegue (Sistema IoT)

Este documento detalla los pasos necesarios para levantar el backend del Sistema IoT para espacios institucionales. Tienes dos opciones principales para levantar el proyecto: de forma tradicional (local) o usando Docker (recomendado para producción o equipos de trabajo).

---

## Opción 1: Despliegue Rápido con Docker (Recomendado)

Esta es la forma más fácil y libre de errores de correr el proyecto, ya que no importa si usas Windows, Mac o Linux, el entorno de Python 3.11 estará aislado y configurado correctamente.

### Requisitos Previos:
- Tener instalado [Docker Desktop](https://www.docker.com/products/docker-desktop/).

### Pasos:

1. **Abrir la terminal** en la carpeta principal del proyecto (donde se encuentra el archivo `docker-compose.yml`).
2. **Construir y levantar el servidor** ejecutando el siguiente comando:
   ```bash
   docker compose up --build
   ```
3. Docker descargará las dependencias necesarias, aplicará las migraciones a la base de datos de manera automática y levantará el servidor en el puerto 8000.
4. **Para apagar el servidor**, puedes presionar `Ctrl + C` en la terminal, o correr:
   ```bash
   docker compose down
   ```

> [!NOTE]
> Cualquier cambio que hagas en el código fuente se reflejará instantáneamente gracias a los volúmenes de Docker configurados en el `docker-compose.yml`.

---

## Opción 2: Despliegue Local Tradicional (Desarrollo)

Si prefieres no usar Docker y ejecutar todo directamente desde tu consola local de Python.

### Requisitos Previos:
- Tener instalado Python 3.10 o superior.

### Pasos:

1. **Crear un entorno virtual** (opcional pero muy recomendado):
   ```bash
   python -m venv venv
   ```

2. **Activar el entorno virtual**:
   - En **Windows**:
     ```powershell
     .\venv\Scripts\activate
     ```
   - En **Linux/Mac**:
     ```bash
     source venv/bin/activate
     ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Variables de Entorno**:
   El proyecto usa la librería `decouple`. Asegúrate de tener tu archivo `.env` configurado en la raíz con lo siguiente:
   ```env
   SECRET_KEY=tu-clave-secreta-larga-aqui
   DEBUG=True
   ALLOWED_HOSTS=127.0.0.1,localhost
   CORS_ALLOWED_ORIGINS=http://localhost:3000
   ```

5. **Aplicar Migraciones** (Crear la base de datos SQLite):
   ```bash
   python manage.py migrate
   ```

6. **Crear un Superusuario** (Opcional, para entrar al panel de admin):
   ```bash
   python manage.py createsuperuser
   ```

7. **Levantar el servidor**:
   ```bash
   python manage.py runserver
   ```

---

## Rutas Importantes una vez iniciado

Una vez que el servidor reporte estar corriendo exitosamente (`Starting development server at http://127.0.0.1:8000/`), podrás acceder a:

- 📖 **Documentación Interactiva (Swagger):** [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
  > *Aquí puedes explorar gráficamente todos los endpoints de la API REST, ver qué JSON se espera y hacer pruebas en vivo.*

- 🛠️ **Panel de Administración:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
  > *Desde aquí puedes generar las API Keys para los dispositivos ESP32.*

- 🔑 **Autenticación (Generación de Token):** `POST http://127.0.0.1:8000/api/v1/auth/token/`
  > *Tu frontend en React/Vue debe consumir este endpoint para recibir los JSON Web Tokens.*
