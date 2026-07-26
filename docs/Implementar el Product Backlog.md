# Implementar el Product Backlog

El objetivo es implementar las funcionalidades detalladas en el documento `Product Backlog.md` dentro de la aplicación existente (Django + React). Al revisar el código base actual, se observa que ya están creadas las estructuras de las aplicaciones de Django (modelos y carpetas para `autenticacion`, `laboratorio`, `dispositivos`, etc.) y la estructura básica del frontend en React. El trabajo consistirá en desarrollar los endpoints de la API (DRF) y las vistas/componentes del frontend para cada historia de usuario.

## User Review Required

> [!WARNING]
> El Product Backlog contiene 42 Historias de Usuario distribuidas en múltiples Épicas y 4 Sprints. Implementar todo en un solo paso es inmanejable y propenso a errores. 
> 
> Propongo dividir el trabajo en fases iterativas, comenzando con una **Fase 1** que abarque las bases del sistema, y luego avanzar con las siguientes a medida que completemos y verifiquemos cada una. Por favor, revisa el plan a continuación y confírmame si estás de acuerdo en empezar por la **Fase 1**.

## Open Questions

- ¿Existe algún diseño específico en Figma o un template particular que debamos seguir para el Dashboard y los formularios en React, más allá de usar Bootstrap 5/Zustand como indica el README?
- Para la HU-01 (Login), ¿el usuario administrador ya existe en la base de datos o deberíamos crear un script/comando para generar el primer superusuario?

## Proposed Changes

### Fase 1: Autenticación, Laboratorios y Dispositivos (Épicas 1, 2 y 3)

Esta fase se centrará en establecer la seguridad y la estructura física (laboratorios y sensores ESP32).

#### Backend (Django)
- **Autenticación (HU-01, HU-02):** Configurar JWT (JSON Web Tokens) mediante `djangorestframework-simplejwt`. Crear endpoints para login (`/api/v1/auth/login/`) y validación de tokens.
- **Laboratorio (HU-03 a HU-05):** Crear serializadores y ViewSets para operaciones CRUD (Crear, Leer, Actualizar) del modelo `Laboratorio`. Endpoints en `/api/v1/laboratorios/`.
- **Dispositivos IoT (HU-06 a HU-08):** Crear serializadores y ViewSets para registrar y visualizar el estado del ESP32 y su historial de comunicación. Endpoints en `/api/v1/dispositivos/`.

#### Frontend (React)
- **Login:** Conectar la vista `/login` existente con el endpoint de Django, guardando el token JWT en Zustand o localStorage.
- **Dashboard - Laboratorios:** Crear la vista para listar laboratorios registrados y un modal/formulario para agregar nuevos o editarlos.
- **Dashboard - Dispositivos:** Crear la vista `/dashboard/dispositivos` para registrar un ESP32, ver su estado de conexión y su historial.

*(Las siguientes fases cubrirán Monitoreo de Ocupación (Épica 4), Control IPv4 (Épica 5), Automatizaciones (Épica 8), Dashboard y Alertas. Las detallaremos cuando completemos la Fase 1).*

## Verification Plan

### Automated Tests
- Ejecutar el servidor de Django y verificar que los nuevos endpoints devuelvan códigos HTTP correctos (200 OK, 201 Created).
- Ejecutar el entorno de desarrollo de Vite para verificar que el frontend compila sin errores.

### Manual Verification
1. Ingresar a `http://localhost:5173/login`, introducir credenciales de prueba y verificar el redireccionamiento exitoso al dashboard.
2. Navegar a la sección de Laboratorios, intentar registrar un nuevo laboratorio y confirmar que aparezca en la lista.
3. Navegar a la sección de Dispositivos, registrar la IP/MAC de un ESP32 de prueba y verificar que se refleje su estado correctamente.
