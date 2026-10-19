"""weather-unit 의 static/weather/outfits/README.md 만들기 (세트·아이콘·소품 표는 outfit_visual_map.json 에서 자동).

  py make_readme.py <weather-unit 경로>
"""
import json, sys
from pathlib import Path

repo = Path(sys.argv[1])
out = repo / "static" / "weather" / "outfits"
m = json.loads((out / "outfit_visual_map.json").read_text(encoding="utf-8"))
sys.stdout.reconfigure(encoding="utf-8")
KO = {"spring": "봄", "summer": "여름", "autumn": "가을", "winter": "겨울"}
OCC = {"DAILY": "일상", "OFFICE": "출근", "EXERCISE": "운동", "RAIN": "비"}
SLOT = {"outer": "아우터", "top": "상의", "onePiece": "원피스", "bottom": "하의", "shoes": "신발"}


def set_table(g):
    rows = ["| 계절 | 그림 | 세트 이름(key) | 용도 | 옷 (카탈로그 id) |", "|---|---|---|---|---|"]
    for k, s in m["sets"].items():
        if s["gender"] != g:
            continue
        clothes = " · ".join(f"{m['items'][i]['short']} `{i}`" for sl, i in s["items"].items())
        name = s["label"].split("· ", 2)[-1]
        rows.append(f"| {KO[s['season']]} | <img src=\"{s['poster']}\" width=\"90\"> | **{name}**<br>`{k}` | {OCC[s['occasion']]} | {clothes} |")
    return "\n".join(rows)


def icon_table():
    count = {}
    for i, it in m["items"].items():
        count.setdefault(it["icon"], []).append(it["short"])
    rows, cells = [], []
    for k, ic in m["icons"].items():
        cells.append(f"<img src=\"{ic['file']}\" width=\"44\"><br>**{ic['label']}**<br>`{k}` · {len(count.get(k, []))}개")
    for i in range(0, len(cells), 7):
        rows.append("| " + " | ".join(cells[i:i + 7]) + " |")
    head = "| " + " | ".join([" "] * 7) + " |\n|" + "---|" * 7
    return head + "\n" + "\n".join(rows)


def acc_table():
    rows = ["| 아이콘 | 소품 | key | 추천 기준 (초안) |", "|---|---|---|---|"]
    for k, a in m["accessories"]["items"].items():
        rows.append(f"| <img src=\"{a['file']}\" width=\"40\"> | **{a['label']}** | `{k}` | {a['rule']} |")
    return "\n".join(rows)


nf = sum(1 for s in m["sets"].values() if s["gender"] == "F")
nm = len(m["sets"]) - nf
text = f"""# 옷 추천 → 캐릭터 · 옷 아이콘 · 소품 (outfits)

백엔드가 날씨(기온 · 하늘 · 강수 · 습도 등)를 보고 **옷 카탈로그(`clothing-catalog.json`)에서 옷을 골라 보내면**,
이 폴더의 파일로 화면에 **① 그 옷차림의 캐릭터 그림 ② 옷 아이콘과 이름 ③ 챙길 소품**을 보여 줍니다.
날씨 판단은 백엔드가 하고, 여기서는 **그림만 고릅니다**. 모든 그림은 미리 만들어 두었으므로 어느 컴퓨터에서도 그대로 동작합니다.

- 착장 세트(캐릭터 그림) **{len(m['sets'])}벌** = 여 {nf} · 남 {nm} — 각각 340×340 정지 PNG · MP4 · GIF
- 옷 아이콘 **{len(m['icons'])}개** — 카탈로그 옷 **{len(m['items'])}개 전부**가 아이콘 1개에 연결됨
- 소품 아이콘 **{len(m['accessories']['items'])}개** + 추천 기준 초안
- 최종본: 2026-10-14

## 1. 폴더 구성

```
static/weather/outfits/
├─ outfit_visual_map.json   ← 연결표 (옷 id → 아이콘·짧은 이름 / 착장 세트 / 소품)  ※ 팀은 이 파일을 씀
├─ outfit_visual.js         ← 고르는 함수 2개: pickOutfitVisual · pickAccessories (순수 JS, 라이브러리 없음)
├─ outfit_visual_map.js     ← JSON과 같은 내용 (서버 없이 HTML을 파일로 열 때용 — 미리보기 페이지가 씀)
└─ assets/
   ├─ characters/   <세트 key>_340_poster.png · _340.mp4 · _340.gif   ({len(m['sets'])}벌 × 3)
   └─ icons/        <아이콘 key>.svg (옷 {len(m['icons'])}) · acc_<소품 key>.svg (소품 {len(m['accessories']['items'])})
```

`weather-life` 프로젝트에는 이 폴더를 통째로 `src/main/resources/static/weather/outfits/`에 복사하면 됩니다.
JSON 안의 그림 경로(`assets/...`)는 이 폴더 기준 상대 경로입니다.

## 2. 화면에 넣는 법

### 2-1. 백엔드 결과 → 캐릭터 + 옷 아이콘

백엔드 결과 예시(의상 추천 API):
```json
{{"outfits":[{{"structure":"SEPARATES",
  "top":{{"id":"C019","name":"후드 티셔츠","slot":"TOP"}}, "bottom":{{"id":"C045","name":"조거 팬츠","slot":"BOTTOM"}},
  "onePiece":null, "innerTop":null, "outer":{{"id":"C058","name":"블루종","slot":"OUTER"}}, "outerUsage":"WEAR",
  "baseLayer":null, "shoes":{{"id":"C138","name":"기본 운동화","slot":"SHOES"}}, "accessories":[] }}]}}
```

```html
<script src="/weather/outfits/outfit_visual.js"></script>
<script type="module">   // module = 맨 위에서 await 사용 가능
  const BASE = "/weather/outfits/";
  const map = await (await fetch(BASE + "outfit_visual_map.json")).json();
  const api = await (await fetch("/api/...")).json();          // 백엔드 결과
  const r = pickOutfitVisual(api.outfits[0], "F", map);        // 성별 "F" | "M"

  // ① 캐릭터 (추천 복장 칸 — 정지 그림 권장, 영상이 필요하면 r.set.mp4 / r.set.gif)
  img.src = BASE + r.set.poster;   img.alt = r.set.label;

  // ② 착장 구성 (칸마다 아이콘 + 짧은 이름)
  r.icons.forEach(x => addRow(BASE + x.iconFile, x.name));   // x.name = 짧은 이름(예: 방한화), x.fullName = 카탈로그 이름
</script>
```

반환값 `r`:
| 값 | 뜻 |
|---|---|
| `r.setKey`, `r.set` | 고른 착장 세트 (`label` · `poster` · `mp4` · `gif` · `season` · `occasion`) |
| `r.icons[]` | 칸별 `slot` · `slotLabel` · `id` · `name`(짧은 이름) · `fullName` · `iconKey` · `iconFile` · `usage`(아우터를 입는지/챙기기만 하는지) |
| `r.score` | 얼마나 비슷한지 (높을수록 비슷) |

**세트 고르는 법**: 같은 성별 세트 중 백엔드 결과와 **옷이 가장 많이 겹치는** 세트를 고릅니다.
아우터 종류(없음 · 얇은 겉옷 · 재킷 · 코트 · 패딩)와 하의 모양(반바지 · 바지 · 스커트 · 원피스)이 같으면 각 4점,
운동복 · 비 대비 옷이 같으면 각 3점, 칸별 아이콘이 같으면 2점(신발 1점), 같은 옷 id면 1점을 더합니다.
아우터를 입지 않고 챙기기만(`outerUsage` ≠ `WEAR`) 하면 그림을 고를 때는 아우터가 없는 것으로 봅니다.

### 2-2. 날씨 → 소품

```js
const accs = pickAccessories(
  {{ temp: 26, sky: "흐림", pty: "비", pop: 90, precip: 25, humidity: 92, wind: 4, di: 79, tempMin: 23, tempMax: 27, pm: null }},
  api.outfits[0], map);              // → [{{key, label, file, why}}] 기본 3개, 비·미세먼지 날 4개
accs.forEach(a => addAcc(BASE + a.file, a.label));
```
날씨 값 중 없는 것은 무시합니다. 미세먼지(`pm`: 좋음/보통/나쁨/매우나쁨)는 **팀 자료가 아직 없어서** 값이 올 때만 KF94 마스크가 나옵니다.

### 2-3. Thymeleaf로 서버에서 바로 넣을 때

```html
<img class="outfit-card" th:src="@{{|/weather/outfits/assets/characters/${{setKey}}_340_poster.png|}}" th:alt="${{setLabel}}">
<img th:src="@{{|/weather/outfits/assets/icons/${{iconKey}}.svg|}}" alt=""> <span th:text="${{shortName}}">방한화</span>
```
서버(Java)에서 세트를 고르려면 `outfit_visual.js`의 점수 규칙을 그대로 옮기면 됩니다(코드 50줄 정도).

### 2-4. 확인용 페이지

- `preview/outfit_link/index.html` — 백엔드 결과를 붙여넣으면 고른 세트 · 아이콘이 바로 보임
- `preview/ui_mockup/index.html` — 실제 화면 가정 목업 (여/남 · 예시 날씨 11개 · 불쾌지수 온도계 · 소품)

## 3. 착장 세트 — 여 {nf}벌 (머리는 계절별로 다름: 봄 로즈베이지 웨이브 · 여름 크림 단발 · 가을/겨울 갈색 긴머리)

{set_table('F')}

## 4. 착장 세트 — 남 {nm}벌 (한 명으로 통일: 짧은 갈색 댄디컷)

{set_table('M')}

## 5. 옷 아이콘 {len(m['icons'])}개

카탈로그 옷 {len(m['items'])}개는 모두 아래 아이콘 중 하나에 연결됩니다(같은 모양의 옷은 같은 아이콘). 화면에는 아이콘 + **짧은 이름**을 보여 줍니다.
예) `C071` 발열 내의 상하의 → **따뜻한 상하의** · `C142` 접지력 있는 방수 방한화 → **방한화**

{icon_table()}

**노출이 많은 옷 7개**(나시 · 끈나시 · 스포츠 브라 · 요가 탑 등, JSON `notRecommended`)는 아이콘을 따로 만들지 않고
「시원한 반팔」 · 「운동용 상의」로 바꿔 보여 줍니다. 백엔드 추천에서 빼 주기를 요청했습니다.

## 6. 소품 {len(m['accessories']['items'])}개

카탈로그에는 아직 소품이 없고, 백엔드 결과의 `accessories`도 비어 있습니다. 아래 기준은 **화면 시연용 초안**이며 최종 기준은 백엔드가 정합니다.
화면에는 **기본 3개, 비 · 미세먼지 날만 4개**까지 보여 줍니다. 우산은 비가 올 때만(눈만 올 때는 아님) 나옵니다.

{acc_table()}

## 7. 그림을 더 만들거나 바꾸려면

세트 목록 · 아이콘 · 연결표를 만드는 프로그램은 `tools/outfit_link/`에 있습니다. 그림을 바꾸거나 세트를 늘릴 때 보시면 좋아요(경로는 원래 작업 폴더 기준).

1. `outfit_sets.py`에 세트 추가 (옷 id + 영어 옷 설명)
2. `py make_outfit_sets.py --prompts` → Gemini 요청문 · 안내 페이지 생성 (요청문 예: `docs/착장세트_요청문_Gemini.md`)
3. Gemini에서 같은 캐릭터 그림을 첨부해 한 장에 여러 벌 생성 → `py make_outfit_sets.py` 가 사람마다 잘라 카드 · MP4 · GIF 생성
4. `py build_map.py` → 이 폴더의 JSON · 아이콘 · 그림을 다시 만듦

## 8. 팀이 정할 것 (질문)

1. 노출이 많은 옷 7개를 추천에서 빼 줄 수 있는지
2. `outfits`가 여러 개 오면 첫 번째만 보여 주면 되는지
3. 소품을 카탈로그 · `accessories`에 넣을지, 이 기준 초안을 쓸지
4. 결과에 습도 · 풍속 · 강수확률 · 최저/최고 기온을 같이 보내 줄 수 있는지 (소품 기준에 필요)
5. 카드 실제 크기 (지금 파일 340×340, 목업에서는 240×240으로 표시)
"""
(out / "README.md").write_text(text, encoding="utf-8")
print("README", len(text), "chars")
