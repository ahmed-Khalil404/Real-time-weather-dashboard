#ifndef SENSOR_ADDRESS
#endif
#include <Adafruit_BME280.h>
#include <Wire.h>
#include <SPI.h>

Adafruit_BME280 sensor;
int temp;
int press;
int alt;
int hum;

#define SEA_LEVEL_PRESSURE (1013.25)
#define SWITCH_CTRL_DEFAULT true
volatile int switch_ctrl = SWITCH_CTRL_DEFAULT;

bool satellite_connected = false;
unsigned long last_send_time = 0;
bool value_confirmed = false;

void send_data() {
    read_sensor_data();
    char command[50];
    sprintf(command, "AT+SEND=1,0,8,1,%d,%d,%d,%d\r\n", temp, press, alt, hum);
    SATELLITE_SERIAL.print(command);
    Serial.println("Données envoyées au satellite.");
}

void read_sensor_data() {
    temp = sensor.readTemperature();
    press = sensor.readPressure() / 100.0F;
    alt = sensor.readAltitude(SEA_LEVEL_PRESSURE);
    hum = sensor.readHumidity();
    delay(50);
}

void setup() {
    Wire.setSDA(SENSOR_SDA_PIN);
    Wire.setSCL(SENSOR_SCL_PIN);
    Wire.begin();
    
    unsigned status = sensor.begin(SENSOR_ADDRESS, &Wire);
    if (!status) {
        USB_SERIAL.println("Échec critique : capteur introuvable");
        USB_SERIAL.println("Vérifiez le câblage, l'adresse et l'identifiant du capteur.");
        USB_SERIAL.print("Identifiant du capteur : 0x");
        USB_SERIAL.println(sensor.sensorID(), 16);
        USB_SERIAL.println("0xFF : Adresse incorrecte ou capteur BMP180/BMP085");
        USB_SERIAL.println("0x56-0x58 : BMP280, 0x60 : BME280, 0x61 : BME680");
        while (1) delay(10);
    }
    USB_SERIAL.println("Capteur initialisé avec succès");

    switch_ctrl = SWITCH_CTRL_DEFAULT;
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, HIGH);

    #if defined(POWER_ENABLE_PIN)
        pinMode(POWER_ENABLE_PIN, OUTPUT);
        digitalWrite(POWER_ENABLE_PIN, HIGH);
    #endif
    
    pinMode(CONTROL_PIN, OUTPUT);
    digitalWrite(CONTROL_PIN, HIGH);

    pinMode(SWITCH_PIN, INPUT);
    attachInterrupt(digitalPinToInterrupt(SWITCH_PIN), switch_ctrl_isr, CHANGE);

    Serial.begin(115200);
    while (!Serial);

    Serial.println("Initialisation en cours...");
    update_switch_ctrl();
    Serial.print("Contrôle du commutateur: ");
    Serial.println(switch_ctrl ? "ACTIVÉ" : "DÉSACTIVÉ");

    SATELLITE_SERIAL.begin(115200);
    delay(1000);
    digitalWrite(LED_BUILTIN, LOW);
    SATELLITE_SERIAL.println("AT+JOIN");
    Serial.println("Connexion au satellite...");
}

void loop() {
    if (SATELLITE_SERIAL.available()) {
        String response = SATELLITE_SERIAL.readStringUntil('\n');
        Serial.print("Réponse du satellite: ");
        Serial.println(response);

        if (!satellite_connected && response.indexOf("Successfully joined network") != -1) {
            satellite_connected = true;
            Serial.println("Connexion au satellite réussie");
        }

        if (response.indexOf("QUEUED:1") != -1) {
            Serial.println("Données confirmées par le satellite.");
            value_confirmed = true;
        }
    }

    if (satellite_connected) {
        unsigned long current_time = millis();
        
        if (value_confirmed && current_time - last_send_time >= 120000) {
            value_confirmed = false;
            send_data();
            last_send_time = current_time;
        } else if (!value_confirmed && current_time - last_send_time >= 20000) {
            send_data();
            last_send_time = current_time;
        }
    }

    if (Serial.available()) {
        char c = Serial.read();
        SATELLITE_SERIAL.write(c);
        if (c == '*') {
            switch_ctrl ^= true;
            update_switch_ctrl();
            Serial.print("Contrôle du commutateur: ");
            Serial.println(switch_ctrl ? "ACTIVÉ" : "DÉSACTIVÉ");
        }
    }
}

void switch_ctrl_isr() {
    update_switch_ctrl();
}

void update_switch_ctrl() {
    if (digitalRead(SWITCH_PIN) == LOW) {
        digitalWrite(CONTROL_PIN, switch_ctrl ? HIGH : LOW);
        digitalWrite(LED_BUILTIN, switch_ctrl ? HIGH : LOW);
    } else {
        digitalWrite(CONTROL_PIN, switch_ctrl ? LOW : HIGH);
        digitalWrite(LED_BUILTIN, switch_ctrl ? LOW : HIGH);
    }
}
