# 날씨 캐릭터 고르는 표 — 사용법

그림은 모두 옷을 다 입은 상태로 미리 만들어 둔 완성 사진·영상입니다. 화면에서 옷을 입히거나 합치지 않습니다. weather_character_rules.json은 「이 날씨면 이 파일을 꺼낸다」를 적어 둔 고르는 표일 뿐입니다.

예: 10월 16℃ 맑음 여자 → `f_autumn_knit` → `outfits/assets/characters/f_autumn_knit_340_poster.png`를 그대로 띄웁니다.

영상은 MP4를 우선 쓰고, GIF는 예비로 씁니다.  
백엔드 착장 결과는 `outfit_visual.js`의 `pickOutfitVisual`에 넣고, 결과가 없을 때 이 규칙을 대안으로 씁니다.  
소품은 `outfit_visual.js`의 `pickAccessories`에서 별도로 고릅니다.

## 이 파일이 하는 일

날씨 값을 넣으면 추천 복장, 활동, 온도계 옆 스티커, 빨래 그림의 **파일 키와 경로**를 돌려줍니다.  
`weather_character_rules.json`은 그림을 만들 때 정한 기본 기준입니다. 실제 조합은 백엔드·화면 담당 코드에서 이 표를 불러 쓰면 됩니다.  
결과 경로는 `static/weather/` 기준입니다. Spring 화면에서는 앞에 `/weather/`를 붙이고, 파일이 아직 없으면 «아직 제작 전»을 보여 주세요.

이 작업 폴더의 UI 목업을 파일 더블클릭(`file://`)으로 열 때는 `weather_character_rules.js`를 읽습니다. JSON을 고칠 때마다 이 폴더에서 `py -I make_rules_js.py`를 실행해 JS도 맞춰 주세요.

## 넣는 값

| 이름 | 뜻 | 예 |
|---|---|---|
| `month` | 월, 1~12. 없으면 오늘 날짜의 월 | `10` |
| `temp` | 현재 기온, ℃. 필수 | `16` |
| `pty` | 강수형태 글자 또는 기상청 PTY 코드. 없으면 `없음` | `없음`, `비`, `비눈`, `눈`, `소나기`, `빗방울`, `뇌우` |
| `sky` | 하늘 상태 글자 또는 기상청 SKY 코드. 없으면 `맑음` | `맑음`, `구름많음`, `흐림` |
| `di` | 불쾌지수 숫자. 없으면 스티커 표정은 `normal` | `72` |
| `gender` | 여자 `F`, 남자 `M`. 없으면 `F` | `F` |
| `occasion` | 선택. `일상`·`출근`·`운동` | 생략하면 `일상` |
| `uv` | 선택. 자외선지수 숫자. 없으면 자외선 조건 생략 | `9` |
| `pm` | 선택. 미세먼지 등급 글자. 없으면 미세먼지 조건 생략 | `좋음`, `보통`, `나쁨`, `매우나쁨` |
| `humidity` | 선택. 상대습도 숫자, 0~100%. 없으면 하늘 상태로 빨래 판단 | `40` |

`temp`는 반드시 숫자로 넣습니다. `month`가 없으면 실행 당일의 월을 쓰고, `di`가 없으면 표정은 `normal`이며 DI 80 이상 폭염 조건은 적용하지 않습니다. `occasion`은 `일상`, `uv`는 없음, `pm`은 빈 글자, `humidity`는 없음이 기본입니다. `pty`에 `비`·`빗방울`·`소나기`·`뇌우`·`천둥`이 들어가면 비 예외를 씁니다. `비눈`·`빗방울눈날림`도 비 예외이고, `눈`·`눈날림`만 있으면 비 예외가 아닙니다.

기상청 단기예보 숫자 코드는 글자로 바꾼 다음 규칙에 넣습니다. JSON의 `kma_codes`에도 같은 표가 있습니다.

| 코드 종류 | 숫자 → 하늘/강수형태 |
|---|---|
| `SKY` | `1` 맑음 · `3` 구름많음 · `4` 흐림 |
| `PTY` | `0` 없음 · `1` 비 · `2` 비/눈 · `3` 눈 · `4` 소나기 · `5` 빗방울 · `6` 빗방울눈날림 · `7` 눈날림 |

여름 달에 23℃ 미만이면 가벼운 봄·가을 착장과 봄·가을 액티비티를 고릅니다(서늘한 날 수영 추천 방지). 6월은 봄 착장, 7~8월은 가을 착장입니다. 기준은 JSON의 `season.cool_summer_outfit`(`below_temp: 23`, `spring_months: [3,4,5,6]`, `autumn_months: [7,8,9,10,11]`)에 있습니다.

## 고르는 순서

1. 월로 계절을 고릅니다: 봄 3~5월, 여름 6~8월, 가을 9~11월, 겨울 12~2월.
2. 28℃ 이상이면 여름 겉모습, 5℃ 이하면 겨울 겉모습으로 바꿉니다. 여름인데 23℃ 미만이면 봄·가을 착장과 액티비티를 씁니다.
3. 강수형태에서 비·빗방울·소나기·뇌우·천둥을 확인합니다.
4. 비가 오면 해당 계절의 비 착장을 먼저 고릅니다. 없으면 일상 착장입니다. 비가 없을 때는 출근·운동 착장도 고를 수 있습니다.
5. 활동은 비 → 미세먼지 나쁨 → 폭염(33℃ 이상 또는 DI 80 이상) → 한파(-5℃ 이하) → 계절 순으로 고릅니다.
6. 스티커는 불쾌지수 표정을 먼저 정합니다. 비면 같은 표정의 우산, 비가 없고 맑으면서 30℃ 이상 또는 자외선지수 8 이상이면 선글라스, 그 밖에는 표정 스티커를 고릅니다.
7. 빨래는 -5℃ 이하 얼음 → 비 → 습도 70% 이상 → 습도 없고 흐림 → 그 밖은 잘 마름 순서로 고릅니다.

> **예외 먼저**: 비·천둥 → 집에서 쉬기 · 미세먼지 나쁨/폭염 → 에어컨을 켜고 쉬기 · 한파 → 추위에 떨기. 예외가 없을 때 계절 활동을 보여 줍니다.

활동의 미세먼지 등급에 `나쁨`이 들어가면 `나쁨`과 `매우나쁨`을 모두 포함합니다. 비가 가장 먼저입니다. 미세먼지 날도 `home_ac` / `m_home_ac`를 씁니다. 우산 스티커는 온도계 옆 그림이며, 추천 소품의 우산은 기존 소품 규칙에서 따로 고릅니다. `variety_optional`은 화면에서 다른 옷을 번갈아 보여 주고 싶을 때만 씁니다.

## 옷 · 활동 파일

아래 `src`는 README를 `weather-unit/static/weather/`에 복사했을 때 보이는 **저장소 상대 경로**입니다. 이 작업 폴더에서 원본을 볼 때는 착장 `../옷추천_연결_20261014/assets/characters/`, 활동 `../활동_20261014/`, 스티커 `../표정_20261015/`을 확인하세요. 화면에서 `/weather/`를 붙일 경로는 JSON 결과에 들어 있습니다.

| 겉모습 | 여자 기본 착장 | 남자 기본 착장 | 활동 |
|---|---|---|---|
| 봄 | <img src="outfits/assets/characters/f_spring_basic_340_poster.png" width="76" alt="봄 여자 착장"><br>`f_spring_basic`(18℃ 이상), `f_spring_campus`(18℃ 미만) | <img src="outfits/assets/characters/m_spring_denim_340_poster.png" width="76" alt="봄 남자 착장"><br>`m_spring_denim` / `m_spring_zipup` | 여 `spring_jump` · 남 `m_spring_bike` |
| 여름 | <img src="outfits/assets/characters/f_summer_basic_340_poster.png" width="76" alt="여름 여자 착장"><br>`f_summer_basic` (23℃ 미만이면 6월 봄·7~8월 가을 착장) | <img src="outfits/assets/characters/m_summer_tee_340_poster.png" width="76" alt="여름 남자 착장"><br>`m_summer_tee` (23℃ 미만은 봄·가을 착장) | 여 `summer_swim` · 남 `m_summer_surf` |
| 가을 | <img src="outfits/assets/characters/f_autumn_basic_340_poster.png" width="76" alt="가을 여자 착장"><br>`f_autumn_basic`(18℃ 이상), `f_autumn_knit`(18℃ 미만) | <img src="outfits/assets/characters/m_autumn_sweat_340_poster.png" width="76" alt="가을 남자 착장"><br>`m_autumn_sweat` / `m_autumn_blouson` | 여 `autumn_walk` · 남 `m_autumn_hike` |
| 겨울 | <img src="outfits/assets/characters/f_winter_padding_340_poster.png" width="76" alt="겨울 여자 착장"><br>`f_winter_halfcoat`(&gt;0℃) / `f_winter_padding`(0~-10℃) / `f_winter_longpadding`(≤-10℃) | <img src="outfits/assets/characters/m_winter_padding_340_poster.png" width="76" alt="겨울 남자 착장"><br>`m_winter_duffle`(&gt;0℃) / `m_winter_padding`(≤0℃) | ≤-5℃ 떨기, -5~0℃ 맑음은 족욕·스키, 그 밖은 조금 추움·조깅 |
| 비·천둥 | `f_spring_rain`(봄·가을), `f_summer_rain`(여름) | `m_summer_rain`(여름). 봄·가을·겨울은 기본 착장 | 여 `summer_rain` · 남 `m_rain_game` |
| 미세먼지 나쁨 · 폭염 | 착장은 위의 기온·계절 기준을 유지 | 착장은 위의 기온·계절 기준을 유지 | 여 `home_ac` · 남 `m_home_ac` |

활동 포스터는 `activities/activity_<key>_340_poster.png`, 영상은 같은 키의 `.mp4`·`.gif`입니다. `home_ac`·`m_home_ac`는 작업 폴더에서 제작 중이며, 현재 `weather-unit`에는 아직 없으므로로 표시했습니다. 겨울 활동 키는 여자 `winter_cold` / `winter_onsen` / `winter_chilly`, 남자 `m_winter_cold` / `m_winter_ski` / `m_winter_jog`입니다.

## 온도계 옆 스티커 18개

불쾌지수 단계는 `comfort`(68 미만), `normal`(68 이상 75 미만), `bad`(75 이상 80 미만), `very_bad`(80 이상)입니다. 비가 오면 `umbrella_<단계>`를 고르므로 우산을 들어도 표정이 바뀝니다. 비가 없을 때 맑고 덥거나 자외선이 강하면 `sunglasses`를 고릅니다. 아래 경로는 `weather-unit/static/weather/`에 복사할 때 쓰는 상대 경로입니다. 원본은 `../표정_20261015/`에 있습니다. 종전 `f_umbrella.png`·`m_umbrella.png`는 보관하지만 새 규칙에서는 고르지 않습니다.

| 성별 | 키 | 포스터 경로 · 미리보기 | 표정·소품 |
|---|---|---|---|
| 여자 | `comfort` | <img src="stickers/f_comfort.png" width="56" alt="아주 행복한 여자 스티커"><br>`stickers/f_comfort.png` | 눈을 접고 크게 웃음 |
| 여자 | `normal` | <img src="stickers/f_normal.png" width="56" alt="미소 짓는 여자 스티커"><br>`stickers/f_normal.png` | 부드러운 미소 |
| 여자 | `bad` | <img src="stickers/f_bad.png" width="56" alt="무표정인 여자 스티커"><br>`stickers/f_bad.png` | 약간 지친 무표정 |
| 여자 | `very_bad` | <img src="stickers/f_very_bad.png" width="56" alt="화난 여자 스티커"><br>`stickers/f_very_bad.png` | 귀엽게 화남 |
| 여자 | `umbrella_comfort` | <img src="stickers/f_umbrella_comfort.png" width="56" alt="아주 행복한 우산 여자"><br>`stickers/f_umbrella_comfort.png` | 비·쾌적, 크게 웃음 |
| 여자 | `umbrella_normal` | <img src="stickers/f_umbrella_normal.png" width="56" alt="미소 짓는 우산 여자"><br>`stickers/f_umbrella_normal.png` | 비·보통, 부드러운 미소 |
| 여자 | `umbrella_bad` | <img src="stickers/f_umbrella_bad.png" width="56" alt="무표정 우산 여자"><br>`stickers/f_umbrella_bad.png` | 비·나쁨, 지친 무표정 |
| 여자 | `umbrella_very_bad` | <img src="stickers/f_umbrella_very_bad.png" width="56" alt="화난 우산 여자"><br>`stickers/f_umbrella_very_bad.png` | 비·매우 나쁨, 귀엽게 화남 |
| 여자 | `sunglasses` | <img src="stickers/f_sunglasses.png" width="56" alt="선글라스 쓴 여자 스티커"><br>`stickers/f_sunglasses.png` | 맑고 30℃ 이상 또는 자외선지수 8 이상 |
| 남자 | `comfort` | <img src="stickers/m_comfort.png" width="56" alt="아주 행복한 남자 스티커"><br>`stickers/m_comfort.png` | 눈을 접고 크게 웃음 |
| 남자 | `normal` | <img src="stickers/m_normal.png" width="56" alt="미소 짓는 남자 스티커"><br>`stickers/m_normal.png` | 부드러운 미소 |
| 남자 | `bad` | <img src="stickers/m_bad.png" width="56" alt="무표정인 남자 스티커"><br>`stickers/m_bad.png` | 약간 지친 무표정 |
| 남자 | `very_bad` | <img src="stickers/m_very_bad.png" width="56" alt="화난 남자 스티커"><br>`stickers/m_very_bad.png` | 귀엽게 화남 |
| 남자 | `umbrella_comfort` | <img src="stickers/m_umbrella_comfort.png" width="56" alt="아주 행복한 우산 남자"><br>`stickers/m_umbrella_comfort.png` | 비·쾌적, 크게 웃음 |
| 남자 | `umbrella_normal` | <img src="stickers/m_umbrella_normal.png" width="56" alt="미소 짓는 우산 남자"><br>`stickers/m_umbrella_normal.png` | 비·보통, 부드러운 미소 |
| 남자 | `umbrella_bad` | <img src="stickers/m_umbrella_bad.png" width="56" alt="무표정 우산 남자"><br>`stickers/m_umbrella_bad.png` | 비·나쁨, 지친 무표정 |
| 남자 | `umbrella_very_bad` | <img src="stickers/m_umbrella_very_bad.png" width="56" alt="화난 우산 남자"><br>`stickers/m_umbrella_very_bad.png` | 비·매우 나쁨, 귀엽게 화남 |
| 남자 | `sunglasses` | <img src="stickers/m_sunglasses.png" width="56" alt="선글라스 쓴 남자 스티커"><br>`stickers/m_sunglasses.png` | 맑고 30℃ 이상 또는 자외선지수 8 이상 |

출근은 계절별 `*_office` 등 출근 착장으로, 운동은 **여름에만** `*_athleisure`로 바뀝니다. 정확한 착장 키 목록은 JSON에 있습니다. 착장 이름과 포스터 경로는 기존 `outfits/outfit_visual_map.json`의 `sets`와 일치합니다.

## 빨래 그림 3개

빨래 칸도 이미 완성된 그림 파일 하나를 고릅니다. 세 그림은 티셔츠·수건·양말이 같은 빨랫줄에 걸린 모습입니다. 아래 경로는 `static/weather/` 기준이며, 현재 작업 그림은 `../빨래_20261015/`에 있습니다.

| 먼저 맞는 조건 | 키 | 그림 경로 |
|---|---|---|
| -5℃ 이하 | `frozen` | <img src="laundry/laundry_frozen.png" width="76" alt="얼어붙은 빨래"><br>`laundry/laundry_frozen.png` |
| 비·빗방울·소나기·뇌우·천둥 | `damp` | <img src="laundry/laundry_damp.png" width="76" alt="축축한 빨래"><br>`laundry/laundry_damp.png` |
| 습도 값이 있고 70% 이상 | `damp` | `laundry/laundry_damp.png` |
| 습도 값이 없고 하늘이 흐림 | `damp` | `laundry/laundry_damp.png` |
| 그 밖(맑은 봄·가을 포함) | `dry` | <img src="laundry/laundry_dry.png" width="76" alt="바삭하게 마른 빨래"><br>`laundry/laundry_dry.png` |

## 화면에 보여 줄 이름

키는 파일을 고를 때 쓰고, 아래 이름은 사용자에게 보여 줄 때 씁니다. 모두 JSON의 `labels`와 같습니다.

| 종류 | 키 | 표시 이름 |
|---|---|---|
| 활동 | `spring_jump` | 봄날 점프 |
| 활동 | `m_spring_bike` | 봄 자전거 |
| 활동 | `summer_swim` | 여름 수영 |
| 활동 | `m_summer_surf` | 여름 서핑 |
| 활동 | `autumn_walk` | 가을 산책 |
| 활동 | `m_autumn_hike` | 가을 등산 |
| 활동 | `winter_cold` | 추위에 떨기 |
| 활동 | `m_winter_cold` | 추위에 떨기 |
| 활동 | `winter_onsen` | 따뜻한 족욕 |
| 활동 | `m_winter_ski` | 겨울 스키 |
| 활동 | `winter_chilly` | 쌀쌀한 겨울 |
| 활동 | `m_winter_jog` | 겨울 조깅 |
| 활동 | `summer_rain` | 비 오는 날 집에서 쉬기 |
| 활동 | `m_rain_game` | 비 오는 날 집에서 게임하기 |
| 활동 | `home_ac` | 에어컨 켜고 쉬기 |
| 활동 | `m_home_ac` | 에어컨 켜고 쉬기 |
| 스티커 | `comfort` | 쾌적 · 아주 행복한 미소 |
| 스티커 | `normal` | 보통 · 부드러운 미소 |
| 스티커 | `bad` | 나쁨 · 지친 무표정 |
| 스티커 | `very_bad` | 매우 나쁨 · 귀엽게 화남 |
| 스티커 | `umbrella_comfort` | 비 · 쾌적한 미소 |
| 스티커 | `umbrella_normal` | 비 · 부드러운 미소 |
| 스티커 | `umbrella_bad` | 비 · 지친 무표정 |
| 스티커 | `umbrella_very_bad` | 비 · 귀엽게 화남 |
| 스티커 | `sunglasses` | 맑고 뜨거운 날 · 선글라스 |
| 빨래 | `dry` | 잘 마른 빨래 |
| 빨래 | `damp` | 축축한 빨래 |
| 빨래 | `frozen` | 얼어붙은 빨래 |

## 화면에서 불러오는 예

`weather_character_rules.json`과 `pick_example.js`를 `static/weather/`에 복사한 뒤 서버에서 실행하는 예입니다. `pickWeatherCharacter`는 파일 경로와 대체 문구를 돌려줍니다. 화면 배치와 실제 날씨 계산은 팀 코드가 맡습니다.

```html
<script src="/weather/pick_example.js"></script>
<div id="activity-card"></div>
<img id="weather-sticker" alt="오늘 날씨 스티커">
<img id="laundry-image" alt="오늘의 빨래 상태">
<script>
fetch('/weather/weather_character_rules.json')
  .then(response => response.json())
  .then(rules => {
    const result = pickWeatherCharacter(
      { month: 10, temp: 16, pty: '없음', sky: '맑음', di: 72, gender: 'F' }, rules);
    const base = '/weather/';
    document.querySelector('#activity-card').innerHTML = `
      <video autoplay muted loop playsinline poster="${base + result.activity.poster}"
             aria-label="${result.activity.label}">
        <source src="${base + result.activity.mp4}" type="video/mp4">
        <img src="${base + result.activity.gif}" alt="${result.activity.label}">
      </video>`;
    document.querySelector('#weather-sticker').src = base + result.sticker.poster;
    document.querySelector('#weather-sticker').alt = result.sticker.label;
    document.querySelector('#laundry-image').src = base + result.laundry.poster;
    document.querySelector('#laundry-image').alt = result.laundry.label;
    // 착장 포스터: base + result.outfit.poster
  });
</script>
```

영상 파일이 없거나 움직임을 줄이는 설정이면 포스터만 보여 주세요. 현재 없는 파일과 알 수 없는 키는 `py -I check_rules.py C:\Users\human\Documents\weather-unit\static\weather`로 확인할 수 있습니다. 검사 대상은 `weather-unit`이므로 로컬 작업 폴더에 그림이 있어도 복사 전에는로 나옵니다.

## 샘플 날씨 × 여자·남자

26개 날씨 × 여자·남자 = 52건을 실행한 결과입니다. 현재 없는 그림은 check_rules.py로 확인합니다. 입력의 `—`는 생략값입니다.

| 예시 | 성별 | 입력 (월·기온·강수·하늘·DI·UV·PM·습도) | 착장 set | 활동 | 스티커 | 빨래 |
|---|---|---|---|---|---|---|
| 봄 맑음 | F | 4월 · 20℃ · 없음 · 맑음 · 65 · — · — · — | f_spring_basic | spring_jump | comfort | dry |
| 봄 맑음 | M | 4월 · 20℃ · 없음 · 맑음 · 65 · — · — · — | m_spring_denim | m_spring_bike | comfort | dry |
| 선택값 생략 | F | 4월 · 20℃ · — · — · — · — · — · — | f_spring_basic | spring_jump | normal | dry |
| 선택값 생략 | M | 4월 · 20℃ · — · — · — · — · — · — | m_spring_denim | m_spring_bike | normal | dry |
| KMA 숫자 비 | F | 7월 · 24℃ · 1 · 4 · 77 · — · — · — | f_summer_rain | summer_rain | umbrella_bad | damp |
| KMA 숫자 비 | M | 7월 · 24℃ · 1 · 4 · 77 · — · — · — | m_summer_rain | m_rain_game | umbrella_bad | damp |
| KMA 문자 빗방울 | F | 6월 · 20℃ · 5 · 3 · 70 · — · — · — | f_spring_rain | summer_rain | umbrella_normal | damp |
| KMA 문자 빗방울 | M | 6월 · 20℃ · 5 · 3 · 70 · — · — · — | m_spring_denim | m_rain_game | umbrella_normal | damp |
| 서늘한 6월 | F | 6월 · 22℃ · 0 · 1 · 65 · — · — · — | f_spring_basic | spring_jump | comfort | dry |
| 서늘한 6월 | M | 6월 · 22℃ · 0 · 1 · 65 · — · — · — | m_spring_denim | m_spring_bike | comfort | dry |
| 서늘한 7월 | F | 7월 · 22℃ · 0 · 1 · 65 · — · — · — | f_autumn_basic | autumn_walk | comfort | dry |
| 서늘한 7월 | M | 7월 · 22℃ · 0 · 1 · 65 · — · — · — | m_autumn_sweat | m_autumn_hike | comfort | dry |
| 봄비 | F | 4월 · 14℃ · 비 · 흐림 · 70 · — · — · — | f_spring_rain | summer_rain | umbrella_normal | damp |
| 봄비 | M | 4월 · 14℃ · 비 · 흐림 · 70 · — · — · — | m_spring_zipup | m_rain_game | umbrella_normal | damp |
| 가을비 쾌적 | F | 10월 · 16℃ · 비 · 흐림 · 60 · — · — · — | f_spring_rain | summer_rain | umbrella_comfort | damp |
| 가을비 쾌적 | M | 10월 · 16℃ · 비 · 흐림 · 60 · — · — · — | m_autumn_blouson | m_rain_game | umbrella_comfort | damp |
| 한여름 | F | 8월 · 33℃ · 없음 · 맑음 · 82 · — · — · — | f_summer_basic | home_ac | sunglasses | dry |
| 한여름 | M | 8월 · 33℃ · 없음 · 맑음 · 82 · — · — · — | m_summer_tee | m_home_ac | sunglasses | dry |
| 장마 | F | 7월 · 26℃ · 비 · 흐림 · 77 · — · — · — | f_summer_rain | summer_rain | umbrella_bad | damp |
| 장마 | M | 7월 · 26℃ · 비 · 흐림 · 77 · — · — · — | m_summer_rain | m_rain_game | umbrella_bad | damp |
| 여름 천둥 | F | 7월 · 29℃ · 뇌우 · 흐림 · 81 · — · — · — | f_summer_rain | summer_rain | umbrella_very_bad | damp |
| 여름 천둥 | M | 7월 · 29℃ · 뇌우 · 흐림 · 81 · — · — · — | m_summer_rain | m_rain_game | umbrella_very_bad | damp |
| 가을 16℃ | F | 10월 · 16℃ · 없음 · 맑음 · 65 · — · — · — | f_autumn_knit | autumn_walk | comfort | dry |
| 가을 16℃ | M | 10월 · 16℃ · 없음 · 맑음 · 65 · — · — · — | m_autumn_blouson | m_autumn_hike | comfort | dry |
| 가을 22℃ | F | 10월 · 22℃ · 없음 · 맑음 · 72 · — · — · — | f_autumn_basic | autumn_walk | normal | dry |
| 가을 22℃ | M | 10월 · 22℃ · 없음 · 맑음 · 72 · — · — · — | m_autumn_sweat | m_autumn_hike | normal | dry |
| 초겨울 | F | 12월 · 4℃ · 없음 · 흐림 · 60 · — · — · — | f_winter_halfcoat | winter_chilly | comfort | damp |
| 초겨울 | M | 12월 · 4℃ · 없음 · 흐림 · 60 · — · — · — | m_winter_duffle | m_winter_jog | comfort | damp |
| 겨울 주말 | F | 1월 · -2℃ · 없음 · 맑음 · 58 · — · — · — | f_winter_padding | winter_onsen | comfort | dry |
| 겨울 주말 | M | 1월 · -2℃ · 없음 · 맑음 · 58 · — · — · — | m_winter_padding | m_winter_ski | comfort | dry |
| 한파 | F | 1월 · -12℃ · 눈 · 흐림 · 55 · — · — · — | f_winter_longpadding | winter_cold | comfort | frozen |
| 한파 | M | 1월 · -12℃ · 눈 · 흐림 · 55 · — · — · — | m_winter_padding | m_winter_cold | comfort | frozen |
| 4월 30℃ | F | 4월 · 30℃ · 없음 · 맑음 · 80 · — · — · — | f_summer_basic | home_ac | sunglasses | dry |
| 4월 30℃ | M | 4월 · 30℃ · 없음 · 맑음 · 80 · — · — · — | m_summer_tee | m_home_ac | sunglasses | dry |
| 10월 3℃ | F | 10월 · 3℃ · 없음 · 맑음 · 63 · — · — · — | f_winter_halfcoat | winter_chilly | comfort | dry |
| 10월 3℃ | M | 10월 · 3℃ · 없음 · 맑음 · 63 · — · — · — | m_winter_duffle | m_winter_jog | comfort | dry |
| 자외선 강한 봄 | F | 4월 · 24℃ · 없음 · 맑음 · 66 · 9 · — · — | f_spring_basic | spring_jump | sunglasses | dry |
| 자외선 강한 봄 | M | 4월 · 24℃ · 없음 · 맑음 · 66 · 9 · — · — | m_spring_denim | m_spring_bike | sunglasses | dry |
| 폭염 35℃ | F | 8월 · 35℃ · 없음 · 맑음 · 86 · — · — · — | f_summer_basic | home_ac | sunglasses | dry |
| 폭염 35℃ | M | 8월 · 35℃ · 없음 · 맑음 · 86 · — · — · — | m_summer_tee | m_home_ac | sunglasses | dry |
| 미세먼지 나쁨 | F | 4월 · 18℃ · 없음 · 맑음 · 65 · — · 나쁨 · — | f_spring_basic | home_ac | comfort | dry |
| 미세먼지 나쁨 | M | 4월 · 18℃ · 없음 · 맑음 · 65 · — · 나쁨 · — | m_spring_denim | m_home_ac | comfort | dry |
| 빨래 잘 마름 | F | 6월 · 27℃ · 없음 · 맑음 · 72 · — · — · 40 | f_summer_basic | summer_swim | normal | dry |
| 빨래 잘 마름 | M | 6월 · 27℃ · 없음 · 맑음 · 72 · — · — · 40 | m_summer_tee | m_summer_surf | normal | dry |
| 빨래 축축함 | F | 7월 · 24℃ · 없음 · 흐림 · 76 · — · — · 85 | f_summer_basic | summer_swim | bad | damp |
| 빨래 축축함 | M | 7월 · 24℃ · 없음 · 흐림 · 76 · — · — · 85 | m_summer_tee | m_summer_surf | bad | damp |
| 빨래 얼음 경계 -5℃ | F | 1월 · -5℃ · 없음 · 맑음 · 58 · — · — · — | f_winter_padding | winter_cold | comfort | frozen |
| 빨래 얼음 경계 -5℃ | M | 1월 · -5℃ · 없음 · 맑음 · 58 · — · — · — | m_winter_padding | m_winter_cold | comfort | frozen |
| 빨래 안 얼음 경계 -4℃ | F | 1월 · -4℃ · 없음 · 맑음 · 58 · — · — · — | f_winter_padding | winter_onsen | comfort | dry |
| 빨래 안 얼음 경계 -4℃ | M | 1월 · -4℃ · 없음 · 맑음 · 58 · — · — · — | m_winter_padding | m_winter_ski | comfort | dry |
| 빨래 얼음 | F | 1월 · -11℃ · 눈 · 흐림 · 55 · — · — · 60 | f_winter_longpadding | winter_cold | comfort | frozen |
| 빨래 얼음 | M | 1월 · -11℃ · 눈 · 흐림 · 55 · — · — · 60 | m_winter_padding | m_winter_cold | comfort | frozen |
