# Arquitectura del sistema

## Visión general

El proyecto se organiza como una aplicación web full-stack que integra hardware IoT con una capa de backend para procesamiento de eventos y una capa de frontend para visualización y administración.

## Componentes

### Backend
El backend está desarrollado en Django y expone una API REST mediante Django REST Framework. Su responsabilidad es:

- gestionar usuarios y autenticación,
- administrar laboratorios, equipos y dispositivos,
- recibir eventos del hardware,
- procesar ocupación y estado de conexión,
- generar alertas y reportes,
- ejecutar reglas de automatización.

### Frontend
El frontend está construido con React + Vite. Consume la API del backend y permite:

- ver un resumen operativo,
- administrar entidades del sistema,
- consultar estados en tiempo real,
- exponer flujos básicos de usuario para el control del sistema.

## Módulos principales

- Autenticación: login, logout, perfil y registro de usuarios.
- Laboratorio: registros de espacios institucionales.
- Dispositivos: gestión de ESP32 y mensajes de comunicación.
- Ocupación: eventos de ocupación obtenidos desde sensores PIR.
- Equipos: estado de conexión y eventos de actividad.
- Dashboard: métricas generales del sistema.
- Alertas: registro de eventos críticos o notables.
- Reportes: exportación de datos a CSV.
- Control: envío de comandos y seguimiento de ejecución.
- Automatización: reglas que generan comandos según condiciones.

## Flujo de datos

1. El dispositivo IoT envía eventos al backend mediante endpoints protegidos.
2. El backend valida la autenticación por API key y guarda los datos.
3. Los módulos de ocupación, conexión y automatización procesan la información.
4. El frontend consulta estos datos a través de la API para mostrarlos al usuario.

## Persistencia

Por defecto se usa SQLite en desarrollo, configurable mediante DATABASE_URL. La capa de modelos de Django centraliza la lógica de negocio y relación entre entidades.

## Seguridad

- autenticación basada en sesiones y JWT,
- protección de endpoints de hardware con API Key,
- configuración de CORS para permitir el acceso del frontend local.
