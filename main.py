#!/usr/bin/env python3
"""
Controller da terminale per le emozioni di Mirokai.
Funziona su qualsiasi terminale Linux senza bisogno di permessi speciali o pynput.
"""

import threading
import subprocess
import sys

# Codici ANSI per colori
COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_YELLOW = "\033[93m"
COLOR_RESET = "\033[0m"

EMOTION_MAP = {
    '1': 'miroka_angry',
    '2': 'miroka_happy',
    '3': 'miroka_sad',
    '4': 'miroka_disgust',
    '5': 'miroka_fear',
    '6': 'miroka_surprise',
    'a': 'miroka_interrogative',
    'b': 'miroka_focus',
    'c': 'miroka_thinking',
    'd': 'miroka_listening',
    'e': 'miroka_seeing',
    'f': 'miroka_boring',
}

PACKAGE_NAME = 'my_miroka_controller'
current_process = None
current_lock = threading.Lock()


def run_emotion(node_name: str) -> None:
    global current_process

    with current_lock:
        if current_process and current_process.poll() is None:
            print(f"{COLOR_YELLOW}[STOP] Termino l'emozione precedente...{COLOR_RESET}")
            current_process.terminate()
            try:
                current_process.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                current_process.kill()

        print(f"{COLOR_GREEN}[START] Avvio nodo ROS2: {node_name}{COLOR_RESET}")
        try:
            current_process = subprocess.Popen(
                ['ros2', 'run', PACKAGE_NAME, node_name],
                stdout=sys.stdout,
                stderr=sys.stderr
            )
        except Exception as e:
            print(f"{COLOR_RED}[ERRORE] Impossibile avviare {node_name}: {e}{COLOR_RESET}")


def main() -> None:
    print("=== Miroka Keyboard Controller ===")
    for k, v in EMOTION_MAP.items():
        print(f"  [{k}] → {v}")
    print("Digita il tasto e premi INVIO (Ctrl+C per uscire).\n")

    try:
        while True:
            cmd = input("Mirokai > ").strip().lower()
            if not cmd:
                continue

            if cmd in EMOTION_MAP:
                threading.Thread(
                    target=run_emotion,
                    args=(EMOTION_MAP[cmd],),
                    daemon=True
                ).start()
            else:
                print(f"{COLOR_RED}[TASTO NON VALIDO] Scegli tra: {list(EMOTION_MAP.keys())}{COLOR_RESET}")

    except (KeyboardInterrupt, EOFError):
        print(f"\n{COLOR_YELLOW}[EXIT] Chiusura controller...{COLOR_RESET}")
        with current_lock:
            if current_process and current_process.poll() is None:
                current_process.terminate()
                current_process.wait()
        sys.exit(0)


if __name__ == '__main__':
    main()
