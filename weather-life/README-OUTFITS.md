# Weather Life · 고정 세트 기반 옷 추천 v2

기존 170종 자유 조합을 **고정 캐릭터 36세트 → 새 의류 56종 → 조건부 소품 19종**으로 교체했습니다.
확정 목록의 `alt`/이름과 아이콘 key를 그대로 사용합니다. 예전의 여러 의류를 숨겨서 다시 추천하거나, 새 캐릭터 세트를 생성하지 않습니다.

## 추천 흐름

1. 명시한 성별과 바지/치마/원피스 선호에 맞는 기존 세트만 후보로 둡니다.
2. 기온·습도·바람·강수를 반영한 추천용 보정 기온으로 적합한 세트를 고릅니다.
3. 달력 계절은 동점에 가까운 후보를 위한 작은 가점입니다. 쌀쌀한 여름에는 봄/가을, 더운 봄/가을에는 여름 세트가 나옵니다.
4. 선택한 세트의 `pieces`에 등록된 옷만 조합합니다. 용도는 제한하지 않으므로 일상 추천에 애슬레저 세트도 나올 수 있습니다.
5. 신발은 날씨에 맞춰 고릅니다. 추우면 발열 내의를 추가하고 필요한 소품만 반환합니다. 필요 없으면 `[]`입니다.

예: `f_spring_campus`는 집업 + 조거·트레이닝 + 허용 이너 + 날씨에 맞는 신발입니다.
원피스 세트에 바지를 붙이거나 패딩 세트에 반바지를 붙이지 않습니다. 일교차가 크면 소품의 `light_outer`로 겉옷을 챙기도록 안내하며, 그림에 없는 겉옷을 착용 슬롯에 추가하지 않습니다.

## 실행

원본 프로젝트의 Spring Boot 4.1.1 / JDK 21 / Gradle Wrapper 9.7.1 설정을 유지합니다.
기존 MariaDB·기상청 환경 설정을 사용합니다. 옷 추천 자체는 로컬 JSON과 규칙으로 계산하며 AI API를 호출하지 않습니다.

```bash
./gradlew test bootJar
./gradlew bootRun
```

Windows: `./gradlew` 대신 `.\gradlew.bat` 사용. 테스트는 H2와 테스트용 설정을 사용합니다.

## 바로 호출하기

```http
POST /api/outfits/recommend
Content-Type: application/json

{
  "temperature": 32,
  "humidity": 70,
  "windSpeed": 2,
  "sky": "CLOUDY",
  "precipitation": "NONE",
  "gender": "FEMALE",
  "date": "2026-10-15",
  "count": 1,
  "seed": 42
}
```

10월이어도 더운 날씨를 우선하여 등록된 여름 세트를 선택합니다.

| API | 내용 |
|---|---|
| `POST /api/outfits/recommend` | 직접 전달한 날씨로 추천 |
| `GET /api/outfits/catalog` | 새 의류 56개와 아이콘 경로 |
| `GET /api/outfits/sets` | 고정 세트 36개, 기온 설정, 슬롯별 허용 옷 key |
| `GET /api/outfits/accessories` | 소품 19개와 아이콘 경로 |
| `GET /api/outfits/today?gu=영등포구&gender=FEMALE` | 저장된 오늘 예보로 시간별 추천 |
| `GET /api/outfits/by-date?gu=영등포구&date=2026-10-15&gender=MALE` | 지정 날짜의 시간별 추천 |
| `GET /api/outfits/by-hour?gu=영등포구&at=2026-10-15T14:00:00&gender=FEMALE` | 지정 시각의 추천 |

날씨 조회형 GET은 `regionName`도 계속 지원하며 `gender`, `count`, `seed`를 선택적으로 받습니다.
기존 시간별 응답 구조를 유지하고 **각 시각마다 기본 1세트**를 반환합니다. 하루 대표 1세트를 별도로 집계하는 API는 아닙니다.

## 요청값

| 필드 | 값 / 기본값 |
|---|---|
| `temperature`, `humidity` | 필수. ℃ -50~50 / % 0~100 |
| `windSpeed` | m/s 0~60. 기본 0 |
| `sky` | SUNNY / PARTLY_CLOUDY / CLOUDY. 기본 CLOUDY |
| `precipitation` | NONE / RAIN / SNOW / MIXED. 기본 NONE |
| `gender` | FEMALE / MALE / UNISEX. **프론트에서 선택 성별을 전달하세요.** |
| `date` | 예보 대상 날짜 YYYY-MM-DD. 생략하면 한국 기준 오늘 |
| `count` | 1~5. **기본 1**. 늘리면 서로 다른 세트를 적합도 순서로 반환 |
| `seed` | 생략하면 난수. 같은 입력·날짜·seed는 같은 결과 |
| `preference` | ANY / PANTS / SKIRT / ONE_PIECE. 기본 ANY |
| `thermalPreference` | NORMAL / FEEL_COLD / FEEL_HOT. 기본 NORMAL |
| `minTemperature`, `maxTemperature` | 선택. 최저 ≤ 현재 ≤ 최고. 일교차 안내용 |
| `precipitationProbability` | 선택. % 0~100. 접이식 우산 판단에 사용 |
| `precipitationAmount` | 선택. **시간당 mm** 0~1000. 장화 판단에 사용 |
| `airQuality` | 선택. GOOD / NORMAL / BAD / VERY_BAD. 없으면 마스크 판단 생략 |
| `occasion` | DAILY / OFFICE / EXERCISE / HOME. 구 호출 호환용으로 받으며 **선택/보정 조건으로 쓰지 않음** |

성별 미지정/UNISEX는 남녀 세트를 모두 후보로 사용하고 실제 캐릭터 성별을 `setGender`로 반환합니다.
공용 캐릭터 이미지가 별도로 없기 때문에 구 버전의 '공통 의류만' 의미와 다릅니다.
실내복 캐릭터 세트도 없습니다. HOME을 전달해도 실외 날씨로 추천하며 경고를 반환합니다.
명시한 하의 선호에 맞는 세트가 전혀 없으면 422입니다. 날씨 범위만 맞지 않으면 가장 가까운 등록 세트와 경고를 반환합니다.

## 프론트에서 읽을 값

`outfits[0]`이 가장 적합한 세트입니다. 배열 원소를 서로 합치지 마세요.

| 필드 | 사용 방법 |
|---|---|
| `setKey` | `f_spring_campus` 등 캐릭터 세트 식별자 |
| `setName`, `setGender`, `season` | 선택 세트의 이름·캐릭터 성별·분류 계절 |
| `visual.videoPath` | 캐릭터 MP4 경로 |
| `visual.posterPath`, `visual.gifPath` | 정지 이미지 / 대체 GIF 경로 |
| `top`, `bottom`, `onePiece`, `innerTop`, `outer`, `shoes`, `baseLayer` | 세부 의류. 없는 슬롯은 null |
| 각 의류의 `id`, `iconKey` | 새 56개 key. 예: `zipup`, `jogger` |
| 각 의류의 `name`, `iconPath` | 표시 이름과 SVG 경로 |
| `outerUsage` | 현재 고정 세트에 겉옷이 있으면 WEAR, 없으면 NONE |
| `accessoryItems` | `{key, name, iconPath, reason}` 배열. **새 소품 UI에서 사용** |
| `accessories` | 기존 호출부를 위한 이름 문자열 배열. accessoryItems와 같은 항목 |
| `reasons`, `advice`, `warnings` | 선택 이유, 날씨 안내, 범위 밖 등의 제한 |
| `outerSelectionTemperature` | 구 API 호환용 최저기온 보정 참고값. 세트의 겉옷을 교체하는 기준으로 사용하지 않음 |

정적 파일 URL에는 `static/`이 들어가지 않습니다.
`/weather/outfits/assets/icons/zipup.svg` → 프로젝트 파일 위치는 `src/main/resources/static/weather/outfits/assets/icons/zipup.svg`입니다.

**첨부된 백엔드 ZIP에는 실제 PNG/MP4/GIF/SVG 파일이 없었습니다.** 이번 수정은 제공된 목록에 맞춘 경로와 key를 반환합니다.
프론트 작업자가 가진 `assets` 폴더를 위 위치에 배치해야 그림이 표시됩니다. 실제 이미지 재생/화면 검증은 수행하지 않았습니다.
프론트 연결 변경점은 [`docs/OUTFIT_V2_MIGRATION.md`](docs/OUTFIT_V2_MIGRATION.md)를 참고하세요.

## 소품 규칙

최소 개수를 채우지 않습니다. 한 날에 여러 조건이 맞으면 여러 개가 나옵니다. 우산/접이식 우산은 중복하지 않습니다.

| 소품 key | 조건 |
|---|---|
| umbrella | 비/진눈깨비, 풍속 10m/s 미만 |
| folding_umbrella | 강수 없음 + 강수확률 ≥40%, 풍속 10m/s 미만 |
| rain_boots | 비/진눈깨비 + 시간당 강수량 ≥10mm. 추천 신발을 대신할 대안 |
| parasol | 맑음·강수 없음·≥28℃·풍속 7m/s 미만 |
| sunglasses | 맑음·강수 없음·≥20℃ |
| sunscreen | 맑음/구름 많음·강수 없음·≥18℃. UV를 추정하지 않음 |
| cap | 맑음·강수 없음·≥25℃·풍속 7m/s 미만 |
| fan | ≥30℃ 또는 기존 불쾌지수 계산값 ≥80 |
| water_bottle | ≥28℃ 또는 애슬레저 세트 |
| cool_sleeve | ≥30℃ |
| light_outer | 겉옷이 없는 세트 + 일교차 ≥10℃ |
| scarf / gloves | ≤5℃ / ≤0℃ |
| beanie | ≤0℃ 또는 ≤5℃ + 풍속 ≥5m/s |
| earmuffs | ≤-5℃ 또는 ≤3℃ + 풍속 ≥8m/s |
| hotpack / thermos | ≤-5℃ / ≤3℃ |
| lip_balm | 습도 ≤35% |
| mask | 전달된 airQuality가 BAD / VERY_BAD일 때만 |

소품의 온도 조건은 원본 기온을 사용합니다. 옷의 보정 기온과 구분합니다.
DB 예보의 POP/PCP도 전달합니다. PCP의 `강수없음`은 0, `30~50mm`/`50mm 이상`은 하한값을 쓰고, `미만`/알 수 없는 값은 null로 둡니다.
미세먼지 API 수집은 이번 작업에 추가하지 않았습니다.

## 설정을 수정할 파일

| 파일 | 역할 |
|---|---|
| `data/clothing-catalog.json` | 새 의류 56개. 예전 C001 등은 제거 |
| `data/outfit-sets.json` | 기존 세트 36개, 권장 기온, `pieces` 허용 조합 |
| `data/accessory-catalog.json` | 소품 19개 이름/아이콘 경로 |
| `WeatherRules.java` | 옷 선택용 기온 보정. 습도 최대 +2, 햇빛 +1, 찬바람 최대 -4, 체질 ±2 |
| `OutfitService.java` | 날씨 점수와 세트 안의 의류 선택 |
| `AccessoryService.java` | 날씨 조건별 소품 선택 |
| `ShortForecastOutfitMapper.java` | 날짜·시간별 예보, POP/PCP 전달 |

세트 점수는 `100 - |보정기온 - 적정기온|×4`, 비 세트 가점 24, 강풍 대응 가점 8 등을 사용합니다.
달력 계절은 +0.5에 그칩니다. 먼저 권장 기온에 들어오는 후보를 고르므로 계절 가점으로 더운 날 겨울옷을 선택하지 않습니다.
이 값들은 프로젝트용 수작업 경험 규칙이며 학습 모델·공식 체감온도 공식·검증된 착용 만족도 점수가 아닙니다.
일반 패딩·코트·바람막이를 방수로 가정하지 않습니다. 추운 비에는 보온 세트와 방수 신발/소품을 고르고 겉옷의 한계를 안내합니다.
56개 중 고정 세트에 연결되지 않은 항목도 카탈로그에는 유지합니다. 항목을 모두 쓰려고 기존 이미지와 다른 조합을 만들지 않습니다.

검증 내역: [`docs/outfits/VERIFICATION.md`](docs/outfits/VERIFICATION.md)
