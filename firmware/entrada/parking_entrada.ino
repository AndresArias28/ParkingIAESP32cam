#include <WiFi.h>
#include <WebServer.h>
#include <HTTPClient.h>
#include "esp_camera.h"
#include "secrets.h"

// Clasificación cada 2 segundos. La IA se ejecuta en el servidor Python.
const char *CAMERA_ID = "entrance-01";
const unsigned long CAPTURE_INTERVAL_MS = 2000;
WebServer server(80);
unsigned long nextCaptureAt = 0;
bool cameraReady = false;
bool wifiWasConnected = false;
unsigned long nextReconnectAt = 0;

void captureImage() {
  camera_fb_t *frame = esp_camera_fb_get();
  if (!frame) {
    server.send(503, "text/plain", "Error capturando imagen");
    return;
  }
  server.sendHeader("Cache-Control", "no-store");
  server.setContentLength(frame->len);
  server.send(200, "image/jpeg", "");
  WiFiClient client = server.client();
  size_t sent = 0;
  while (sent < frame->len && client.connected()) {
    size_t chunk = min((size_t)1024, frame->len - sent);
    size_t written = client.write(frame->buf + sent, chunk);
    if (written == 0) break;
    sent += written;
    delay(1);
  }
  esp_camera_fb_return(frame);
}

void sendForPrediction() {
  camera_fb_t *frame = esp_camera_fb_get();
  if (!frame) {
    Serial.println("No se pudo capturar JPEG");
    return;
  }

  WiFiClient client;
  HTTPClient http;
  String url = String("http://") + BACKEND_IP + ":" + BACKEND_PORT +
               "/api/v1/predict?camera=" + CAMERA_ID;
  http.setTimeout(5000);
  if (http.begin(client, url)) {
    http.addHeader("Content-Type", "image/jpeg");
    http.addHeader("X-Camera-Token", CAMERA_TOKEN);
    int status = http.POST(frame->buf, frame->len);
    if (status == 200) {
      Serial.println(http.getString());
    } else {
      Serial.printf("Servidor: HTTP %d\n", status);
    }
    http.end();
  } else {
    Serial.println("No se pudo iniciar HTTP");
  }
  esp_camera_fb_return(frame);
}

void setup() {
  Serial.begin(115200);
  pinMode(4, OUTPUT);
  digitalWrite(4, LOW);

  if (!psramFound()) {
    Serial.println("No se detecto PSRAM");
    return;
  }

  camera_config_t config = {};
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
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

  if (esp_camera_init(&config) != ESP_OK) {
    Serial.println("Fallo al iniciar la camara");
    return;
  }
  cameraReady = true;
  if (ROUTER_SSID[0] == '\0') {
    Serial.println("Configurar ROUTER_SSID en secrets.h");
    cameraReady = false;
    return;
  }
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.begin(ROUTER_SSID, ROUTER_PASSWORD);
  unsigned long started = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - started < 15000) {
    delay(250);
  }
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Sin conexion al router; se reintentara");
  }
  server.on("/", HTTP_GET, []() {
    server.send(200, "text/plain", "Parking IA entrance-01; foto en /capture");
  });
  server.on("/capture", HTTP_GET, captureImage);
  server.begin();
  nextReconnectAt = millis() + 10000;
  nextCaptureAt = millis() + CAPTURE_INTERVAL_MS;
}

void loop() {
  if (!cameraReady) {
    delay(1000);
    return;
  }
  unsigned long now = millis();
  bool wifiConnected = WiFi.status() == WL_CONNECTED;
  if (wifiConnected != wifiWasConnected) {
    wifiWasConnected = wifiConnected;
    if (wifiConnected) {
      Serial.print("Camara en http://");
      Serial.print(WiFi.localIP());
      Serial.println("/capture");
    } else {
      Serial.println("Conexion al router perdida");
    }
  }
  if (!wifiConnected && (long)(now - nextReconnectAt) >= 0) {
    WiFi.reconnect();
    nextReconnectAt = now + 10000;
  }
  if (wifiConnected) server.handleClient();
  if ((long)(now - nextCaptureAt) >= 0) {
    nextCaptureAt = now + CAPTURE_INTERVAL_MS;
    if (wifiConnected) sendForPrediction();
  }
  delay(2);
}
