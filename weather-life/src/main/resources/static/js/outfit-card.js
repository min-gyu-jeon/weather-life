(() => {
    let latestRequest = 0;

    document.addEventListener("DOMContentLoaded", () => {
        const card = document.querySelector(".wl-outfit");
        const select = document.querySelector('select[name="district"]');
        if (!card || !select) return;

        const image = card.querySelector(".wl-life-character");
        const items = card.querySelector(".wl-outfit-items");
        const title = card.querySelector(".wl-life-headline");
        const description = card.querySelector(".wl-life-desc");

        const load = async () => {
            const requestId = ++latestRequest;
            window.dispatchEvent(new Event("outfit-weather-loading"));

            // 이전 지역의 추천을 새 지역의 결과처럼 보여주지 않기
            image.hidden = true;
            items.replaceChildren();
            title.textContent = "추천 복장을 불러오는 중이에요";
            description.textContent = "";

            try {
                const params = new URLSearchParams({
                    gu: select.value,
                    gender: "FEMALE",
                    count: "1"
                });

                const res = await fetch(`/api/outfits/today?${params}`);
                const data = await res.json();

                if (requestId !== latestRequest) return;
                if (!res.ok) {
                    throw new Error(data.message || `HTTP ${res.status}`);
                }

                const parts = new Intl.DateTimeFormat("en-CA", {
                    timeZone: "Asia/Seoul",
                    year: "numeric",
                    month: "2-digit",
                    day: "2-digit",
                    hour: "2-digit",
                    hourCycle: "h23"
                }).formatToParts(new Date());

                const part = (type) =>
                    parts.find(p => p.type === type).value;

                const today = `${part("year")}-${part("month")}-${part("day")}`;
                const hour = `${part("hour")}:00`;

                if (data.date !== today) {
                    throw new Error("오늘 날짜의 추천 정보가 없습니다.");
                }

                const recommendations = data.hourlyRecommendations ?? {};
                const time = Object.keys(recommendations)
                    .sort()
                    .find(time => time >= hour);

                if (!time) {
                    throw new Error("현재 시간 이후의 추천 정보가 없습니다.");
                }

                const recommendation = recommendations[time];
                const outfit = recommendation.outfits?.[0];

                if (!outfit?.visual?.posterPath) {
                    throw new Error("추천 캐릭터 정보가 없습니다.");
                }

                image.onload = () => {
                    if (requestId === latestRequest) image.hidden = false;
                };

                image.onerror = () => {
                    if (requestId !== latestRequest) return;
                    image.hidden = true;
                    description.textContent =
                        `${time} 예보 기준 · 캐릭터 이미지를 불러오지 못했어요`;
                };

                image.alt = outfit.setName;
                image.src = outfit.visual.posterPath;

                const clothes = [
                    outfit.baseLayer,
                    outfit.innerTop,
                    outfit.top,
                    outfit.onePiece,
                    outfit.bottom,
                    ...(outfit.outerUsage !== "NONE" ? [outfit.outer] : []),
                    outfit.shoes
                ].filter(item => item?.iconPath);

                const fragment = document.createDocumentFragment();

                clothes.forEach(item => {
                    const li = document.createElement("li");
                    const icon = document.createElement("img");

                    const carry = item === outfit.outer &&
                        outfit.outerUsage !== "WEAR";
                    const name = item.name + (carry ? " (챙기기)" : "");

                    icon.src = item.iconPath;
                    icon.alt = name;
                    icon.title = name;
                    li.appendChild(icon);
                    fragment.appendChild(li);
                });

                items.replaceChildren(fragment);
                title.textContent = outfit.setName;
                description.textContent =
                    `${select.value} · ${time} 예보 기준 · 기온 ${recommendation.input.temperature}°C`;

                console.info("[weather-life] 복장 연결:", time, outfit.setKey);
                window.dispatchEvent(new CustomEvent("outfit-weather-ready", {
    detail: {
    input: recommendation.input,
    outfit,
    date: data.date,
    time,
    district: select.value
}
}));
            } catch (error) {
                if (requestId !== latestRequest) return;
                window.dispatchEvent(new Event("outfit-weather-failed"));

                image.hidden = true;
                items.replaceChildren();
                title.textContent = "추천 복장을 불러오지 못했어요";
                description.textContent = error.message;
                console.warn("[weather-life] 복장 요청 실패:", error.message);
            }
        };

        load();
        select.addEventListener("change", load);
    });
})();