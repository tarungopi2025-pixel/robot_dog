# Voice Controlled Quadruped Robot Dog

A four-servo quadruped robot dog controlled by Python voice recognition and a Raspberry Pi Pico. The robot receives commands over USB serial and performs movements such as sitting, standing, greeting, dancing, walking, push-ups, and singing a Christmas melody through a passive buzzer.

## Features

- Voice-controlled robot actions
- Clap detection to make the robot stand
- Flexible command recognition with alternative phrases
- Serial communication between laptop and Raspberry Pi Pico
- PCA9685 PWM servo driver control
- Smooth servo interpolation for natural movement
- Greeting gesture with a back-leg bend and front-leg wave
- Passive buzzer melody: "We Wish You a Merry Christmas"
- Automatic microphone sensitivity handling

## Hardware Used

- Raspberry Pi Pico
- PCA9685 16-channel PWM servo driver
- 4 x servo motors
- Passive buzzer
- External 5V servo power supply or battery pack
- Jumper wires
- USB cable for Raspberry Pi Pico

## Servo Channel Mapping

| Robot Leg | PCA9685 Channel |
|---|---:|
| Front Left | 0 |
| Front Right | 1 |
| Back Left | 2 |
| Back Right | 3 |

## Raspberry Pi Pico to PCA9685 Connections

| Raspberry Pi Pico | PCA9685 | Purpose |
|---|---|---|
| GP4 | SDA | I2C data |
| GP5 | SCL | I2C clock |
| 3V3 | VCC | PCA9685 logic power |
| GND | GND | Common ground |

> The PCA9685 `VCC` pin is for logic power. Do not power the servos from the Pico 3V3 pin.

## Servo Power Connections

| External Servo Supply | PCA9685 |
|---|---|
| 5V positive | V+ |
| Ground | GND |

Important: Connect the external supply ground, PCA9685 ground, and Raspberry Pi Pico ground together. A common ground is required for reliable servo control.

## Passive Buzzer Connection

| Passive Buzzer | Raspberry Pi Pico |
|---|---|
| Positive / Signal | GP10 |
| Negative | GND |

The Arduino/Pico code uses:

```cpp
const uint8_t BUZZER_PIN = 10;
```

## Wiring Overview

```text
Laptop
  |
  | USB Serial
  |
Raspberry Pi Pico
  |-- GP4  -> PCA9685 SDA
  |-- GP5  -> PCA9685 SCL
  |-- 3V3  -> PCA9685 VCC
  |-- GND  -> PCA9685 GND
  |-- GP10 -> Passive Buzzer Signal
  |
PCA9685
  |-- Channel 0 -> Front Left Servo
  |-- Channel 1 -> Front Right Servo
  |-- Channel 2 -> Back Left Servo
  |-- Channel 3 -> Back Right Servo
  |
External 5V Supply
  |-- 5V  -> PCA9685 V+
  |-- GND -> PCA9685 GND
```

## Software Requirements

### Laptop

Install Python dependencies:

```bash
pip install pyserial SpeechRecognition pyaudio
```

### Arduino IDE

Install these libraries from the Arduino Library Manager:

```text
Adafruit PWM Servo Driver Library
Adafruit BusIO
```

Select the correct Raspberry Pi Pico board and upload the robot firmware.

## Running the Voice Controller

1. Connect the Raspberry Pi Pico to the laptop through USB.
2. Confirm the correct COM port in `cobot.py`.

```python
SERIAL_PORT = "COM6"
```

3. Confirm the microphone index in `cobot.py`.

```python
MIC_DEVICE_INDEX = 18
```

4. Run:

```bash
python cobot.py
```

5. Stay quiet during microphone calibration.
6. Speak a command clearly.

## Supported Voice Commands

| Action | Example Voice Commands | Pico Command |
|---|---|---|
| Sit | sit, sleep, lie down, rest | `SIT` |
| Stand | stand, wake up, rise, get up | `STAND` |
| Walk | walk, go forward, move, come here | `WALK` |
| Back | back, reverse, retreat, go back | `BACK` |
| Pounce | jump, pounce, attack, charge | `POUNCE` |
| Push-up | push up, workout, exercise, gym | `PUSHUP` |
| Greet | hello, good morning, handshake, namaste, vanakkam | `GREET` |
| Look | look, watch, focus, attention | `LOOK` |
| Dance | dance, party, groove, celebrate | `DANCE` |
| Sing | sing, merry christmas, play christmas song | `SING` |
| Close controller | shut, shutdown, stop, quit, exit | `SIT` then closes |

## Gesture Details

### Greeting

When a greeting phrase is detected, the robot:

1. Bends the back-left leg inward.
2. Raises the front-right leg.
3. Slowly waves the front-right leg.
4. Returns to its neutral standing position.

### Singing

When the `SING` command is received, the robot:

1. Moves to the standing pose.
2. Plays "We Wish You a Merry Christmas" through the passive buzzer.
3. Performs a gentle body jiggle during the melody.
4. Returns to the neutral standing pose.

## Important Safety Notes

- Use a separate regulated 5V supply for the servos.
- Do not power four servos from the Pico USB port.
- Ensure all grounds are connected together.
- Test servo directions at low movement angles before using full movement.
- Keep hands clear of moving servo arms and linkages.
- Do not force a servo arm manually while the servo is powered.
- Use a stable surface so the robot does not fall during testing.

## Project Structure

```text
robot-dog/
├── cobot.py                 # Python voice recognition and serial controller
├── robot_dog_firmware.ino   # Raspberry Pi Pico / Arduino firmware
└── README.md
```

## Future Improvements

- Better forward walking gait calibration
- Obstacle detection with ultrasonic sensor
- Bluetooth or Wi-Fi control
- Camera-based object tracking
- Battery-powered mobile version
- More expressive body gestures
- Offline speech recognition

## Author

Tarun Gopi Parthasarathi  
B.Tech Electronics and Communication Engineering, VIT Chennai

## License

This project is intended for learning, experimentation, and personal robotics development.
