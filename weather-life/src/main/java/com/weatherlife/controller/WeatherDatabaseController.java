package com.weatherlife.controller;

import com.weatherlife.dto.ForecastDayResponse;
import com.weatherlife.service.SeoulDistrictService;
import com.weatherlife.service.WeatherQueryService;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.List;

/** 날씨 공개 API는 DB만 조회합니다. 외부 기상청 API를 호출하지 않습니다. */
@RestController
@RequestMapping("/api/weather")
public class WeatherDatabaseController {
    private final WeatherQueryService service;
    private final SeoulDistrictService districts;

    public WeatherDatabaseController(WeatherQueryService service, SeoulDistrictService districts) {
        this.service = service;
        this.districts = districts;
    }

    /** /api/weather/short?gu=영등포구&date=2026-10-15 (regionName 구/동도 지원) */
    @GetMapping(value = "/short", produces = MediaType.APPLICATION_JSON_VALUE)
    public ForecastDayResponse day(@RequestParam(required = false) String regionName,
                                   @RequestParam(required = false) String gu,
                                   @RequestParam(required = false) LocalDate date) {
        return service.getDay(resolve(regionName, gu), date == null ? LocalDate.now(ZoneId.of("Asia/Seoul")) : date);
    }

    /** /api/weather/hour?gu=영등포구&at=2026-10-15T09:00 */
    public record OneHourWeather(String regionName, ForecastDayResponse.Hour weather) { }

    @GetMapping(value = "/hour", produces = MediaType.APPLICATION_JSON_VALUE)
    public OneHourWeather hour(@RequestParam(required = false) String regionName,
                               @RequestParam(required = false) String gu,
                               @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime at) {
        String selected = resolve(regionName, gu);
        return new OneHourWeather(selected, service.getHour(selected, at));
    }

    /** 화면의 구 선택 콤보박스 구성용 */
    @GetMapping(value = "/districts", produces = MediaType.APPLICATION_JSON_VALUE)
    public List<String> districts() {
        return districts.allDistricts().stream().map(SeoulDistrictService.District::gu).toList();
    }

    private static String resolve(String regionName, String gu) {
        String selected = gu != null && !gu.isBlank() ? gu : regionName;
        if (selected == null || selected.isBlank())
            throw new IllegalArgumentException("regionName 또는 gu 파라미터를 지정해 주세요.");
        return selected;
    }
}
