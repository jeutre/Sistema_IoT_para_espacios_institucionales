# 🚀 GUÍA: Poner el Dashboard en Tiempo Real (ESP32 Simulado)

## El Problema Que Tenías

Tu dashboard mostraba:
- 0% ocupación
- 0 dispositivos conectados  
- Alertas diciendo "ESP32 se desconectó hace 3 min"

**Causa raíz:** La base de datos estaba vacía. No había laboratorios, ESP32 registrados, ni datos de ocupación. El ESP32 real no estaba reportando datos al backend.

---

## La Solución: 3 Pasos

### Paso 1️⃣: Crear Datos Iniciales (YA HECHO ✓)

```powershell
python setup_datos_iniciales.py
```

**Resultado:**
- ✓ 3 Laboratorios creados
- ✓ 3 ESP32 registrados (ESP32-LAB-01, ESP32-LAB-02, ESP32-LAB-03)
- ✓ 4 Equipos IPv4 creados
- ✓ API Key generada: `QPbDter3.qK0iLwBYH1eYG1RZDKmz82CWKD0kLJvk`

---

### Paso 2️⃣: Configurar Autenticación de API Key en Django (YA HECHO ✓)

Se agregó `ApiKeyAuthentication` a `config/settings.py`:

```python
'DEFAULT_AUTHENTICATION_CLASSES': (
    'rest_framework_api_key.authentication.ApiKeyAuthentication',  # ← NUEVO
    'rest_framework_simplejwt.authentication.JWTAuthentication',
    ...
)
```

**Por qué?** Porque el ESP32 se autentica con API Key, no con JWT. El endpoint `/api/v1/ocupacion/pir/` necesita este header:

```
Authorization: Api-Key QPbDter3.qK0iLwBYH1eYG1RZDKmz82CWKD0kLJvk
```

---

### Paso 3️⃣: Ejecutar el Simulador ESP32 (EN PROGRESO)

**En una terminal abierta:**

```powershell
python esp32_simulador.py \
    --base-url http://localhost:8000 \
    --dispositivo-id 1 \
    --api-key QPbDter3.qK0iLwBYH1eYG1RZDKmz82CWKD0kLJvk \
    --interval 10 \
    --modo realistic
```

**Esto hace:**
- Cada 10 segundos, envía un evento de ocupación al backend
- Alterna entre "ocupado" (70%) y "vacío" (30%) de forma realista
- Simula un ESP32 real enviando datos del sensor PIR

---

## ¿Qué Verás en el Dashboard?

**Mientras el simulador está corriendo:**

✅ **En tiempo real (se actualiza cada 10 segundos):**
- Dispositivos activos: 1/3 (ESP32-LAB-01 conectado)
- Ocupación: cambio entre 0% → 100% según el simulador
- Horas pico: gráfico de actividad por hora
- Alertas: desaparecen (porque el dispositivo ahora comunica)
- KPIs: disponibilidad, eficiencia, inactividad

✅ **En la vista Ocupación:**
- Listado de eventos en tiempo real
- Historial por dispositivo
- Filtros por fecha

---

## Si el Simulador da Error

### Error: "No se pudo conectar a http://localhost:8000"

→ **Solución:** Verifica que Django esté corriendo:

```powershell
# En otra terminal (en la raíz del proyecto)
python manage.py runserver
```

Django debe estar en `http://localhost:8000`

### Error: "Error 401: Las credenciales de autenticación no se proveyeron"

→ **Solución:** Comprueba que:

1. La API Key sea correcta (la que salió en el setup)
2. Django se haya recargado después de cambiar `settings.py`
3. Si no, detén (`Ctrl+C`) y relanza: `python manage.py runserver`

---

## Para Probar tu ESP32 Real (Después)

Cuando tengas el ESP32 físico conectado, reemplaza en el firmware:

```cpp
// En el código C++ del ESP32:
const char* API_URL = "http://192.168.1.X:8000/api/v1/ocupacion/pir/";
const char* API_KEY = "QPbDter3.qK0iLwBYH1eYG1RZDKmz82CWKD0kLJvk";
const int DISPOSITIVO_ID = 1;  // O el ID que uses

// En cada lectura del PIR:
HTTPClient http;
http.addHeader("Authorization", "Api-Key " + String(API_KEY));
http.addHeader("Content-Type", "application/json");

String payload = "{\"dispositivo_id\": " + String(DISPOSITIVO_ID) + ", \"estado\": \"ocupado\"}";
int httpCode = http.POST(payload);
```

---

## Dashboard URLs

| Página | URL |
|--------|-----|
| **Dashboard** | http://localhost:5173/dashboard |
| **Ocupación** | http://localhost:5173/dashboard/ocupacion |
| **Alertas** | http://localhost:5173/dashboard/alertas |
| **Laboratorios** | http://localhost:5173/dashboard/laboratorios |
| **Reportes** | http://localhost:5173/dashboard/reportes |
| **Admin Django** | http://localhost:8000/admin/ |
| **API Swagger** | http://localhost:8000/api/schema/swagger-ui/ |

---

## Checklist para Pruebas Reales

- [ ] Backend Django corriendo en http://localhost:8000
- [ ] Frontend Vite corriendo en http://localhost:5173
- [ ] Simulador ESP32 corriendo (reportando cada 10s)
- [ ] Dashboard mostrando cambios en tiempo real
- [ ] Alertas desaparecen cuando el dispositivo comunica
- [ ] KPIs se actualizan con ocupación real
- [ ] Historial de ocupación registra todos los eventos

Una vez que todo esto funcione, tu sistema está listo para pruebas reales con el ESP32 físico.

---

## Archivos Clave Creados

```
proyecto/
├── setup_datos_iniciales.py       # ← Ejecuta primero para crear datos
├── esp32_simulador.py              # ← Emula el ESP32 real
├── consultar_credenciales.py       # ← Script para consultar BD (opcional)
└── docs/
    └── Guía-Pruebas-Reales.md      # ← Este archivo
```

---

## Próximos Pasos (Después de Pruebas)

1. **Firmware C++ del ESP32:** Configura el código del ESP32 para reportar datos reales
2. **Tests de Aceptación:** Ejecuta `python manage.py test` para verificar todo
3. **Integración Flutter:** Conecta la app Flutter si la tienes
4. **Monitoreo en Producción:** Configura logs y alertas en tiempo real

¡El sistema está listo para ir a pruebas reales! 🚀
