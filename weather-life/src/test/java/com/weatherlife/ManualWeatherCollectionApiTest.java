package com.weatherlife;

import com.weatherlife.repository.HourlyForecastRepository;
import com.weatherlife.service.OfficialWeatherService;
import com.weatherlife.service.SeoulDistrictService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDate;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/** 실제 기상청 대신 고정 응답을 사용하여 수동 호출 -> H2 저장 -> 조회를 확인합니다. */
@SpringBootTest(properties = "weather.collection.manual-enabled=true")
@AutoConfigureMockMvc
class ManualWeatherCollectionApiTest {
    @Autowired MockMvc mvc;
    @Autowired HourlyForecastRepository repository;
    @Autowired SeoulDistrictService districts;
    @MockitoBean OfficialWeatherService official;

    private final LocalDate date = LocalDate.now(ZoneId.of("Asia/Seoul"));

    @BeforeEach void clear() {
        repository.deleteAll();
    }

    private String forecast() {
        String day = date.format(DateTimeFormatter.BASIC_ISO_DATE);
        var items = new ArrayList<String>();
        for (var category : new String[][]{{"TMP", "16"}, {"REH", "70"}, {"WSD", "2.8"},
                {"SKY", "1"}, {"PTY", "0"}, {"POP", "70"}, {"PCP", "강수없음"}}) {
            items.add("{\"baseDate\":\"" + day + "\",\"baseTime\":\"0800\",\"fcstDate\":\"" + day
                    + "\",\"fcstTime\":\"0900\",\"category\":\"" + category[0]
                    + "\",\"fcstValue\":\"" + category[1] + "\"}");
        }
        return "{\"response\":{\"header\":{\"resultCode\":\"00\"},\"body\":{\"totalCount\":7,"
                + "\"items\":{\"item\":[" + String.join(",", items) + "]}}}}";
    }

    @Test void manualCollectionFeedsAllFourRequiredApisWithoutExtraExternalCalls() throws Exception {
        given(official.getShortRangeForecast("서울특별시 영등포구")).willReturn(forecast());
        mvc.perform(post("/api/internal/weather/collect").param("regionName", "영등포구"))
                .andExpect(status().isOk()).andExpect(jsonPath("$.inserted").value(1));
        assertThat(repository.count()).isEqualTo(1);

        mvc.perform(get("/api/weather/short").param("gu", "영등포구").param("date", date.toString()))
                .andExpect(status().isOk()).andExpect(jsonPath("$.hourly[0].temperature").value("16"));
        mvc.perform(get("/api/weather/hour").param("gu", "영등포구").param("at", date + "T09:00:00"))
                .andExpect(status().isOk()).andExpect(jsonPath("$.weather.temperature").value("16"));
        mvc.perform(get("/api/outfits/by-date").param("gu", "영등포구").param("date", date.toString())
                        .param("gender", "FEMALE").param("seed", "42"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.hourlyRecommendations['09:00'].outfits[0].setGender").value("FEMALE"));
        mvc.perform(get("/api/outfits/by-hour").param("gu", "영등포구").param("at", date + "T09:00:00")
                        .param("gender", "FEMALE").param("seed", "42"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.outfits[0].accessoryItems[0].key").value("folding_umbrella"));
        verify(official).getShortRangeForecast("서울특별시 영등포구");
        verifyNoMoreInteractions(official);
    }

    @Test void collectAllStoresEachUniqueGridOnce() throws Exception {
        given(official.getShortRangeForecast(anyString())).willReturn(forecast());
        int gridCount = districts.uniqueGridRepresentatives().size();
        mvc.perform(post("/api/internal/weather/collect-all"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.districtCount").value(25))
                .andExpect(jsonPath("$.succeededGrids").value(gridCount))
                .andExpect(jsonPath("$.failedGrids").value(0))
                .andExpect(jsonPath("$.inserted").value(gridCount));
        assertThat(repository.count()).isEqualTo(gridCount);
        verify(official, times(gridCount)).getShortRangeForecast(anyString());
    }
}
