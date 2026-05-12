#!/usr/bin/env python3
"""HTML Game Generator — AI-powered Saudi English mini-game factory."""

import os
import sys
import datetime
from openai import OpenAI

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import config
from templates import GAME_TYPES, CEFR_LEVELS, load_system_prompt, build_user_prompt, extract_html
from validator import print_validation


def print_banner():
    print("""
+==========================================+
|  Saudi English Game Generator           |
|  沙特成人英语 HTML 小游戏自动生产         |
+==========================================+
      """)

def interactive():
    import random
    print_banner()

    # Game type: random
    choice = random.choice(list(GAME_TYPES.keys()))
    gt = GAME_TYPES[choice]

    # CEFR Level
    print(f"CEFR Levels: {', '.join(CEFR_LEVELS)}")
    level = input(f"CEFR Level [random]: ").strip().upper()
    if level not in CEFR_LEVELS:
        level = random.choice(CEFR_LEVELS)
        print(f"  → {level}")

    # Extra
    custom = input("Extra requirements [none]: ").strip()

    # Confirm
    print(f"""
+==========================================+
|  Game:    {gt['name'][:35]:<35} |
|  Level:   {level:<35} |
+==========================================+
""")
    confirm = input("Generate? [Y/n]: ").strip().lower()
    if confirm and confirm not in ('y', 'yes'):
        print("Cancelled."); sys.exit(0)

    generate(choice, level, gt['grammar'], gt['scene'], custom)


def generate(game_type, level, grammar, scene, custom=""):
    gt = GAME_TYPES[game_type]
    template_name = gt['template']

    print(f"\n[LOAD] Prompt={template_name}, Level={level}")

    system_prompt = load_system_prompt(template_name)
    user_prompt = build_user_prompt(game_type, level, grammar, scene, custom)

    print(f"[AI] Calling {config.MODEL} (temp={config.TEMPERATURE})...")
    client = OpenAI(api_key=config.API_KEY, base_url=config.BASE_URL)

    try:
        response = client.chat.completions.create(
            model=config.MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=config.MAX_TOKENS,
            temperature=config.TEMPERATURE,
        )
    except Exception as e:
        print(f"[FAIL] API call failed: {e}")
        sys.exit(1)

    raw = response.choices[0].message.content
    html = extract_html(raw)

    if not html or len(html) < 200:
        print("[FAIL] AI returned insufficient content. Debug saved.")
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
        with open(os.path.join(config.OUTPUT_DIR, "debug.txt"), "w", encoding="utf-8") as f:
            f.write(raw)
        sys.exit(1)

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = gt['name'].split(" / ")[0].replace(" ", "_").replace("'", "").lower()
    filename = f"{safe_name}_{level}_{ts}.html"
    filepath = os.path.join(config.OUTPUT_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(filepath) / 1024
    print(f"\n[DONE] Generated: {filepath}")
    print(f"   Size: {size_kb:.1f}KB")
    print_validation(filepath)
    return filepath


if __name__ == "__main__":
    interactive()
