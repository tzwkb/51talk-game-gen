import os
import re
from config import MAX_FILE_SIZE_KB


def validate(filepath):
    results = []
    if not os.path.exists(filepath):
        return [("FAIL", f"File not found: {filepath}")]

    # 1. File size
    size_kb = os.path.getsize(filepath) / 1024
    if size_kb > MAX_FILE_SIZE_KB:
        results.append(("WARN", f"File size {size_kb:.0f}KB exceeds {MAX_FILE_SIZE_KB}KB limit"))
    else:
        results.append(("OK", f"File size: {size_kb:.1f}KB"))

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 2. HTML structure
    checks = [
        ("<!DOCTYPE html>", "DOCTYPE declaration"),
        ("<html", "html tag"),
        ("<body", "body tag"),
        ("<script", "script tag"),
        ("</html>", "closing html tag"),
    ]
    for token, desc in checks:
        if token in content:
            results.append(("OK", f"Has {desc}"))
        else:
            results.append(("FAIL", f"Missing {desc}"))

    # 3. No external dependencies
    externals = re.findall(r'(src|href)=["\']https?://', content)
    if externals:
        results.append(("WARN", f"Found {len(externals)} external URL(s) — may not be offline-safe"))
    else:
        results.append(("OK", "No external dependencies"))

    # 4. Basic JS sanity (look for obvious syntax issues)
    scripts = re.findall(r"<script[^>]*>(.*?)</script>", content, re.DOTALL)
    js_ok = True
    for i, s in enumerate(scripts):
        opens = s.count("{") - s.count("}")
        if opens != 0:
            results.append(("WARN", f"Script #{i+1}: brace mismatch ({opens:+d})"))
            js_ok = False
    if js_ok:
        results.append(("OK", "JS brace balance OK"))

    # 5. Responsive viewport
    if 'viewport' in content.lower():
        results.append(("OK", "Has viewport meta"))
    else:
        results.append(("WARN", "Missing viewport meta"))

    # 6. GAME_DATA
    if 'GAME_DATA' in content:
        results.append(("OK", "Has GAME_DATA object"))
    else:
        results.append(("WARN", "Missing GAME_DATA object"))

    return results


def print_validation(filepath):
    print(f"\n{'='*50}")
    print(f"Validating: {os.path.basename(filepath)}")
    print(f"{'='*50}")
    all_ok = True
    for status, msg in validate(filepath):
        icon = {"OK": "[OK]", "WARN": "[WARN]", "FAIL": "[FAIL]"}.get(status, "?")
        print(f"  {icon} {msg}")
        if status == "FAIL":
            all_ok = False
    if all_ok:
        print(f"\n[OK] Validation passed!")
    else:
        print(f"\n[FAIL] Validation failed — check FAIL items above.")
    return all_ok
