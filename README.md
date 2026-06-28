# Sistema IoT para Espacios Institucionales

Este proyecto es una plataforma web para el monitoreo y gestión de dispositivos IoT (ESP32) en espacios institucionales. Está construido con **Django Rest Framework** en el backend y **React (Vite) + Zustand** en el frontend.

## 🚀 Guía de Instalación Rápida

Si acabas de clonar este repositorio en una computadora nueva, tienes dos opciones para ejecutarlo. Hemos simplificado el proceso incluyendo una base de datos local y configuración preestablecida.

> **💡 Nota sobre la portabilidad del proyecto:**
> A diferencia de los proyectos estándar de Django que te obligan a reconstruir todo el entorno, la base de datos y los usuarios desde cero cada vez que cambias de PC, hemos "hackeado" este comportamiento. La base de datos (`db.sqlite3`) y las variables de entorno (`.env`) están intencionalmente incluidas en el repositorio. Esto significa que **al clonar el proyecto te llevas una copia exacta y funcional** (Plug & Play), ahorrándote horas de configuración y dolores de cabeza al cambiar de equipo.

---

### Opción A: Ejecución con Docker (Recomendado 🐳)

La forma más fácil y moderna de correr el proyecto en cualquier computadora sin instalar dependencias. **Si usas esta opción, NO necesitas instalar Python, Node.js, ni hacer los pasos manuales.**

Asegúrate de tener [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y simplemente ejecuta en la terminal (en la raíz del proyecto):
```powershell
docker-compose up -d --build
```
Esto descargará todo lo necesario y levantará automáticamente tanto el backend en el puerto 8000 como el frontend en el puerto 5173.

¡Listo! Ya puedes saltar a la sección de **Probar el Proyecto**.

---

### Opción B: Instalación y Ejecución Manual

Si no tienes Docker instalado, deberás configurar ambos entornos de manera manual.

#### 1. Configurar el Backend (Django)

Abre la terminal en la raíz del proyecto (`Sistema_IoT_para_espacios_institucionales`) y ejecuta:

1. **Crear entorno virtual de Python:**
   ```powershell
   python -m venv venv
   ```

2. **Activar el entorno virtual:**
   - En Windows (Powershell):
     ```powershell
     .\venv\Scripts\activate
     ```
   - En Mac/Linux:
     ```bash
     source venv/bin/activate
     ```

3. **Instalar dependencias del Backend:**
   ```powershell
   pip install -r requirements.txt
   ```
*(Nota: La base de datos `db.sqlite3` y las variables de entorno `.env` ya vienen preconfiguradas, no necesitas hacer migraciones).*

#### 2. Configurar el Frontend (React/Vite)

Abre una **nueva** terminal (o pestaña) e ingresa a la carpeta del frontend:

1. **Ingresar a la carpeta:**
   ```powershell
   cd frontend
   ```

2. **Instalar dependencias de Node.js:**
   ```powershell
   npm install
   ```

#### 3. Ejecutar Manualmente

Para correr el proyecto localmente, necesitas tener dos terminales abiertas al mismo tiempo:

- **Terminal 1 (Backend Django - Raíz del proyecto con venv activado):**
  ```powershell
  python manage.py runserver
  ```

- **Terminal 2 (Frontend React - Dentro de la carpeta /frontend):**
  ```powershell
  npm run dev
  ```

---

### Probar el Proyecto ⚡

Ya sea que usaste Docker o la instalación manual, abre tu navegador y dirígete a `http://localhost:5173`. 
Puedes iniciar sesión con el usuario de pruebas por defecto:
- **Usuario:** `admin`
- **Contraseña:** `admin`

## 📡 Conexión de Hardware (ESP32)

Para vincular dispositivos físicos (ESP32):
1. Inicia sesión en el panel admin de Django: `http://localhost:8000/admin/`.
2. Genera una **API Key** desde la sección correspondiente.
3. Copia esa llave y configúrala en el código C++ (Arduino) de tu placa junto a las peticiones POST hacia la ruta `/api/v1/dispositivos/historial/recibir/`.
