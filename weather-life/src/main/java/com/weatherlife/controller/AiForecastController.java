package com.weatherlife.controller;

import com.weatherlife.dto.AiForecastResponse;
import com.weatherlife.service.AiForecastService;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.util.List;

/** 프론트 → Spring Boot → 별도 AI 서버 순서로 호출합니다. */
@RestController
@RequestMapping("/api/weather")
public class AiForecastController {
    private final AiForecastService service;

    public AiForecastController(AiForecastService service) {
        this.service = service;
    }

    /** GET /api/weather/ai?gu=영등포구 (regionName도 지원) */
    @GetMapping(value = "/ai", produces = MediaType.APPLICATION_JSON_VALUE)
    public AiForecastResponse forecast(@RequestParam(required = false) String gu,
                                       @RequestParam(required = false) String regionName) {
        String selected = gu != null && !gu.isBlank() ? gu : regionName;
        if (selected == null || selected.isBlank()) {
            throw new IllegalArgumentException("regionName 또는 gu 파라미터를 지정해 주세요.");
        }
        return service.getForecast(selected);
    }

    /**
     * AI 예측 테스트 API
     * AI 서버 연결 없이 고정된 샘플 데이터를 반환합니다.
     * 프론트엔드 개발 및 연동 테스트용
     */
    @GetMapping(value = "/aitest", produces = MediaType.APPLICATION_JSON_VALUE)
    public AiForecastResponse forecastTest() {

        return new AiForecastResponse(
                "영등포구",
                "Pangu-Weather",
                List.of(
                        new AiForecastResponse.Forecast(
                                LocalDate.parse("2026-10-16"),
                                OffsetDateTime.parse("2026-10-16T00:00:00Z"),
                                16.743
                        ),
                        new AiForecastResponse.Forecast(
                                LocalDate.parse("2026-10-17"),
                                OffsetDateTime.parse("2026-10-17T00:00:00Z"),
                                16.668
                        ),
                        new AiForecastResponse.Forecast(
                                LocalDate.parse("2026-10-18"),
                                OffsetDateTime.parse("2026-10-18T00:00:00Z"),
                                18.679
                        )
                )
        );
    }
}
