package com.weatherlife;

import com.weatherlife.dto.OutfitTypes.Precipitation;
import com.weatherlife.dto.OutfitTypes.Sky;
import com.weatherlife.entity.HourlyForecast;
import com.weatherlife.service.ShortForecastOutfitMapper;
import org.junit.jupiter.api.Test;

import java.time.LocalDate;
import java.util.HashSet;
import java.util.List;
import java.util.Map;

import static org.assertj.core.api.Assertions.*;

/** 실제 서비스가 사용하는 DB 예보 -> 시간별 추천 입력 변환을 검사합니다. */
class ShortForecastOutfitMapperTest {
    private final ShortForecastOutfitMapper mapper = new ShortForecastOutfitMapper();
    private final LocalDate date = LocalDate.of(2026, 10, 14);

    private HourlyForecast stored(LocalDate day, int hour, Map<String, String> values) {
        var forecast = new HourlyForecast(58, 126, day.atTime(hour, 0));
        forecast.replaceWith(day.atTime(2, 0), day.atTime(2, 20), values);
        return forecast;
    }

    @Test void sortsRequestedDayAndConvertsWeatherCodes() {
        var converted = mapper.convertStored(List.of(
                stored(date.plusDays(1), 9, Map.of("TMP", "30")),
                stored(date, 10, Map.of("TMP", "15", "REH", "35", "WSD", "3", "SKY", "3", "PTY", "1")),
                stored(date, 9, Map.of("TMP", "14", "REH", "40", "WSD", "2.9", "SKY", "1", "PTY", "0")),
                stored(date, 15, Map.of("TMX", "19")),
                stored(date, 6, Map.of("TMN", "10"))
        ), date);
        assertThat(converted.hourlyRequests().keySet()).containsExactly("09:00", "10:00");
        assertThat(converted.skippedHours()).containsExactly("06:00", "15:00");
        var atNine = converted.hourlyRequests().get("09:00");
        assertThat(atNine.temperature()).isEqualTo(14);
        assertThat(atNine.humidity()).isEqualTo(40);
        assertThat(atNine.windSpeed()).isEqualTo(2.9);
        assertThat(atNine.sky()).isEqualTo(Sky.SUNNY);
        assertThat(atNine.precipitation()).isEqualTo(Precipitation.NONE);
        assertThat(atNine.minTemperature()).isEqualTo(10);
        assertThat(atNine.maxTemperature()).isEqualTo(19);
        assertThat(atNine.gender().name()).isEqualTo("UNISEX");
        assertThat(atNine.occasion().name()).isEqualTo("DAILY");
        assertThat(atNine.count()).isEqualTo(1);
        var atTen = converted.hourlyRequests().get("10:00");
        assertThat(atTen.sky()).isEqualTo(Sky.PARTLY_CLOUDY);
        assertThat(atTen.precipitation()).isEqualTo(Precipitation.RAIN);
    }

    @Test void missingRequiredWeatherDoesNotBecomeInventedSunnyOrCalm() {
        var converted = mapper.convertStored(List.of(
                stored(date, 9, Map.of("TMP", "15", "REH", "40", "PTY", "0")),
                stored(date, 10, Map.of("TMP", "16", "REH", "42", "WSD", "2", "SKY", "4", "PTY", "7"))
        ), date);
        assertThat(converted.skippedHours()).containsExactly("09:00");
        assertThat(converted.hourlyRequests()).containsOnlyKeys("10:00");
        assertThat(converted.hourlyRequests().get("10:00").precipitation()).isEqualTo(Precipitation.SNOW);
        assertThat(converted.hourlyRequests().get("10:00").sky()).isEqualTo(Sky.CLOUDY);
    }

    @Test void seedIsRandomForNewRequestsUnlessExplicitlyGiven() {
        var rows = List.of(stored(date, 9,
                Map.of("TMP", "14", "REH", "40", "WSD", "2.9", "SKY", "1", "PTY", "0")));
        var seeds = new HashSet<Long>();
        for (int i = 0; i < 10; i++) {
            seeds.add(mapper.convertStored(rows, date).hourlyRequests().get("09:00").seed());
        }
        assertThat(seeds.size()).isGreaterThan(1);
    }

    @Test void futureOnlyForecastProducesEmptyMap() {
        var result = mapper.convertStored(List.of(stored(date.plusDays(1), 9, Map.of("TMP", "22"))), date);
        assertThat(result.hourlyRequests()).isEmpty();
        assertThat(result.skippedHours()).isEmpty();
    }

    @Test void optionalRainValuesAreMappedWithoutFabricatingMissingData() {
        for (String pcp : List.of("10.0mm", "30.0~50.0mm", "50.0mm 이상", "1.0mm 미만", "강수없음", "미상")) {
            var row = stored(date, 9, Map.of("TMP", "24", "REH", "80", "WSD", "2",
                    "SKY", "4", "PTY", "1", "POP", "60", "PCP", pcp));
            var result = mapper.convertStored(List.of(row), date).hourlyRequests().get("09:00");
            assertThat(result.date()).isEqualTo(date);
            assertThat(result.precipitationProbability()).isEqualTo(60);
            assertThat(result.airQuality()).isNull();
            Double expected = switch (pcp) {
                case "10.0mm" -> 10.0;
                case "30.0~50.0mm" -> 30.0;
                case "50.0mm 이상" -> 50.0;
                case "강수없음" -> 0.0;
                default -> null;
            };
            assertThat(result.precipitationAmount()).isEqualTo(expected);
        }
    }
}
