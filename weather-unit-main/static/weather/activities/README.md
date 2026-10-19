# 추천 액티비티 — `static/weather/activities/`

2026-10-15 최종본. 화면의 **「추천 액티비티」 칸**에 들어가는 짧은 반복 영상 16개입니다(여자 8 · 남자 8).
모두 340×340 px이고 **MP4 · GIF · 정지 PNG(`_poster.png`)** 세 가지가 있습니다. 화면에는 **MP4를 권장**합니다. GIF는 혹시 몰라 같이 만든 예비 파일입니다.
동작 그림 2~4장을 넘기는 방식입니다(장마다 0.8~1.2초, 겹쳐서 부드럽게 넘어가고 끊김 없이 반복).

파일 이름: `activity_<key>_340.mp4` · `activity_<key>_340.gif` · `activity_<key>_340_poster.png`

<img src="../../../docs/액티비티_한눈에보기.png" width="760" alt="추천 액티비티 16개 — 위 여자, 아래 남자">

| 언제 | 여자 key | 장면 | 남자 key | 장면 |
|---|---|---|---|---|
| 봄 | `spring_jump` | 벚꽃 아래 셀카, 햄스터가 어깨로 점프 | `m_spring_bike` | 벚꽃길 자전거(헬멧) |
| 여름 | `summer_swim` | 수영(반팔 래시가드) | `m_summer_surf` | 파도 서핑(구명조끼) |
| 가을 | `autumn_walk` | 단풍 공원 산책 | `m_autumn_hike` | 단풍 산 등산 |
| 겨울 · 쌀쌀 | `winter_chilly` | 조금 추워서 입김 불기 | `m_winter_jog` | 입김 나는 조깅 |
| 겨울 · -5~0℃ 맑음 | `winter_onsen` | 온천 족욕(옷 다 입고 발만) | `m_winter_ski` | 설산 스키(헬멧 · 고글) |
| **비 · 소나기 · 천둥** | `summer_rain` | 집 창가에서 휴식 | `m_rain_game` | 집에서 게임 |
| **한파 (-5℃ 이하)** | `winter_cold` | 추위에 떨기 | `m_winter_cold` | 추위에 떨기 |
| **폭염 · 미세먼지 나쁨** | `home_ac` | 에어컨 켜고 집에서 쉬기 | `m_home_ac` | 에어컨 켜고 집에서 쉬기 |

굵은 줄은 **예외**입니다. 비 오는 날 수영처럼 어색한 추천이 나오지 않도록, 예외가 계절보다 먼저입니다.
어떤 날씨에 어떤 key를 고르는지는 **[기준표 README](../rules/README.md)** 를 보시면 좋아요.

## 넣는 법 (Thymeleaf 예시)

```html
<video class="weather-card" autoplay muted loop playsinline
       th:poster="@{/weather/activities/activity_autumn_walk_340_poster.png}"
       aria-label="단풍 공원을 산책하는 캐릭터">
  <source th:src="@{/weather/activities/activity_autumn_walk_340.mp4}" type="video/mp4">
  <img th:src="@{/weather/activities/activity_autumn_walk_340.gif}" alt="단풍 공원을 산책하는 캐릭터">
</video>
```

원본(Gemini가 만든 2×2 그림)은 `characters/activity_sheets/`, 영상을 만드는 프로그램은 `tools/activity/`에 있습니다.
