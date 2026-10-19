# 저장된 시간별 예보 → 고정 세트 추천

`TodayOutfitService`가 DB에서 대상 날짜의 예보를 읽고 `ShortForecastOutfitMapper`가 시간별 요청으로 변환합니다.
날씨 수집 API를 다시 호출하지 않습니다. 최저/최고기온은 대상 날짜의 TMP 및 TMN/TMX로 계산합니다.
필수 TMP/REH/WSD/SKY/PTY가 없거나 잘못된 시간은 `skippedHours`에 기록합니다.
POP/PCP는 선택 입력이며 없을 때 임의 값을 만들지 않습니다.

```http
GET /api/outfits/today?gu=영등포구&gender=FEMALE
GET /api/outfits/by-date?gu=영등포구&date=2026-10-15&gender=FEMALE
GET /api/outfits/by-hour?gu=영등포구&at=2026-10-15T09:00:00&gender=MALE&count=1&seed=42
```

`gu` 대신 기존 `regionName`도 사용 가능합니다.
날짜/시각은 한국 기준입니다. 과거·미래 예보 조회에서는 실행일이 아니라 **조회한 날짜**를 계절 보조값으로 사용합니다.
`gender`/`count`/`seed`는 각 시간의 요청에 전달합니다. 기본 1세트이며 count는 1~5입니다.
seed를 지정하면 같은 입력과 설정에서 결과를 재현할 수 있습니다.

날짜 조회 응답은 `{date, regionName, hourlyRecommendations, skippedHours}` 형태입니다.
`hourlyRecommendations["09:00"]`에 직접 추천 API와 동일한 응답이 들어갑니다.
시각 조회 응답은 직접 추천 API와 동일합니다.

각 시간의 `outfits[0].setKey`로 캐릭터를, 각 슬롯의 `iconPath`로 옷 아이콘을,
`accessoryItems`로 필요한 소품을 표시하세요. 세부 필드는 `README-OUTFITS.md`를 참고하세요.
기존 빈 배열·404/400/422 처리 흐름을 유지하며 잘못된 추천 입력도 400으로 반환합니다.
