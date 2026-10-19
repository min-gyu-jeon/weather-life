package com.weatherlife.scheduler;

import com.weatherlife.service.SeoulWeatherCollectionService;
import com.weatherlife.service.WeatherRetentionService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

/** 서울 25개 구 전체 수집: 매일 8회 발표 + 매일 00:05 과거자료 정리. */
@Component
public class WeatherCollectScheduler {
    private static final Logger log = LoggerFactory.getLogger(WeatherCollectScheduler.class);
    private final SeoulWeatherCollectionService batch;
    private final WeatherRetentionService retention;
    private final boolean enabled;

    public WeatherCollectScheduler(SeoulWeatherCollectionService batch, WeatherRetentionService retention,
                                   @Value("${weather.collection.enabled:false}") boolean enabled) {
        this.batch = batch;
        this.retention = retention;
        this.enabled = enabled;
    }

    // 기상청 발표 02/05/08/11/14/17/20/23시, API 제공은 보통 10분 이후.
    @Scheduled(cron = "0 20 2,5,8,11,14,17,20,23 * * *", zone = "Asia/Seoul")
    public void refresh() {
        if (!enabled) return;
        var result = batch.collectAll();
        log.info("서울 단기예보 수집: 자치구 {}개, 실제 격자 {}개, 성공 {}, 실패 {}, INSERT {}, UPDATE {}",
                result.districtCount(), result.uniqueGridCount(), result.succeededGrids(),
                result.failedGrids(), result.inserted(), result.updated());
    }

    @Scheduled(cron = "0 5 0 * * *", zone = "Asia/Seoul")
    public void cleanup() {
        if (!enabled) return;
        log.info("기상 DB 전날 이전 예보 정리: {}건 삭제", retention.deleteBeforeToday());
    }

    // 로컬에서 껐다 켠 경우에도 지나간 날의 데이터를 정리합니다.
    // 서버 시작 시 기상청 외부 호출은 하지 않습니다. 수동 collect-all로 최초 데이터 적재 가능합니다.
    @EventListener(ApplicationReadyEvent.class)
    public void onApplicationReady() {
        if (!enabled) return;
        cleanup();
        batch.collectAll();
    }
}
