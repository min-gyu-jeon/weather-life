(() => {
    let version = 0;
    let rulesPromise;

    const getRules = () => {
        if (!rulesPromise) {
            rulesPromise = fetch(
                "/weather/rules/weather_character_rules.json"
            ).then(response => {
                if (!response.ok) throw new Error("운동 선택표 요청 실패");
                return response.json();
            }).catch(error => {
                rulesPromise = null;
                throw error;
            });
        }
        return rulesPromise;
    };

    const card = () => document.querySelector(".wl-exercise");

    const clear = (message) => {
        version++;
        const box = card();
        if (!box) return;

        const video = box.querySelector("video.wl-life-character");
        if (video) {
            video.pause();
            video.hidden = true;
        }

        box.querySelector(".wl-exercise-options").replaceChildren();
        box.querySelector(".wl-life-headline").textContent = message;
        box.querySelector(".wl-life-desc").textContent = "";
    };

    window.addEventListener("outfit-weather-loading", () => {
        clear("추천 활동을 불러오는 중이에요");
    });

    window.addEventListener("outfit-weather-failed", () => {
        clear("날씨 정보가 없어 추천 활동을 표시할 수 없어요");
    });

    window.addEventListener("outfit-weather-ready", async event => {
        const current = ++version;
        const { input, date, time, district } = event.detail;

        try {
            const rules = await getRules();
            if (current !== version) return;

            const result = pickWeatherCharacter({
                month: Number(date.split("-")[1]),
                temp: input.temperature,
                humidity: input.humidity,
                pty: {
                    NONE: "없음",
                    RAIN: "비",
                    SNOW: "눈",
                    MIXED: "비눈"
                }[input.precipitation],
                sky: {
                    SUNNY: "맑음",
                    PARTLY_CLOUDY: "구름많음",
                    CLOUDY: "흐림"
                }[input.sky],
                gender: "F",
                pm: {
                    GOOD: "좋음",
                    NORMAL: "보통",
                    BAD: "나쁨",
                    VERY_BAD: "매우나쁨"
                }[input.airQuality]
            }, rules);

            const activity = result.activity;
            const box = card();
            if (!box) return;

            const visual = box.querySelector(".wl-life-visual");
            const previous = visual.querySelector(".wl-life-character");
            const video = document.createElement("video");

            video.className = "wl-life-character";
            video.autoplay = true;
            video.muted = true;
            video.loop = true;
            video.playsInline = true;
            video.poster = "/weather/" + activity.poster;
            video.setAttribute("aria-label", activity.label);

            const poster = document.createElement("img");
            poster.className = "wl-life-character";
            poster.src = video.poster;
            poster.alt = activity.label;
            poster.onerror = () => {
                if (current !== version) return;
                poster.hidden = true;
                box.querySelector(".wl-life-desc").textContent =
                    "활동 이미지를 불러오지 못했어요.";
            };

            video.addEventListener("error", () => {
                if (current === version && video.isConnected) {
                    video.replaceWith(poster);
                }
            });

            if (previous instanceof HTMLVideoElement) previous.pause();

            if (matchMedia("(prefers-reduced-motion: reduce)").matches) {
                previous.replaceWith(poster);
            } else {
                previous.replaceWith(video);
                video.src = "/weather/" + activity.mp4;
                video.play().catch(() => {
                    // 자동 재생이 막히면 포스터를 표시
                });
            }

            box.querySelector(".wl-exercise-options").replaceChildren();
            box.querySelector(".wl-life-headline").textContent =
                activity.label;
            box.querySelector(".wl-life-desc").textContent =
                `${district} · ${time} 예보에 따른 활동 예시`;

            console.info(
                "[weather-life] 활동 연결:", time, activity.key
            );
        } catch (error) {
            if (current !== version) return;
            clear("추천 활동을 불러오지 못했어요");
            console.warn("[weather-life] 활동 연결 실패:", error.message);
        }
    });
})();