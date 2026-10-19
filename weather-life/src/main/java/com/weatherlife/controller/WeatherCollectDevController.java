package com.weatherlife.controller;

import com.weatherlife.service.SeoulWeatherCollectionService;
import com.weatherlife.service.WeatherCollectionService;
import com.weatherlife.service.WeatherRetentionService;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/** 수동 수집·DB 저장 API. weather.collection.manual-enabled=true일 때만 활성화됩니다. */
@RestController
@RequestMapping("/api/internal/weather")
@ConditionalOnProperty(name = "weather.collection.manual-enabled", havingValue = "true")
public class WeatherCollectDevController {
    private final WeatherCollectionService collector;
    private final SeoulWeatherCollectionService seoulCollector;
    private final WeatherRetentionService retention;

    public WeatherCollectDevController(WeatherCollectionService collector,
                                       SeoulWeatherCollectionService seoulCollector,
                                       WeatherRetentionService retention) {
        this.collector = collector;
        this.seoulCollector = seoulCollector;
        this.retention = retention;
    }

    /** 지정 지역의 최신 단기예보를 호출하여 DB에 저장합니다. */
    @PostMapping(value = "/collect", produces = MediaType.APPLICATION_JSON_VALUE)
    public WeatherCollectionService.CollectionResult collect(@RequestParam String regionName) {
        return collector.collect(regionName);
    }

    /** 개발 전용: 모든 서울 구를 한 번에 수집 (현재 CSV 기준 고유격자 14개). */
    @PostMapping(value = "/collect-all", produces = MediaType.APPLICATION_JSON_VALUE)
    public SeoulWeatherCollectionService.BatchResult collectAll() {
        return seoulCollector.collectAll();
    }

    /** 개발 전용: 자정 이전 데이터 즉시 정리. */
    @PostMapping(value = "/cleanup", produces = MediaType.APPLICATION_JSON_VALUE)
    public Map<String, Integer> cleanup() {
        return Map.of("deleted", retention.deleteBeforeToday());
    }
}
