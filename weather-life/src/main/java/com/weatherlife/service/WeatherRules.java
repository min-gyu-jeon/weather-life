package com.weatherlife.service;

import com.weatherlife.dto.OutfitRequest;
import java.util.ArrayList;
import java.util.List;
import static com.weatherlife.dto.OutfitTypes.*;

/** 옷 추천용 경험 보정입니다. 공식 체감온도나 학습 모델의 결과가 아닙니다. */
public final class WeatherRules {
    private WeatherRules() { }
    public record Context(OutfitRequest request, double temperature, double outerTemperature,
                          boolean wet, boolean windy, boolean baseLayerRequired,
                          List<String> advice, List<String> warnings) { }

    public static Context evaluate(OutfitRequest r) {
        boolean wet = r.precipitation() != Precipitation.NONE;
        boolean windy = r.windSpeed() >= 7;
        double t = adjust(r.temperature(), r);
        double outerT = r.minTemperature() == null ? t : adjust(r.minTemperature(), r);
        var advice = new ArrayList<String>();
        var warnings = new ArrayList<String>();
        if (r.precipitation() == Precipitation.RAIN || r.precipitation() == Precipitation.MIXED)
            advice.add("비에 맞는 신발과 필요한 소품을 함께 선택했습니다.");
        if (r.precipitation() == Precipitation.SNOW || r.precipitation() == Precipitation.MIXED)
            advice.add("눈·진눈깨비에는 접지력이 있는 방수 방한화를 선택했습니다.");
        if (windy) advice.add("강풍에는 방풍 겉옷이 있는 고정 세트를 우선합니다.");
        if (r.humidity() >= 70 && r.temperature() >= 23)
            advice.add("덥고 습한 조건은 통풍성을 반영했습니다.");
        if (r.minTemperature() != null && r.maxTemperature() != null
                && r.maxTemperature() - r.minTemperature() >= 10)
            advice.add("현재 날씨에 맞는 세트를 선택하고 일교차는 겉옷 챙기기 안내에 반영합니다.");
        if (r.temperature() < -10 || r.temperature() > 35)
            warnings.add("극단적인 기온입니다. 등록된 의상 세트만으로 충분한 보호를 보장하지 않습니다.");
        if (r.windSpeed() >= 15) warnings.add("매우 강한 바람입니다. 야외활동 여부를 별도로 판단하세요.");
        if (wet && r.windSpeed() >= 10) warnings.add("강풍 때문에 우산 소품을 제외했습니다. 우산 사용에 주의하세요.");
        if (r.occasion() == Occasion.HOME)
            warnings.add("고정 캐릭터 목록에는 실내복 세트가 없습니다. HOME을 포함한 용도 값은 추천을 제한하지 않으며 입력 날씨를 실외 조건으로 처리합니다.");
        return new Context(r, round(t), round(outerT), wet, windy, t <= 5,
                List.copyOf(advice), List.copyOf(warnings));
    }
    private static double adjust(double value, OutfitRequest r) {
        double t = value;
        if (value >= 25 && r.humidity() >= 70) t += Math.min(2, (r.humidity() - 60) / 20);
        if (value >= 20 && r.sky() == Sky.SUNNY) t += 1;
        if (value <= 20 && r.windSpeed() >= 4) t -= Math.min(4, r.windSpeed() * 0.5);
        if (r.thermalPreference() == ThermalPreference.FEEL_COLD) t -= 2;
        if (r.thermalPreference() == ThermalPreference.FEEL_HOT) t += 2;
        return Math.max(-50, Math.min(50, t));
    }
    private static double round(double n) { return Math.round(n * 10) / 10.0; }
}
