#!/usr/bin/env python3
"""HTML Game Generator — AI-powered Saudi English mini-game factory."""

import os
import sys
import datetime
from openai import OpenAI

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

import config
from templates import CEFR_LEVELS, load_system_prompt, build_user_prompt, extract_html
from validator import print_validation, check_js_syntax, has_quiz_smell, find_bugs, build_fix_prompt


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

    print(f"CEFR Levels: {', '.join(CEFR_LEVELS)}")
    level = input("CEFR Level [random]: ").strip().upper()
    if level not in CEFR_LEVELS:
        level = random.choice(CEFR_LEVELS)
        print(f"  -> {level}")

    print("\n提示词示例: 「像flappy bird的飞行游戏」「neon赛博朋克消除」「沙漠跑酷」")
    print("留空 → AI自由发挥")
    custom = input("风格/玩法提示 [留空=自由]: ").strip()

    mode_label = f"Custom: {custom[:35]}" if custom else "Free Invention"
    print(f"""
+==========================================+
|  AI will invent a brand new game.        |
|  Level: {level:<33}|
|  Mode:  {mode_label:<33}|
+==========================================+
""")
    confirm = input("Generate? [Y/n]: ").strip().lower()
    if confirm and confirm not in ('y', 'yes'):
        print("Cancelled."); sys.exit(0)

    generate(level, custom)


def generate(level, custom=""):
    system_prompt = load_system_prompt("creative")
    user_prompt = build_user_prompt("13", level, "AI decides everything", "AI decides", custom)

    if custom:
        print(f"\n[AI] Generating game for {level} — Style: {custom[:60]}...")
    else:
        print(f"\n[AI] Inventing a new game for {level} (free invention)...")
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

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
        {"role": "assistant", "content": raw},
    ]

    for attempt in range(3):
        js_ok, js_err = check_js_syntax(html)
        quiz_smells = has_quiz_smell(html)
        bugs = find_bugs(html)

        if js_ok and not quiz_smells and not bugs:
            print(f"[CHECK] No issues (attempt {attempt+1})")
            break

        print(f"[FIX] Attempt {attempt+2}/3:")
        if not js_ok: print(f"  JS: {js_err[:100]}")
        for b in bugs: print(f"  BUG: {b}")
        for q in quiz_smells: print(f"  QUIZ: {q}")

        fix_prompt = build_fix_prompt(bugs, js_err if not js_ok else "")
        if quiz_smells:
            fix_prompt += f"\n\nAlso fix quiz-like elements: {'; '.join(quiz_smells)}"
        messages.append({"role": "user", "content": fix_prompt})

        try:
            fix_resp = client.chat.completions.create(
                model=config.MODEL,
                messages=messages,
                max_tokens=config.MAX_TOKENS,
                temperature=0.3,
            )
        except Exception as e:
            print(f"[FAIL] Fix API call failed: {e}")
            break

        fixed_raw = fix_resp.choices[0].message.content
        fixed_html = extract_html(fixed_raw)
        if fixed_html and len(fixed_html) > 200:
            html = fixed_html
            messages.append({"role": "assistant", "content": fixed_raw})
        else:
            print("[FIX] Fix returned invalid content, keeping original")
            break

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"game_{level}_{ts}.html"
    filepath = os.path.join(config.OUTPUT_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html)

    size_kb = os.path.getsize(filepath) / 1024
    js_ok, js_err = check_js_syntax(html)
    print(f"\n[DONE] {filepath}")
    print(f"   Size: {size_kb:.1f}KB | JS: {'OK' if js_ok else js_err[:60]}")
    print_validation(filepath)
    return filepath


if __name__ == "__main__":
    interactive()
