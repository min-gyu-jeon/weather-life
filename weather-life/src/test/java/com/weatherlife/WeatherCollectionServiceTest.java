package com.weatherlife;

import com.weatherlife.repository.HourlyForecastRepository;
import com.weatherlife.service.OfficialWeatherService;
import com.weatherlife.service.WeatherCollectionService;
import com.weatherlife.service.WeatherForecastMappingException;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import static org.assertj.core.api.Assertions.*;
import static org.mockito.BDDMockito.given;

@SpringBootTest(properties = "spring.jpa.hibernate.ddl-auto=create-drop")
class WeatherCollectionServiceTest {
    @Autowired WeatherCollectionService collector;
    @Autowired HourlyForecastRepository repository;
    @MockitoBean OfficialWeatherService official;
    private static final String REGION = "서울특별시 영등포구 신길제1동";
    @BeforeEach void clear() { repository.deleteAll(); }

    private static String fixture(String baseTime, String temperature) {
        var categories = new String[][] {{"TMP", temperature}, {"REH","40"}, {"WSD","2.9"},
                {"SKY","1"}, {"PTY","0"}, {"POP","0"}, {"PCP","강수없음"}};
        var items = new java.util.ArrayList<String>();
        for (String[] category : categories) {
            items.add("{\"baseDate\":\"20261014\",\"baseTime\":\"" + baseTime
                    + "\",\"fcstDate\":\"20261014\",\"fcstTime\":\"0900\",\"category\":\""
                    + category[0] + "\",\"fcstValue\":\"" + category[1] + "\"}");
        }
        return "{\"response\":{\"header\":{\"resultCode\":\"00\"},\"body\":{\"totalCount\":7,"
                + "\"items\":{\"item\":[" + String.join(",",items) + "]}}}}";
    }

    @Test void sameEditionDoesNotDuplicateAndNewerEditionUpdates() {
        given(official.getShortRangeForecast(REGION)).willReturn(
                fixture("0800","14"), fixture("0800","14"), fixture("1100","16"));
        var first = collector.collect(REGION);
        assertThat(first.inserted()).isEqualTo(1);
        assertThat(repository.count()).isEqualTo(1);
        var second = collector.collect(REGION);
        assertThat(second.unchanged()).isEqualTo(1);
        assertThat(repository.count()).isEqualTo(1);
        var third = collector.collect(REGION);
        assertThat(third.updated()).isEqualTo(1);
        assertThat(repository.findAll().getFirst().getTmp()).isEqualTo("16");
    }

    @Test void malformedOrTruncatedResponsesDoNotDestroyOldForecast() {
        given(official.getShortRangeForecast(REGION)).willReturn(
                fixture("0800","14"),
                fixture("1100","16").replace("\"totalCount\":7", "\"totalCount\":999"));
        collector.collect(REGION);
        assertThatThrownBy(() -> collector.collect(REGION))
                .isInstanceOf(WeatherForecastMappingException.class);
        assertThat(repository.count()).isEqualTo(1);
        assertThat(repository.findAll().getFirst().getTmp()).isEqualTo("14");
    }

    @Test void apiErrorsAndMissingStructureDoNotDestroyOldForecast() {
        given(official.getShortRangeForecast(REGION)).willReturn(
                fixture("0800", "14"),
                "{\"response\":{\"header\":{\"resultCode\":\"03\",\"resultMsg\":\"ERROR\"}}}",
                "{}");
        collector.collect(REGION);
        for (int attempt = 0; attempt < 2; attempt++) {
            assertThatThrownBy(() -> collector.collect(REGION))
                    .isInstanceOf(WeatherForecastMappingException.class);
            assertThat(repository.count()).isEqualTo(1);
            assertThat(repository.findAll().getFirst().getTmp()).isEqualTo("14");
        }
    }
}
