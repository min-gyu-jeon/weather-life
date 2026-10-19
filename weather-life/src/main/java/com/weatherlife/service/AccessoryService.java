package com.weatherlife.service;

import com.weatherlife.dto.OutfitResponse.AccessoryItem;
import com.weatherlife.dto.OutfitTypes.*;
import org.springframework.stereotype.Service;

import java.time.LocalTime;
import java.util.ArrayList;
import java.util.List;

/** 예보 조건에 필요한 소품만 반환합니다. 빈 목록도 정상입니다. */
@Service
public class AccessoryService {
    private final AccessoryCatalog catalog;

    public AccessoryService(AccessoryCatalog catalog) {
        this.catalog = catalog;
    }

    public List<AccessoryItem> select(
            WeatherRules.Context ctx,
            OutfitSetCatalog.Definition set,
            OuterUsage outerUsage) {
        return select(ctx, set, outerUsage, null);
    }

    public List<AccessoryItem> select(
            WeatherRules.Context ctx,
            OutfitSetCatalog.Definition set,
            OuterUsage outerUsage,
            LocalTime forecastTime) {

        var r = ctx.request();
        double t = r.temperature();

        // 서비스용 고정 시간대 기준이며 실제 일출·일몰 계산은 아닙니다.
        boolean daytime = forecastTime != null
                && forecastTime.getHour() >= 6
                && forecastTime.getHour() < 18;

        boolean rain = r.precipitation() == Precipitation.RAIN
                || r.precipitation() == Precipitation.MIXED;
        boolean sunny = r.sky() == Sky.SUNNY && !ctx.wet();

        var result = new ArrayList<AccessoryItem>();

        if (rain && r.windSpeed() < 10) {
            add(result, "umbrella", "비 또는 진눈깨비 예보가 있습니다.");
        } else if (!ctx.wet() && r.windSpeed() < 10
                && r.precipitationProbability() != null
                && r.precipitationProbability() >= 40) {
            add(result, "folding_umbrella", "강수확률이 40% 이상입니다.");
        }

        if (rain && r.precipitationAmount() != null
                && r.precipitationAmount() >= 10) {
            add(result, "rain_boots",
                    "시간당 강수량이 10mm 이상이어서 장화를 고려하세요.");
        }

        if (daytime && sunny && t >= 28 && !ctx.windy()) {
            add(result, "parasol", "낮 시간의 맑고 더운 예보에 대비합니다.");
        }

        if (daytime && sunny && t >= 20) {
            add(result, "sunglasses", "낮 시간 맑은 예보의 눈부심 대비용입니다.");
        }

        if (daytime && !ctx.wet() && r.sky() != Sky.CLOUDY && t >= 18) {
            add(result, "sunscreen",
                    "낮 시간 외출 준비용입니다. 자외선 예측값을 사용한 추천은 아닙니다.");
        }

        if (daytime && sunny && t >= 25 && !ctx.windy()) {
            add(result, "cap", "낮 시간의 맑고 더운 예보에 대비합니다.");
        }

        Double di = DiscomfortIndexCalculator.calculate(
                r.temperature().toString(), r.humidity().toString());

        if (t >= 30 || (di != null && di >= 80)) {
            add(result, "fan", "높은 기온 또는 불쾌지수에 대비합니다.");
        }

        if (t >= 25 || r.occasion() == Occasion.EXERCISE
                || set.tags().contains("SPORT")) {
            add(result, "water_bottle",
                    "25℃ 이상이거나 운동 목적의 외출입니다.");
        }

        if (t >= 30) {
            add(result, "cool_sleeve", "30℃ 이상의 더운 날에 사용할 수 있습니다.");
        }

        boolean hasRange = r.minTemperature() != null
                && r.maxTemperature() != null;

        boolean wideRange = hasRange
                && r.maxTemperature() - r.minTemperature() >= 8;

        boolean coolMorningEvening = hasRange
                && r.minTemperature() <= 18
                && r.maxTemperature() - r.minTemperature() >= 5;

        if (outerUsage == OuterUsage.CARRY
                || (outerUsage == OuterUsage.NONE
                    && (wideRange || coolMorningEvening))) {
            add(result, "light_outer",
                    "최저기온과 일교차에 대비해 별도로 겉옷을 챙기세요.");
        }

        if (t <= 5) {
            add(result, "scarf", "5℃ 이하의 추위에 대비합니다.");
        }
        if (t <= 0) {
            add(result, "gloves", "0℃ 이하의 추위에 대비합니다.");
        }
        if (t <= 0 || (t <= 5 && r.windSpeed() >= 5)) {
            add(result, "beanie", "낮은 기온과 찬바람에 대비합니다.");
        }
        if (t <= -5 || (t <= 3 && r.windSpeed() >= 8)) {
            add(result, "earmuffs", "매우 춥거나 찬바람이 강합니다.");
        }
        if (t <= -5) {
            add(result, "hotpack", "-5℃ 이하의 추위에 대비합니다.");
        }
        if (t <= 3) {
            add(result, "thermos", "따뜻한 음료를 챙길 수 있습니다.");
        }
        if (r.humidity() <= 35) {
            add(result, "lip_balm", "습도 35% 이하의 건조한 날입니다.");
        }
        if (r.airQuality() == AirQuality.BAD
                || r.airQuality() == AirQuality.VERY_BAD) {
            add(result, "mask", "미세먼지 등급이 나쁨 이상입니다.");
        }

        return List.copyOf(result);
    }

    private void add(List<AccessoryItem> result, String key, String reason) {
        var item = catalog.item(key);
        result.add(new AccessoryItem(
                item.key(), item.name(), item.iconPath(), reason));
    }
}