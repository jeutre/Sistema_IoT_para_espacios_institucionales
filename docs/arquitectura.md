# Análisis y Arquitectura del Sistema IoT

## 🏗️ Visión General del Proyecto

```
┌─────────────────────────────────────────────────────────────────┐
│                    SISTEMA IoT                                    │
│         Monitoreo de Espacios Institucionales                    │
├──────────────────────┬──────────────────────────────────────────┤
│     FRONTEND (5173)  │         BACKEND (8000)                    │
│   React + Vite       │      Django REST Framework                │
│   Zustand (Estado)   │      SQLite / PostgreSQL                  │
│   Axios (HTTP)       │      JWT Auth + API Keys                  │
└──────────┬───────────┴──────────────────┬───────────────────────┘
           │                              │
           │       HTTP / JSON            │
           └──────────────────────────────┘
                          │
           ┌──────────────┴──────────────┐
           │         HARDWARE            │
           │    ESP32 / Sensores          │
           │    Conexión WiFi             │
           └─────────────────────────────┘
```

---

## 🧩 Estructura del Proyecto

### Backend (Django) — `apps/`

| App | Modelo Principal | Función |
|-----|-----------------|---------|
| `apps.dispositivos` | `Dispositivo` | Representa cada ESP32 físico (IP, MAC, estado, laboratorio al que pertenece) |
| `apps.laboratorio` | `Laboratorio` | Lugares físicos donde se instalan los dispositivos (nombre, capacidad, ubicación) |
| `apps.ocupacion` | `EventoOcupacion` | Registra cuando un espacio está ocupado/vacío basado en sensores |
| `apps.alertas` | `Alerta` | Alertas generadas por desconexión, movimientos fuera de horario, etc. |
| `apps.autenticacion` | `SesionUsuario` | Login, registro, JWT, perfiles de usuario |
| `apps.equipos` | — | Equipos institucionales (proyectores, PCs, etc.) |
| `apps.reportes` | — | Exportación de datos y estadísticas |
| `apps.control` | — | Control remoto de dispositivos |
| `apps.automatizacion` | — | Reglas de automatización |

### Frontend (React) — `frontend/src/pages/`

| Página | Ruta | Función |
|--------|------|---------|
| `Dashboard` | `/dashboard` | Centro de comando principal |
| `Dispositivos` | `/dashboard/dispositivos` | Gestión de ESP32 |
| `Ocupacion` | `/dashboard/ocupacion` | Monitoreo en vivo de espacios |
| `AlertasIoT` | `/dashboard/alertas` | Centro de alertas y notificaciones |
| `Reportes` | `/dashboard/reportes` | Exportación de datos |
| `Auditoria` | `/dashboard/auditoria` | Logs de seguridad |
| `Perfil` | `/dashboard/perfil` | Datos del usuario |

---

## 🔌 Cómo se Conecta un ESP32 al Sistema

### Diagrama de Flujo

```
ESP32 Físico
    │
    ├── 1. Se conecta a WiFi
    │
    ├── 2. Envía POST a:
    │      POST /api/v1/dispositivos/historial/recibir/
    │      Headers: Authorization: Api-Key XXXXXXXXXX
    │      Body: {
    │        "dispositivo_id": 1,
    │        "mensaje": "ocupado" | "vacio" | "temperatura:25"
    │      }
    │
    ├── 3. Backend recibe el mensaje:
    │      ├── Actualiza estado del dispositivo → "conectado"
    │      ├── Crea un HistorialComunicacion
    │      ├── Si el mensaje indica ocupación → crea EventoOcupacion
    │      └── Si hay anomalía → crea Alerta
    │
    └── 4. Frontend (React) consulta periódicamente:
          GET /api/v1/dispositivos/esp32/      ← Lista dispositivos
          GET /api/v1/dispositivos/historial/  ← Historial
          GET /api/v1/ocupacion/eventos/       ← Estado ocupación
          GET /api/v1/alertas/alertas/         ← Alertas activas
```

### Endpoints Clave para Hardware

| Método | Endpoint | Autenticación | Descripción |
|--------|----------|--------------|-------------|
| `POST` | `/api/v1/dispositivos/historial/recibir/` | API Key | El ESP32 envía datos aquí |
| `GET` | `/api/v1/dispositivos/esp32/{id}/ping/` | JWT | Frontend verifica conectividad |
| `GET` | `/api/v1/dispositivos/esp32/` | JWT | Lista todos los dispositivos |
| `POST` | `/api/v1/dispositivos/esp32/` | JWT | Registrar nuevo dispositivo |

---

## 🛠️ Guía de Usuario

### Primeros Pasos

1. **Iniciar sesión** → `http://localhost:5173/login`
   - Usuario: `admin` | Contraseña: `admin`

2. **Registrar un laboratorio** → Menú Admin Django: `http://localhost:8000/admin/`
   - Login con las mismas credenciales
   - Sección "Laboratorios" → Añadir nuevo

3. **Registrar un dispositivo ESP32** → Página "Dispositivos ESP32"
   - Click en botón de nuevo dispositivo
   - Asignar: Identificador único, IP, Laboratorio, MAC Address

4. **Generar API Key** → Admin Django → API Keys
   - Necesaria para que el ESP32 pueda enviar datos

### Flujo de Trabajo Diario

```
Dashboard Principal
    ├── Ver dispositivos activos / totales
    ├── Ver alertas críticas
    ├── Ver eficiencia energética
    └── Ver ocupación actual
         │
         ├── Dispositivos → Estado en tiempo real de cada ESP32
         ├── Ocupación → Espacios ocupados/libres con sensores
         ├── Alertas → Notificaciones de eventos anómalos
         ├── Reportes → Exportar datos históricos
         └── Auditoría → Registro de accesos al sistema
```

---

## 🤖 Integración con Componentes Electrónicos

### ¿Qué necesitas para conectar un ESP32?

```
┌─────────────────────────────────────────────────────┐
│               MATERIAL NECESARIO                     │
├─────────────────────────────────────────────────────┤
│ 1. ESP32 (o ESP8266) con WiFi                       │
│ 2. Sensor de movimiento (PIR) → Detecta ocupación   │
│ 3. Sensor de temperatura/humedad (DHT22) → Clima    │
│ 4. LEDs o relés → Control de iluminación            │
│ 5. Fuente de alimentación 5V                        │
└─────────────────────────────────────────────────────┘
```

### Código de ejemplo para ESP32 (Arduino IDE)

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// Configuración WiFi
const char* ssid = "TU_WIFI";
const char* password = "TU_CONTRASEÑA";

// Configuración API
const char* serverUrl = "http://IP_DEL_SERVIDOR:8000/api/v1/dispositivos/historial/recibir/";
const char* apiKey = "API_KEY_GENERADA_EN_ADMIN";
const int dispositivoId = 1;  // ID en la base de datos

// Sensor PIR
const int pirPin = 4;
bool estadoAnterior = false;

void setup() {
  Serial.begin(115200);
  pinMode(pirPin, INPUT);
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("Conectado a WiFi");
}

void loop() {
  bool ocupado = digitalRead(pirPin) == HIGH;
  
  // Solo enviar cuando cambie el estado
  if (ocupado != estadoAnterior) {
    enviarEstado(ocupado ? "ocupado" : "vacio");
    estadoAnterior = ocupado;
  }
  
  delay(5000); // Revisar cada 5 segundos
}

void enviarEstado(String estado) {
  if (WiFi.status() != WL_CONNECTED) return;
  
  HTTPClient http;
  http.begin(serverUrl);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("Authorization", String("Api-Key ") + apiKey);
  
  StaticJsonDocument<200> doc;
  doc["dispositivo_id"] = dispositivoId;
  doc["mensaje"] = estado;
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  int httpCode = http.POST(jsonString);
  
  if (httpCode > 0) {
    Serial.printf("Respuesta: %d\n", httpCode);
  } else {
    Serial.printf("Error: %s\n", http.errorToString(httpCode).c_str());
  }
  
  http.end();
}
```

### ¿Qué pasa cuando conectas un componente?

1. **ESP32 se conecta a WiFi** → Obtiene IP
2. **ESP32 envía POST** al backend con el mensaje (ej: "ocupado")
3. **Backend recibe y procesa**:
   - Marca el dispositivo como "conectado" en la BD
   - Crea un evento de ocupación si aplica
   - El frontend ve los cambios en tiempo real (polling cada 30s)
4. **Dashboard actualizado** → Puedes ver el cambio desde cualquier navegador

---

## ⚡ Arquitectura de Comunicación

```
           FRONTEND                          BACKEND
      (React - Puerto 5173)            (Django - Puerto 8000)
              │                               │
              │  ──────── JWT Auth ──────────►│
              │  ◄─────── Access Token ───────│
              │                               │
              │  ─── GET /api/v1/esp32/ ─────►│  ← Lista dispositivos
              │  ─── GET /api/v1/eventos/ ───►│  ← Estado ocupación
              │  ─── GET /api/v1/alertas/ ───►│  ← Alertas
              │                               │
              │                               │
         ┌────┴────┐                    ┌─────┴─────┐
         │ Usuario │                    │ BD SQLite │
         └─────────┘                    └─────┬─────┘
                                              │
                                     ┌────────┴────────┐
                                     │   ESP32 Físico   │
                                     │  (WiFi + Sensor) │
                                     │                  │
                                     │ POST /recibir/   │
                                     │ con API Key      │
                                     └─────────────────┘
```

### Seguridad

- **JWT (JSON Web Tokens)** → Para autenticación de usuarios en el frontend
- **API Keys** → Para que los dispositivos físicos (ESP32) envíen datos
- **CORS** → Solo orígenes permitidos pueden consumir la API
- **Refresh Token** → Tokens rotativos para sesiones largas

---

## 📊 Modelo de Datos (BD)

```
Laboratorio
    ├── id, nombre, ubicacion, capacidad
    │
    └── Dispositivo (ESP32)
        ├── id, identificador, mac_address, ip
        ├── estado (conectado/desconectado)
        ├── ultima_conexion
        │
        ├── HistorialComunicacion
        │   ├── mensaje (texto del ESP32)
        │   └── recibido_en
        │
        ├── EventoOcupacion
        │   ├── estado (ocupado/vacio)
        │   └── registrado_en
        │
        └── Alerta (vía GenericForeignKey)
            ├── tipo, nivel, descripcion
            └── creado_en
```

---

## 🚀 Próximos Pasos / Mejoras Sugeridas

1. **WebSockets en vez de polling** → Actualización en tiempo real sin refrescar
2. **MQTT para ESP32** → Protocolo más eficiente que HTTP para IoT
3. **Gráficos históricos reales** → Con datos de la BD en vez de mock
4. **Control bidireccional** → Encender/apagar LEDs desde el dashboard
5. **Notificaciones push** → Alertas en el teléfono
6. **Autenticación biométrica real** → Con cámara y reconocimiento facial
7. **Exportación PDF real** → Con librería como jsPDF o ReportLab