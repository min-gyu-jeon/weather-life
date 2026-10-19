"""규칙에 적힌 키와 파일을 납품 폴더에서 확인한다. py -I check_rules.py <static/weather>"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
rules = json.loads(Path(__file__).with_name("weather_character_rules.json").read_text(encoding="utf-8"))
if len(sys.argv) != 2:
    print("사용법: py -I check_rules.py <static/weather 폴더>")
    sys.exit(2)
root = Path(sys.argv[1])
map_file = root / "outfits" / "outfit_visual_map.json"
if not map_file.is_file():
    print(f"연결표를 찾지 못했습니다: {map_file}")
    sys.exit(2)
known_outfits = set(json.loads(map_file.read_text(encoding="utf-8"))["sets"])
known_activities = set(rules["activity"]["known_keys"])
face_stages = {row["stage"] for row in rules["sticker"]["first_match"]}
known_stickers = face_stages | {
    rules["sticker"]["rain"].replace("{stage}", stage) for stage in face_stages
} | {rules["sticker"]["sunny"]["stage"]}
known_laundry = set(rules["laundry"]["known_keys"])
outfits = set()
activities = set()

def add_gender_keys(target, entry):
    target.update(entry[g] for g in ("F", "M") if g in entry)

for rows in rules["outfit"]["daily_first_match"].values():
    for row in rows:
        add_gender_keys(outfits, row)
for by_season in rules["outfit"]["occasion_if_dry"].values():
    for entry in by_season.values():
        add_gender_keys(outfits, entry)
for entry in rules["rain"]["outfit_if_available"].values():
    add_gender_keys(outfits, entry)
for key, alternates in rules["outfit"]["variety_optional"].items():
    outfits.add(key)
    outfits.update(alternates)
add_gender_keys(activities, rules["rain"]["activity"])
add_gender_keys(activities, rules["activity"]["fine_dust"]["activity"])
add_gender_keys(activities, rules["activity"]["heat_wave"]["activity"])
for entry in rules["activity"]["by_season"].values():
    add_gender_keys(activities, entry)
for row in rules["activity"]["winter_first_match"]:
    add_gender_keys(activities, row)

unknown = [f"outfit:{key}" for key in outfits - known_outfits]
unknown += [f"activity:{key}" for key in activities - known_activities]
allowed_faces = {"comfort", "normal", "bad", "very_bad"}
allowed_stickers = allowed_faces | {f"umbrella_{stage}" for stage in allowed_faces} | {"sunglasses"}
unknown += [f"sticker:{key}" for key in known_stickers - allowed_stickers]
unknown += [f"laundry:{key}" for key in known_laundry - {"dry", "damp", "frozen"}]
if rules["laundry"]["frozen_if_temp_at_most"] != -5:
    unknown.append("laundry:frozen threshold must be -5℃")
if rules["activity"]["fine_dust"]["activity"] != rules["activity"]["heat_wave"]["activity"]:
    unknown.append("activity:fine-dust must keep home_ac/m_home_ac")
for kind, keys in (("activity", known_activities), ("sticker", known_stickers), ("laundry", known_laundry)):
    labels = rules.get("labels", {}).get(kind, {})
    unknown += [f"label:{kind}:{key}" for key in keys if not isinstance(labels.get(key), str) or not labels[key].strip()]
expected_kma = {
    "SKY": {"1": "맑음", "3": "구름많음", "4": "흐림"},
    "PTY": {"0": "없음", "1": "비", "2": "비/눈", "3": "눈", "4": "소나기",
            "5": "빗방울", "6": "빗방울눈날림", "7": "눈날림"},
}
if rules.get("kma_codes") != expected_kma:
    unknown.append("kma_codes:SKY/PTY mapping")
found = missing = 0

def check(kind, key, fields):
    global found, missing
    for format_name, pattern in fields.items():
        rel = pattern.replace("{key}", key)
        file = root / rel
        if file.is_file():
            print(f"✅ found {rel}")
            found += 1
        else:
            print(f"⬜ not made yet {rel}")
            missing += 1

for key in sorted(outfits & known_outfits):
    check("outfit", key, rules["files"]["outfit"])
for key in sorted(activities & known_activities):
    check("activity", key, rules["files"]["activity"])
for gender in ("f", "m"):
    for sticker in sorted(known_stickers):
        rel = rules["files"]["sticker"]["poster"].replace("{gender}", gender).replace("{sticker}", sticker)
        if (root / rel).is_file():
            print(f"✅ found {rel}")
            found += 1
        else:
            print(f"⬜ not made yet {rel}")
            missing += 1
for key in sorted(known_laundry):
    check("laundry", key, rules["files"]["laundry"])
for key in sorted(unknown):
    print(f"❌ unknown key {key}")
print(f"합계: ✅ found {found}파일 · ⬜ not made yet {missing}파일 · ❌ unknown key {len(unknown)}개")
sys.exit(1 if unknown else 0)
