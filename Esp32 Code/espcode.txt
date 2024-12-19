#include <Wire.h>
#include "MAX30105.h"
#include <WiFi.h>

MAX30105 particleSensor;

// Wi-Fi credentials
const char* ssid = "";  // Fill in your SSID
const char* password = "";  // Fill in your password

// Wi-Fi Server setup
WiFiServer server(80);

// Heart rate calculation parameters
const byte RATE_SIZE = 4; // Increase this for more averaging; 4 is good.
byte rates[RATE_SIZE];     // Array to store heart rates
byte rateSpot = 0;         // Current index for heart rates
long lastBeat = 0;         // Time at which the last beat occurred
float beatsPerMinute;      // Current beats per minute
int beatAvg;               // Average beats per minute

void setup() {
    Serial.begin(115200);
    Serial.println("Initializing...");

    // Initialize the MAX30105 sensor
    if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) {
        Serial.println("MAX30105 was not found. Please check wiring/power.");
        while (1);
    }
    Serial.println("Place your finger on the sensor with steady pressure.");

    // Configure the MAX30105 sensor
    particleSensor.setup();  // Configure sensor with default settings
    particleSensor.setPulseAmplitudeRed(0x0A);  // Set Red LED brightness
    particleSensor.setPulseAmplitudeGreen(0);    // Turn off Green LED

    // Set up Wi-Fi connection
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nConnected to WiFi");
    Serial.println(WiFi.localIP());

    // Start the server
    server.begin();
}

void loop() {
    // Wait for a client to connect
    WiFiClient client = server.available();

    if (client) {
        Serial.println("Client connected.");
        
        while (client.connected()) {
            long irValue = particleSensor.getIR();  // Get the IR value

            // Check for a detected beat
            if (checkForBeat(irValue)) {
                // We sensed a beat!
                long delta = millis() - lastBeat;  // Calculate the time since the last beat
                lastBeat = millis();                // Update the last beat time

                beatsPerMinute = 60 / (delta / 1000.0);  // Calculate BPM

                // Only store the BPM if it's within a reasonable range
                if (beatsPerMinute < 255 && beatsPerMinute > 20) {
                    rates[rateSpot++] = (byte)beatsPerMinute;  // Store this reading in the array
                    rateSpot %= RATE_SIZE;                     // Wrap variable

                    // Calculate the average of the readings
                    beatAvg = 0;
                    for (byte x = 0; x < RATE_SIZE; x++)
                        beatAvg += rates[x];
                    beatAvg /= RATE_SIZE;
                }
            }

            // Send data to the client (IR value, BPM, and Avg BPM)
            String data = String(irValue) + "," + String(beatsPerMinute) + "," + String(beatAvg);
            client.println(data);

            // Log the data to the serial monitor
            Serial.print("IR=");
            Serial.print(irValue);
            Serial.print(", BPM=");
            Serial.print(beatsPerMinute);
            Serial.print(", Avg BPM=");
            Serial.print(beatAvg);

            if (irValue < 50000)
                Serial.print(" No finger?");

            Serial.println();

            delay(100);  // Delay to avoid flooding the serial output
        }

        // Close the connection when the client disconnects
        Serial.println("Client disconnected.");
        client.stop();
    }
}

// Function to check for a beat
bool checkForBeat(long irValue) {
    static long lastIRValue = 0;  // To hold the last IR value
    bool beatDetected = false;

    if (irValue > 50000 && lastIRValue <= 50000) {
        beatDetected = true;  // A beat is detected if IR value crosses the threshold
    }

    lastIRValue = irValue;  // Update the last IR value
    return beatDetected;
}