#include <WiFi.h>
#include <WebSocketsClient.h>
#include "driver/i2s.h"
#include <ESP32Servo.h>

// === Pines y Objetos ===
Servo servo1, servo2, servo3, servo4, servo5, servo6;

// === Configuración de Red y Servidor ===
char ssid[50] = "..::AMJ Technology::...4GHZ";
char password[50] = "@13032025@";
const char* host = "kinema-a9rs.onrender.com"; // URL de Kinema limpia
const int port = 443;

WebSocketsClient webSocket;

// === Pines del Micrófono I2S ===
#define I2S_SCK 27
#define I2S_WS 33
#define I2S_SD 32

// === Variables de Audio ===
uint8_t bufferEnvio[1024];
int indiceBuffer = 0;
uint32_t umbralVoz = 600000000; // Sensibilidad del micrófono

// =================================================================
// RUTINAS DE SERVOS
// =================================================================
void o() { servo6.write(180); delay(1000); servo5.write(90); servo4.write(90); servo3.write(70); servo2.write(90); servo1.write(90); }
void x() { servo6.write(180); delay(1000); servo5.write(60); servo4.write(180); servo3.write(0); servo2.write(30); servo1.write(130); }
void g() { servo6.write(180); delay(1000); servo5.write(60); servo4.write(180); servo3.write(0); servo2.write(20); servo1.write(70); }
void c() { servo6.write(180); delay(1000); servo5.write(100); servo4.write(90); servo3.write(60); servo2.write(40); servo1.write(100); }
void d() { servo6.write(180); delay(1000); servo5.write(90); servo4.write(90); servo3.write(80); servo2.write(0); servo1.write(40); }
void termine() { servo6.write(180); delay(1000); servo5.write(60); servo4.write(180); servo3.write(0); servo2.write(0); servo1.write(130); }
void teamo() { servo6.write(180); delay(1000); servo5.write(90); servo4.write(90); servo3.write(110); servo2.write(60); servo1.write(90); }
void cerradacompleta() { servo6.write(0); delay(1000); servo5.write(60); servo4.write(180); servo3.write(0); servo2.write(180); servo1.write(130); }
void hola() { servo6.write(0); delay(1000); servo1.write(0); servo2.write(0); servo3.write(180); servo4.write(180); servo5.write(60); }
void paz() { servo6.write(0); delay(1000); servo1.write(130); servo2.write(0); servo3.write(180); servo4.write(180); servo5.write(60); }
void rock() { servo6.write(0); delay(1000); servo1.write(0); servo2.write(0); servo3.write(0); servo4.write(180); servo5.write(180); }
void cerrada() { servo6.write(0); delay(1000); servo5.write(60); servo4.write(180); servo3.write(0); servo2.write(180); servo1.write(130); }
void abierta() { servo6.write(0); delay(1000); servo1.write(0); servo2.write(0); servo3.write(180); servo4.write(0); servo5.write(180); }
void esp322() { servo6.write(0); delay(1000); servo5.write(60); servo4.write(180); servo3.write(180); servo2.write(180); servo1.write(130); }
void adios() { servo6.write(0); delay(1000); for (int i = 0; i < 3; i++) { servo1.write(0); servo2.write(0); servo3.write(180); servo4.write(0); servo5.write(180); delay(1000); servo5.write(60); servo4.write(180); servo3.write(0); servo2.write(180); servo1.write(130); delay(1000); } }
void uno() { servo6.write(0); delay(1000); servo5.write(60); servo4.write(180); servo3.write(0); servo2.write(0); servo1.write(130); }
void dos() { servo6.write(0); delay(1000); servo5.write(60); servo4.write(180); servo3.write(180); servo2.write(0); servo1.write(130); }
void tres() { servo6.write(0); delay(1000); servo1.write(0); servo2.write(0); servo3.write(180); servo4.write(180); servo5.write(55); }
void cuatro() { servo6.write(0); delay(1000); servo1.write(180); servo2.write(0); servo3.write(180); servo4.write(0); servo5.write(180); }
void cinco() { servo6.write(0); delay(1000); servo1.write(0); servo2.write(0); servo3.write(180); servo4.write(0); servo5.write(160); }
void seis() { servo6.write(0); delay(1000); servo1.write(180); servo2.write(0); servo3.write(180); servo4.write(0); servo5.write(55); }
void siete() { servo6.write(0); delay(1000); servo1.write(180); servo2.write(0); servo3.write(180); servo4.write(180); servo5.write(180); }
void ocho() { servo6.write(0); delay(1000); servo1.write(180); servo2.write(0); servo3.write(0); servo4.write(0); servo5.write(180); }
void nueve() { servo6.write(0); delay(1000); servo2.write(180); delay(100); servo1.write(180); servo3.write(180); servo4.write(0); servo5.write(180); }
void diez() { servo6.write(0); delay(1000); servo5.write(60); servo4.write(180); servo3.write(0); servo2.write(180); servo1.write(70); }
void upt() { servo6.write(0); delay(1000); servo5.write(60); servo4.write(180); servo3.write(180); servo2.write(0); servo1.write(130); delay(1000); servo5.write(60); servo4.write(180); servo3.write(180); servo2.write(40); servo1.write(130); delay(1000); servo4.write(180); servo5.write(60); servo3.write(0); delay(300); servo1.write(180); delay(300); servo2.write(180); }

// =================================================================
// PROCESAR PALABRAS DE VOSK
// =================================================================
void ejecutarComando(String cmd) {
  if (cmd.indexOf("hola") != -1) hola();
  else if (cmd.indexOf("paz") != -1) paz();
  else if (cmd.indexOf("rock") != -1) rock();
  else if (cmd.indexOf("cerrada") != -1) cerrada();
  else if (cmd.indexOf("abierta") != -1) abierta();
  else if (cmd.indexOf("uno") != -1) uno();
  else if (cmd.indexOf("dos") != -1) dos();
  else if (cmd.indexOf("tres") != -1) tres();
  else if (cmd.indexOf("cuatro") != -1) cuatro();
  else if (cmd.indexOf("cinco") != -1) cinco();
  else if (cmd.indexOf("seis") != -1) seis();
  else if (cmd.indexOf("siete") != -1) siete();
  else if (cmd.indexOf("ocho") != -1) ocho();
  else if (cmd.indexOf("nueve") != -1) nueve();
  else if (cmd.indexOf("diez") != -1) diez();
  else if (cmd.indexOf("adiós") != -1 || cmd.indexOf("adios") != -1) adios();
  else if (cmd.indexOf("upt") != -1) upt();
  else if (cmd.indexOf("esp32") != -1) esp322();
  else if (cmd.indexOf("terminé") != -1 || cmd.indexOf("termine") != -1) termine();
  else if (cmd.indexOf("te amo") != -1 || cmd.indexOf("teamo") != -1) teamo();
  else if (cmd.indexOf("letra o") != -1) o();
  else if (cmd.indexOf("letra x") != -1) x();
  else if (cmd.indexOf("letra g") != -1) g();
  else if (cmd.indexOf("letra c") != -1) c();
  else if (cmd.indexOf("letra d") != -1) d();
}

// =================================================================
// EVENTOS DEL WEBSOCKET (Recibir texto de Render)
// =================================================================
void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
  if (type == WStype_CONNECTED) {
    Serial.println(">> Conectado al servidor Kinema!");
  } else if (type == WStype_TEXT) {
    String mensaje = (char*)payload;
    if (mensaje.startsWith("TEXTO:")) {
      String comando = mensaje.substring(6); 
      Serial.println("🗣️ Vosk tradujo: " + comando);
      ejecutarComando(comando);
    }
  }
}

// =================================================================
// CONFIGURACIÓN INICIAL
// =================================================================
void setup() {
  Serial.begin(115200);

  // Inicializar Servos
  ESP32PWM::allocateTimer(0);
  ESP32PWM::allocateTimer(1);
  ESP32PWM::allocateTimer(2);
  ESP32PWM::allocateTimer(3);
  servo1.attach(5);
  servo2.attach(18);
  servo3.attach(19);
  servo4.attach(21);
  servo5.attach(22);
  servo6.attach(23);

  // Conectar a Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Conectando a WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi Conectado.");

  // Configurar Micrófono I2S
  i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
    .sample_rate = 16000,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT,
    .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
    .communication_format = I2S_COMM_FORMAT_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 8,
    .dma_buf_len = 512,
    .use_apll = false
  };
  i2s_pin_config_t pin_config = {
    .bck_io_num = I2S_SCK,
    .ws_io_num = I2S_WS,
    .data_out_num = I2S_PIN_NO_CHANGE,
    .data_in_num = I2S_SD
  };
  i2s_driver_install(I2S_NUM_0, &i2s_config, 0, NULL);
  i2s_set_pin(I2S_NUM_0, &pin_config);

  // Conectar al Servidor Render
  webSocket.beginSSL(host, port, "/ws");
  webSocket.onEvent(webSocketEvent);
  webSocket.setReconnectInterval(5000);
}

// =================================================================
// BUCLE PRINCIPAL (Leer micro y enviar audio)
// =================================================================
void loop() {
  webSocket.loop();

  // Leer audio del micrófono I2S
  int32_t samples[256];
  size_t bytes_read;
  i2s_read(I2S_NUM_0, samples, sizeof(samples), &bytes_read, portMAX_DELAY);

  if (bytes_read > 0) {
    int num_samples = bytes_read / sizeof(int32_t);
    int32_t max_val = INT32_MIN;
    int32_t min_val = INT32_MAX;

    int16_t samples16[256];
    
    // Procesar las muestras
    for (int i = 0; i < num_samples; i++) {
      int64_t sample = (int64_t)samples[i] * 4;
      int32_t sample_constrain = (int32_t)constrain(sample, INT32_MIN, INT32_MAX);
      if (sample_constrain > max_val) max_val = sample_constrain;
      if (sample_constrain < min_val) min_val = sample_constrain;
      samples16[i] = sample_constrain >> 16;
    }

    uint32_t amplitud = (uint32_t)max_val - (uint32_t)min_val;

    // Solo enviamos audio a Render si estás hablando (supera el umbral de ruido)
    if (amplitud > umbralVoz) {
      for (int i = 0; i < num_samples; i++) {
        if (indiceBuffer < 1024) {
          bufferEnvio[indiceBuffer++] = samples16[i] & 0xFF;
          bufferEnvio[indiceBuffer++] = (samples16[i] >> 8) & 0xFF;
        }
        if (indiceBuffer >= 1024) { 
          webSocket.sendBIN(bufferEnvio, 1024);
          indiceBuffer = 0;
        }
      }
    }
  }
}
