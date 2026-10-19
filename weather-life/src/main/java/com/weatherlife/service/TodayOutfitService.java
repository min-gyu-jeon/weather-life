package com.weatherlife.service;

import com.weatherlife.dto.OutfitResponse;
import com.weatherlife.dto.TodayOutfitResponse;
import com.weatherlife.dto.OutfitTypes.Gender;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** 저장된 DB 예보를 시간별 의상·준비물 추천으로 변환합니다. */
@Service
public class TodayOutfitService {
    private static final ZoneId KST = ZoneId.of("Asia/Seoul");

    private final WeatherQueryService weatherQueryService;
    private final ShortForecastOutfitMapper mapper;
    private final OutfitService outfitService;

    public TodayOutfitService(
            WeatherQueryService weatherQueryService,
            ShortForecastOutfitMapper mapper,
            OutfitService outfitService) {
        this.weatherQueryService = weatherQueryService;
        this.mapper = mapper;
        this.outfitService = outfitService;
    }

    public TodayOutfitResponse recommendToday(
            String regionName,
            Gender gender,
            Integer count,
            Long seed) {
        return recommendForDate(
                regionName, LocalDate.now(KST), gender, count, seed);
    }

    /** 하루의 최저·최고기온을 계산한 뒤 지정 시각의 추천을 반환합니다. */
    public OutfitResponse recommendForHour(
            String regionName,
            LocalDateTime at,
            Gender gender,
            Integer count,
            Long seed) {

        var rows = weatherQueryService.loadDay(
                regionName, at.toLocalDate());
        var converted = mapper.convertStored(rows, at.toLocalDate());

        String hourKey = at.toLocalTime()
                .format(DateTimeFormatter.ofPattern("HH:mm"));
        var request = converted.hourlyRequests().get(hourKey);

        if (request == null) {
            throw new ForecastNotFoundException(
                    at + " 의상 추천용 예보가 없습니다.");
        }

        return outfitService.recommend(
                request.withSelection(gender, count, seed),
                at.toLocalTime());
    }

    public TodayOutfitResponse recommendForDate(
            String regionName,
            LocalDate date,
            Gender gender,
            Integer count,
            Long seed) {

        var rows = weatherQueryService.loadDay(regionName, date);
        var converted = mapper.convertStored(rows, date);

        Map<String, OutfitResponse> recommendations =
                new LinkedHashMap<>();
        List<String> skipped =
                new ArrayList<>(converted.skippedHours());

        for (var entry : converted.hourlyRequests().entrySet()) {
            try {
                recommendations.put(
                        entry.getKey(),
                        outfitService.recommend(
                                entry.getValue()
                                        .withSelection(gender, count, seed),
                                LocalTime.parse(entry.getKey())));
            } catch (NoOutfitException ex) {
                skipped.add(entry.getKey());
            }
        }

        skipped.sort(String::compareTo);

        return new TodayOutfitResponse(
                date,
                regionName,
                Collections.unmodifiableMap(recommendations),
                List.copyOf(skipped));
    }
}