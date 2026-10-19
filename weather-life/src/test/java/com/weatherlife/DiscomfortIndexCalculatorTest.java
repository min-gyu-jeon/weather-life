package com.weatherlife;

import com.weatherlife.dto.ForecastDayResponse;
import com.weatherlife.entity.HourlyForecast;
import com.weatherlife.service.DiscomfortIndexCalculator;
import org.junit.jupiter.api.Test;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.Map;
import static org.assertj.core.api.Assertions.assertThat;

class DiscomfortIndexCalculatorTest {
    @Test void knownWeatherIsRoundedToOneDecimalPlace() {
        assertThat(DiscomfortIndexCalculator.calculate("14", "40")).isEqualTo(57.5);
        assertThat(DiscomfortIndexCalculator.calculate("30", "70")).isEqualTo(81.4);
    }

    @Test void missingOrInvalidValuesAreNotInvented() {
        assertThat(DiscomfortIndexCalculator.calculate(null, "50")).isNull();
        assertThat(DiscomfortIndexCalculator.calculate("30", null)).isNull();
        assertThat(DiscomfortIndexCalculator.calculate("", "50")).isNull();
        assertThat(DiscomfortIndexCalculator.calculate("not-a-number", "50")).isNull();
        assertThat(DiscomfortIndexCalculator.calculate("20", "101")).isNull();
        assertThat(DiscomfortIndexCalculator.calculate("20", "-1")).isNull();
        assertThat(DiscomfortIndexCalculator.calculate("NaN", "40")).isNull();
    }

    @Test void perHourJsonDtoIncludesComputedValueWithoutAnyDbColumn() {
        var row = new HourlyForecast(58, 126, LocalDateTime.of(2026, 10, 14, 9, 0));
        row.replaceWith(LocalDateTime.of(2026, 10, 14, 8, 0),
                LocalDateTime.of(2026, 10, 14, 8, 20),
                Map.of("TMP", "14", "REH", "40", "WSD", "2.9", "SKY", "1", "PTY", "0"));
        var dto = ForecastDayResponse.from(LocalDate.of(2026, 10, 14), "영등포구", java.util.List.of(row));
        assertThat(dto.hourly()).hasSize(1);
        assertThat(dto.hourly().getFirst().discomfortIndex()).isEqualTo(57.5);
    }
}
