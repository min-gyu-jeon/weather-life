// 참고용 선택 함수. 실제 앱의 날씨 판단과 화면 연결은 팀 코드에서 결정한다.
function pickWeatherCharacter(weather, rules) {
  if (weather?.temp === undefined || weather.temp === null || weather.temp === "") {
    throw new Error("기온(temp) 값이 필요합니다.");
  }
  const codeText = (value, table) => {
    const code = typeof value === "number" || (typeof value === "string" && /^\d+$/.test(value.trim()))
      ? String(value).trim() : null;
    return code === null ? value : (table[code] ?? value);
  };
  const numberOrMissing = value => value === undefined || value === null || value === ""
    ? undefined : Number(value);
  const w = { ...weather };
  w.month = numberOrMissing(w.month) ?? new Date().getMonth() + 1;
  w.temp = Number(w.temp);
  w.di = numberOrMissing(w.di);
  w.uv = numberOrMissing(w.uv);
  w.humidity = numberOrMissing(w.humidity);
  w.gender = w.gender || "F";
  w.occasion = w.occasion || "일상";
  w.pm = w.pm || "";
  w.pty = codeText(w.pty === undefined || w.pty === null || w.pty === "" ? "없음" : w.pty, rules.kma_codes.PTY);
  w.sky = codeText(w.sky === undefined || w.sky === null || w.sky === "" ? "맑음" : w.sky, rules.kma_codes.SKY);
  if (!Number.isInteger(w.month) || w.month < 1 || w.month > 12 ||
      !Number.isFinite(w.temp) || (w.di !== undefined && !Number.isFinite(w.di)) ||
      !["F", "M"].includes(w.gender) || typeof w.pty !== "string" ||
      typeof w.sky !== "string" || typeof w.pm !== "string" ||
      (w.uv !== undefined && !Number.isFinite(w.uv)) ||
      (w.humidity !== undefined && (!Number.isFinite(w.humidity) || w.humidity < 0 || w.humidity > 100)) ||
      !["일상", "출근", "운동"].includes(w.occasion)) {
    throw new Error("날씨 입력값(month/temp/pty/sky/di/gender/occasion/uv/pm/humidity)을 확인하세요.");
  }
  const match = c => (c.min_temp === undefined || w.temp >= c.min_temp) &&
    (c.min_temp_exclusive === undefined || w.temp > c.min_temp_exclusive) &&
    (c.max_temp === undefined || w.temp <= c.max_temp) &&
    (c.sky === undefined || w.sky === c.sky);
  const fromRows = rows => rows.find(row => match(row.when))[w.gender];
  let season = Object.keys(rules.season.months)
    .find(name => rules.season.months[name].includes(w.month));
  if (w.temp >= rules.season.summer_if_temp_at_least) season = "summer";
  if (w.temp <= rules.season.winter_if_temp_at_most) season = "winter";
  const cool = rules.season.cool_summer_outfit;
  const outfitSeason = season === "summer" && w.temp < cool.below_temp
    ? cool.spring_months.includes(w.month) ? "spring"
      : cool.autumn_months.includes(w.month) ? "autumn" : "summer"
    : season;
  const rain = rules.rain.pty_contains_any.some(word => w.pty.includes(word));
  const daily = fromRows(rules.outfit.daily_first_match[outfitSeason]);
  const rainSet = rules.rain.outfit_if_available[outfitSeason]?.[w.gender];
  const occasionSet = rules.outfit.occasion_if_dry[w.occasion]?.[outfitSeason]?.[w.gender];
  const outfitKey = rain ? (rainSet || daily) : (occasionSet || daily);
  const fineDust = w.pm.includes(rules.activity.fine_dust.pm_contains);
  const heatWave = w.temp >= rules.activity.heat_wave.min_temp ||
    (w.di !== undefined && w.di >= rules.activity.heat_wave.min_di);
  const activityKey = rain ? rules.rain.activity[w.gender] :
    fineDust ? rules.activity.fine_dust.activity[w.gender] :
    heatWave ? rules.activity.heat_wave.activity[w.gender] :
    season === "winter" ? fromRows(rules.activity.winter_first_match) :
    rules.activity.by_season[outfitSeason][w.gender];   // 서늘한 여름날은 옷과 같이 봄·가을 액티비티 (10-15: 18℃ 6월에 수영 X)
  const mood = w.di === undefined ? "normal" : rules.sticker.first_match.find(row =>
    row.when.di_below === undefined || w.di < row.when.di_below).stage;
  const sunny = rules.sticker.sunny;
  const sticker = rain ? rules.sticker.rain.replace("{stage}", mood) :
    w.sky === sunny.sky && (w.temp >= sunny.min_temp || w.uv >= sunny.min_uv)
      ? sunny.stage : mood;
  const paths = (kind, key) => Object.fromEntries(Object.entries(rules.files[kind])
    .map(([format, pattern]) => [format, pattern.replaceAll("{key}", key)]));
  const stickerPath = rules.files.sticker.poster
    .replace("{gender}", w.gender.toLowerCase()).replace("{sticker}", sticker);
  // 한파(-5℃ 이하)는 비나 습도보다 먼저 얼음 빨래로 고른다.
  const frozen = w.temp <= rules.laundry.frozen_if_temp_at_most;
  const laundry = frozen ? "frozen" :
    rain ? "damp" :
    w.humidity !== undefined && w.humidity >= rules.laundry.damp_if_humidity_at_least ? "damp" :
    w.humidity === undefined && w.sky === rules.laundry.damp_if_humidity_missing_and_sky ? "damp" :
    rules.laundry.default;
  return {
    season, rain, fineDust, heatWave,
    outfit: { key: outfitKey, ...paths("outfit", outfitKey) },
    activity: { key: activityKey, label: rules.labels.activity[activityKey], ...paths("activity", activityKey) },
    sticker: { key: sticker, label: rules.labels.sticker[sticker], poster: stickerPath },
    laundry: { key: laundry, label: rules.labels.laundry[laundry], ...paths("laundry", laundry) }
  };
}

if (typeof module !== "undefined") module.exports = { pickWeatherCharacter };
if (typeof require !== "undefined" && require.main === module) {
  const fs = require("fs");
  const path = require("path");
  const rules = JSON.parse(fs.readFileSync(path.join(__dirname, "weather_character_rules.json"), "utf8"));
  const samples = JSON.parse(fs.readFileSync(path.join(__dirname, "samples.json"), "utf8"));
  console.log("| 예시 | 성별 | 입력 (월·기온·강수·하늘·DI·UV·PM·습도) | 착장 set | 활동 | 스티커 | 빨래 |");
  console.log("|---|---|---|---|---|---|---|");
  for (const sample of samples) for (const gender of ["F", "M"]) {
    const w = { ...sample.weather, gender };
    const r = pickWeatherCharacter(w, rules);
    console.log(`| ${sample.name} | ${gender} | ${w.month ?? "오늘"}월 · ${w.temp}℃ · ${w.pty ?? "—"} · ${w.sky ?? "—"} · ${w.di ?? "—"} · ${w.uv ?? "—"} · ${w.pm || "—"} · ${w.humidity ?? "—"} | ${r.outfit.key} | ${r.activity.key} | ${r.sticker.key} | ${r.laundry.key} |`);
  }
}
