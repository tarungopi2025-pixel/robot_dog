import re
import sys
import time
import math
import struct
import threading
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import serial
import speech_recognition as sr


# ============================================================
# VOICE CONTROLLED ROBOT DOG — FINAL HIGH SENSITIVITY VERSION
# ============================================================

# ---------------- HARDWARE ----------------
SERIAL_PORT = "COM6"
BAUD_RATE = 115200

# Your working Intel laptop microphone
MIC_DEVICE_INDEX = 18

SERIAL_READ_TIMEOUT = 0.05
SERIAL_BOOT_DELAY_SECONDS = 2.0


# ---------------- SPEECH SETTINGS ----------------
SPEECH_LANGUAGES = ("en-IN", "en-US")

AMBIENT_CALIBRATION_SECONDS = 1.2
LISTEN_TIMEOUT_SECONDS = 1.5
PHRASE_TIME_LIMIT_SECONDS = 4.2
GOOGLE_TIMEOUT_SECONDS = 7.0

# Lower value = more sensitive microphone
MIN_ENERGY_THRESHOLD = 35
MAX_ENERGY_THRESHOLD = 105
CALIBRATION_SENSITIVITY_FACTOR = 0.55

UNKNOWN_AUDIO_BEFORE_BOOST = 2
UNKNOWN_SENSITIVITY_FACTOR = 0.82

# Avoid hearing the servo movement as a command
POST_COMMAND_AUDIO_IGNORE_SECONDS = 0.55

SAVE_UNRECOGNIZED_AUDIO = False
UNRECOGNIZED_AUDIO_FILE = Path("last_unrecognized.wav")


# ---------------- CLAP SETTINGS ----------------
AUDIO_ANALYSIS_RATE = 16000
AUDIO_FRAME_MS = 10

STRICT_CLAP_PEAK = 25000
STRICT_CLAP_CREST = 8.0
STRICT_CLAP_MAX_ACTIVE_SPAN = 0.12
STRICT_CLAP_MIN_IMPULSE_SHARE = 0.64

FALLBACK_CLAP_PEAK = 28000
FALLBACK_CLAP_CREST = 6.5
FALLBACK_CLAP_MAX_ACTIVE_SPAN = 0.18
FALLBACK_CLAP_MIN_IMPULSE_SHARE = 0.52

CLAP_LOCKOUT_SECONDS = 2.5
IGNORE_CLAP_AFTER_COMMAND_SECONDS = 1.0

DEBUG_AUDIO = False


# ============================================================
# COMMAND VOCABULARY
# ============================================================

COMMAND_ALIASES: Dict[str, Tuple[str, ...]] = {
    "SIT": (
        "sit",
        "sit down",
        "sit please",
        "sit now",
        "dog sit",
        "puppy sit",
        "take a seat",
        "take your seat",
        "seat",
        "seated",
        "sitting",
        "settle",
        "settle down",
        "go down",
        "get down",
        "down",
        "lower",
        "lower down",
        "crouch",
        "crouch down",
        "kneel",
        "kneel down",
        "rest",
        "take rest",
        "relax",
        "sleep",
        "sleep now",
        "go to sleep",
        "lie",
        "lie down",
        "lay",
        "lay down",
        "good night",
        "night night",
        "bedtime",
        "set",
    ),

    "STAND": (
        "stand",
        "stand up",
        "stand please",
        "stand now",
        "dog stand",
        "puppy stand",
        "standing",
        "get up",
        "getup",
        "get up now",
        "rise",
        "rise up",
        "come up",
        "lift up",
        "straighten up",
        "on your feet",
        "get on your feet",
        "wake",
        "wake up",
        "wake now",
        "awake",
        "be awake",
        "ready",
        "get ready",
        "up",
        "stand tall",
        "sand",
        "sand up",
        "stent",
        "stend",
    ),

    "WALK": (
        "walk",
        "walk now",
        "walk please",
        "dog walk",
        "puppy walk",
        "walking",
        "walk forward",
        "walk ahead",
        "move",
        "move now",
        "move forward",
        "move ahead",
        "go",
        "go now",
        "go forward",
        "go ahead",
        "go there",
        "come here",
        "come forward",
        "come closer",
        "forward",
        "ahead",
        "proceed",
        "advance",
        "start walking",
        "start moving",
        "take a step",
        "take steps",
        "step forward",
        "march",
        "crawl",
        "crawl forward",
        "keep going",
        "continue",
        "move on",
        "wal",
        "wall",
        "walkie",
        "wok",
        "work",
    ),

    "BACK": (
        "back",
        "back please",
        "dog back",
        "puppy back",
        "go back",
        "go backward",
        "go backwards",
        "backward",
        "backwards",
        "move back",
        "move backward",
        "move backwards",
        "walk back",
        "walk backward",
        "step back",
        "step backwards",
        "back up",
        "reverse",
        "reverse back",
        "retreat",
        "retreat back",
        "return",
        "come back",
        "go behind",
        "back off",
        "move away",
        "black",
    ),

    "POUNCE": (
        "pounce",
        "pounce now",
        "pounce please",
        "dog pounce",
        "jump",
        "jump now",
        "jump up",
        "jump please",
        "dog jump",
        "leap",
        "leap up",
        "hop",
        "hop now",
        "attack",
        "attack now",
        "attack mode",
        "go attack",
        "charge",
        "charge now",
        "lunge",
        "spring",
        "bounce",
        "strike",
        "rush",
        "go jump",
        "go pounce",
        "ponce",
        "pounds",
    ),

    "PUSHUP": (
        "pushup",
        "push up",
        "pushups",
        "push ups",
        "do pushup",
        "do push up",
        "do pushups",
        "do push ups",
        "pushup now",
        "push up now",
        "exercise",
        "do exercise",
        "exercise now",
        "workout",
        "work out",
        "do workout",
        "do work out",
        "training",
        "train",
        "fitness",
        "gym",
        "do gym",
        "dog exercise",
        "push app",
    ),

    "GREET": (
        "greet",
        "greet me",
        "greet us",
        "greeting",
        "greetings",
        "greet please",
        "wave",
        "wave hello",
        "wave hi",
        "wave please",
        "give a wave",
        "say hello",
        "say hi",
        "say hey",
        "hello",
        "hello there",
        "hello dog",
        "hi",
        "hi dog",
        "hey",
        "hey dog",
        "good morning",
        "morning",
        "morning dog",
        "good afternoon",
        "afternoon",
        "good evening",
        "evening",
        "good day",
        "have a good day",
        "welcome",
        "welcome me",
        "nice to meet you",
        "nice meeting you",
        "how are you",
        "whats up",
        "what is up",
        "namaste",
        "vanakkam",
        "vannakkam",
        "handshake",
        "hand shake",
        "shake hands",
        "say vanakkam",
        "dog",
        "doggy",
        "puppy",
        "robot dog",
        "cobot",
        "great",
        "grade",
    ),

    "LOOK": (
        "look",
        "look now",
        "look please",
        "dog look",
        "look here",
        "look at me",
        "look around",
        "look forward",
        "watch",
        "watch me",
        "watch here",
        "watch this",
        "stare",
        "observe",
        "see",
        "focus",
        "focus here",
        "focus on me",
        "attention",
        "pay attention",
        "be alert",
        "alert",
        "stay alert",
        "check",
        "check here",
        "check this",
        "notice me",
    ),

    "DANCE": (
        "dance",
        "dance now",
        "dance please",
        "dog dance",
        "dancing",
        "do a dance",
        "party",
        "party now",
        "groove",
        "groove now",
        "play",
        "play now",
        "boogie",
        "boogy",
        "shake",
        "shake it",
        "shake it off",
        "happy dance",
        "celebrate",
        "celebration",
        "celebrate now",
        "spin",
        "spin now",
        "twirl",
        "move to music",
        "show me your moves",
        "show your moves",
        "dance dog",
        "dense",
        "dents",
    ),

    "SING": (
        "sing",
        "sing now",
        "sing please",
        "sing a song",
        "sing song",
        "sing christmas",
        "sing merry christmas",
        "merry christmas",
        "we wish you a merry christmas",
        "christmas song",
        "play christmas song",
        "play merry christmas",
        "play a song",
        "play song",
        "play music",
        "play a tune",
        "music",
        "carol",
        "christmas carol",
        "sing carol",
        "perform song",
        "perform music",
        "buzzer song",
        "dog sing",
        "robot sing",
    ),
}

# These send SIT and close the controller
SHUTDOWN_ALIASES = (
    "shutdown",
    "shut down",
    "shut",
    "shutting down",
    "shut it down",
    "close",
    "close app",
    "close program",
    "close controller",
    "quit",
    "quite",
    "exit",
    "end",
    "end program",
    "finish",
    "terminate",
    "power off",
    "turn off",
    "switch off",
    "stop",
    "stop listening",
    "stop program",
    "stop controller",
    "bye",
    "goodbye",
    "good bye",
    "see you",
    "see you later",
    "enough",
    "no more",
)

COMMAND_COOLDOWNS = {
    "SIT": 1.0,
    "STAND": 1.4,
    "WALK": 0.45,
    "BACK": 0.45,
    "POUNCE": 1.0,
    "PUSHUP": 1.0,
    "GREET": 0.75,
    "LOOK": 0.65,
    "DANCE": 1.0,
    "SING": 12.0,
}

ALL_COMMAND_PHRASES = sorted(
    [
        (phrase, command)
        for command, phrases in COMMAND_ALIASES.items()
        for phrase in phrases
    ],
    key=lambda item: (len(item[0].split()), len(item[0])),
    reverse=True,
)


# ============================================================
# PICO SERIAL
# ============================================================

class PicoSerial:
    def __init__(self):
        self.port: Optional[serial.Serial] = None
        self.reader_thread: Optional[threading.Thread] = None
        self.stop_reader = threading.Event()
        self.write_lock = threading.Lock()

    def connect(self):
        print(f"\n Connecting to Pico on {SERIAL_PORT}...")

        try:
            self.port = serial.Serial(
                port=SERIAL_PORT,
                baudrate=BAUD_RATE,
                timeout=SERIAL_READ_TIMEOUT,
                write_timeout=1.0,
            )

            time.sleep(SERIAL_BOOT_DELAY_SECONDS)

            self.port.reset_input_buffer()
            self.port.reset_output_buffer()

            self.reader_thread = threading.Thread(
                target=self._serial_read_loop,
                daemon=True,
            )

            self.reader_thread.start()

            print(" Pico connected successfully.")

        except serial.SerialException as error:
            print(f" Pico connection failed: {error}")
            print("Close Arduino Serial Monitor / Thonny and verify COM6.")
            sys.exit(1)

    def _serial_read_loop(self):
        while not self.stop_reader.is_set():
            try:
                if self.port is None or not self.port.is_open:
                    return

                raw = self.port.readline()

                if not raw:
                    time.sleep(0.01)
                    continue

                reply = raw.decode(
                    "utf-8",
                    errors="replace",
                ).strip()

                if reply:
                    print(f"\n Robot: {reply}")

            except serial.SerialException:
                print("\n Pico serial connection lost.")
                return

            except Exception:
                time.sleep(0.02)

    def send(self, command: str) -> bool:
        try:
            if self.port is None or not self.port.is_open:
                print(" Pico serial port is unavailable.")
                return False

            with self.write_lock:
                self.port.write(f"{command}\n".encode("utf-8"))
                self.port.flush()

            print(f" Sent to Pico: {command}")
            return True

        except Exception as error:
            print(f" Serial send error: {error}")
            return False

    def close(self):
        self.stop_reader.set()

        if self.reader_thread and self.reader_thread.is_alive():
            self.reader_thread.join(timeout=0.5)

        try:
            if self.port and self.port.is_open:
                self.port.close()
        except Exception:
            pass


class CommandGate:
    def __init__(self, pico: PicoSerial):
        self.pico = pico
        self.last_sent: Dict[str, float] = {}

    def send(self, command: str, force: bool = False) -> bool:
        now = time.monotonic()

        cooldown = COMMAND_COOLDOWNS.get(command, 0.55)
        previous = self.last_sent.get(command, -999.0)

        if not force and now - previous < cooldown:
            return False

        if self.pico.send(command):
            self.last_sent[command] = now
            return True

        return False


# ============================================================
# CLAP DETECTION
# ============================================================

@dataclass
class AudioProfile:
    peak: int
    rms: float
    crest_factor: float
    active_span_seconds: float
    impulse_energy_share: float


def build_audio_profile(audio: sr.AudioData) -> AudioProfile:
    raw_audio = audio.get_raw_data(
        convert_rate=AUDIO_ANALYSIS_RATE,
        convert_width=2,
    )

    sample_count = len(raw_audio) // 2

    if sample_count <= 0:
        return AudioProfile(0, 0.0, 0.0, 0.0, 0.0)

    samples = struct.unpack(
        f"<{sample_count}h",
        raw_audio[:sample_count * 2],
    )

    peak = max(abs(sample) for sample in samples)

    rms = math.sqrt(
        sum(sample * sample for sample in samples) / len(samples)
    )

    crest_factor = peak / max(rms, 1.0)

    frame_size = max(
        1,
        int(AUDIO_ANALYSIS_RATE * AUDIO_FRAME_MS / 1000),
    )

    frames: List[float] = []

    for start in range(0, len(samples), frame_size):
        frame = samples[start:start + frame_size]

        if frame:
            frames.append(
                math.sqrt(
                    sum(sample * sample for sample in frame) / len(frame)
                )
            )

    if not frames:
        return AudioProfile(peak, rms, crest_factor, 0.0, 0.0)

    peak_frame = max(
        range(len(frames)),
        key=frames.__getitem__,
    )

    active_threshold = max(500.0, frames[peak_frame] * 0.38)

    left = peak_frame
    right = peak_frame

    while left > 0 and frames[left - 1] >= active_threshold:
        left -= 1

    while right < len(frames) - 1 and frames[right + 1] >= active_threshold:
        right += 1

    active_span = (
        (right - left + 1)
        * AUDIO_FRAME_MS
        / 1000.0
    )

    total_energy = sum(value * value for value in frames)

    local_start = max(0, peak_frame - 1)
    local_end = min(len(frames), peak_frame + 2)

    local_energy = sum(
        value * value
        for value in frames[local_start:local_end]
    )

    impulse_share = local_energy / max(total_energy, 1.0)

    return AudioProfile(
        peak,
        rms,
        crest_factor,
        active_span,
        impulse_share,
    )


def is_clap(audio: sr.AudioData, strict: bool = True) -> bool:
    profile = build_audio_profile(audio)

    if DEBUG_AUDIO:
        print(
            f"\n[AUDIO] Peak={profile.peak}, "
            f"Crest={profile.crest_factor:.2f}, "
            f"Span={profile.active_span_seconds:.3f}s, "
            f"Impulse={profile.impulse_energy_share:.2f}"
        )

    if strict:
        return (
            profile.peak >= STRICT_CLAP_PEAK
            and profile.crest_factor >= STRICT_CLAP_CREST
            and profile.active_span_seconds <= STRICT_CLAP_MAX_ACTIVE_SPAN
            and profile.impulse_energy_share >= STRICT_CLAP_MIN_IMPULSE_SHARE
        )

    return (
        profile.peak >= FALLBACK_CLAP_PEAK
        and profile.crest_factor >= FALLBACK_CLAP_CREST
        and profile.active_span_seconds <= FALLBACK_CLAP_MAX_ACTIVE_SPAN
        and profile.impulse_energy_share >= FALLBACK_CLAP_MIN_IMPULSE_SHARE
    )


# ============================================================
# COMMAND MATCHING
# ============================================================

def normalize_text(text: str) -> str:
    text = text.lower()
    text = text.replace("-", " ")
    text = text.replace("_", " ")

    text = re.sub(r"[^a-z0-9\s]", " ", text)

    return re.sub(r"\s+", " ", text).strip()


def contains_phrase(text: str, phrase: str) -> bool:
    pattern = r"(?<!\w)" + re.escape(phrase) + r"(?!\w)"
    return re.search(pattern, text) is not None


def fuzzy_phrase_match(text: str, phrase: str) -> bool:
    compact_phrase = phrase.replace(" ", "")

    if len(compact_phrase) < 3:
        return False

    words = text.split()
    phrase_words = phrase.split()

    if not words:
        return False

    minimum_window = max(1, len(phrase_words) - 1)
    maximum_window = min(
        len(words),
        len(phrase_words) + 1,
    )

    if len(compact_phrase) <= 4:
        minimum_score = 0.72
    elif len(compact_phrase) <= 6:
        minimum_score = 0.82
    elif len(compact_phrase) <= 9:
        minimum_score = 0.84
    else:
        minimum_score = 0.80

    for window_size in range(
        minimum_window,
        maximum_window + 1,
    ):
        for start in range(len(words) - window_size + 1):
            candidate = "".join(
                words[start:start + window_size]
            )

            if len(candidate) < 3:
                continue

            if len(compact_phrase) <= 4:
                if candidate[:2] != compact_phrase[:2]:
                    continue

            similarity = SequenceMatcher(
                None,
                candidate,
                compact_phrase,
            ).ratio()

            if similarity >= minimum_score:
                return True

    return False


def is_shutdown_command(text: str, fuzzy: bool = True) -> bool:
    for phrase in SHUTDOWN_ALIASES:
        if contains_phrase(text, phrase):
            return True

    if fuzzy:
        for phrase in SHUTDOWN_ALIASES:
            if fuzzy_phrase_match(text, phrase):
                return True

    return False


def find_robot_command(
    text: str,
    use_fuzzy: bool = True,
) -> Optional[str]:
    for phrase, command in ALL_COMMAND_PHRASES:
        if contains_phrase(text, phrase):
            return command

    if use_fuzzy:
        for phrase, command in ALL_COMMAND_PHRASES:
            if fuzzy_phrase_match(text, phrase):
                return command

    return None


# ============================================================
# SPEECH RECOGNITION
# ============================================================

def build_recognizer() -> sr.Recognizer:
    recognizer = sr.Recognizer()

    recognizer.dynamic_energy_threshold = False
    recognizer.pause_threshold = 0.75
    recognizer.phrase_threshold = 0.08
    recognizer.non_speaking_duration = 0.25
    recognizer.operation_timeout = GOOGLE_TIMEOUT_SECONDS

    return recognizer


def get_microphone() -> sr.Microphone:
    microphones = sr.Microphone.list_microphone_names()

    print("\n" + "-" * 62)
    print(" MICROPHONE SELECTED")
    print("-" * 62)

    if 0 <= MIC_DEVICE_INDEX < len(microphones):
        print(f"[{MIC_DEVICE_INDEX}] {microphones[MIC_DEVICE_INDEX]}")
        return sr.Microphone(device_index=MIC_DEVICE_INDEX)

    print(" Microphone 18 unavailable. Using Windows default.")
    return sr.Microphone()


def calibrate_microphone(
    recognizer: sr.Recognizer,
    source,
):
    print("\n Calibrating background noise.")
    print("Stay quiet for 1.2 seconds...")

    recognizer.adjust_for_ambient_noise(
        source,
        duration=AMBIENT_CALIBRATION_SECONDS,
    )

    measured_threshold = recognizer.energy_threshold

    high_sensitivity_threshold = int(
        measured_threshold * CALIBRATION_SENSITIVITY_FACTOR
    )

    recognizer.energy_threshold = max(
        MIN_ENERGY_THRESHOLD,
        min(MAX_ENERGY_THRESHOLD, high_sensitivity_threshold),
    )

    recognizer.dynamic_energy_threshold = False

    print(" Calibration complete.")
    print(
        f" High-sensitivity threshold: "
        f"{recognizer.energy_threshold:.0f}"
    )


def save_unclear_audio(audio: sr.AudioData):
    if not SAVE_UNRECOGNIZED_AUDIO:
        return

    try:
        UNRECOGNIZED_AUDIO_FILE.write_bytes(
            audio.get_wav_data()
        )
    except Exception:
        pass


def recognize_speech_candidates(
    recognizer: sr.Recognizer,
    audio: sr.AudioData,
) -> List[str]:
    candidates: List[str] = []

    for language in SPEECH_LANGUAGES:
        try:
            result = recognizer.recognize_google(
                audio,
                language=language,
                show_all=True,
            )

            if isinstance(result, dict):
                alternatives = result.get("alternative", [])

                for alternative in alternatives[:8]:
                    transcript = normalize_text(
                        alternative.get("transcript", "")
                    )

                    if transcript and transcript not in candidates:
                        candidates.append(transcript)

            elif isinstance(result, str):
                transcript = normalize_text(result)

                if transcript and transcript not in candidates:
                    candidates.append(transcript)

            if candidates:
                return candidates

        except sr.UnknownValueError:
            continue

        except sr.RequestError as error:
            print(f"\n Google Speech Recognition error: {error}")
            return []

        except Exception as error:
            print(f"\n Speech recognition error: {error}")
            return []

    return candidates


def interpret_candidates(
    candidates: List[str],
) -> Tuple[Optional[str], Optional[str], bool]:
    if not candidates:
        return None, None, False

    if is_shutdown_command(candidates[0], fuzzy=True):
        return None, candidates[0], True

    for text in candidates[1:]:
        if is_shutdown_command(text, fuzzy=False):
            return None, text, True

    for text in candidates:
        command = find_robot_command(text, use_fuzzy=False)

        if command:
            return command, text, False

    for text in candidates:
        command = find_robot_command(text, use_fuzzy=True)

        if command:
            return command, text, False

    return None, candidates[0], False


# ============================================================
# MAIN ROBOT CONTROLLER
# ============================================================

class ShutdownRequested(Exception):
    pass


class RobotDogVoiceController:
    def __init__(self):
        self.pico = PicoSerial()
        self.command_gate = CommandGate(self.pico)

        self.recognizer = build_recognizer()
        self.microphone = get_microphone()

        self.last_clap_time = -999.0
        self.ignore_clap_until = 0.0
        self.ignore_audio_until = 0.0
        self.unknown_audio_count = 0

    def show_banner(self):
        print("\n" + "=" * 64)
        print(" VOICE CONTROLLED ROBOT DOG — FINAL CONTROLLER")
        print("=" * 64)

        print("\nMain actions:")
        print("sit | stand | walk | back | pounce")
        print("pushup | greet | look | dance | sing")

        print("\nExamples:")
        print("good morning | hello | doggy -> GREET")
        print("walk | wal | come here -> WALK")
        print("go back | reverse | black -> BACK")
        print("sing | merry christmas -> SING")
        print("shut | shutdown | quit | stop -> CLOSE")

        print("\n Clap once: STAND")

    def increase_microphone_sensitivity(self):
        current = self.recognizer.energy_threshold

        updated = max(
            MIN_ENERGY_THRESHOLD,
            int(current * UNKNOWN_SENSITIVITY_FACTOR),
        )

        if updated < current:
            self.recognizer.energy_threshold = updated

            print(
                f" Voice sensitivity increased "
                f"(threshold: {updated})"
            )

    def after_robot_command(self):
        now = time.monotonic()

        self.ignore_clap_until = (
            now + IGNORE_CLAP_AFTER_COMMAND_SECONDS
        )

        self.ignore_audio_until = (
            now + POST_COMMAND_AUDIO_IGNORE_SECONDS
        )

    def trigger_clap(self):
        now = time.monotonic()

        if now < self.ignore_clap_until:
            return

        if now - self.last_clap_time < CLAP_LOCKOUT_SECONDS:
            return

        self.last_clap_time = now

        print(" Clap detected.")
        self.command_gate.send("STAND")
        self.after_robot_command()

    def process_recognized_speech(
        self,
        candidates: List[str],
    ):
        command, matched_text, shutdown = interpret_candidates(candidates)

        top_text = candidates[0]

        if matched_text and matched_text != top_text:
            print(
                f' You said: "{top_text}" '
                f'-> understood as: "{matched_text}"'
            )
        else:
            print(f' You said: "{top_text}"')

        if shutdown:
            print(" Closing controller.")
            self.command_gate.send("SIT", force=True)
            self.after_robot_command()
            raise ShutdownRequested

        if command is None:
            print(" No robot command found.")
            return

        self.unknown_audio_count = 0

        self.command_gate.send(command)
        self.after_robot_command()

    def handle_unknown_audio(
        self,
        audio: sr.AudioData,
    ):
        self.unknown_audio_count += 1

        if self.unknown_audio_count >= UNKNOWN_AUDIO_BEFORE_BOOST:
            self.increase_microphone_sensitivity()
            self.unknown_audio_count = 0

        print(" Voice unclear — listening again.")
        save_unclear_audio(audio)

    def run(self):
        self.show_banner()
        self.pico.connect()

        try:
            with self.microphone as source:
                calibrate_microphone(
                    self.recognizer,
                    source,
                )

                print("\n System ready.")
                print(" Speak normally, around 20–40 cm from laptop.\n")

                while True:
                    if time.monotonic() < self.ignore_audio_until:
                        time.sleep(0.05)
                        continue

                    try:
                        audio = self.recognizer.listen(
                            source,
                            timeout=LISTEN_TIMEOUT_SECONDS,
                            phrase_time_limit=PHRASE_TIME_LIMIT_SECONDS,
                        )

                    except sr.WaitTimeoutError:
                        continue

                    if is_clap(audio, strict=True):
                        self.trigger_clap()
                        continue

                    print(
                        " Processing speech...",
                        end="\r",
                        flush=True,
                    )

                    candidates = recognize_speech_candidates(
                        self.recognizer,
                        audio,
                    )

                    if candidates:
                        print(" " * 65, end="\r")
                        self.process_recognized_speech(candidates)
                        continue

                    if is_clap(audio, strict=False):
                        self.trigger_clap()
                        continue

                    self.handle_unknown_audio(audio)

        except ShutdownRequested:
            print(" Voice controller closed.")

        except KeyboardInterrupt:
            print("\n Keyboard stop received.")
            self.command_gate.send("SIT", force=True)

        finally:
            self.pico.close()
            print(" Pico disconnected.")


if __name__ == "__main__":
    RobotDogVoiceController().run()
