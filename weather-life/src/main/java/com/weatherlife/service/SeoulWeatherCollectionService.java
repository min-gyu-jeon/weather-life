package com.weatherlife.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

/** 서울 25개 구 전체 수집(대표 예보격자 중복 호출 생략). */
@Service
public class SeoulWeatherCollectionService {
    private static final Logger log = LoggerFactory.getLogger(SeoulWeatherCollectionService.class);
    private final SeoulDistrictService districts;
    private final WeatherCollectionService collector;
    private final WeatherRetentionService retention;

    public record BatchResult(int districtCount, int uniqueGridCount, int succeededGrids, int failedGrids,
                              int inserted, int updated, int unchanged, int skipped, int removedOldRows,
                              List<String> failedRegions) { }

    public SeoulWeatherCollectionService(SeoulDistrictService districts, WeatherCollectionService collector, WeatherRetentionService retention) {
        this.districts = districts;
        this.collector = collector;
        this.retention = retention;
    }

    public synchronized BatchResult collectAll() {
        int removed = retention.deleteBeforeToday();
        var representatives = districts.uniqueGridRepresentatives();
        int done = 0, added = 0, changed = 0, same = 0, skipped = 0;
        List<String> failures = new ArrayList<>();
        for (var district : representatives) {
            try {
                var result = collector.collect(district.regionName());
                done++;
                added += result.inserted();
                changed += result.updated();
                same += result.unchanged();
                skipped += result.skipped();
                log.info("단기예보 수집 성공: {} ({}, {})", district.regionName(), district.gridX(), district.gridY());
            } catch (Exception e) {
                failures.add(district.regionName());
                log.error("단기예보 수집 실패: {} (나머지 구 수집 계속)", district.regionName(), e);
            }
        }
        return new BatchResult(districts.allDistricts().size(), representatives.size(), done, failures.size(),
                added, changed, same, skipped, removed, List.copyOf(failures));
    }
}
