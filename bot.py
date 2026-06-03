"""
bot.py — Hidden Object Game Auto-Clicker Bot
Mac 전용 / Korean OCR + coordinate matching
"""

import time
import random
import json
import os
import mss
import easyocr
import pyautogui
import numpy as np
from PIL import Image

# ──────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────

# Path to the coordinate map built with map_coords.py
COORD_MAP_FILE = "coord_map.json"

# Screen region to capture (bottom word bar of the game window)
# Adjust these values to match where the Korean words appear on your screen.
# Format: {"top": y, "left": x, "width": w, "height": h}  (all in pixels)
CAPTURE_REGION = {
    "top": 1300,    # ← adjust: top edge of the word bar
    "left": 400,    # ← adjust: left edge
    "width": 1200,  # ← adjust: width of the word bar
    "height": 120,  # ← adjust: height of the word bar
}

# OCR confidence threshold — detections below this are skipped
OCR_CONFIDENCE_THRESHOLD = 0.4

# Delay range (seconds) between each click to mimic human behaviour
CLICK_DELAY_MIN = 0.3
CLICK_DELAY_MAX = 0.8

# Total clicks expected per round
CLICKS_PER_ROUND = 26

# Startup grace period so you can alt-tab to the game
STARTUP_DELAY = 3


# ──────────────────────────────────────────
# LOAD COORDINATE DICTIONARY
# ──────────────────────────────────────────

def load_coord_map(path: str) -> dict:
    """Load the {word: [x, y]} dictionary from a JSON file."""
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Coordinate map not found: {path}\n"
            "Run map_coords.py first to build it."
        )
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"[+] Loaded {len(data)} items from coordinate map.")
    return data


# ──────────────────────────────────────────
# SCREEN CAPTURE
# ──────────────────────────────────────────

def capture_word_bar(region: dict) -> np.ndarray:
    """Capture the bottom word bar region and return as an RGB numpy array."""
    with mss.mss() as sct:
        screenshot = sct.grab(region)
    # mss returns BGRA; convert to RGB for EasyOCR
    img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
    return np.array(img)


# ──────────────────────────────────────────
# OCR
# ──────────────────────────────────────────

def ocr_words(reader: easyocr.Reader, image: np.ndarray) -> list[str]:
    """
    Run EasyOCR on the captured image.
    Returns a list of Korean words that exceed the confidence threshold.
    """
    results = reader.readtext(image, detail=1)  # detail=1 → [bbox, text, confidence]
    words = []
    for (bbox, text, confidence) in results:
        text = text.strip()
        if not text:
            continue
        if confidence < OCR_CONFIDENCE_THRESHOLD:
            print(f"  [skip] '{text}' confidence={confidence:.2f} (below threshold)")
            continue
        print(f"  [ocr]  '{text}' confidence={confidence:.2f}")
        words.append(text)
    return words


# ──────────────────────────────────────────
# CLICKING
# ──────────────────────────────────────────

def click_item(word: str, coord_map: dict) -> bool:
    """
    Look up the word in the coordinate map and click it.
    Returns True if the word was found and clicked.
    """
    if word not in coord_map:
        print(f"  [miss] '{word}' not found in coordinate map")
        return False

    x, y = coord_map[word]
    # Small random jitter (±5 px) so clicks don't land on the exact pixel every time
    x += random.randint(-5, 5)
    y += random.randint(-5, 5)

    pyautogui.click(x, y)
    print(f"  [click] '{word}' → ({x}, {y})")
    return True


# ──────────────────────────────────────────
# MAIN LOOP
# ──────────────────────────────────────────

def run_bot():
    print(f"[*] Starting in {STARTUP_DELAY}s — switch to the game window now…")
    time.sleep(STARTUP_DELAY)

    # Initialise EasyOCR once (slow first call downloads model weights)
    print("[*] Initialising EasyOCR (Korean)…")
    reader = easyocr.Reader(["ko"], gpu=False)

    # Load pre-mapped coordinates
    coord_map = load_coord_map(COORD_MAP_FILE)

    clicks_done = 0

    print(f"[*] Bot running — target: {CLICKS_PER_ROUND} clicks per round\n")

    while clicks_done < CLICKS_PER_ROUND:
        # 1. Capture the word bar
        image = capture_word_bar(CAPTURE_REGION)

        # 2. OCR — extract visible Korean words
        words = ocr_words(reader, image)
        if not words:
            print("  [warn] No words detected, retrying…")
            time.sleep(0.5)
            continue

        # 3. For each detected word, try to click the matching object
        for word in words:
            if clicks_done >= CLICKS_PER_ROUND:
                break

            clicked = click_item(word, coord_map)
            if clicked:
                clicks_done += 1
                print(f"  [{clicks_done}/{CLICKS_PER_ROUND}] clicked")
                # Randomised human-like delay between clicks
                delay = random.uniform(CLICK_DELAY_MIN, CLICK_DELAY_MAX)
                time.sleep(delay)

        # Brief pause before re-scanning for the next word
        time.sleep(0.3)

    print(f"\n[✓] Round complete — {clicks_done} items clicked.")


if __name__ == "__main__":
    run_bot()
