/* 옷 추천 API 결과 1개(outfit) → 보여 줄 착장 세트(캐릭터 그림) + 옷 아이콘 목록.
 * map = outfit_visual_map.json 내용 (브라우저 미리보기에서는 window.OUTFIT_VISUAL_MAP)
 * gender = "F" | "M"
 * 반환 = { setKey, set, score, outerKind, lower, sport, rain, icons: [{slot, slotLabel, id, name, fullName, iconKey, iconLabel, iconFile, usage}] }
 * 세트 고르기 = 같은 성별 세트 중 백엔드 결과와 가장 많이 겹치는 것 (점수는 build_map.py howTo 참고)
 */
(function (root) {
  var SLOTS = [
    ["outer", "아우터"], ["top", "상의"], ["innerTop", "이너"], ["onePiece", "원피스"],
    ["bottom", "하의"], ["baseLayer", "내의"], ["shoes", "신발"]
  ];
  var SLOT_W = { top: 2, bottom: 2, onePiece: 2, outer: 2, shoes: 1 };

  // 칸별 id → 비교용 특징
  function features(ids, items) {
    var outerId = ids.outer, f = { icon: {}, id: {}, outerKind: "NONE", lower: "PANTS", sport: false, rain: false };
    Object.keys(ids).forEach(function (slot) {
      var info = items[ids[slot]];
      if (!info) return;
      f.icon[slot] = info.icon; f.id[slot] = ids[slot];
      if (info.sport) f.sport = true;
      if (info.icon === "rain" || info.icon === "rain_sneakers") f.rain = true;
    });
    if (outerId && items[outerId]) f.outerKind = items[outerId].outerKind || "THIN";
    var low = items[ids.onePiece] || items[ids.bottom];
    if (low && low.lower) f.lower = low.lower;
    return f;
  }

  function score(a, b) {
    var s = 0;
    if (a.outerKind === b.outerKind) s += 4;
    if (a.lower === b.lower) s += 4;
    if (a.sport === b.sport) s += a.sport ? 3 : 0;
    if (a.rain === b.rain) s += a.rain ? 3 : 0;
    Object.keys(SLOT_W).forEach(function (slot) {
      if (a.icon[slot] && a.icon[slot] === b.icon[slot]) s += SLOT_W[slot];
      if (a.id[slot] && a.id[slot] === b.id[slot]) s += 1;
    });
    return s;
  }

  function pickOutfitVisual(outfit, gender, map) {
    gender = gender === "M" ? "M" : "F";
    var items = map.items, icons = [], ids = {};
    SLOTS.forEach(function (s) {
      var it = outfit[s[0]];
      if (!it || !it.id) return;
      // 아우터를 입지 않고 챙기기만 하면 그림 고를 때는 빼고 아이콘에만 표시
      if (!(s[0] === "outer" && outfit.outerUsage && outfit.outerUsage !== "WEAR")) ids[s[0]] = it.id;
      var info = items[it.id];
      var iconKey = info ? info.icon : null;
      icons.push({
        slot: s[0], slotLabel: s[1], id: it.id,
        name: (info && info.short) || it.name || it.id,   // 화면용 짧은 이름 (예: 방한화)
        fullName: it.name || (info && info.name) || it.id,
        iconKey: iconKey,
        iconLabel: iconKey ? map.icons[iconKey].label : "모르는 옷",
        iconFile: iconKey ? map.icons[iconKey].file : null,
        usage: s[0] === "outer" ? (outfit.outerUsage || "WEAR") : null
      });
    });
    var want = features(ids, items);
    if (gender === "M" && (want.lower === "SKIRT" || want.lower === "ONEPIECE")) want.lower = "PANTS";
    var best = null, bestScore = -1;
    Object.keys(map.sets).forEach(function (k) {
      var st = map.sets[k];
      if (st.gender !== gender) return;
      var sc = score(want, features(st.items, items)) + (st.status === "ready" ? 0.5 : 0);
      if (sc > bestScore) { bestScore = sc; best = k; }
    });
    return { setKey: best, set: map.sets[best], score: bestScore, outerKind: want.outerKind, lower: want.lower,
             sport: want.sport, rain: want.rain, icons: icons };
  }

  /* 날씨 값 → 소품 목록 (기준 초안 = accessories.py · map.accessories.items[*].rule 과 같아야 함)
   * weather = { temp, tempMin, tempMax, sky, pty, pop, precip, humidity, wind, di, pm }  (없는 값은 무시)
   * outfit  = 백엔드 결과 1개 (운동복·아우터 챙기기 판단용, 없어도 됨)
   * 반환 = [{ key, label, file, why }]  — 중요한 것부터, 기본 3개(비·미세먼지 날은 4개). max를 주면 그 개수 */
  function pickAccessories(weather, outfit, map, max) {
    var w = weather || {}, t = w.temp, has = function (v) { return typeof v === "number" && !isNaN(v); };
    // 우산은 비(비·비눈·빗방울)일 때만 — 눈만 오는 한파에는 필요 없음 (동업자 10-14)
    var wet = /비/.test(w.pty || ""), sunny = /맑/.test(w.sky || ""), fair = sunny || /구름/.test(w.sky || "");
    var sport = false, carry = false, wearing = !!(outfit && outfit.outer && (!outfit.outerUsage || outfit.outerUsage === "WEAR"));
    if (outfit && map) {
      ["top", "bottom", "onePiece", "outer", "shoes"].forEach(function (s) {
        var it = outfit[s]; if (it && map.items[it.id] && map.items[it.id].sport) sport = true;
      });
      carry = !!(outfit.outer && outfit.outerUsage && outfit.outerUsage !== "WEAR");
    }
    var R = [
      ["mask", /나쁨/.test(w.pm || ""), "미세먼지 " + w.pm],
      ["umbrella", wet, (w.pty || "") + " 예보"],
      ["rain_boots", has(w.precip) && w.precip >= 10, "강수량 " + w.precip + "mm"],
      ["folding_umbrella", !wet && has(w.pop) && w.pop >= 40, "강수확률 " + w.pop + "%"],
      ["hotpack", has(t) && t <= -5, t + "℃"],
      ["gloves", has(t) && t <= 0, t + "℃"],
      ["scarf", has(t) && t <= 5, t + "℃"],
      ["beanie", has(t) && (t <= 0 || (t <= 5 && has(w.wind) && w.wind >= 5)), "추위·바람"],
      ["earmuffs", has(t) && (t <= -5 || (t <= 3 && has(w.wind) && w.wind >= 8)), "한파·강풍"],
      ["thermos", has(t) && t <= 3, t + "℃"],
      ["fan", (has(t) && t >= 30) || (has(w.di) && w.di >= 80), "더위"],
      ["water_bottle", (has(t) && t >= 28) || sport, sport ? "운동" : t + "℃"],
      ["parasol", sunny && has(t) && t >= 28, "맑고 더움"],
      ["cool_sleeve", has(t) && t >= 30, t + "℃"],
      ["cap", sunny && has(t) && t >= 25, "햇빛"],
      ["sunglasses", sunny && has(t) && t >= 20, "햇빛"],
      ["sunscreen", fair && has(t) && t >= 18, "자외선"],
      // 이미 아우터를 입고 있으면 「겉옷 챙기기」는 안 띄움
      ["light_outer", carry || (!wearing && has(w.tempMax) && has(w.tempMin) && w.tempMax - w.tempMin >= 10), carry ? "겉옷 챙기기" : "일교차 큼"],
      ["lip_balm", has(w.humidity) && w.humidity <= 35, "건조함"]
    ];
    var items = (map && map.accessories) ? map.accessories.items : {};
    // 개수: 기본 3개, 비·미세먼지처럼 꼭 챙길 것이 있는 날만 4개 (동업자 「추천은 1~3개 많으면 4개정도」). 목록 순서 = 중요한 순서
    var hit = R.filter(function (r) { return r[1] && items[r[0]]; });
    var must = hit.some(function (r) { return r[0] === "mask" || r[0] === "umbrella"; });
    return hit.slice(0, max || (must ? 4 : 3)).map(function (r) {
      return { key: r[0], label: items[r[0]].label, file: items[r[0]].file, why: r[2] };
    });
  }

  root.pickOutfitVisual = pickOutfitVisual;
  root.pickAccessories = pickAccessories;
  if (typeof module !== "undefined") { module.exports = pickOutfitVisual; module.exports.pickAccessories = pickAccessories; }
})(typeof window !== "undefined" ? window : globalThis);
