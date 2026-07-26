# Guía de Configuración: ESP32 a Django API

Esta guía contiene los pasos y el código necesario (en C++ / Arduino IDE) para que tu microcontrolador ESP32 lea un sensor de movimiento (PIR) y reporte de forma segura el estado de ocupación hacia tu sistema web.

## 1. Obtener la Llave de Seguridad (API Key)

Dado que la API está protegida, el ESP32 necesita una llave para que el servidor lo autorice a enviar datos.
1. Abre tu navegador y dirígete al panel de administración: `http://localhost:8000/admin/` (o la IP de tu PC en la red local, ej. `http://192.168.1.x:8000/admin/`).
2. Inicia sesión. Si no tienes un súper usuario, puedes crear uno desde la terminal de tu proyecto ejecutando: `python manage.py createsuperuser`.
3. Busca la sección **API Keys** y haz clic en "Add".
4. Ponle un nombre (ej. "Llave ESP32") y guárdala.
5. **IMPORTANTE:** Copia la clave generada que te mostrará la pantalla (una vez cerrada, no podrás volver a verla entera).

## 2. Preparar el entorno de Arduino IDE

Asegúrate de tener instalada la placa ESP32 en tu Arduino IDE y también instalar la librería **ArduinoJson** (puedes buscarla en el gestor de librerías de Arduino).

## 3. Código Fuente para el ESP32

Copia y pega el siguiente código. Deberás modificar las credenciales WiFi y colocar la API Key que generaste.

```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ==========================================
// 🔧 CONFIGURACIÓN DEL USUARIO
// ==========================================
const char* ssid = "TU_RED_WIFI";
const char* password = "TU_PASSWORD_WIFI";

// Reemplaza por la IP de la computadora donde corre el backend Django
const char* serverUrl = "http://192.168.1.X:8000/api/v1/ocupacion/pir/"; 
const char* apiKey = "TU_API_KEY_GENERADA_EN_DJANGO"; 

// El ID del dispositivo registrado en tu base de datos (Django)
const int DISPOSITIVO_ID = 1; 

// Pin donde está conectado el sensor PIR
const int PIR_PIN = 14; 

// ==========================================
// VARIABLES DE ESTADO
// ==========================================
int pirState = LOW;             
int lastPirState = LOW;         

void setup() {
  Serial.begin(115200);
  pinMode(PIR_PIN, INPUT);

  // 1. Conectar al WiFi
  Serial.println("Conectando a la red WiFi...");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("¡WiFi Conectado!");
  Serial.print("Dirección IP asignada (Registra esta IP en el sistema web): ");
  Serial.println(WiFi.localIP());
}

void loop() {
  // 2. Leer estado del PIR
  pirState = digitalRead(PIR_PIN);

  // 3. Detectar CAMBIOS de estado (para no saturar el servidor)
  if (pirState != lastPirState) {
    if (pirState == HIGH) {
      Serial.println("¡Movimiento detectado! Enviando estado: ocupado...");
      enviarEstadoOcupacion("ocupado");
    } else {
      Serial.println("Sin movimiento. Enviando estado: vacio...");
      enviarEstadoOcupacion("vacio");
    }
    lastPirState = pirState;
  }
  
  // Pequeña pausa para estabilizar
  delay(1000);
}

// ==========================================
// 📡 FUNCIÓN PARA ENVIAR DATOS A DJANGO
// ==========================================
void enviarEstadoOcupacion(String estado) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    
    // Configurar Cabeceras (Headers)
    http.addHeader("Content-Type", "application/json");
    
    // Autorización con API Key (El formato es 'Api-Key LLAVE')
    String authHeader = "Api-Key " + String(apiKey);
    http.addHeader("Authorization", authHeader);

    // Crear el JSON
    StaticJsonDocument<200> jsonDoc;
    jsonDoc["dispositivo_id"] = DISPOSITIVO_ID;
    jsonDoc["estado"] = estado;
    
    String requestBody;
    serializeJson(jsonDoc, requestBody);

    // Realizar la petición POST
    int httpResponseCode = http.POST(requestBody);

    if (httpResponseCode > 0) {
      Serial.print("Código de Respuesta HTTP: ");
      Serial.println(httpResponseCode);
      String response = http.getString();
      Serial.println(response);
    } else {
      Serial.print("Error en la petición POST: ");
      Serial.println(httpResponseCode);
    }
    
    http.end();
  } else {
    Serial.println("Error: WiFi desconectado.");
  }
}
```

## 4. Pruebas y Validación

1. Sube el código al ESP32.
2. Abre el **Monitor Serie** (Serial Monitor) a 115200 baudios.
3. Al conectar al WiFi, te imprimirá la **IP local** del ESP32.
4. **Paso crucial:** Ve a tu sistema web (en tu PC), dirígete a `Dashboard -> Equipos IPv4` y registra un **Nuevo Equipo**. En la "Dirección IPv4", coloca la IP que te dio el Monitor Serie. Esto permitirá que el Ping Automático lo detecte como "Activo".
5. Pasa tu mano frente al sensor PIR. El Monitor Serie debería decir "Código de Respuesta HTTP: 201" (Creado con éxito).
6. Ve a tu sistema web -> `Ocupación`. Deberías ver en "Tiempo Real" que el laboratorio acaba de cambiar a "OCUPADO".
