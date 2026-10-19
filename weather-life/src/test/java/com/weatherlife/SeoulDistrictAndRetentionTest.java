package com.weatherlife;

import com.weatherlife.entity.HourlyForecast;
import com.weatherlife.repository.HourlyForecastRepository;
import com.weatherlife.service.SeoulDistrictService;
import com.weatherlife.service.WeatherRetentionService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.time.LocalDate;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
class SeoulDistrictAndRetentionTest {
    @Autowired SeoulDistrictService districts;
    @Autowired WeatherRetentionService retention;
    @Autowired HourlyForecastRepository repository;

    @Test void allSeoulDistrictsAreAvailableAndDuplicateGridsAreDeduplicated() {
        assertThat(districts.allDistricts()).hasSize(25);
        // 첨부 CSV의 자치구 대표격자 좌표 기준 25개 구 -> 14개 고유격자
        assertThat(districts.uniqueGridRepresentatives()).hasSize(14);
        assertThat(districts.normalizeRegionName("영등포구")).isEqualTo("서울특별시 영등포구");
        assertThat(districts.normalizeRegionName("서울특별시 영등포구 신길제1동"))
                .isEqualTo("서울특별시 영등포구 신길제1동");
    }

    @Test void cleanupDeletesYesterdayOnlyAndPreservesTodayAndTomorrow() {
        repository.deleteAll();
        LocalDate today = LocalDate.of(2026, 10, 15);
        var gu = districts.allDistricts().stream().filter(d -> d.gu().equals("영등포구")).findFirst().orElseThrow();
        for (LocalDate day : new LocalDate[]{today.minusDays(1), today, today.plusDays(1)}) {
            HourlyForecast f = new HourlyForecast(gu.gridX(), gu.gridY(), day.atTime(9, 0));
            f.replaceWith(today.minusDays(1).atTime(23,0), today.atStartOfDay(),
                    Map.of("TMP", "15", "REH", "50", "WSD", "2", "SKY", "1", "PTY", "0"));
            repository.save(f);
        }
        repository.flush();
        assertThat(retention.deleteBefore(today)).isEqualTo(1);
        assertThat(repository.findAll()).extracting(HourlyForecast::getForecastAt)
                .containsExactlyInAnyOrder(today.atTime(9,0), today.plusDays(1).atTime(9,0));
    }
}
