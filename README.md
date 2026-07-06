# Sistema IoT para Espacios Institucionales

Este proyecto es una plataforma web para el monitoreo y gestión de dispositivos IoT (ESP32) en espacios institucionales. Está construido con **Django Rest Framework** en el backend y **React (Vite) + Zustand** en el frontend.

## 🚀 Guía de Instalación Rápida

Si acabas de clonar este repositorio en una computadora nueva, tienes dos opciones para ejecutarlo. Hemos simplificado el proceso incluyendo una base de datos local y configuración preestablecida.

> **💡 Nota sobre la portabilidad del proyecto:**
> A diferencia de los proyectos estándar de Django que te obligan a reconstruir todo el entorno, la base de datos y los usuarios desde cero cada vez que cambias de PC, hemos "hackeado" este comportamiento. La base de datos (`db.sqlite3`) y las variables de entorno (`.env`) están intencionalmente incluidas en el repositorio. Esto significa que **al clonar el proyecto te llevas una copia exacta y funcional** (Plug & Play), ahorrándote horas de configuración y dolores de cabeza al cambiar de equipo.

---

### Opción A: Ejecución con Docker (Recomendado 🐳)

La forma más fácil y moderna de correr el proyecto en cualquier computadora sin instalar dependencias. **Si usas esta opción, NO necesitas instalar Python, Node.js, ni hacer los pasos manuales.**

> ⚠️ **Requisito Indispensable:** Debes tener [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado **Y ABIERTO** en tu computadora (debes ver la ballena cargando y decir "Engine running"). Si al ejecutar el comando te sale un error diciendo que *'docker-compose' no se reconoce* o *'failed to connect to the docker API'*, significa que Docker está cerrado o no lo tienes instalado, en cuyo caso debes usar la **Opción B**.

tienes que abrir un terminal en powershell como administrador y ejecutar el siguiente comando:
```wsl --install
```
reinicia la pc o laptop

instala docker desktop y tenlo abierto.

ir a tu carpeta raiz del proyecto

Ejecuta en la terminal (en la raíz del proyecto):
```powershell
docker-compose up -d --build
```

> **⏳ Ten paciencia (Sólo la primera vez):** 
> La letra `-d` significa que se ejecutará de forma silenciosa en segundo plano. La consola te devolverá el control casi de inmediato y no verás letras moverse. **Sin embargo, Docker estará descargando GBs de información de internet**. 
> Dale de **2 a 5 minutos** de tiempo antes de intentar abrir la página web, de lo contrario tu navegador dirá que no puede conectarse. 
> 
> *(Si prefieres ver el progreso en vivo en la consola, simplemente quita el `-d`: corre `docker-compose up --build`)*.

Esto levantará el backend en el puerto 8000 y el frontend en el puerto 5173. ¡Listo! Salta a la sección de **Probar el Proyecto**.

> 🛑 **¿Cómo apagar el proyecto en Docker?**
> Como lo ejecutamos en segundo plano con la letra `-d`, los servidores seguirán corriendo aunque cierres la terminal. Cuando termines de trabajar y quieras apagarlos para no consumir memoria, simplemente abre la terminal en la raíz del proyecto y ejecuta:
> ```powershell
> docker-compose down
> ```
---

### Opción B: Ejecución Manual Local

Si el comando de Docker te dio error porque no lo tienes instalado, hazlo de forma manual. 

> **¿Ya habías ejecutado el proyecto en esta PC antes?**
> Si es así, **sáltate los pasos 1 y 2** y ve directo al paso 3. Los pasos 1 y 2 son **sólo la primera vez** que descargas el código.

#### 1. Instalar Backend (Django) - *Sólo primera vez*
Abre la terminal en la raíz y ejecuta:
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

#### 2. Instalar Frontend (React) - *Sólo primera vez*
Abre otra terminal en la carpeta `/frontend` y ejecuta:
```powershell
npm install
```

> 🛑 **¿Error de ejecución de scripts en PowerShell?** 
> Si al correr `npm` o activar el entorno (`.\venv\...`) te sale un texto rojo diciendo que "la ejecución de scripts está deshabilitada", debes correr este comando una sola vez como administrador en PowerShell para dar permisos:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` (presiona 'S' para confirmar).

#### 3. Levantar los servidores (Cada vez que vayas a programar)
Necesitas tener dos terminales abiertas:

- **Terminal 1 (Raíz del proyecto):**
  ```powershell
  .\venv\Scripts\activate
  python manage.py runserver
  ```

- **Terminal 2 (Dentro de la carpeta /frontend):**
  ```powershell
  npm run dev
  ```

---

### Probar el Proyecto ⚡

Ya sea que usaste Docker o la instalación manual, abre tu navegador y dirígete a `http://localhost:5173`. 
Puedes iniciar sesión con el usuario de pruebas por defecto:
- **Usuario:** `admin`
- **Contraseña:** `admin`

## �️ Documentación del Frontend

La interfaz web está construida con React + Vite y se encarga de consumir la API del backend para mostrar información operativa y permitir la interacción con el sistema.

### Tecnologías del frontend
- React 19
- Vite
- Zustand para manejo de estado global
- React Router DOM para navegación
- Axios para comunicación con la API

### Estructura principal
- [frontend/src/main.jsx](frontend/src/main.jsx): punto de entrada de la aplicación.
- [frontend/src/App.jsx](frontend/src/App.jsx): configuración de rutas y protección de vistas.
- [frontend/src/pages](frontend/src/pages): páginas de la interfaz como login, dashboard, dispositivos, ocupación, alertas y reportes.
- [frontend/src/store](frontend/src/store): almacenes globales para autenticación, tema, toast y estado IoT.
- [frontend/src/axiosConfig.js](frontend/src/axiosConfig.js): configuración centralizada de Axios, tokens JWT y refresh automático.

### Rutas principales
- `/`: landing page pública.
- `/login`: inicio de sesión.
- `/register`: registro de usuarios.
- `/biometria`: vista de autenticación biométrica.
- `/dashboard`: panel principal protegido.
- `/dashboard/dispositivos`: gestión de dispositivos.
- `/dashboard/ocupacion`: visualización de ocupación.
- `/dashboard/alertas`: listado de alertas.
- `/dashboard/reportes`: reportes del sistema.
- `/dashboard/auditoria`: auditoría y trazabilidad.

### Flujo de autenticación
El frontend usa Zustand para administrar el estado de sesión. Al iniciar sesión, guarda los tokens JWT en el almacenamiento local y los reutiliza en las peticiones con Axios. Si un token expira, se intenta refrescar automáticamente antes de redirigir al login.

### Comandos útiles
Desde la carpeta [frontend](frontend):
```powershell
npm install
npm run dev
npm run build
```

### Notas de desarrollo
- Las rutas privadas están protegidas mediante un componente de validación de autenticación.
- El diseño está dividido en páginas y componentes reutilizables.
- Los mensajes de feedback al usuario se gestionan con un sistema de toasts.

## �📡 Conexión de Hardware (ESP32)

Para vincular dispositivos físicos (ESP32):
1. Inicia sesión en el panel admin de Django: `http://localhost:8000/admin/`.
2. Genera una **API Key** desde la sección correspondiente.
3. Copia esa llave y configúrala en el código C++ (Arduino) de tu placa junto a las peticiones POST hacia la ruta `/api/v1/dispositivos/historial/recibir/`.
