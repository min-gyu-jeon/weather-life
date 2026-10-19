# tools/outfit_link — 착장 세트 · 아이콘 · 연결표를 만든 프로그램

`static/weather/outfits/`의 파일을 만든 Python 프로그램입니다. 경로는 원래 작업 폴더(`학원프로젝트_날씨캐릭터/06_제작작업/옷추천_연결_20261014/`) 기준이라 이 저장소에서 바로 돌아가지는 않습니다. **어떻게 만들었는지 보는 용도**입니다.
필요한 것: Python 3 · Pillow · numpy · ffmpeg (그림을 영상으로 만들 때).

| 파일 | 하는 일 |
|---|---|
| `outfit_sets.py` | **착장 세트 목록** (여 20 · 남 16). 세트마다 카탈로그 옷 id와 Gemini에 줄 영어 옷 설명. 세트를 바꾸려면 여기만 고침 |
| `accessories.py` | 소품 19개와 추천 기준 글 (기준 계산은 `outfit_visual.js`의 `pickAccessories`) |
| `build_map.py` | 카탈로그 170개 → 아이콘 묶음 · 짧은 이름 · 세트 그림 복사 → `outfit_visual_map.json` · `.js` · `assets/` 생성. 빠진 id · 중복 id가 있으면 멈춤 |
| `icons_svg.py` | 옷 아이콘 56개를 코드로 그림 (그라데이션 · 그늘 · 바닥 그림자) |
| `acc_svg.py` | 소품 아이콘 19개 (같은 그림체) |
| `make_outfit_sets.py` | `--prompts` = Gemini 요청문 · 안내 페이지 생성 / 그냥 실행 = Gemini 그림(한 장에 여러 명) → 사람마다 자르기 → 배경 제거 → 340 카드 PNG · MP4 · GIF → `build_map.py` |
| `make_overview.py` | 세트 36벌 한눈에 보기 그림 (`docs/착장세트_한눈에보기.png`) |
| `make_readme.py` | `static/weather/outfits/README.md` 생성 (표는 JSON에서 자동) |

순서: `outfit_sets.py` 수정 → `make_outfit_sets.py --prompts` → Gemini → `make_outfit_sets.py` → (`make_overview.py` · `make_readme.py`).
