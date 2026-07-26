# Plan de Implementación: Fase 2

El objetivo de esta fase es cubrir el **Monitoreo de Ocupación** (historial y métricas avanzadas) y el **Monitoreo de Equipos vía IPv4**, correspondientes a las Épicas 4 y 5 del Product Backlog.

## User Review Required

> [!IMPORTANT]
> Para lograr el monitoreo de los equipos, el sistema requiere ejecutar Pings constantes en segundo plano. Según la documentación de tu proyecto, se está utilizando `apscheduler` para las tareas en segundo plano de Django. Implementaremos un *job* que se ejecute cada minuto para hacer ping a todos los equipos registrados.
> 
> Por favor, revisa las funcionalidades listadas abajo y confírmame tu aprobación (Proceed) para iniciar el desarrollo.

## Open Questions

- ¿La página de **Equipos** debe ser una vista independiente en el menú lateral o prefieres que los equipos se administren dentro del detalle de cada Laboratorio? (Propondré una vista independiente `/dashboard/equipos` para mayor facilidad).

## Proposed Changes

### 1. Monitoreo de Ocupación (HU-11, HU-12)
- **Backend:** Añadir métricas en `apps.ocupacion.views` para retornar "horas pico" y estadísticas agregadas.
- **Frontend (`Ocupacion.jsx`):** 
  - Extender la vista para que no solo muestre el tiempo real, sino que incluya una pestaña de **Historial**.
  - Agregar un gráfico simple de barras (usando `chart.js` o similar si está instalado, o barras con CSS) para mostrar las "Horas Pico".

### 2. Gestión y Control de Equipos IPv4 (HU-13 a HU-18)
- **Backend:**
  - **CRUD de Equipos:** Activar y verificar los serializadores y ViewSets para el modelo `Equipo`.
  - **Background Task:** Configurar una tarea de `apscheduler` que haga ping a las IPs registradas y actualice los campos `estado_conexion` y genere un `EventoConexion` cuando el estado cambie.
- **Frontend:**
  - **Nueva Vista `Equipos.jsx`:** Crear la interfaz gráfica (CRUD) para registrar direcciones IP y MAC asociadas a un laboratorio.
  - **Visualización de Estados:** Añadir dos listas/filtros en la vista: "Equipos Activos" (HU-15) y "Equipos Inactivos" (HU-16).
  - **Historial:** Ver el historial de conexiones/desconexiones de cada equipo.

## Verification Plan

### Automated Tests
- Ejecutar el servidor de Django y validar que los logs de `apscheduler` se levanten correctamente y ejecuten los Pings sin crashear.

### Manual Verification
1. Ingresar al sistema y crear un Equipo con la IP local (`127.0.0.1` o `localhost`) para verificar que el Ping automático lo detecte como "Activo".
2. Revisar la pestaña de Ocupación para confirmar que el historial y gráficos renderizan.
3. Crear un equipo con una IP falsa (`192.168.254.254`) y comprobar que el sistema lo marque como "Inactivo" e indique sus minutos inactivo.
