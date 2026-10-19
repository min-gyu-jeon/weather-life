(() => {
    let layer;

    function setWeatherEffect(type = "none") {
        if (layer) {
            layer.remove();
            layer = null;
        }

        if (type !== "rain" && type !== "snow") return;

        layer = document.createElement("div");
        layer.className = "weather-effects";
        layer.dataset.effect = type;
        layer.setAttribute("aria-hidden", "true");

        const rain = type === "rain";
        const count = rain ? 65 : 40;
        const fragment = document.createDocumentFragment();

        for (let i = 0; i < count; i++) {
            const particle = document.createElement("span");
            const duration = rain
                ? 0.7 + Math.random() * 0.6
                : 5 + Math.random() * 5;

            particle.className = "weather-particle";
            particle.style.left = `${Math.random() * 100}%`;
            particle.style.opacity = `${0.4 + Math.random() * 0.6}`;

            particle.style.setProperty("--duration", `${duration}s`);
            particle.style.setProperty(
                "--delay",
                `${-Math.random() * duration}s`
            );
            particle.style.setProperty(
                "--drift",
                `${rain ? -35 : Math.random() * 120 - 60}px`
            );
            particle.style.setProperty(
                "--length",
                `${14 + Math.random() * 14}px`
            );
            particle.style.setProperty(
                "--size",
                `${3 + Math.random() * 5}px`
            );

            fragment.appendChild(particle);
        }

        layer.appendChild(fragment);
        document.body.appendChild(layer);
    }

    window.setWeatherEffect = setWeatherEffect;
})();