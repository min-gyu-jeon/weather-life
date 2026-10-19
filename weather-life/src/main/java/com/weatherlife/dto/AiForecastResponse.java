package com.weatherlife.dto;

import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.util.List;

/** 프론트가 필요한 AI 모델의 일별 기온 예측만 전달합니다. */
public record AiForecastResponse(String regionName, String model, List<Forecast> forecasts) {
    public record Forecast(LocalDate date, OffsetDateTime validTimeKst, double temperatureC) { }
}
