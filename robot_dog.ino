#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

// ============================================================
// HARDWARE
// ============================================================

// PCA9685 on default I2C address 0x40
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(0x40);

// Passive buzzer pin:
// Raspberry Pi Pico: GP2
// Arduino Nano/Uno: D2
const uint8_t BUZZER_PIN = 2;

// Servo hardware channel map
const int FL = 0; // Front Left
const int FR = 1; // Front Right
const int BL = 2; // Back Left
const int BR = 3; // Back Right

// PCA9685 Duty Cycle Ticks
const int SERVO_MIN = 150;
const int SERVO_MAX = 600;

// Live current angles
int currentAngles[4] = {90, 90, 90, 90};

// ============================================================
// EXISTING POSES — UNCHANGED
// ============================================================

const int STAND_ANGLES[4] = {90, 90, 90, 90};
const int SIT_ANGLES[4]   = {170, 0, 0, 170};

// New gentle sing sway — temporary only, returns to stand.
const int SING_SWAY_A[4] = {96, 96, 96, 96};
const int SING_SWAY_B[4] = {84, 84, 84, 84};

// ============================================================
// WE WISH YOU A MERRY CHRISTMAS MELODY
// ============================================================

const int NOTE_D4  = 294;
const int NOTE_E4  = 330;
const int NOTE_FS4 = 370;
const int NOTE_G4  = 392;
const int NOTE_A4  = 440;
const int NOTE_B4  = 494;
const int NOTE_C5  = 523;

const int MERRY_BEAT_MS = 155;

const int MERRY_MELODY[] = {
  NOTE_G4, NOTE_G4, NOTE_A4, NOTE_G4, NOTE_FS4, NOTE_E4,
  NOTE_E4, NOTE_E4, NOTE_A4, NOTE_A4, NOTE_B4, NOTE_A4, NOTE_G4,
  NOTE_FS4, NOTE_FS4, NOTE_B4, NOTE_B4, NOTE_C5, NOTE_B4, NOTE_A4,
  NOTE_G4, NOTE_E4, NOTE_E4, NOTE_FS4, NOTE_A4, NOTE_G4, NOTE_FS4, NOTE_E4,
  NOTE_D4, NOTE_D4, NOTE_E4, NOTE_A4, NOTE_FS4, NOTE_G4
};

const uint8_t MERRY_BEATS[] = {
  1, 1, 1, 1, 1, 2,
  1, 1, 1, 1, 1, 1, 2,
  1, 1, 1, 1, 1, 1, 2,
  1, 1, 1, 1, 1, 1, 1, 2,
  1, 1, 1, 1, 1, 3
};

const int MERRY_NOTE_COUNT =
  sizeof(MERRY_MELODY) / sizeof(MERRY_MELODY[0]);

// ============================================================
// SETUP
// ============================================================

void setup() {
  Serial.begin(115200);

  Wire.begin();

  pwm.begin();
  pwm.setOscillatorFrequency(27000000);
  pwm.setPWMFreq(50);

  pinMode(BUZZER_PIN, OUTPUT);
  noTone(BUZZER_PIN);

  delay(10);

  // Original startup stand pose
  moveToPose(STAND_ANGLES, 1, 0);
}

// ============================================================
// MAIN LOOP
// ============================================================

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "STAND") {
      Serial.println("Executing: Stand Up");
      moveToPose(STAND_ANGLES, 35, 12);
    }
    else if (command == "SIT") {
      Serial.println("Executing: Sit Down");
      moveToPose(SIT_ANGLES, 35, 12);
    }
    else if (command == "WALK") {
      Serial.println("Executing: Seesaw Crawl Forward");
      cuteWalk(4);
    }
    else if (command == "BACK") {
      Serial.println("Executing: Seesaw Crawl Backward");
      cuteBackward(4);
    }
    else if (command == "POUNCE") {
      Serial.println("Executing: Sudden Pounce");
      cutePounce();
    }
    else if (command == "PUSHUP") {
      Serial.println("Executing: Gym Reps");
      doPushups(3);
    }
    else if (command == "GREET") {
      Serial.println("Executing: Wave Hello");
      waveHi(3);
    }
    else if (command == "LOOK") {
      Serial.println("Executing: Look At Owner");
      lookAtMe();
    }
    else if (command == "DANCE") {
      Serial.println("Executing: Cute Dance Routine");
      cuteDance(2);
    }
    else if (command == "SING") {
      Serial.println("Executing: Merry Christmas Song");
      singMerryChristmas();
    }
  }
}

// ============================================================
// MOTION ENGINES — ORIGINAL ANGLES UNCHANGED
// ============================================================

void cuteWalk(int cycles) {
  int swing = 40;

  for (int i = 0; i < cycles; i++) {
    int dropRear[4] = {90, 90, 90 - swing, 90 + swing};
    moveToPose(dropRear, 15, 8);

    int reachFront[4] = {
      90 + swing, 90 - swing,
      90 - swing, 90 + swing
    };
    moveToPose(reachFront, 12, 6);

    moveToPose(STAND_ANGLES, 20, 10);

    int dropFront[4] = {90 - swing, 90 + swing, 90, 90};
    moveToPose(dropFront, 15, 8);

    int reachRear[4] = {
      90 - swing, 90 + swing,
      90 + swing, 90 - swing
    };
    moveToPose(reachRear, 12, 6);

    moveToPose(STAND_ANGLES, 20, 10);
  }
}

void cuteBackward(int cycles) {
  int swing = 40;

  for (int i = 0; i < cycles; i++) {
    int dropFront[4] = {90 + swing, 90 - swing, 90, 90};
    moveToPose(dropFront, 15, 8);

    int reachRearBwd[4] = {
      90 + swing, 90 - swing,
      90 - swing, 90 + swing
    };
    moveToPose(reachRearBwd, 12, 6);

    moveToPose(STAND_ANGLES, 20, 10);

    int dropRear[4] = {90, 90, 90 + swing, 90 - swing};
    moveToPose(dropRear, 15, 8);

    int reachFrontBwd[4] = {
      90 - swing, 90 + swing,
      90 + swing, 90 - swing
    };
    moveToPose(reachFrontBwd, 12, 6);

    moveToPose(STAND_ANGLES, 20, 10);
  }
}

void cutePounce() {
  int crouch[4] = {0, 170, 170, 0};

  moveToPose(crouch, 30, 15);
  delay(800);

  moveToPose(STAND_ANGLES, 1, 0);
  delay(1000);
}

void cuteDance(int repetitions) {
  int swing = 25;

  int tapLeft[4]  = {65, 90, 90, 90};
  int tapRight[4] = {90, 115, 90, 90};

  for (int r = 0; r < repetitions; r++) {
    for (int i = 0; i < 2; i++) {
      int swayA[4] = {
        90 + swing, 90 + swing,
        90 + swing, 90 + swing
      };

      int swayB[4] = {
        90 - swing, 90 - swing,
        90 - swing, 90 - swing
      };

      moveToPose(swayA, 10, 8);
      moveToPose(swayB, 10, 8);
    }

    moveToPose(STAND_ANGLES, 8, 5);

    for (int i = 0; i < 2; i++) {
      moveToPose(tapLeft, 8, 6);
      moveToPose(STAND_ANGLES, 8, 6);

      moveToPose(tapRight, 8, 6);
      moveToPose(STAND_ANGLES, 8, 6);
    }

    int bounceLow[4] = {120, 60, 60, 120};

    for (int i = 0; i < 2; i++) {
      moveToPose(bounceLow, 6, 4);
      delay(40);

      moveToPose(STAND_ANGLES, 6, 4);
      delay(40);
    }
  }

  moveToPose(STAND_ANGLES, 15, 10);
}

void doPushups(int reps) {
  int pushupDown[4] = {0, 170, 170, 0};

  for (int i = 0; i < reps; i++) {
    moveToPose(pushupDown, 35, 12);
    delay(500);

    moveToPose(STAND_ANGLES, 35, 12);
    delay(500);
  }
}

void lookAtMe() {
  int lookPose[4] = {90, 90, 0, 170};

  moveToPose(lookPose, 35, 12);
  delay(2500);

  moveToPose(STAND_ANGLES, 25, 10);
}

void waveHi(int shakes) {
  // BL fully inward = 0° based on your existing calibration
  // FR raised, then slowly waves
  int greetPose[4] = {90, 130, 0, 90};

  moveToPose(greetPose, 25, 10);
  delay(250);

  for (int i = 0; i < shakes; i++) {
    setAngle(FR, 55);   // Front-right paw inward
    delay(320);         // Slow wave

    setAngle(FR, 130);  // Front-right paw outward
    delay(320);
  }

  delay(250);

  // Return safely to your original standing pose
  moveToPose(STAND_ANGLES, 25, 10);
}

// ============================================================
// SING: MERRY CHRISTMAS + GENTLE BODY JIGGLE
// ============================================================

void playNoteWithJiggle(
  int frequency,
  int durationMs,
  bool swayToA
) {
  if (frequency > 0) {
    tone(BUZZER_PIN, frequency);
  } else {
    noTone(BUZZER_PIN);
  }

  // Small safe jiggle around your existing 90-degree stand pose.
  if (swayToA) {
    moveToPose(SING_SWAY_A, 4, 6);
  } else {
    moveToPose(SING_SWAY_B, 4, 6);
  }

  const int movementTimeMs = 24;
  const int noteGapMs = 18;

  int remainingTime = durationMs - movementTimeMs - noteGapMs;

  if (remainingTime > 0) {
    delay(remainingTime);
  }

  noTone(BUZZER_PIN);
  delay(noteGapMs);
}

void singMerryChristmas() {
  // Makes it safely stand before singing.
  moveToPose(STAND_ANGLES, 20, 8);
  delay(150);

  for (int i = 0; i < MERRY_NOTE_COUNT; i++) {
    int noteDuration = MERRY_BEATS[i] * MERRY_BEAT_MS;

    // Alternate soft body sway with each note.
    bool swayToA = (i % 2 == 0);

    playNoteWithJiggle(
      MERRY_MELODY[i],
      noteDuration,
      swayToA
    );
  }

  noTone(BUZZER_PIN);

  // Return exactly to your original stand pose.
  moveToPose(STAND_ANGLES, 15, 8);
}

// ============================================================
// PCA9685 SERVO FUNCTIONS
// ============================================================

void setAngle(uint8_t channel, int angle) {
  angle = constrain(angle, 0, 180);

  uint16_t pulse = map(
    angle,
    0,
    180,
    SERVO_MIN,
    SERVO_MAX
  );

  pwm.setPWM(channel, 0, pulse);
}

void moveToPose(
  const int targetPose[4],
  int steps,
  int delayMs
) {
  float increments[4];
  float tempAngles[4];

  for (int i = 0; i < 4; i++) {
    increments[i] = (
      targetPose[i] - currentAngles[i]
    ) / (float)steps;

    tempAngles[i] = currentAngles[i];
  }

  for (int step = 1; step <= steps; step++) {
    for (int i = 0; i < 4; i++) {
      tempAngles[i] += increments[i];

      int channel =
        (i == 0) ? FL :
        (i == 1) ? FR :
        (i == 2) ? BL :
                   BR;

      setAngle(channel, (int)tempAngles[i]);
    }

    if (delayMs > 0) {
      delay(delayMs);
    }
  }

  for (int i = 0; i < 4; i++) {
    currentAngles[i] = targetPose[i];
  }
}
