"""weather_character_rules.json → weather_character_rules.js (10-15 Claude)

왜: 파일을 더블클릭해서 연 화면(file://)에서는 Chrome이 다른 폴더의 JSON을 fetch로 못 읽는다.
    (동업자 10-15 「야외활동 아직 제작전으로나옴」 · 「표정 안바뀜」 = 기준표가 안 읽혀서 생긴 일)
    <script src>로 읽는 JS는 더블클릭으로 열어도 된다 → 같은 내용을 JS로도 둔다.

규칙: JSON이 원본이다. JSON을 고친 뒤에는 꼭  py -I make_rules_js.py  를 다시 돌린다.
"""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
src = HERE / "weather_character_rules.json"
dst = HERE / "weather_character_rules.js"

rules = json.loads(src.read_text(encoding="utf-8"))
body = json.dumps(rules, ensure_ascii=False, indent=2)
dst.write_text(
    "// 자동 생성 파일 — 고치지 마세요. 원본 = weather_character_rules.json → py -I make_rules_js.py\n"
    "// 더블클릭으로 연 화면(file://)에서도 기준표를 읽게 하려고 JSON과 같은 내용을 담아 둠.\n"
    f"window.WEATHER_CHARACTER_RULES = {body};\n",
    encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")
print(f"ok → {dst.name} ({dst.stat().st_size:,} bytes)")
