# PulseNet: Wearable Health Monitoring System

PulseNet is an innovative project that utilizes Photoplethysmography (PPG) technology to monitor heart rate and blood oxygen levels in real-time. By leveraging the MAX30102 sensor and the ESP32 microcontroller, PulseNet offers a compact and efficient solution for wearable health monitoring. 

## Features
- **Heart Rate Monitoring**: Continuously tracks heart rate using the MAX30102's red/infrared LEDs and photodetector for precise PPG signal capture.
- **Blood Oxygen Measurement**: Provides real-time SpO2 (blood oxygen saturation) levels.
- **Compact and Low-Power Design**: Optimized for wearable devices to enable continuous health monitoring.
- **Wi-Fi Connectivity**: Transmits PPG data to connected devices in real-time using the ESP32 microcontroller.
- **User-Friendly GUI**: Displays heart rate and oxygen levels visually for better health awareness.

## Hardware Components
- **MAX30102 Sensor**: Integrated module with red/infrared LEDs and a photodetector for PPG signal acquisition.
- **ESP32 Microcontroller**: Handles data acquisition and wireless transmission via Wi-Fi.
- **Wearable Form Factor**: Designed to be lightweight and compact for user comfort.

## Software Features
- **PPG Signal Processing**: Extracts and analyzes heart rate and SpO2 data from raw PPG signals.
- **Real-Time Visualization**: GUI application for displaying health metrics in a user-friendly interface.
- **Wireless Communication**: Real-time data transfer to connected devices through Wi-Fi.

## Applications
- Personal health tracking
- Cardiovascular health awareness
- Fitness monitoring
- Remote health diagnostics

## How It Works
1. **PPG Signal Capture**: The MAX30102 sensor uses its LEDs to emit light into the skin and measures the reflected light through its photodetector.
2. **Data Processing**: The ESP32 microcontroller processes the captured PPG signals to calculate heart rate and SpO2 levels.
3. **Data Transmission**: Processed data is transmitted wirelessly via Wi-Fi.
4. **Visualization**: A user-friendly GUI displays the heart rate and oxygen levels in real-time.

## Getting Started
### Prerequisites
- ESP32 Microcontroller
- MAX30102 Sensor Module
- Arduino IDE or ESP-IDF for firmware development
- Python or JavaScript for GUI development

### Setup Instructions
1. **Hardware Setup**:
   - Connect the MAX30102 sensor to the ESP32 microcontroller.
   - Power the setup with a portable battery pack for wearable usage.

2. **Firmware Development**:
   - Install required libraries for MAX30102 and ESP32.
   - Upload the firmware to ESP32 using the Arduino IDE or ESP-IDF.

3. **GUI Application**:
   - Develop or run the provided GUI application to visualize data.
   - Ensure your device is connected to the same Wi-Fi network as the ESP32.

4. **Start Monitoring**:
   - Wear the device and begin real-time monitoring of your heart rate and blood oxygen levels.

---
PulseNet showcases the potential of wearable technology to promote cardiovascular health awareness and empower individuals with real-time health insights. Stay tuned for future updates and enhancements!
