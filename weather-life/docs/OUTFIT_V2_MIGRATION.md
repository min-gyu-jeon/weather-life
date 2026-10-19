# 고정 세트 추천 v2 · 프론트 연결 안내

## 바뀐 응답

- 캐릭터는 `outfits[0].setKey` 또는 `visual.videoPath`로 선택합니다.
- 예전 의류 ID `C001` 등의 연결은 사용하지 않습니다. 새 의류 ID는 `tee_short`, `zipup`, `jogger`처럼 옷 아이콘 key와 같습니다.
- 개별 의류에는 `iconKey`와 실제 정적 URL인 `iconPath`가 함께 들어옵니다.
- 소품은 백엔드가 선정한 `accessoryItems`를 사용합니다. 필요한 소품이 없으면 빈 배열입니다.
- 기존 `accessories` 문자열 배열도 제공하지만 이미지 연결에는 `accessoryItems`를 사용하세요.
- 기본 코디 수가 3에서 **1**로 변경되었습니다. `count=3`을 지정하면 서로 다른 세트 최대 3개를 받습니다.
- `occasion`은 호환 필드로만 남겼습니다. 날씨에 맞으면 일상/출근/운동 세트를 모두 선택할 수 있습니다.
- `gender`를 반드시 화면 선택값에 맞게 전달하세요. 미지정/UNISEX는 남녀 세트를 함께 검토합니다.
- `selectionTemperature`는 옷 추천용 보정값이며 공식 체감온도가 아닙니다.

## 호출 예시

```javascript
const response = await fetch('/api/outfits/by-hour?' + new URLSearchParams({
  gu: '영등포구',
  at: '2026-10-15T14:00:00',
  gender: 'FEMALE'
}));
const data = await response.json();
if (!response.ok) throw new Error(data.message ?? '옷 추천 조회 실패');
const outfit = data.outfits[0];

// 이 세트 자체를 캐릭터 그림으로 사용합니다.
video.src = outfit.visual.videoPath;
video.poster = outfit.visual.posterPath;

// null 슬롯은 숨기고, 각각의 iconPath/name으로 렌더링합니다.
const clothes = [outfit.top, outfit.innerTop, outfit.bottom, outfit.onePiece,
                 outfit.outer, outfit.baseLayer, outfit.shoes].filter(Boolean);
const extras = outfit.accessoryItems; // []일 수 있습니다.
```

프론트의 기존 `pickAccessories`에서 다시 '기본 3개'를 채우면 이번 규칙과 달라집니다.
백엔드에서 반환한 소품 목록을 그대로 렌더링하세요. 세부 옷도 프론트에서 다시 무작위로 뽑지 않습니다.

## 이미지 파일 배치

원본 목록의 `static/weather/outfits/assets/...`를 Spring Boot 프로젝트에서 다음 위치로 복사하세요.

- 캐릭터: `src/main/resources/static/weather/outfits/assets/characters/`
- 옷/소품 아이콘: `src/main/resources/static/weather/outfits/assets/icons/`

`setKey`가 `f_spring_campus`이면 파일은 다음과 같습니다.

- `f_spring_campus_340.mp4`
- `f_spring_campus_340_poster.png`
- `f_spring_campus_340.gif`

프론트 소스(`outfit_visual.js`, 기존 `outfit_visual_map.json`)와 실제 자산은 이번 첨부에 없었으므로 그 파일 자체를 수정하지 않았습니다.
새 백엔드는 필요한 경로를 직접 제공하여 구 170개 ID 연결표 없이 사용할 수 있습니다.

## 수정된 백엔드 범위

- `dto`: Garment, OutfitTypes, OutfitRequest, OutfitResponse
- `service`: ClothingCatalog, OutfitService, WeatherRules, NoOutfitException, ShortForecastOutfitMapper, TodayOutfitService
- `controller`: TodayOutfitController, TodayOutfitExceptionHandler
- 추가: OutfitSetCatalog, AccessoryCatalog, AccessoryService, OutfitCatalogController
- `resources/data`: clothing-catalog.json 교체, outfit-sets.json / accessory-catalog.json 추가
- 관련 테스트·문서·HTTP 요청 예시 갱신

기존 날씨 수집·DB 스키마·기상청 호출·불쾌지수 계산식·대시보드 템플릿은 유지합니다.
