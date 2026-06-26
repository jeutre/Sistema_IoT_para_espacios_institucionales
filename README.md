# Sistema IoT para Espacios Institucionales

Este proyecto es una plataforma web para el monitoreo y gestión de dispositivos IoT (ESP32) en espacios institucionales. Está construido con **Django Rest Framework** en el backend y **React (Vite) + Zustand** en el frontend.

## 🚀 Guía de Instalación Rápida (Para nuevos clones)

Si acabas de clonar este repositorio en tu computadora, debes seguir estos pasos para que el proyecto funcione, ya que por seguridad ciertas carpetas y configuraciones (`venv`, `node_modules`, `db.sqlite3`, `.env`) no se suben a Git.

### 1. Configurar el Backend (Django)

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

4. **Crear archivo de variables de entorno:**
   Crea un archivo llamado `.env` exactamente en la raíz del proyecto y pega lo siguiente dentro de él:
   ```ini
   SECRET_KEY=django-insecure-up=7x3kjun^g@m3ny##+z(36&0oj$_ktk-9^j)3-kbjq-61@x-
   DEBUG=True
   ALLOWED_HOSTS=127.0.0.1,localhost
   CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173
   DATABASE_URL=sqlite:///db.sqlite3
   ```

5. **Aplicar migraciones para crear la base de datos local:**
   ```powershell
   python manage.py migrate
   ```

6. **Crear un usuario administrador:**
   ```powershell
   python manage.py createsuperuser
   ```
   *(Sigue las instrucciones en pantalla para crear un usuario y contraseña).*

---

### 2. Configurar el Frontend (React/Vite)

Abre una **nueva** terminal (o pestaña) e ingresa a la carpeta del frontend:

1. **Ingresar a la carpeta:**
   ```powershell
   cd frontend
   ```

2. **Instalar dependencias de Node.js:**
   ```powershell
   npm install
   ```

---

### 3. Ejecutar el Proyecto ⚡

Para correr el proyecto localmente, necesitas tener dos terminales abiertas al mismo tiempo:

- **Terminal 1 (Backend Django - Raíz del proyecto con venv activado):**
  ```powershell
  python manage.py runserver 8000
  ```

- **Terminal 2 (Frontend React - Dentro de la carpeta /frontend):**
  ```powershell
  npm run dev
  ```

¡Listo! Abre tu navegador y dirígete a `http://localhost:5173`. Inicia sesión con el superusuario que creaste en el paso 1.6.

## 📡 Conexión de Hardware (ESP32)

Para vincular dispositivos físicos (ESP32):
1. Inicia sesión en el panel admin de Django: `http://localhost:8000/admin/`.
2. Genera una **API Key** desde la sección correspondiente.
3. Copia esa llave y configúrala en el código C++ (Arduino) de tu placa junto a las peticiones POST hacia la ruta `/api/v1/dispositivos/historial/recibir/`.
