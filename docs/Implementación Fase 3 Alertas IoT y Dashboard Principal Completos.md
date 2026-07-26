# Implementación Fase 3: Alertas IoT y Dashboard Principal Completos

Esta fase transformará los componentes estáticos (mock) de las Alertas y el Dashboard Principal para que consuman información 100% real de la base de datos y respondan en tiempo real.

## User Review Required
> [!IMPORTANT]
> - El modelo `Alerta` en el backend usa una relación genérica (`GenericForeignKey`) para vincularse a Equipos o ESP32s. Crearemos un campo serializado adicional para mandar el nombre del dispositivo al frontend.
> - Se reemplazarán todos los gráficos estáticos del Dashboard Principal por datos en vivo provenientes del backend.

## Open Questions
- ¿Deseas que los nodos de la "Topología de Red" en el Dashboard Principal incluyan también los Equipos PC, o solo los módulos ESP32? (Por defecto incluiré ambos diferenciados por color).

## Proposed Changes

---

### Backend (Django)

#### [MODIFY] `apps/alertas/serializers.py`
- Añadir `SerializerMethodField` para obtener el nombre del dispositivo/equipo relacionado (`objeto_relacionado`).
- Formatear el campo `tipo` y `creado_en` para que coincidan con la estructura que el frontend espera (`mensaje`, `tiempo_relativo`, `dispositivo_nombre`).

#### [MODIFY] `apps/alertas/views.py`
- Añadir endpoints personalizados (o usar viewsets base) para marcar las alertas como `leidas`.

---

### Frontend (React)

#### [MODIFY] `frontend/src/store/iotStore.js`
- Quitar los datos simulados en `fetchAlertas` y conectar directamente al endpoint `/alertas/`.
- Crear una función para procesar la ocupación por laboratorio para el gráfico.
- Crear una función para simular/procesar la actividad histórica de dispositivos en 24h.

#### [MODIFY] `frontend/src/pages/AlertasIoT.jsx`
- Adaptar las propiedades renderizadas (`alerta.descripcion` en lugar de `mensaje`, usar la propiedad del serializer para el nombre del dispositivo).
- Implementar la funcionalidad del botón "Atender" para marcar la alerta como leída usando un nuevo método en `iotStore.js`.

#### [MODIFY] `frontend/src/pages/Dashboard.jsx`
- **Gráfico de Ocupación por Laboratorio**: Renderizar barras dinámicas agrupando el estado actual de los `laboratorios` o historial de `ocupacion`.
- **Topología de Red**: Generar dinámicamente el arreglo `networkNodes` usando la lista de `dispositivos` reales del backend, asignándoles coordenadas (x,y) calculadas o distribuidas.
- **Alertas Recientes**: Mapear directamente las alertas entrantes.

## Verification Plan

### Manual Verification
1. Generar una alerta desconectando un equipo o inyectando un registro de ocupación fuera de horario.
2. Ir a la vista `Alertas IoT` y verificar que la alerta aparece.
3. Dar clic en "Atender" y validar que desaparece de las alertas pendientes.
4. Entrar al `Dashboard` y corroborar que los gráficos y la Topología reflejan los datos exactos del sistema.
