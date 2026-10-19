"""옷 추천 API 결과(카탈로그 id) → 캐릭터 그림 · 옷 아이콘 연결표 만들기 (M29).

  py build_map.py            카탈로그를 읽어 outfit_visual_map.json/.js · assets/ 를 다시 만든다

입력  = ../../03_기획자료/clothing-catalog_20261014/clothing-catalog.json (원본은 읽기만)
       캐릭터 파일 = ../최종_4계절_추천복장_20261013 · ../추가착장_4계절_20261014 · ../남성캐릭터_기본_20261014
출력  = outfit_visual_map.json (팀용) · outfit_visual_map.js (미리보기용, 같은 내용) · assets/icons/*.svg · assets/characters/*
검사  = 카탈로그 170개가 모두 아이콘 1개에 들어갔는지 · 없는 id·중복 id가 없는지 · 캐릭터 파일이 있는지
"""
import json, shutil, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = HERE.parent
CATALOG = WORK.parent / "03_기획자료" / "clothing-catalog_20261014" / "clothing-catalog.json"
FINAL = WORK / "최종_4계절_추천복장_20261013"
EXTRA = WORK / "추가착장_4계절_20261014"
MALE = WORK / "남성캐릭터_기본_20261014"
ASSETS = HERE / "assets"

# ---------- 아이콘 묶음: key → (이름, 카탈로그 id 목록) ----------
ICONS = {
    # 상의 (15) — 나시·끈나시·스포츠 탑은 아이콘 없음: 반팔/운동용 상의로 바꿔 보여 줌 (REPLACED 참고)
    "tee_short":   ("반팔 티",          "C001 C002 C074 C075 C006 C007 C072 C073"),
    "sport_tee":   ("기능성 티",        "C143 C144 C145 C146 C147 C148"),
    "collar_tee":  ("카라티",          "C003 C010"),
    "shirt_short": ("반팔 셔츠",        "C004 C005 C076"),
    "knit_thin":   ("여름 니트",        "C020 C021 C086 C087"),
    "tee_long":    ("긴팔 티",          "C008 C009 C078 C079"),
    "shirt":       ("셔츠",            "C011 C012 C013 C014 C080"),
    "check_shirt": ("체크·데님 셔츠",    "C015 C016"),
    "blouse":      ("블라우스",         "C081 C082 C083 C084"),
    "sweatshirt":  ("맨투맨",          "C017 C018 C085"),
    "hoodie":      ("후드티",          "C019"),
    "knit":        ("니트",            "C022 C023 C024 C088 C089"),
    "turtleneck":  ("터틀넥",          "C025 C026"),
    "knit_vest":   ("조끼·뷔스티에",     "C027 C077"),
    "pajama":      ("잠옷·라운지웨어",    "C158 C159 C160 C161 C162 C163 C164 C165 C166 C167 C168 C169 C170"),
    # 하의 (13)
    "shorts":      ("반바지",          "C028 C029 C030 C090 C091"),
    "sport_shorts": ("운동 반바지",      "C031 C149 C150"),
    "jeans":       ("청바지",          "C032 C033 C034 C035 C037 C092 C093"),
    "slacks":      ("슬랙스·면바지",     "C038 C039 C040 C041 C094"),
    "cargo":       ("카고 팬츠",        "C044"),
    "jogger":      ("조거·트레이닝",     "C045 C152 C153"),
    "warm_pants":  ("기모·울 바지",      "C036 C042 C043 C046"),
    "leggings":    ("레깅스",          "C151"),
    "skirt_mini":  ("미니 스커트",       "C095 C096"),
    "pleats":      ("플리츠 스커트",     "C101 C154"),
    "skirt_midi":  ("미디 스커트",       "C097 C098 C099 C103"),
    "skirt_long":  ("롱스커트",         "C100 C102 C104"),
    "leather_skirt": ("가죽 스커트",     "C105"),
    # 원피스류 (6)
    "dress_sleeveless": ("민소매 원피스", "C106 C108"),
    "dress_short": ("반팔 원피스",       "C107 C109 C111"),
    "dress_long":  ("롱·셔츠 원피스",    "C110 C112"),
    "dress_knit":  ("니트 원피스",       "C113 C114"),
    "bustier_dress": ("뷔스티에·멜빵치마", "C115 C116"),
    "jumpsuit":    ("점프수트·멜빵바지",  "C117 C118"),
    # 아우터 (15)
    "cardigan":    ("가디건",          "C052 C119 C120 C121"),
    "windbreaker": ("바람막이",         "C047 C155"),
    "zipup":       ("집업",            "C050 C051 C122 C123"),
    "jacket_casual": ("사파리·야상",     "C048 C049 C125"),
    "blazer":      ("블레이저",         "C053 C124"),
    "denim_jacket": ("데님 재킷",       "C054 C055"),
    "leather_jacket": ("가죽 재킷",     "C056 C126"),
    "blouson":     ("블루종·항공점퍼",   "C057 C058 C156"),
    "trench":      ("트렌치코트",       "C059"),
    "coat_short":  ("숏코트",          "C060 C062 C063 C129"),
    "coat_long":   ("롱코트",          "C061 C127 C128"),
    "light_padding": ("경량패딩·플리스", "C064 C065 C070 C133"),
    "padding":     ("패딩",            "C066 C067 C068 C131 C132 C136 C157"),
    "fur":         ("무스탕·퍼",        "C069 C130"),
    "rain":        ("레인재킷",        "C134 C135"),
    # 신발 (6) · 내의 (1)
    "sneakers":    ("운동화",          "C138"),
    "mesh_sneakers": ("통풍 운동화",     "C137"),
    "loafers":     ("로퍼",            "C139"),
    "boots":       ("앵클부츠",         "C140"),
    "rain_sneakers": ("방수 운동화",     "C141"),
    "winter_boots": ("방한화",          "C142"),
    "thermal":     ("따뜻한 상하의",     "C071"),
}

# 화면에 보일 짧은 이름 (동업자 「발열 내의 상하의, 접지력 있는 방수 방한화 이런거 너무 긴데 / 그냥 방한화 / 따뜻한 상하의 이런게나음」)
# 없는 id는 카탈로그 이름을 그대로 쓴다.
SHORT = {
    "C001": "반팔 티", "C002": "오버핏 반팔티", "C003": "카라티", "C004": "린넨 셔츠", "C008": "긴팔 티", "C009": "헨리넥 티",
    "C010": "얇은 카라티", "C014": "린넨 셔츠", "C016": "체크 셔츠", "C018": "맨투맨", "C020": "쿨니트", "C022": "니트",
    "C026": "케이블 니트", "C029": "버뮤다 팬츠", "C031": "운동 반바지", "C034": "일자 청바지", "C037": "쿨데님",
    "C038": "슬랙스", "C041": "린넨 바지", "C043": "울 팬츠", "C053": "블레이저", "C056": "라이더 재킷", "C057": "항공점퍼",
    "C061": "롱코트", "C064": "경량 패딩", "C065": "패딩 조끼", "C071": "따뜻한 상하의", "C074": "크롭 티", "C075": "루즈핏 티",
    "C076": "린넨 블라우스", "C078": "시스루 티", "C079": "오프숄더 티", "C086": "그물 니트", "C103": "울 스커트",
    "C104": "코듀로이 스커트", "C106": "끈 원피스", "C107": "반팔 원피스", "C122": "크롭 집업", "C126": "가죽 트렌치",
    "C133": "패딩 조끼", "C134": "레인재킷", "C135": "방풍 재킷", "C136": "다운 파카", "C140": "앵클부츠", "C142": "방한화",
    "C143": "기능성 반팔", "C144": "기능성 긴팔", "C145": "보온 긴팔", "C151": "레깅스", "C152": "트레이닝 바지",
    "C153": "기모 트레이닝", "C155": "바람막이", "C156": "보온 재킷", "C157": "방한 재킷", "C158": "잠옷 상의",
    "C159": "라운지 반팔", "C160": "잠옷 상의", "C161": "라운지 긴팔", "C162": "수면 상의", "C163": "잠옷 반바지",
    "C164": "잠옷 바지", "C165": "잠옷 바지", "C166": "라운지 바지", "C167": "수면 바지", "C168": "원피스 잠옷",
    "C169": "원피스 잠옷", "C170": "수면 원피스",
    # 노출이 많은 옷은 건전한 표시로 바꿈 (동업자 「나시,스포츠탑은 좀 권장하지 않음 / 건전해야해」)
    "C006": "시원한 반팔", "C007": "시원한 반팔", "C072": "시원한 반팔", "C073": "시원한 반팔",
    "C146": "운동용 반팔", "C147": "운동용 상의", "C148": "운동용 상의", "C106": "여름 원피스",
}
# 화면에 그대로 보여 주지 않고 바꿔 보여 주는 옷 → 백엔드에 「추천에서 빼 달라」고 요청할 목록
REPLACED = {"C006": "민소매 러닝", "C007": "나시", "C072": "스트랩 나시", "C073": "끈나시",
            "C146": "헬스 나시", "C147": "스포츠 브라", "C148": "요가 탑"}

# 아우터 아이콘 → 캐릭터를 고를 때의 아우터 종류
OUTER_KIND = {"cardigan": "THIN", "windbreaker": "THIN", "zipup": "THIN", "rain": "THIN",
              "jacket_casual": "JACKET", "blazer": "JACKET", "denim_jacket": "JACKET", "leather_jacket": "JACKET",
              "blouson": "JACKET", "trench": "JACKET", "light_padding": "JACKET",
              "coat_short": "COAT", "coat_long": "COAT", "padding": "PADDING", "fur": "PADDING"}

def build_items(catalog):
    by_id = {x["id"]: x for x in catalog["items"]}
    items, seen = {}, {}
    for key, (label, ids) in ICONS.items():
        for i in ids.split():
            if i not in by_id:
                sys.exit(f"없는 id: {i} ({key})")
            if i in seen:
                sys.exit(f"중복 id: {i} ({seen[i]}, {key})")
            seen[i] = key
    missing = sorted(set(by_id) - set(seen))
    if missing:
        sys.exit(f"아이콘이 없는 id {len(missing)}개: {missing}")
    for i, x in by_id.items():
        key = seen[i]
        lower = {"SHORTS": "SHORTS", "SKIRT": "SKIRT", "PANTS": "PANTS"}.get(x["bottomType"])
        if x["slot"] == "ONE_PIECE":
            lower = "PANTS" if key == "jumpsuit" else "ONEPIECE"   # 점프수트·멜빵바지 = 바지 모양
        items[i] = {"name": x["name"], "short": SHORT.get(i, x["name"]), "replaced": i in REPLACED, "slot": x["slot"], "icon": key,
                    "lower": lower, "outerKind": OUTER_KIND.get(key) if x["slot"] == "OUTER" else None,
                    "sport": x["style"] == "SPORT"}
    return items


# ---------- 추천 착장 세트 (목록 = outfit_sets.py) ----------
# status: ready = 그림 있음 · temp = 아직 없어 같은 계절(남성은 기본 캐릭터) 그림으로 임시 표시
SET_DIR = WORK / "착장세트_20261014"


def copy_sets(items):
    from outfit_sets import SETS, SEASON_KO, OCC_KO
    if (ASSETS / "characters").exists():
        shutil.rmtree(ASSETS / "characters")   # 예전 이름의 그림이 남지 않게
    (ASSETS / "characters").mkdir(parents=True)
    sets = {}
    for s in SETS:
        for slot, i in s["items"].items():
            if i not in items:
                sys.exit(f"세트 {s['key']}: 없는 id {i}")
        folder, stem = (WORK / s["src"][0], s["src"][1]) if s.get("src") else (SET_DIR, f"outfit_{s['key']}_340")
        files = {"poster": folder / f"{stem}_poster.png", "mp4": folder / f"{stem}.mp4", "gif": folder / f"{stem}.gif"}
        ready = all(p.exists() for p in files.values())
        out = {}
        if ready:
            for ext, p in files.items():
                dst = ASSETS / "characters" / (f"{s['key']}_340_poster.png" if ext == "poster" else f"{s['key']}_340.{ext}")
                shutil.copy2(p, dst)
                out[ext] = f"assets/characters/{dst.name}"
        sets[s["key"]] = {"gender": s["g"], "season": s["season"], "occasion": s["occ"],
                          "label": f"{'여' if s['g'] == 'F' else '남'} · {SEASON_KO[s['season']]} {OCC_KO[s['occ']]} · {s['label']}",
                          "items": s["items"], "status": "ready" if ready else "temp", **out}
    # 그림이 없는 세트 → 같은 성별·계절의 그림 있는 세트, 없으면 남성 기본 캐릭터
    base = MALE / "male_base_340_poster.png"
    shutil.copy2(base, ASSETS / "characters" / "male_base_340_poster.png")
    for k, v in sets.items():
        if v["status"] == "ready":
            continue
        alt = next((x for x in sets.values() if x["status"] == "ready" and x["gender"] == v["gender"] and x["season"] == v["season"]), None)
        if alt:
            v.update({e: alt[e] for e in ("poster", "mp4", "gif")})
        else:
            v["poster"] = "assets/characters/male_base_340_poster.png"
    return sets


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    items = build_items(catalog)
    sets = copy_sets(items)
    import icons_svg
    icon_dir = ASSETS / "icons"
    if icon_dir.exists():
        shutil.rmtree(icon_dir)        # 예전 묶음 이름의 아이콘이 남지 않게
    icon_dir.mkdir(parents=True)
    if set(icons_svg.KEYS) != set(ICONS):
        sys.exit(f"아이콘 그림과 묶음이 다름: {set(icons_svg.KEYS) ^ set(ICONS)}")
    for key in ICONS:
        (icon_dir / f"{key}.svg").write_text(icons_svg.svg(key), encoding="utf-8")
    import acc_svg
    from accessories import ACCESSORIES
    for key, _, _ in ACCESSORIES:
        (icon_dir / f"acc_{key}.svg").write_text(acc_svg.svg(key), encoding="utf-8")
    data = {
        "version": "2026-10-14",
        "source": "clothing-catalog.json v" + catalog.get("version", "?"),
        "howTo": "API outfits[0]와 sets(같은 성별)의 items를 비교해 점수가 가장 높은 세트의 그림을 보여 준다 (outfit_visual.js). "
                 "점수 = 아우터 종류·하의 모양 같음 각 4 · 운동/비 같음 각 3 · 칸별 아이콘 같음(상의·하의·원피스·아우터 2, 신발 1) · 완전히 같은 id +1. "
                 "아우터가 없거나 outerUsage가 WEAR가 아니면 아우터 없음. 칸마다 icons[items[id].icon]과 items[id].short(짧은 이름)를 보여 준다.",
        "notRecommended": {"note": "노출이 많은 옷 — 화면에는 반팔·운동용 상의로 바꿔 보여 준다. 백엔드 추천에서 빼 주기를 요청.",
                           "items": REPLACED},
        "icons": {k: {"label": v[0], "file": f"assets/icons/{k}.svg"} for k, v in ICONS.items()},
        "items": items,
        "sets": sets,
        "accessories": {
            "note": "소품 20개 + 추천 기준 초안(백엔드가 최종 기준을 정함). 카탈로그에는 아직 소품이 없음. "
                    "날씨 값으로 고르는 함수 = outfit_visual.js pickAccessories(weather, outfit, map). 미세먼지(pm)는 팀 자료가 없어 값이 올 때만 동작.",
            "items": {k: {"label": l, "rule": r, "file": f"assets/icons/acc_{k}.svg"} for k, l, r in ACCESSORIES},
        },
    }
    text = json.dumps(data, ensure_ascii=False, indent=1)
    (HERE / "outfit_visual_map.json").write_text(text, encoding="utf-8")
    (HERE / "outfit_visual_map.js").write_text("window.OUTFIT_VISUAL_MAP = " + text + ";\n", encoding="utf-8")
    for g in "FM":
        ss = [v for v in sets.values() if v["gender"] == g]
        print(f"{'여' if g == 'F' else '남'} 세트 {len(ss)} (그림 있음 {sum(v['status'] == 'ready' for v in ss)})")
    print(f"items {len(items)} (모두 아이콘 있음) · icons {len(ICONS)}")


if __name__ == "__main__":
    sys.path.insert(0, str(HERE))
    main()
