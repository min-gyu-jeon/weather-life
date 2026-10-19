package com.weatherlife.service;

import com.weatherlife.repository.HourlyForecastRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneId;

/** 오늘 자정(KST) 이전 예보 시각의 행만 삭제. issuedAt 기준 삭제 아님! */
@Service
public class WeatherRetentionService {
    private static final ZoneId KST = ZoneId.of("Asia/Seoul");
    private final HourlyForecastRepository repository;

    public WeatherRetentionService(HourlyForecastRepository repository) {
        this.repository = repository;
    }

    @Transactional
    public int deleteBeforeToday() {
        return deleteBefore(LocalDate.now(KST));
    }

    @Transactional
    public int deleteBefore(LocalDate today) {
        LocalDateTime cutoff = today.atStartOfDay();
        return repository.deleteForecastsBefore(cutoff);
    }
}
