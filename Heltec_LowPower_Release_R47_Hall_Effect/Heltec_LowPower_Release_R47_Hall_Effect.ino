#include "Arduino.h"
#include "innerWdt.h"
#include <Wire.h>
#include "HT_SSD1306Wire.h"
#include "CubeCell_NeoPixel.h"
#include "LoRaWan_APP.h"
//#include "LoRa_APP.h"
#include "GPS_Air530.h"
#include "GPS_Air530Z.h"
#include "globals.h"
#include "motor.h"
#include "subroutines.h"
#include "display.h"
#include "radio.h"
#include "sleep.h"
#include "gps.h"

void setNeoPixelColor(uint8_t red, uint8_t green, uint8_t blue) {
  rgbpixel.setPixelColor(0, rgbpixel.Color(red, green, blue));
  rgbpixel.show();
}

void setup() {
  // Initialize serial communication
  Serial.begin(115200);

  // Initialize OLED display
  VextON(); // Enable OLED power
  oled.init();
  oled.clear();
  oled.setFont(ArialMT_Plain_10);
  oled.drawString(0, 0, "Waiting for data...");
  oled.display();

  // Initialize NeoPixel
  rgbpixel.begin();
  rgbpixel.clear(); // Turn off all LEDs initially
  rgbpixel.show();
}

void loop() {
  // Check if data is available from the serial port
  if (Serial.available() > 0) {
    // Read and parse the incoming serial data
    String serialData = Serial.readStringUntil('\n');

    // Update the NeoPixel color based on the received data
    if (serialData.startsWith("RED")) {
      setNeoPixelColor(255, 0, 0); // Red color
    } else if (serialData.startsWith("GREEN")) {
      setNeoPixelColor(0, 255, 0); // Green color
    } else if (serialData.startsWith("BLUE")) {
      setNeoPixelColor(0, 0, 255); // Blue color
    } else {
      setNeoPixelColor(255, 255, 255); // Default white for unknown data
    }

    // Display the received data on the OLED
    oled.clear();
    oled.setFont(ArialMT_Plain_10);
    oled.drawString(0, 0, "Data received:");
    oled.setFont(ArialMT_Plain_16);
    oled.drawString(0, 20, serialData);
    oled.display();

    // Print to serial monitor (optional)
    Serial.println("Received: " + serialData);
  }
}
