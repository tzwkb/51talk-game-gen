import os
import re
import subprocess
import tempfile
from config import MAX_FILE_SIZE_KB


def validate(filepath):
    results = []
    if not os.path.exists(filepath):
        return [("FAIL", f"File not found: {filepath}")]

    size_kb = os.path.getsize(filepath) / 1024
    if size_kb > MAX_FILE_SIZE_KB:
        results.append(("WARN", f"File size {size_kb:.0f}KB exceeds {MAX_FILE_SIZE_KB}KB limit"))
    else:
        results.append(("OK", f"File size: {size_kb:.1f}KB"))

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    checks = [
        ("<!DOCTYPE html>", "DOCTYPE"),
        ("<html", "html tag"),
        ("<body", "body tag"),
        ("<script", "script tag"),
        ("</html>", "closing html tag"),
    ]
    for token, desc in checks:
        tag = ("OK", f"Has {desc}") if token in content else ("FAIL", f"Missing {desc}")
        results.append(tag)

    externals = re.findall(r'(src|href)=["\']https?://', content)
    if externals:
        results.append(("WARN", f"Found {len(externals)} external URL(s)"))
    else:
        results.append(("OK", "No external dependencies"))

    if 'viewport' in content.lower():
        results.append(("OK", "Has viewport meta"))
    else:
        results.append(("WARN", "Missing viewport meta"))

    return results


def check_js_syntax(html_content):
    """Try node --check first, fallback to basic heuristics. Returns (ok:bool, error_msg:str)."""
    scripts = re.findall(r"<script[^>]*>(.*?)</script>", html_content, re.DOTALL)
    if not scripts:
        return True, ""

    js_code = "\n".join(scripts)

    # Try node --check
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, encoding='utf-8') as f:
            f.write(js_code)
            tmp = f.name
        result = subprocess.run(['node', '--check', tmp], capture_output=True, text=True, timeout=10)
        os.unlink(tmp)
        if result.returncode != 0:
            return False, result.stderr.strip()[:500]
        return True, ""
    except (FileNotFoundError, subprocess.TimeoutExpired):
        if os.path.exists(tmp):
            os.unlink(tmp)

    # Fallback: regex heuristics
    errors = []
    # Unclosed template literals
    if js_code.count('`') % 2 != 0:
        errors.append("Unclosed template literal (backtick)")
    # Unclosed regex
    unescaped_slash = re.findall(r'(?<!\\)/(?!/)', js_code)
    if len(unescaped_slash) % 2 != 0:
        errors.append("Possible unclosed regex")
    # Brace/bracket mismatch
    for a, b, name in [('{', '}', 'brace'), ('(', ')', 'paren'), ('[', ']', 'bracket')]:
        diff = js_code.count(a) - js_code.count(b)
        if diff != 0:
            errors.append(f"{name} mismatch ({diff:+d})")

    if errors:
        return False, "; ".join(errors)
    return True, ""


COMMON_BUGS = [
    (r'=\s*var\(--', 'CSS var() used in JavaScript (use getComputedStyle or hardcode color)'),
    (r'\.style\.\w+\s*=\s*var\(', 'CSS var() in JS style assignment'),
    (r'getElementById\([\'"]\w+[\'"]\)\.\w+\(', 'getElementById chained without null check'),
    (r'addEventListener\([\'"][\w-]+[\'"],\s*\(\)', 'addEventListener with arrow function missing event param in touch handler'),
    (r'innerHTML\s*\+=\s*', 'innerHTML += (use insertAdjacentHTML or rebuild, += corrupts event listeners)'),
    (r'setTimeout\(\s*function\s*\(\)', 'setTimeout with function() instead of arrow (this binding risk)'),
    (r'(?<!\.)preventDefault\(\)', 'preventDefault() possibly called on non-event object'),
    (r'const\s+\w+\s*=\s*document\.\w+\([\'"][\w-]+[\'"]\);\s*\n\s*\w+\.addEventListener', 'DOM element used without null guard'),
]
FIX_HINTS = {
    'CSS var() in JavaScript': 'Replace var(--xxx) with a hardcoded color value like "#FF0000" or use getComputedStyle(document.documentElement).getPropertyValue("--xxx").',
    'CSS var() in JS style assignment': 'Replace var(--xxx) with a hardcoded CSS value.',
    'getElementById chained without null check': 'Store element in a const, check if it exists before calling methods on it.',
    'addEventListener with arrow function missing event param': 'Add the event parameter: (e) => { ... } and call e.preventDefault() for touch events.',
    'innerHTML +=': 'Replace with insertAdjacentHTML("beforeend", ...) or rebuild entire innerHTML at once.',
    'setTimeout with function()': 'Use arrow function: setTimeout(() => { ... }, delay) to preserve this binding.',
    'preventDefault() possibly called on non-event object': 'Make sure the function receives an event object: (e) => { e.preventDefault(); ... }',
    'DOM element used without null guard': 'Add null check: if (!el) return; before using the element.',
}

def find_bugs(html_content):
    bugs = []
    for pattern, desc in COMMON_BUGS:
        if re.search(pattern, html_content, re.DOTALL):
            bugs.append(desc)
    return bugs

def build_fix_prompt(bugs, js_err=""):
    lines = [f"Your HTML has {len(bugs)} issue(s). Fix them ALL and return the complete corrected HTML.\n"]
    if js_err:
        lines.append(f"JS Syntax Error:\n```\n{js_err}\n```\n")
    for i, bug in enumerate(bugs, 1):
        hint = FIX_HINTS.get(bug, "Check the code logic.")
        lines.append(f"{i}. {bug}\n   Fix: {hint}\n")
    lines.append("Return ONLY the complete corrected HTML from <!DOCTYPE html> to </html>. No explanation.")
    return "\n".join(lines)


def has_quiz_smell(html_content):
    """Check if the game still looks like a quiz/test."""
    smells = []
    lower = html_content.lower()
    if 'correct!' in lower and 'wrong!' in lower:
        smells.append("Contains 'Correct!'/'Wrong!' text")
    if re.search(r'question\s+\d+\s*(of|/)', lower):
        smells.append("Contains 'Question X of Y' pattern")
    if html_content.count('progress-dot') > 3 or html_content.count('progressDot') > 3:
        smells.append("Uses progress dots")
    return smells


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
        print(f"[OK] Structure passed")
    return all_ok
