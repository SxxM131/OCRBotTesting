"""
map_coords.py — Interactive Coordinate Mapping Helper
게임 내 각 아이템의 화면 좌표를 직접 클릭해서 기록하는 도구
"""

import json
import os
import time
import threading
import pyautogui
from pynput import mouse, keyboard

# ──────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────

OUTPUT_FILE = "coord_map.json"

# Full list of all 35 Korean item names in your game.
# Edit this list to match the actual words shown in your game.
ITEM_NAMES = [
    "사과",   # apple
    "책",     # book
    "의자",   # chair
    "시계",   # clock
    "컵",     # cup
    "개",     # dog
    "달걀",   # egg
    "부채",   # fan
    "물고기", # fish
    "꽃",     # flower
    "개구리", # frog
    "안경",   # glasses
    "모자",   # hat
    "열쇠",   # key
    "연",     # kite
    "램프",   # lamp
    "잎",     # leaf
    "편지",   # letter
    "자석",   # magnet
    "달",     # moon
    "버섯",   # mushroom
    "바늘",   # needle
    "양파",   # onion
    "연필",   # pencil
    "우산",   # umbrella
    "토끼",   # rabbit
    "반지",   # ring
    "가위",   # scissors
    "신발",   # shoe
    "별",     # star
    "태양",   # sun
    "나무",   # tree
    "우산2",  # umbrella2 (example duplicate type)
    "지갑",   # wallet
    "창문",   # window
    # ← add / edit until you have all 35 items
]


# ──────────────────────────────────────────
# STATE
# ──────────────────────────────────────────

coord_map: dict = {}      # {word: [x, y]}
current_index: int = 0    # which item we're currently waiting to click
done_event = threading.Event()


def load_existing(path: str) -> dict:
    """Resume from a partially saved file if it exists."""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"[+] Resumed — {len(data)} coordinates already saved.")
        return data
    return {}


def save(path: str, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def prompt_next():
    """Print instructions for the next item to map."""
    global current_index
    if current_index >= len(ITEM_NAMES):
        print("\n[✓] All items mapped!")
        done_event.set()
        return
    name = ITEM_NAMES[current_index]
    print(f"\n[{current_index + 1}/{len(ITEM_NAMES)}] Click on: '{name}'"
          f"  (Press ESC to quit and save progress)")


# ──────────────────────────────────────────
# MOUSE LISTENER
# ──────────────────────────────────────────

def on_click(x, y, button, pressed):
    global current_index

    # Only act on left-button press events
    if button != mouse.Button.left or not pressed:
        return
    if done_event.is_set():
        return

    name = ITEM_NAMES[current_index]
    coord_map[name] = [x, y]
    save(OUTPUT_FILE, coord_map)
    print(f"  Saved '{name}' → ({x}, {y})")

    current_index += 1
    prompt_next()

    if current_index >= len(ITEM_NAMES):
        done_event.set()


# ──────────────────────────────────────────
# KEYBOARD LISTENER  (ESC to quit early)
# ──────────────────────────────────────────

def on_press(key):
    if key == keyboard.Key.esc:
        print("\n[!] ESC pressed — saving and quitting.")
        save(OUTPUT_FILE, coord_map)
        done_event.set()


# ──────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────

def main():
    global coord_map, current_index

    print("=" * 55)
    print("  Coordinate Mapping Helper")
    print("=" * 55)
    print("Instructions:")
    print("  1. Switch to your game window.")
    print("  2. Click on each highlighted item when prompted.")
    print("  3. Press ESC at any time to save and quit.")
    print("  4. Re-run the script to resume where you left off.")
    print()

    # Load any previously saved coordinates
    coord_map = load_existing(OUTPUT_FILE)

    # Skip already-mapped items
    already = set(coord_map.keys())
    for i, name in enumerate(ITEM_NAMES):
        if name not in already:
            current_index = i
            break
    else:
        print("[✓] All items already mapped. Nothing to do.")
        return

    print(f"[*] Starting in 3 seconds — switch to the game now…")
    time.sleep(3)

    prompt_next()

    # Start listeners in non-blocking mode
    mouse_listener = mouse.Listener(on_click=on_click)
    key_listener = keyboard.Listener(on_press=on_press)

    mouse_listener.start()
    key_listener.start()

    # Wait until all items are mapped or user quits
    done_event.wait()

    mouse_listener.stop()
    key_listener.stop()

    print(f"\n[+] Saved {len(coord_map)} coordinates to '{OUTPUT_FILE}'")


if __name__ == "__main__":
    main()
