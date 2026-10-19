
function getSeasonByMonth(month) {
    if (month >= 3 && month <= 5) {
        return { key: "spring", label: "🌱 봄" };
    }
    if (month >= 6 && month <= 8) {
        return { key: "summer", label: "☀️ 여름" };
    }
    if (month >= 9 && month <= 11) {
        return { key: "autumn", label: "🍂 가을" };
    }
    return { key: "winter", label: "❄️ 겨울" };
}

document.addEventListener("DOMContentLoaded", function () {
    // 한국 시간 기준 오늘 날짜
    const today = new Date();
    const koreaDate = new Intl.DateTimeFormat("en-CA", {
        timeZone: "Asia/Seoul",
        year: "numeric",
        month: "2-digit",
        day: "2-digit"
    }).formatToParts(today);

    const getPart = (type) =>
        koreaDate.find(part => part.type === type).value;

    const year = getPart("year");
    const month = getPart("month");
    const day = getPart("day");

    // 오늘 날짜 고정 표시
    const todayDisplay = document.getElementById("todayDisplay");
    if (todayDisplay) {
        todayDisplay.textContent = `📅 ${year}.${month}.${day}`;
    }

    // 오늘 날짜를 기준으로 계절 자동 설정
    const season = getSeasonByMonth(Number(month));

    document.documentElement.dataset.season = season.key;

    const seasonDisplay = document.getElementById("seasonDisplay");
    if (seasonDisplay) {
        seasonDisplay.textContent = season.label;
    }

    // 자치구 선택 (API 연동은 다음 단계)
    const districtSelect = document.getElementById("districtSelect");

    if (districtSelect) {
        districtSelect.addEventListener("change", function () {
            console.log("선택한 구:", districtSelect.value);
        });
    }
});
