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

    prompt = f"""Generate a COMPLETE HTML game with these specifications:

Game Type: {gt['name']}
CEFR Level: {level}
Grammar Focus: {grammar}
Saudi Scenario: {scene}
{diff_inst}
{RESPONSIVE_DESIGN}
"""
    if level == "A1":
        prompt += CEFR_A1_ARABIC
    if custom:
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
