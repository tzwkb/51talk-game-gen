import os
import re
from config import PROMPTS_DIR

GAME_TYPES = {
    "1": {"name": "Coffee Match / 咖啡配对大师", "template": "click_choose", "level": "A1", "grammar": "Verb 'to be', basic greetings", "scene": "Barn's Cafe"},
    "2": {"name": "Daily Match / 我的利雅得日常", "template": "click_choose", "level": "A1", "grammar": "Present Simple, time expressions", "scene": "Al Baik / Football / Weather"},
    "3": {"name": "Weekend Rewind / 周末时光机", "template": "drag_sort", "level": "A2", "grammar": "Past Simple, Future (going to)", "scene": "Boulevard World"},
    "4": {"name": "Kabsa King / 沙特美食推荐王", "template": "click_choose", "level": "A2", "grammar": "Comparatives, 'should'", "scene": "Najd Village / Pharmacy"},
    "5": {"name": "Careem Fix-it / Careem救急", "template": "swipe_card", "level": "B1", "grammar": "Conditionals, Present Perfect", "scene": "Careem / Sanaiya"},
    "6": {"name": "Boulevard Map / 我的林荫地图", "template": "click_choose", "level": "B1", "grammar": "Relative clauses, opinion", "scene": "Boulevard World"},
    "7": {"name": "Whisper to CEO / 传话给CEO", "template": "click_choose", "level": "B2", "grammar": "Reported speech, debate", "scene": "Office / Business Meeting"},
    "8": {"name": "Diplomatic Deal / 外交式谈判", "template": "dialogue_stage", "level": "C1", "grammar": "Causatives, inversion, hedging", "scene": "Real Estate / Pitch / Social"},
    "9": {"name": "Rhetorical Arena / 修辞竞技场", "template": "dialogue_stage", "level": "C1", "grammar": "Rhetorical devices, advanced connectors", "scene": "TED Talk / Debate"},
    "10": {"name": "Word Catch / 单词捕手", "template": "word_catch", "level": "A1", "grammar": "Vocabulary recognition", "scene": "Arcade / Game Center"},
    "11": {"name": "Memory Flip / 记忆翻牌", "template": "memory_flip", "level": "A2", "grammar": "Word-meaning association", "scene": "Card Table / Majlis"},
    "12": {"name": "Spell Builder / 拼词积木", "template": "spell_build", "level": "B1", "grammar": "Spelling and word formation", "scene": "Building Blocks / Workshop"},
    "13": {"name": "AI Free Invent / AI自由发明", "template": "creative", "level": "A2", "grammar": "Any — AI decides", "scene": "Any — AI decides"},
}

CEFR_LEVELS = ["A1", "A2", "B1", "B2", "C1"]

CEFR_DIFFICULTY = {
    "A1": "- Questions: 2-3 options per question, distractors obviously different in topic\n- Sentences: max 6 words per option, very simple vocabulary\n- UI: large text, category icons always shown, no time pressure\n- Feedback: simple encouragement, repeat correct answer",
    "A2": "- Questions: 3 options per question, distractors from related topics but clearly different\n- Sentences: max 8 words per option, common vocabulary\n- UI: standard text size, simple pacing",
    "B1": "- Questions: 3-4 options, distractors same topic but different grammar/meaning\n- Sentences: max 12 words, natural vocabulary\n- UI: standard pacing, auto-advance 1.5s",
    "B2": "- Questions: 3-4 options, distractors grammatically similar but nuanced difference\n- Sentences: natural length, academic/professional vocabulary\n- UI: subtle hint after 10s on harder questions",
    "C1": "- Questions: 4 options, distractors are subtle -- grammatically correct but contextually or stylistically inferior\n- Sentences: natural, complex structures, sophisticated vocabulary\n- UI: no category hints, expects reading comprehension, 10s glow hint on final questions",
}

RESPONSIVE_DESIGN = """
RESPONSIVE DESIGN (PC + Mobile — MUST support both):
- Mobile (< 768px): full-width, touch-optimized, 48px+ touch targets, bottom-aligned controls for thumb reach
- Tablet (768-1024px): centered container ~600px, comfortable spacing
- PC (> 1024px): centered container max-width 800px, larger cards/text, mouse hover effects, optional keyboard shortcuts
- Use CSS media queries for all 3 breakpoints. Use min-width or max-width consistently.
- Landscape orientation: game must work in landscape — rearrange layout to horizontal if needed (side-by-side instead of stacked)
- PC extra: subtle hover states on interactive elements, cursor:pointer, keyboard hints visible
- Never hardcode mobile-only assumptions (like "player holds phone portrait"). Game must adapt.

MOBILE GAME FEEL (Phone-native experience):
- Thumb Zone: place primary interactive elements in the bottom 60% of screen. Top 40% = display/info only. Player should never need to stretch their thumb.
- Gesture-First: swipe between screens (not just tap buttons). Swipe left/right for navigation. Swipe up for details.
- Tilt Optional: if game involves movement, support DeviceOrientation as alternative control. Fallback to touch if unavailable.
- Haptic Patterns: use navigator.vibrate with distinct patterns for different events:
  - Tap/select: [10]
  - Success: [15, 30, 15]
  - Combo milestone: [20, 40, 20, 40, 20]
  - Stage complete: [30, 50, 30, 50, 30]
  - Failure: [50, 50]
- No UI elements in top 20% of screen (hard to reach one-handed)
- Pull-to-refresh or pull-down gesture to show info/menu (optional)
- Bottom sheet for any secondary actions (settings, info, quit)
"""

PREFLIGHT_CHECKLIST = """
PRE-FLIGHT BUG CHECK — Before returning HTML, verify ALL of these:
1. NO CSS custom properties (var(--xxx)) in JavaScript code — use hardcoded values in JS
2. ALL DOM queries (getElementById, querySelector) have null checks before use
3. ALL touch event handlers call e.preventDefault() to prevent page scroll
4. NO innerHTML += — rebuild entire string or use insertAdjacentHTML
5. ALL setTimeout/setInterval use arrow functions, not function()
6. ALL addEventListener callbacks accept event param for touch/mouse handlers
7. Script runs AFTER DOM is ready (DOMContentLoaded or script at end of body)
8. NO trailing commas in JSON-like objects that break older parsers
"""

SESSION_RULES = """
SESSION RULES — Game duration and ending (MOST IMPORTANT):
- The game has exactly 8 rounds/items/customers/words. NOT infinite. NOT timer-based. 8 rounds, then STOP.
- After round 8: immediately show results screen. No "Continue?", no "Next wave", no loop.
- Each round must feel distinct: round 7 says "Almost there!", round 8 says "Last one!" with visual emphasis.
- Progress MUST be visible at all times: "5/8 served" or a tray with 8 slots filling up.
- NO countdown timer (anxiety). NO "game over" with failure. Player always reaches the end.
- If using free-play mechanics (catching, tapping items), show total items needed (e.g., "Catch 8 more" counting down to 0).
- The game loop MUST check: if roundsCompleted >= 8 → endGame(). Never skip this check.
- End screen MUST include:
  1. "You did it!" completion feeling, not score-focused
  2. What the player LEARNED: 3-5 words they encountered, English + Arabic, like collected treasure cards
  3. Visual gallery: all 8 items/achievements displayed beautifully
  4. Star rating that rewards effort (even low accuracy = 2+ stars)
  5. "Play Again" button + gentle CTA
- Wrong = "Now you know!" not "Wrong!".
"""

GAMIFICATION_PUSH = """
GAMIFICATION — Make it feel like a REAL mobile game:
- Micro-Rewards: small celebration every 2-3 successful actions (sparkle burst, sound chime, mascot bounce), not just at the end
- Streak Fire: visual intensity scales with consecutive success — 2x=subtle glow, 4x=particles, 6x=screen border rainbow, 8x=full-screen celebration
- Personal Best: detect when player beats their stored high score → extra celebration with "New Record!" badge + unique animation
- Unlock Preview: show what can be unlocked next (grayed-out badge, "3 more to unlock" hint) to drive replay
- Score Inflation: make numbers feel big and satisfying. 1 correct = +100 not +10. Show with bounce + float animation.
- Screen Shake: subtle CSS transform shake on big moments (combo milestone, new record, stage complete). 2-4px, 200ms.
- Idle Animation: if player hasn't interacted for 3 seconds, mascot does a cute idle animation (bounce/wave/blink) to invite interaction
"""

CEFR_A1_ARABIC = """
ARABIC BILINGUAL MODE (A1 ONLY):
- Every English word/phrase in questions, options, and feedback MUST include its Arabic translation in parentheses.
  Example: "One latte, please (واحد لاتيه، من فضلك)"
- Option labels: show both English AND Arabic, e.g. "Latte (لاتيه)"
- Feedback messages: bilingual, e.g. "Perfect! (ممتاز;)"
- End screen: title and message in both languages
- Always set dir=\"auto\" on elements containing Arabic text for proper RTL rendering
- Use a slightly smaller font for Arabic text (2px less than English) for visual harmony
"""

def load_system_prompt(template_name):
    path = os.path.join(PROMPTS_DIR, f"{template_name}.txt")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Prompt not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def build_user_prompt(game_type, level, grammar, scene, custom=""):
    gt = GAME_TYPES[game_type]
    diff_inst = CEFR_DIFFICULTY.get(level, "")

    if game_type == "13" and custom:
        creative_direction = f"""
## CREATIVE DIRECTION (HIGHEST PRIORITY — follow this first)
The player requested: **{custom}**
Build the entire game around this vision. Genre, core mechanic, visual style, and theme must all serve this direction. Every design decision should reinforce it.
"""
    else:
        creative_direction = ""

    prompt = f"""Generate a COMPLETE HTML game with these specifications:

Game Type: {gt['name']}
CEFR Level: {level}
Grammar Focus: {grammar}
Saudi Scenario: {scene}
{creative_direction}{diff_inst}
{RESPONSIVE_DESIGN}
{GAMIFICATION_PUSH}
{PREFLIGHT_CHECKLIST}
{SESSION_RULES}
"""
    if level == "A1":
        prompt += CEFR_A1_ARABIC
    if custom and game_type != "13":
        prompt += f"\nAdditional Requirements: {custom}"

    prompt += "\n\nOutput ONLY the complete HTML code, starting with <!DOCTYPE html>."
    return prompt

def extract_html(response_text):
    text = response_text.strip()
    m = re.search(r"```(?:html)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if m:
        text = m.group(1).strip()
    text = re.sub(r'^```\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    if not text.startswith("<!DOCTYPE html>"):
        idx = text.find("<!DOCTYPE html>")
        if idx > 0:
            text = text[idx:]
    return text
