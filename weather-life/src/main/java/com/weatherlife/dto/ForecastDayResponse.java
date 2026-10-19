package com.weatherlife.dto;

import com.weatherlife.entity.HourlyForecast;
import com.weatherlife.service.DiscomfortIndexCalculator;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

/** Normalized DB-only API response for the front end. No knowledge of KMA response envelopes is needed. */
public record ForecastDayResponse(LocalDate date, String regionName,
                                  Double minTemperature, Double maxTemperature,
                                  List<Hour> hourly) {
    public static ForecastDayResponse from(LocalDate date, String regionName, List<HourlyForecast> rows) {
        double min = Double.POSITIVE_INFINITY;
        double max = Double.NEGATIVE_INFINITY;
        for (HourlyForecast row : rows) {
            for (String value : new String[] { row.getTmp(), row.getTmn() }) {
                Double n = parse(value);
                if (n != null) min = Math.min(min, n);
            }
            for (String value : new String[] { row.getTmp(), row.getTmx() }) {
                Double n = parse(value);
                if (n != null) max = Math.max(max, n);
            }
        }
        List<Hour> displayed = rows.stream()
                .filter(row -> row.getTmp() != null && row.getReh() != null
                        && row.getWsd() != null && row.getSky() != null && row.getPty() != null)
                .map(Hour::from).toList();
        return new ForecastDayResponse(date, regionName,
                Double.isFinite(min) ? min : null,
                Double.isFinite(max) ? max : null, displayed);
    }
    private static Double parse(String s) {
        try { double n = Double.parseDouble(s); return Double.isFinite(n) ? n : null; }
        catch (RuntimeException ex) { return null; }
    }
    public record Hour(LocalDateTime forecastAt, LocalDateTime issuedAt, LocalDateTime collectedAt,
                       String temperature, String humidity, Double discomfortIndex, String windSpeed, String sky, String precipitation,
                       String precipitationProbability, String precipitationAmount, String snowAmount,
                       String windDirection, String windU, String windV, String waveHeight,
                       String minTemperature, String maxTemperature) {
        public static Hour from(HourlyForecast value) {
            return new Hour(value.getForecastAt(), value.getIssuedAt(), value.getCollectedAt(),
                    value.getTmp(), value.getReh(), DiscomfortIndexCalculator.calculate(value.getTmp(), value.getReh()),
                    value.getWsd(), value.getSky(), value.getPty(),
                    value.getPop(), value.getPcp(), value.getSno(), value.getVec(), value.getUuu(),
                    value.getVvv(), value.getWav(), value.getTmn(), value.getTmx());
        }
    }
}
