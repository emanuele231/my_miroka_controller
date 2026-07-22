#!/usr/bin/env python3
"""
Controller tastiera per le emozioni di Mirokai.
Tasto 1 → Rabbia
Tasto 2 → Felicità
"""

import threading
import subprocess
import sys
from pynput import keyboard

# Mappa tasti → nodi ROS2
EMOTION_MAP = {
    '1': 'miroka_angry',
    '2': 'miroka_happy',
}

current_process = None
current_lock = threading.Lock()


def run_emotion(node_name: str) -> None:
    global current_process

    with current_lock:
        # Ferma l'emozione corrente se attiva
        if current_process and current_process.poll() is None:
            current_process.terminate()
            current_process.wait()
            print(f"\n[STOP] Emozione precedente terminata.")

        print(f"\n[START] Avvio: {node_name}")
        current_process = subprocess.Popen(
            ['ros2', 'run', 'my_miroka_controller', node_name],
            stdout=sys.stdout,   # output visibile nel terminale
            stderr=sys.stderr    # errori visibili nel terminale
        )


def on_press(key: keyboard.Key) -> None:
    try:
        k = key.char
        if k in EMOTION_MAP:
            threading.Thread(
                target=run_emotion,
                args=(EMOTION_MAP[k],),
                daemon=True
            ).start()
    except AttributeError:
        pass  # tasto speciale, ignorato


def main() -> None:
    print("=== Miroka Keyboard Controller ===")
    for k, v in EMOTION_MAP.items():
        print(f"  [{k}] → {v}")
    print("Premi Ctrl+C per uscire.\n")

    with keyboard.Listener(on_press=on_press) as listener:
        try:
            listener.join()
        except KeyboardInterrupt:
            print("\n[EXIT] Chiusura controller...")
            with current_lock:
                if current_process and current_process.poll() is None:
                    current_process.terminate()
                    current_process.wait()
            sys.exit(0)


if __name__ == '__main__':
    main()
