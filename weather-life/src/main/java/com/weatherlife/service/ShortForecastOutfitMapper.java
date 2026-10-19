package com.weatherlife.service;

import com.weatherlife.dto.OutfitRequest;
import com.weatherlife.entity.HourlyForecast;
import com.weatherlife.dto.OutfitTypes.Precipitation;
import com.weatherlife.dto.OutfitTypes.Sky;
import org.springframework.stereotype.Component;

import java.time.LocalDate;
import java.time.LocalTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.concurrent.ThreadLocalRandom;

/** DB에 저장된 예보를 지정 날짜의 시간별 의상 추천 입력으로 변환합니다. */
@Component
public class ShortForecastOutfitMapper {
    private static final DateTimeFormatter OUTPUT_TIME = DateTimeFormatter.ofPattern("HH:mm");

    public record ConversionResult(Map<String, OutfitRequest> hourlyRequests, List<String> skippedHours) { }

    /** DB에서 로드한 정규화된 시간별 행을 그대로 추천용 입력으로 변환합니다. */
    public ConversionResult convertStored(List<HourlyForecast> stored, LocalDate date) {
        TreeMap<LocalTime, Map<String,String>> hourly = new TreeMap<>();
        for (HourlyForecast row : stored) {
            if (row.getForecastAt().toLocalDate().equals(date)) {
                hourly.put(row.getForecastAt().toLocalTime(), row.categories());
            }
        }
        return convertGrouped(hourly, date);
    }

    private ConversionResult convertGrouped(TreeMap<LocalTime, Map<String,String>> hourly, LocalDate date) {
        // TMN/TMX는 매시간 나오지 않습니다. 시간별 TMP 전체 및 TMN/TMX로
        // '조회 날짜의 최저·최고'를 한 번 계산한 다음 모든 시간의 추천에 공통 적용합니다.
        double min = Double.POSITIVE_INFINITY;
        double max = Double.NEGATIVE_INFINITY;
        for (Map<String, String> values : hourly.values()) {
            Double current = parseNumber(values.get("TMP"));
            Double dailyMin = parseNumber(values.get("TMN"));
            Double dailyMax = parseNumber(values.get("TMX"));
            if (current != null) { min = Math.min(min, current); max = Math.max(max, current); }
            if (dailyMin != null) min = Math.min(min, dailyMin);
            if (dailyMax != null) max = Math.max(max, dailyMax);
        }
        Double minTemperature = Double.isFinite(min) ? min : null;
        Double maxTemperature = Double.isFinite(max) ? max : null;

        Map<String, OutfitRequest> result = new LinkedHashMap<>();
        List<String> skipped = new ArrayList<>();
        for (var hour : hourly.entrySet()) {
            String time = hour.getKey().format(OUTPUT_TIME);
            Map<String, String> weather = hour.getValue();
            Double temperature = parseNumber(weather.get("TMP"));
            Double humidity = parseNumber(weather.get("REH"));
            Double windSpeed = parseNumber(weather.get("WSD"));
            Sky sky = toSky(weather.get("SKY"));
            Precipitation rain = toPrecipitation(weather.get("PTY"));

            // 필수 날씨값이 없으면 기본값으로 날씨를 꾸미지 않고 해당 시간만 제외합니다.
            if (temperature == null || humidity == null || windSpeed == null || sky == null || rain == null
                    || temperature < -50 || temperature > 50
                    || humidity < 0 || humidity > 100 || windSpeed < 0 || windSpeed > 60) {
                skipped.add(time);
                continue;
            }
            // 성별·용도·선호도는 null -> OutfitRequest의 기본값 적용.
            // seed도 시간마다 새 난수로 생성하므로 매번 다양한 추천을 만들 수 있습니다.
            OutfitRequest request = new OutfitRequest(
                    temperature, humidity, windSpeed, sky, rain,
                    null, null, null, null,
                    minTemperature, maxTemperature, null,
                    ThreadLocalRandom.current().nextLong(), date,
                    optionalRange(parseNumber(weather.get("POP")), 100),
                    optionalRange(parseRainAmount(weather.get("PCP")), 1000), null
            );
            result.put(time, request);
        }
        return new ConversionResult(Collections.unmodifiableMap(result), List.copyOf(skipped));
    }

    private static Sky toSky(String value) {
        return switch (value == null ? "" : value) {
            case "1" -> Sky.SUNNY;
            case "3" -> Sky.PARTLY_CLOUDY;
            case "4" -> Sky.CLOUDY;
            default -> null;
        };
    }

    private static Precipitation toPrecipitation(String value) {
        // 단기예보의 5~7: 빗방울 / 빗방울눈날림 / 눈날림
        return switch (value == null ? "" : value) {
            case "0" -> Precipitation.NONE;
            case "1", "4", "5" -> Precipitation.RAIN;
            case "2", "6" -> Precipitation.MIXED;
            case "3", "7" -> Precipitation.SNOW;
            default -> null;
        };
    }

    private static Double parseNumber(String value) {
        if (value == null || value.isBlank()) return null;
        try {
            double parsed = Double.parseDouble(value);
            return Double.isFinite(parsed) ? parsed : null;
        } catch (NumberFormatException ex) {
            return null;
        }
    }

    private static Double optionalRange(Double value, double max) {
        return value != null && value >= 0 && value <= max ? value : null;
    }

    /** 범위형 강수량은 하한값을 사용합니다. '미만'·미상은 정확한 값을 만들지 않고 null로 둡니다. */
    private static Double parseRainAmount(String value) {
        if (value == null || value.isBlank()) return null;
        if (value.trim().equals("강수없음")) return 0.0;
        if (value.contains("미만")) return null;
        var matcher = java.util.regex.Pattern.compile("^\\s*(\\d+(?:\\.\\d+)?)(?:\\s*(?:mm)?\\s*(?:이상|[~～-]\\s*\\d+(?:\\.\\d+)?\\s*(?:mm)?)?)?\\s*$")
                .matcher(value);
        return matcher.matches() ? parseNumber(matcher.group(1)) : null;
    }

}
