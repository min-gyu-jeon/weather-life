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

// ===== AI 예측 대상 시각에 가장 가까운 기상청 DB 예보로 오늘/내일/모레 비교 =====
// AI: /api/weather/ai, 기상청: /api/weather/short?gu=...&date=...
// validTimeKst의 실제 UTC offset을 해석하고, DB의 forecastAt은 한국 시간으로 처리합니다.
(() => {
    const LOG = '[weather-life]';
    const KST_OFFSET_MS = 9 * 60 * 60 * 1000;
    const DAY_MS = 24 * 60 * 60 * 1000;
    const DAY_KEYS = ['today', 'tomorrow', 'dayafter'];
    const WEEKDAYS = ['일', '월', '화', '수', '목', '금', '토'];
    let latestRequest = 0;
    let activeController;

    const pad = (n) => String(n).padStart(2, '0');
    const numericValue = (value) => {
        if (!['number', 'string'].includes(typeof value) || String(value).trim() === '') return null;
        const number = Number(value);
        return Number.isFinite(number) ? number : null;
    };

    // AI에는 Z 또는 +09:00 같은 offset이 필수입니다. DB의 LocalDateTime에만 +09:00을 붙입니다.
    const parseForecastTime = (value, assumeKst = false) => {
        if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}/.test(value)) return null;
        const hasOffset = /(?:Z|[+-]\d{2}:\d{2})$/i.test(value);
        if (!hasOffset && !assumeKst) return null;
        const timestamp = Date.parse(hasOffset ? value : `${value}+09:00`);
        return Number.isFinite(timestamp) ? timestamp : null;
    };

    // 브라우저/PC 시간대 설정과 무관하게 한국 날짜·시각을 만듭니다.
    const kstParts = (timestamp) => {
        const date = new Date(timestamp + KST_OFFSET_MS);
        return {
            date: `${date.getUTCFullYear()}-${pad(date.getUTCMonth() + 1)}-${pad(date.getUTCDate())}`,
            time: `${pad(date.getUTCHours())}:${pad(date.getUTCMinutes())}`,
            weekday: WEEKDAYS[date.getUTCDay()]
        };
    };
    const shiftDate = (date, days) =>
        kstParts(Date.parse(`${date}T00:00:00+09:00`) + days * DAY_MS).date;
    const neighboringDates = (date) => [-1, 0, 1].map((offset) => shiftDate(date, offset));
    const targetDates = () => {
        const today = kstParts(Date.now()).date;
        return DAY_KEYS.map((key, offset) => ({ key, date: shiftDate(today, offset) }));
    };

    const fetchAiForecasts = async (district, signal) => {
        const params = new URLSearchParams({ gu: district });
        const response = await fetch(`/api/weather/ai?${params}`, { signal });
        if (!response.ok) throw new Error(`AI 예측 조회 실패 (HTTP ${response.status})`);
        const data = await response.json();
        if (!Array.isArray(data?.forecasts)) throw new Error('AI 예측 목록이 없습니다.');

        const byDate = new Map();
        data.forecasts.forEach((forecast) => {
            const temperature = numericValue(forecast?.temperatureC);
            if (temperature === null) return;
            const timestamp = parseForecastTime(forecast?.validTimeKst);
            // date 필드보다 실제 예측 대상 시각의 한국 날짜를 우선합니다.
            const date = timestamp === null ? forecast?.date : kstParts(timestamp).date;
            if (!date) return;
            const previous = byDate.get(date);
            // 날짜별 여러 값이 온 경우 유효한 시각 중 가장 이른 값을 일관되게 선택합니다.
            if (!previous || (timestamp !== null &&
                    (previous.timestamp === null || timestamp < previous.timestamp))) {
                byDate.set(date, { temperature, timestamp });
            }
        });
        return byDate;
    };

    const fetchKmaDay = async (district, date, signal) => {
        const params = new URLSearchParams({ gu: district, date });
        const response = await fetch(`/api/weather/short?${params}`, { signal });
        // 전날 정리 또는 아직 수집되지 않은 날짜는 정상적인 데이터 부재로 취급합니다.
        if (response.status === 404) return [];
        if (!response.ok) throw new Error(`기상청 예보 조회 실패 (${date}, HTTP ${response.status})`);
        const data = await response.json();
        if (data?.date !== date || !Array.isArray(data?.hourly)) {
            throw new Error(`기상청 예보 응답 형식이 올바르지 않습니다. (${date})`);
        }
        return data.hourly.flatMap((hour) => {
            const timestamp = parseForecastTime(hour?.forecastAt, true);
            const temperature = numericValue(hour?.temperature);
            if (timestamp === null || temperature === null || kstParts(timestamp).date !== date) return [];
            return [{ timestamp, temperature, humidity: numericValue(hour.humidity) }];
        });
    };

    // 시각 차이의 절댓값으로 비교합니다. 차이가 같으면 앞선 예보 시각을 선택합니다.
    const pickNearestForecast = (hours, targetTimestamp) => hours.reduce((best, hour) => {
        const difference = Math.abs(hour.timestamp - targetTimestamp);
        if (!best || difference < best.difference ||
                (difference === best.difference && hour.timestamp < best.timestamp)) {
            return { ...hour, difference };
        }
        return best;
    }, null);

    const setField = (scope, field, value) => {
        scope.querySelectorAll(`[data-field="${field}"]`).forEach((element) => {
            element.textContent = value;
        });
    };
    const setComparison = (card, text, detail = text) => {
        setField(card, 'comparisonTime', text);
        const label = card.querySelector('[data-field="comparisonTime"]');
        if (label) label.title = detail;
    };
    const calcDiscomfortIndex = (tempC, humidityPct) =>
        0.81 * tempC + 0.01 * humidityPct * (0.99 * tempC - 14.3) + 46.3;

    const resetWeather = (dates) => {
        dates.forEach(({ key, date }) => {
            const card = document.querySelector(`[data-day="${key}"]`);
            if (!card) return;
            setField(card, 'aiTemp', '—');
            setField(card, 'kmaTemp', '—');
            setComparison(card, '예보를 불러오는 중');
            delete card.dataset.aiForecastAt;
            delete card.dataset.kmaForecastAt;
            const local = kstParts(Date.parse(`${date}T00:00:00+09:00`));
            setField(card, 'dateLabel', `${date.slice(5, 7)}. ${date.slice(8)} (${local.weekday})`);
        });
        const today = dates[0].date;
        setField(document, 'discomfortDate', `오늘 (${today.slice(5, 7)}월 ${today.slice(8)}일)`);
        setField(document, 'discomfortIndex', '—');
        const marker = document.querySelector('[data-field="discomfortMarker"]');
        if (marker) marker.hidden = true;
    };

    const loadTodayWeather = async (district) => {
        const requestId = ++latestRequest;
        activeController?.abort();
        const controller = new AbortController();
        activeController = controller;
        const { signal } = controller;
        const dates = targetDates();
        resetWeather(dates);

        try {
            const aiByDate = await fetchAiForecasts(district, signal);
            if (requestId !== latestRequest) return;

            const requiredDates = new Set();
            dates.forEach(({ key, date }) => {
                const card = document.querySelector(`[data-day="${key}"]`);
                if (!card) return;
                const ai = aiByDate.get(date);
                if (!ai) {
                    setComparison(card, 'AI 예측 정보 없음');
                    return;
                }
                setField(card, 'aiTemp', Math.round(ai.temperature));
                if (ai.timestamp === null) {
                    setComparison(card, 'AI 예측 시각 확인 불가');
                    return;
                }
                const target = kstParts(ai.timestamp);
                card.dataset.aiForecastAt = `${target.date}T${target.time}`;
                setComparison(card, `AI ${target.time} · 기상청 조회 중`);
                // 자정 전후에는 인접 날짜의 예보가 더 가까울 수 있습니다.
                neighboringDates(date).forEach((day) => requiredDates.add(day));
            });

            const results = await Promise.all([...requiredDates].map(async (date) => {
                try {
                    return { date, hours: await fetchKmaDay(district, date, signal) };
                } catch (error) {
                    if (signal.aborted) throw error;
                    console.warn(LOG, error.message);
                    return { date, hours: [], error };
                }
            }));
            if (requestId !== latestRequest) return;
            const kmaByDate = new Map(results.map((result) => [result.date, result]));

            dates.forEach(({ key, date }) => {
                const card = document.querySelector(`[data-day="${key}"]`);
                const ai = aiByDate.get(date);
                if (!card || !ai || ai.timestamp === null) return;
                const target = kstParts(ai.timestamp);
                // 대상 날짜 조회 자체가 실패하면 다른 날짜로 조용히 대체하지 않습니다.
                if (kmaByDate.get(date)?.error) {
                    setComparison(card, `AI ${target.time} · 기상청 조회 실패`);
                    return;
                }
                const days = neighboringDates(date).map((day) => kmaByDate.get(day));
                const nearest = pickNearestForecast(days.flatMap((day) => day?.hours ?? []), ai.timestamp);
                if (!nearest) {
                    const reason = days.some((day) => day?.error) ? '조회 실패' : '예보 없음';
                    setComparison(card, `AI ${target.time} · 기상청 ${reason}`);
                    return;
                }

                const matched = kstParts(nearest.timestamp);
                const matchedLabel = matched.date === target.date ? matched.time :
                    `${matched.date.slice(5).replace('-', '.')} ${matched.time}`;
                const label = `AI ${target.time} · 기상청 ${matchedLabel} (한국 시간)`;
                const differenceMinutes = Math.round(nearest.difference / 60000);
                const detail = `AI ${target.date} ${target.time} / 기상청 ${matched.date} ${matched.time}` +
                    ` (한국 시간, 차이 ${differenceMinutes}분)`;
                setField(card, 'kmaTemp', Math.round(nearest.temperature));
                setComparison(card, label, detail);
                card.dataset.kmaForecastAt = `${matched.date}T${matched.time}`;

                if (key === 'today' && nearest.humidity !== null &&
                        nearest.humidity >= 0 && nearest.humidity <= 100) {
                    const di = Math.max(0, Math.min(100, calcDiscomfortIndex(ai.temperature, nearest.humidity)));
                    setField(document, 'discomfortIndex', Math.round(di));
                    const marker = document.querySelector('[data-field="discomfortMarker"]');
                    if (marker) {
                        marker.hidden = false;
                        marker.style.bottom = `${di}%`;
                        marker.title = detail;
                    }
                }
                console.info(LOG, '예보 시각 비교:', district, detail);
            });
        } catch (error) {
            if (requestId !== latestRequest || signal.aborted) return;
            dates.forEach(({ key }) => {
                const card = document.querySelector(`[data-day="${key}"]`);
                if (card) setComparison(card, 'AI 예측을 불러오지 못했어요');
            });
            console.warn(LOG, '날씨 비교 조회 실패:', error.message);
        }
    };

    document.addEventListener('DOMContentLoaded', () => {
        const select = document.querySelector('select[name="district"]');
        if (!select) return;
        loadTodayWeather(select.value);
        select.addEventListener('change', () => loadTodayWeather(select.value));
    });
})();
