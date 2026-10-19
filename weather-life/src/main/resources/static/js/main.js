// ===== 단기예보(APIController.getShortForecast, GET /api/short) 로 게이지 갱신 =====
// 단기예보 응답에 있는 강수확률(POP)과 풍속(WSD)으로 '강수확률', '바람 세기' 게이지를 채운다.
// 자외선 지수와 미세먼지는 단기예보에 없는 항목이라 목업 값을 그대로 둔다.
// 진행 상황은 브라우저 개발자도구 Console 에 [weather-life] 로 남긴다.
(() => {
    const LOG = '[weather-life]';
    const REGION_PREFIX = '서울특별시 '; // short_range_region.csv 의 "1단계 2단계" 이름 형식
    const GAUGE_COLORS = ['blue', 'green', 'orange', 'red'];

    // 강수확률(%) 단계
    const popLevel = (pop) => {
        if (pop < 30) return { status: '낮음', color: 'blue' };
        if (pop < 60) return { status: '보통', color: 'orange' };
        return { status: '높음', color: 'red' };
    };

    // 풍속(m/s) 단계: 기상청 기준 4 미만 약함, 4~9 약간 강함, 9 이상 강함
    const windLevel = (wsd) => {
        if (wsd < 4) return { status: '약함', color: 'green' };
        if (wsd < 9) return { status: '약간 강함', color: 'orange' };
        return { status: '강함', color: 'red' };
    };

    const pad = (n) => String(n).padStart(2, '0');

    // 현재 시각 이후 가장 가까운 예보 시각의 항목 값을 { POP: '30', WSD: '2.1', ... } 형태로 돌려준다.
    const pickNearestForecast = (items) => {
        const now = new Date();
        const nowKey = `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}${pad(now.getHours())}00`;

        const bySlot = new Map();
        items.forEach((item) => {
            const slot = `${item.fcstDate}${item.fcstTime}`;
            if (!bySlot.has(slot)) bySlot.set(slot, {});
            bySlot.get(slot)[item.category] = item.fcstValue;
        });

        const slots = [...bySlot.keys()].sort();
        const slot = slots.find((s) => s >= nowKey) ?? slots[slots.length - 1];
        return slot ? { slot, values: bySlot.get(slot) } : null;
    };

    const updateGauge = (key, { value, percent, status, color }) => {
        const gauge = document.querySelector(`.wl-gauge[data-gauge="${key}"]`);
        if (!gauge) return;

        gauge.querySelector('.wl-gauge-num').textContent = value;
        gauge.querySelector('.wl-gauge-status').textContent = status;
        gauge.querySelector('.fill').style.strokeDasharray = `${Math.max(0, Math.min(100, percent))} 100`;
        gauge.classList.remove(...GAUGE_COLORS);
        gauge.classList.add(color);
    };

    const loadShortForecast = async (district) => {
        const regionName = REGION_PREFIX + district;
        console.info(LOG, '단기예보 요청:', regionName);

        try {
            const res = await fetch(`/api/short?regionName=${encodeURIComponent(regionName)}`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);

            const data = await res.json();
            const header = data?.response?.header;
            if (header && header.resultCode !== '00') {
                throw new Error(`기상청 응답 오류 ${header.resultCode} ${header.resultMsg}`);
            }

            const items = data?.response?.body?.items?.item ?? [];
            const nearest = pickNearestForecast(items);
            if (!nearest) throw new Error('예보 항목이 비어 있습니다.');

            const { slot, values } = nearest;
            console.info(LOG, `단기예보 수신: 항목 ${items.length}건, 사용 시각 ${slot}`, values);

            const pop = Number(values.POP);
            if (Number.isFinite(pop)) {
                updateGauge('pop', { value: pop, percent: pop, ...popLevel(pop) });
            }

            const wsd = Number(values.WSD);
            if (Number.isFinite(wsd)) {
                // 14m/s 를 게이지 최대치로 본다.
                updateGauge('wind', { value: wsd.toFixed(1), percent: (wsd / 14) * 100, ...windLevel(wsd) });
            }
        } catch (e) {
            console.warn(LOG, '단기예보를 불러오지 못해 기존 값을 유지합니다:', e.message);
        }
    };

    document.addEventListener('DOMContentLoaded', () => {
        const select = document.querySelector('select[name="district"]');
        if (!select) return;

        loadShortForecast(select.value);
        window.loadOutfitCard(select.value);
        select.addEventListener('change', () => {
            loadShortForecast(select.value);
            window.loadOutfitCard(select.value);
        });
    });
})();

// ===== 오늘의 추천 복장(TodayOutfitController, GET /api/outfits/today) 로 '오늘의 추천 복장' 카드 갱신 =====
// weather-unit 캐릭터/아이콘 그림(static/weather/outfits/assets)을 그대로 사용한다.
// 날씨 DB에 오늘 예보가 없거나 요청이 실패하면 템플릿의 목업 내용을 그대로 둔다.
(() => {
    const LOG = '[weather-life]';

    const pad = (n) => String(n).padStart(2, '0');

    // "HH:mm" 키 중 지금 이후 가장 가까운 시각(없으면 마지막 시각)을 고른다.
    const pickNearestHour = (hourlyRecommendations) => {
        const keys = Object.keys(hourlyRecommendations ?? {}).sort();
        if (keys.length === 0) return null;
        const now = new Date();
        const nowKey = `${pad(now.getHours())}:${pad(now.getMinutes())}`;
        const key = keys.find((k) => k >= nowKey) ?? keys[keys.length - 1];
        return { key, outfitResponse: hourlyRecommendations[key] };
    };

    // 날씨 조건에 맞춘 헤드라인/설명 문구. 백엔드 reasons는 기술 설명이라 화면 문구는 여기서 만든다.
    const buildOutfitCopy = (input, setName) => {
        const precipitation = input?.precipitation;
        const sky = input?.sky;
        const temperature = input?.temperature;

        if (precipitation === 'RAIN' || precipitation === 'MIXED') {
            return { title: '비 오는 날은 방수 아이템이 좋아요!', description: '우산과 방수 아이템으로<br>비에도 쾌적하게 외출하세요.' };
        }
        if (precipitation === 'SNOW') {
            return { title: '눈 오는 날은 미끄럼 방지가 중요해요!', description: '방한 신발과 따뜻한 겉옷으로<br>눈길도 안전하게 다녀오세요.' };
        }
        if (typeof temperature === 'number' && temperature >= 28) {
            return { title: '더운 날엔 가볍고 시원하게 입으세요!', description: '통풍 잘 되는 옷으로<br>더위를 가볍게 이겨내세요.' };
        }
        if (typeof temperature === 'number' && temperature <= 5) {
            return { title: '쌀쌀한 날엔 든든하게 챙겨 입으세요!', description: '보온 아이템을 더해<br>포근하게 외출하세요.' };
        }
        if (sky === 'SUNNY') {
            return { title: '맑은 날, 오늘의 추천 옷차림이에요!', description: `${setName}로<br>가볍게 하루를 시작해보세요.` };
        }
        return { title: '오늘 날씨엔 이 옷차림이 딱이에요!', description: `${setName}로<br>편안한 하루 보내세요.` };
    };

    // 아우터(없으면 상의) + 소품을 최대 4개까지, 모자라면 신발로 채운다.
    const pickDisplayItems = (outfit) => {
        const items = [];
        const main = outfit.outer ?? outfit.top ?? outfit.onePiece;
        if (main) items.push({ name: main.name, image: main.iconPath });
        (outfit.accessoryItems ?? []).forEach((a) => items.push({ name: a.name, image: a.iconPath }));
        if (items.length < 4 && outfit.shoes) items.push({ name: outfit.shoes.name, image: outfit.shoes.iconPath });
        return items.slice(0, 4);
    };

    const renderOutfitCard = (outfitResponse) => {
        const outfit = outfitResponse?.outfits?.[0];
        if (!outfit) return;

        const characterImg = document.getElementById('wl-outfit-character');
        if (characterImg && outfit.visual?.posterPath) {
            characterImg.src = outfit.visual.posterPath;
            characterImg.alt = outfit.setName ? `${outfit.setName} 캐릭터` : '추천 복장 캐릭터';
        }

        const itemsList = document.getElementById('wl-outfit-items');
        if (itemsList) {
            itemsList.replaceChildren();
            pickDisplayItems(outfit).forEach(({ name, image }) => {
                const li = document.createElement('li');
                const img = document.createElement('img');
                img.src = image;
                img.alt = name;
                img.title = name;
                li.appendChild(img);
                itemsList.appendChild(li);
            });
        }

        const { title, description } = buildOutfitCopy(outfitResponse.input, outfit.setName);
        const headline = document.getElementById('wl-outfit-headline');
        if (headline) headline.textContent = title;
        const desc = document.getElementById('wl-outfit-desc');
        if (desc) desc.innerHTML = description;
    };

    const loadOutfitCard = async (district) => {
        console.info(LOG, '오늘의 추천 복장 요청:', district);
        try {
            const res = await fetch(`/api/outfits/today?gu=${encodeURIComponent(district)}`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);

            const data = await res.json();
            const picked = pickNearestHour(data?.hourlyRecommendations);
            if (!picked) throw new Error('추천 가능한 시간대가 없습니다.');

            console.info(LOG, `오늘의 추천 복장 수신: 사용 시각 ${picked.key}`);
            renderOutfitCard(picked.outfitResponse);
        } catch (e) {
            console.warn(LOG, '오늘의 추천 복장을 불러오지 못해 기존 값을 유지합니다:', e.message);
        }
    };

    window.loadOutfitCard = loadOutfitCard;
})();

// ===== 오늘의 날씨: 오늘/내일/모레 AI 예측 온도 + 기상청 온도, 불쾌지수 =====
// AI 예측 온도(AiForecastController.forecast, GET /api/weather/ai)와
// 기상청 온도·습도(APIController.getShortForecast, GET /api/short)로 각 카드를 채운다.
// 불쾌지수는 오늘의 AI 예측 온도 + 기상청 습도(REH)로 계산해 온도계 하단에 표시하고,
// 온도계를 0~100 로 보고 그 값의 위치에 /image/icon/bag.svg 마커를 놓는다.
(() => {
    const LOG = '[weather-life]';
    const REGION_PREFIX = '서울특별시 ';
    const DAY_KEYS = ['today', 'tomorrow', 'dayafter'];
    const WEEKDAYS = ['일', '월', '화', '수', '목', '금', '토'];

    const pad = (n) => String(n).padStart(2, '0');
    const kmaDateKey = (d) => `${d.getFullYear()}${pad(d.getMonth() + 1)}${pad(d.getDate())}`;
    const isoDateKey = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
    const formatDateLabel = (d) => `${pad(d.getMonth() + 1)}. ${pad(d.getDate())} (${WEEKDAYS[d.getDay()]})`;
    const formatDiscomfortDate = (d) => `오늘 (${pad(d.getMonth() + 1)}월 ${pad(d.getDate())}일)`;

    // 오늘/내일/모레 날짜(자정 기준)
    const targetDates = () => {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        return DAY_KEYS.map((key, i) => {
            const date = new Date(today);
            date.setDate(date.getDate() + i);
            return { key, date };
        });
    };

    // AiForecastController.forecast 응답: 날짜(yyyy-MM-dd) -> AI 예측 기온
    const fetchAiTemps = async (district) => {
        const res = await fetch(`/api/weather/ai?gu=${encodeURIComponent(district)}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        const byDate = new Map();
        (data?.forecasts ?? []).forEach((f) => {
            if (f?.date) byDate.set(f.date, f.temperatureC);
        });
        return byDate;
    };

    // APIController.getShortForecast 응답: 날짜(yyyyMMdd) -> { TMP:{hhmm:값}, REH:{hhmm:값} }
    const fetchKmaByDate = async (district) => {
        const regionName = REGION_PREFIX + district;
        const res = await fetch(`/api/short?regionName=${encodeURIComponent(regionName)}`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        const header = data?.response?.header;
        if (header && header.resultCode !== '00') {
            throw new Error(`기상청 응답 오류 ${header.resultCode} ${header.resultMsg}`);
        }

        const items = data?.response?.body?.items?.item ?? [];
        const byDate = new Map();
        items.forEach((item) => {
            if (item.category !== 'TMP' && item.category !== 'REH') return;
            if (!byDate.has(item.fcstDate)) byDate.set(item.fcstDate, { TMP: {}, REH: {} });
            byDate.get(item.fcstDate)[item.category][item.fcstTime] = Number(item.fcstValue);
        });
        return byDate;
    };

    // 기준 시각(HHmm) 이후 가장 가까운 시각의 값을 고른다. 없으면 그 날의 마지막 값을 쓴다.
    const pickByHour = (hourMap, nowHourKey) => {
        const hours = Object.keys(hourMap ?? {}).sort();
        if (hours.length === 0) return null;
        const hour = hours.find((h) => h >= nowHourKey) ?? hours[hours.length - 1];
        return hourMap[hour];
    };

    // 기상청 불쾌지수 공식: 0.81*T + 0.01*RH*(0.99*T - 14.3) + 46.3
    const calcDiscomfortIndex = (tempC, humidityPct) =>
        0.81 * tempC + 0.01 * humidityPct * (0.99 * tempC - 14.3) + 46.3;

    // weather_character_rules.json의 sticker.first_match 구간과 동일한 기준(68/75/80)
    const discomfortLevelLabel = (di) => {
        if (di < 68) return '쾌적';
        if (di < 75) return '보통';
        if (di < 80) return '나쁨';
        return '매우 나쁨';
    };

    // /image/icon/expressions/ 의 01~04 표정 아이콘을 불쾌지수 단계에 맞춰 고른다.
    const discomfortExpressionIcon = (di) => {
        if (di < 68) return '/image/icon/expressions_color/01-comfortable.png';
        if (di < 75) return '/image/icon/expressions_color/02-slight-discomfort.png';
        if (di < 80) return '/image/icon/expressions_color/03-uncomfortable.png';
        return '/image/icon/expressions_color/04-very-uncomfortable.png';
    };

    const setField = (scope, field, value) => {
        scope.querySelectorAll(`[data-field="${field}"]`).forEach((el) => {
            el.textContent = value;
        });
    };

    const loadTodayWeather = async (district) => {
        console.info(LOG, '오늘의 날씨 요청:', district);
        try {
            const [aiTemps, kmaByDate] = await Promise.all([fetchAiTemps(district), fetchKmaByDate(district)]);

            const now = new Date();
            const nowHourKey = `${pad(now.getHours())}00`;
            let todayAiTemp = null;
            let todayHumidity = null;

            targetDates().forEach(({ key, date }) => {
                const card = document.querySelector(`[data-day="${key}"]`);
                if (!card) return;

                const aiTemp = aiTemps.get(isoDateKey(date));
                if (typeof aiTemp === 'number' && Number.isFinite(aiTemp)) {
                    setField(card, 'aiTemp', Math.round(aiTemp));
                    if (key === 'today') todayAiTemp = aiTemp;
                }

                const kmaDay = kmaByDate.get(kmaDateKey(date));
                const kmaTemp = pickByHour(kmaDay?.TMP, nowHourKey);
                if (typeof kmaTemp === 'number' && Number.isFinite(kmaTemp)) {
                    setField(card, 'kmaTemp', Math.round(kmaTemp));
                }

                if (key === 'today') {
                    const reh = pickByHour(kmaDay?.REH, nowHourKey);
                    if (typeof reh === 'number' && Number.isFinite(reh)) todayHumidity = reh;

                    const dateEl = card.querySelector('[data-field="dateLabel"]');
                    if (dateEl) dateEl.textContent = formatDateLabel(date);

                    const discomfortDateEl = document.querySelector('[data-field="discomfortDate"]');
                    if (discomfortDateEl) discomfortDateEl.textContent = formatDiscomfortDate(date);
                }
            });

            if (typeof todayAiTemp === 'number' && typeof todayHumidity === 'number') {
                const di = Math.max(0, Math.min(100, calcDiscomfortIndex(todayAiTemp, todayHumidity)));
                const diRounded = Math.round(di);
                setField(document, 'discomfortIndex', diRounded);
                setField(document, 'discomfortLevel', discomfortLevelLabel(di));

                const marker = document.querySelector('[data-field="discomfortMarker"]');
                if (marker) {
                    marker.style.bottom = `${di}%`;
                    marker.src = discomfortExpressionIcon(di);
                }

                console.info(LOG, `불쾌지수 계산: AI 예측 온도 ${todayAiTemp}, 습도 ${todayHumidity} -> ${diRounded}`);
            }
        } catch (e) {
            console.warn(LOG, '오늘의 날씨를 불러오지 못해 기존 값을 유지합니다:', e.message);
        }
    };

    document.addEventListener('DOMContentLoaded', () => {
        const select = document.querySelector('select[name="district"]');
        if (!select) return;

        loadTodayWeather(select.value);
        select.addEventListener('change', () => loadTodayWeather(select.value));
    });
})();
