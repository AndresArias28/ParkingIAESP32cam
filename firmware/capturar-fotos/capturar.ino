#include <WiFi.h>
#include <WebServer.h>
#include "esp_camera.h"

const char* ssid = "";
const char* password = "";

WebServer server(80);
bool cameraReady = false;

void captureImage() {
  // Descartar una captura previa para reducir imágenes atrasadas.
  camera_fb_t* previous = esp_camera_fb_get();
  if (previous) {
    esp_camera_fb_return(previous);
  }

  camera_fb_t* frame = esp_camera_fb_get();

  if (!frame) {
    server.send(503, "text/plain", "Error capturando imagen");
    return;
  }

  server.sendHeader("Cache-Control", "no-store");
  server.setContentLength(frame->len);
  server.send(200, "image/jpeg", "");

  WiFiClient client = server.client();
  size_t sent = 0;
  unsigned long lastProgress = millis();

  while (sent < frame->len && client.connected()) {
    size_t remaining = frame->len - sent;
    size_t chunk = remaining > 1024 ? 1024 : remaining;
    size_t written = client.write(frame->buf + sent, chunk);

    if (written > 0) {
      sent += written;
      lastProgress = millis();
    } else if (millis() - lastProgress > 5000) {
      break;
    }

    delay(1);
  }

  if (sent != frame->len) {
    client.stop();
    Serial.println("Transferencia JPEG incompleta");
  }

  esp_camera_fb_return(frame);
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  // Mantener apagado el LED blanco.
  pinMode(4, OUTPUT);
  digitalWrite(4, LOW);

  if (!psramFound()) {
    Serial.println("No se detecta PSRAM. Revisa placa y configuracion.");
    return;
  }

  camera_config_t config = {};

  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;

  // Pines de la ESP32-CAM AI Thinker.
  config.pin_d0 = 5;
  config.pin_d1 = 18;
  config.pin_d2 = 19;
  config.pin_d3 = 21;
  config.pin_d4 = 36;
  config.pin_d5 = 39;
  config.pin_d6 = 34;
  config.pin_d7 = 35;

  config.pin_xclk = 0;
  config.pin_pclk = 22;
  config.pin_vsync = 25;
  config.pin_href = 23;
  config.pin_sccb_sda = 26;
  config.pin_sccb_scl = 27;
  config.pin_pwdn = 32;
  config.pin_reset = -1;

  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  config.frame_size = FRAMESIZE_VGA;
  config.jpeg_quality = 12;
  config.fb_count = 1;
  config.fb_location = CAMERA_FB_IN_PSRAM;
  config.grab_mode = CAMERA_GRAB_WHEN_EMPTY;

  esp_err_t result = esp_camera_init(&config);

  if (result != ESP_OK) {
    Serial.printf("Error iniciando camara: 0x%x\n", result);
    return;
  }

  cameraReady = true;
  Serial.println("Camara lista: JPEG 640x480, calidad 12");

  WiFi.mode(WIFI_AP_STA);

  WiFi.softAP("ParkingIA-Entrada", "CAMBIAR_CLAVE_LOCAL");

  Serial.print("IP de acceso directo: ");
  Serial.println(WiFi.softAPIP());
  
  WiFi.setAutoReconnect(true);
  WiFi.begin(ssid, password);

  Serial.print("Conectando al WiFi");

  unsigned long start = millis();

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");

    if (millis() - start > 15000) {
      Serial.println("\ncontinua con wifi directo.");
  
      break;
    }
  }

  server.on("/", HTTP_GET, []() {
    server.send(
      200,
      "text/html; charset=utf-8",
      "<h1>Parking IA - entrance-01</h1>"
      "<p>Camara lista: JPEG 640x480</p>"
      "<a href='/capture'>Tomar fotografia</a>"
    );
  });

  server.on("/capture", HTTP_GET, captureImage);
  server.begin();

  Serial.println("\nAbre esta direccion:");
  Serial.print("http://");
  Serial.print(WiFi.localIP());
  Serial.println("/capture");
}

void loop() {
  if (cameraReady && WiFi.status() == WL_CONNECTED) {
    server.handleClient();
  }
  delay(2);
}
