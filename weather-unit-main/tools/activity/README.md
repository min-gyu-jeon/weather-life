# tools/activity — 추천 액티비티 영상을 만든 프로그램

`make_activity.py`: Gemini가 만든 **2×2 그림 한 장**(흰 테두리로 나뉜 동작 4칸)을 잘라 340×340 반복 애니메이션(MP4 · GIF · 정지 PNG)으로 만듭니다.

```
py make_activity.py <key> [--use 1,2] [--hold 0.8] [--fade 0.15] [--colors 160] [--soften 0.75]
```

| 옵션 | 뜻 |
|---|---|
| `--use 1,2` | 몇 번째 칸만 쓸지 (구도가 다른 칸 빼기). 장마 · 온천은 위 2칸만 씀 |
| `--hold` · `--fade` | 칸마다 보여 주는 시간 · 다음 칸과 겹치는 시간(초) |
| `--colors` | GIF 색 수. GIF가 400KB를 넘으면 128이나 96으로 낮춤 |
| `--soften` | 그림 아래쪽을 흐리게(수영 1차 때 물에 비친 얼굴을 지우던 옵션) |

- 4번째 칸 오른쪽 아래에 있는 Gemini 반짝이 로고는 자동으로 지웁니다(`unmark`).
- 경로는 작업 폴더 기준입니다: 입력 `../활동_원본/<key>.png` → 출력 `../활동_20261014/`. 이 저장소에서는 입력 그림이 `characters/activity_sheets/`에 있으니 경로(`RAW` · `OUT`)를 바꿔서 실행하세요.
- 필요: Python 3 · Pillow · numpy · ffmpeg.
- Gemini 요청문: [`docs/활동_요청문_Gemini.md`](../../docs/활동_요청문_Gemini.md)
