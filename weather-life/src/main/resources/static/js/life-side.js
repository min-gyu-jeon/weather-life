(() => {
    let version = 0;
    let rulesPromise;

    const getRules = () => {
        if (!rulesPromise) {
            rulesPromise = fetch(
                "/weather/rules/weather_character_rules.json"
            ).then(response => {
                if (!response.ok) throw new Error("빨래 선택표 요청 실패");
                return response.json();
            }).catch(error => {
                rulesPromise = null;
                throw error;
            });
        }
        return rulesPromise;
    };

    const reset = message => {
        version++;

        const list = document.querySelector(".wl-belongings-list");
        const image = document.querySelector(".wl-laundry-image");
        const status = document.querySelector(".wl-laundry-status");

        if (list) {
            const li = document.createElement("li");
            li.textContent = message;
            list.replaceChildren(li);
        }

        if (image) image.hidden = true;

        if (status) {
            status.className = "wl-laundry-status";
            status.textContent = message;
        }
    };

    // 복장/운동 박스 높이를 외출 준비물 + 빨래 건조 전망 칸(wl-life-side)의 실제 높이에 맞춘다.
    // 데이터에 따라 준비물 개수·문구 길이가 바뀌므로 높이를 고정값으로 두지 않고 매번 측정한다.
    const syncLifeCardHeights = () => {
        const side = document.querySelector(".wl-life-side");
        const outfit = document.querySelector(".wl-outfit");
        const exercise = document.querySelector(".wl-exercise");
        if (!side || !outfit || !exercise) return;

        outfit.style.height = "";
        exercise.style.height = "";

        const targetHeight = Math.round(side.getBoundingClientRect().height);
        if (targetHeight <= 0) return;

        outfit.style.height = `${targetHeight}px`;
        exercise.style.height = `${targetHeight}px`;
    };

    if (typeof ResizeObserver !== "undefined") {
        window.addEventListener("DOMContentLoaded", () => {
            const side = document.querySelector(".wl-life-side");
            if (side) new ResizeObserver(syncLifeCardHeights).observe(side);
        });
    }
    window.addEventListener("load", syncLifeCardHeights);
    window.addEventListener("resize", syncLifeCardHeights);

    window.addEventListener("outfit-weather-loading", () => {
        reset("불러오는 중이에요");
    });

    window.addEventListener("outfit-weather-failed", () => {
        reset("예보 정보를 불러오지 못했어요");
    });

    window.addEventListener("outfit-weather-ready", async event => {
        const current = ++version;
        const { input, outfit, date, time, district } = event.detail;

        const list = document.querySelector(".wl-belongings-list");
        const image = document.querySelector(".wl-laundry-image");
        const status = document.querySelector(".wl-laundry-status");
        if (!list || !image || !status) return;

        // 외출 준비물: 서버가 추천한 아이콘과 이름 사용
        const accessories = outfit.accessoryItems ?? [];
        const fragment = document.createDocumentFragment();

        accessories.forEach(item => {
            const li = document.createElement("li");
            const frame = document.createElement("span");
            const icon = document.createElement("img");
            const name = document.createElement("span");

            frame.className = "wl-belongings-icon";
            icon.src = item.iconPath;
            icon.alt = "";
            icon.onerror = () => { icon.hidden = true; };
            name.textContent = item.name;
            li.title = item.reason || item.name;

            frame.appendChild(icon);
            li.append(frame, name);
            fragment.appendChild(li);
        });

        if (!accessories.length) {
            const li = document.createElement("li");
            li.textContent = "추가로 추천된 준비물이 없어요";
            fragment.appendChild(li);
        }

        list.replaceChildren(fragment);

        try {
            const precipitation = {
                NONE: "없음",
                RAIN: "비",
                SNOW: "눈",
                MIXED: "비눈"
            }[input.precipitation];

            const sky = {
                SUNNY: "맑음",
                PARTLY_CLOUDY: "구름많음",
                CLOUDY: "흐림"
            }[input.sky];

            if (!precipitation || !sky ||
                input.temperature == null ||
                !Number.isFinite(Number(input.temperature))) {
                throw new Error("빨래 판단에 필요한 예보가 없습니다.");
            }

            const rules = await getRules();
            if (current !== version) return;

            const result = pickWeatherCharacter({
                month: Number(date.split("-")[1]),
                temp: Number(input.temperature),
                humidity: input.humidity,
                pty: precipitation,
                sky,
                gender: "F"
            }, rules);

            // 눈도 실외 건조에 불리한 강수로 처리
            const key = precipitation === "눈" &&
                result.laundry.key !== "frozen"
                ? "damp" : result.laundry.key;

            const states = {
                dry: {
                    text: "건조에 비교적 유리해요",
                    file: "laundry_dry.png"
                },
                damp: {
                    text: "실외 건조가 더딜 수 있어요",
                    file: "laundry_damp.png"
                },
                frozen: {
                    text: "빨래가 얼 수 있어요",
                    file: "laundry_frozen.png"
                }
            };

            const state = states[key];
            if (!state) throw new Error("빨래 상태를 확인할 수 없습니다.");

            image.onload = () => {
                if (current === version) image.hidden = false;
            };
            image.onerror = () => {
                if (current !== version) return;
                image.hidden = true;
            };
            image.alt = state.text;
            image.src = "/weather/laundry/" + state.file;

            const label = document.createElement("strong");
            const note = document.createElement("p");

            label.textContent = state.text;
            note.textContent =
                `${district} · ${time} 예보 기준의 참고 상태`;

            status.className = "wl-laundry-status";
            status.replaceChildren(label, note);

            console.info("[weather-life] 준비물·빨래 연결:", time, key);
        } catch (error) {
            if (current !== version) return;
            image.hidden = true;
            status.textContent = "빨래 상태를 판단할 수 없어요";
            console.warn("[weather-life] 빨래 연결 실패:", error.message);
        }
    });
})();