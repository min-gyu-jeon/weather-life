package com.weatherlife.controller;

import com.weatherlife.dto.OutfitResponse;
import com.weatherlife.dto.TodayOutfitResponse;
import com.weatherlife.dto.OutfitTypes.Gender;
import com.weatherlife.service.TodayOutfitService;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.time.LocalDateTime;

/** 의상 추천은 DB 예보를 사용하며, 구 단축명(gu)과 기존 regionName을 모두 지원. */
@RestController
@RequestMapping("/api/outfits")
public class TodayOutfitController {
    private final TodayOutfitService todayOutfitService;

    public TodayOutfitController(TodayOutfitService todayOutfitService) {
        this.todayOutfitService = todayOutfitService;
    }

    @GetMapping(value = "/by-date", produces = MediaType.APPLICATION_JSON_VALUE)
    public TodayOutfitResponse byDate(@RequestParam(required = false) String regionName,
                                      @RequestParam(required = false) String gu,
                                      @RequestParam LocalDate date,
                                      @RequestParam(required = false) Gender gender,
                                      @RequestParam(required = false) Integer count,
                                      @RequestParam(required = false) Long seed) {
        return todayOutfitService.recommendForDate(resolve(regionName, gu), date, gender, count, seed);
    }

    @GetMapping(value = "/today", produces = MediaType.APPLICATION_JSON_VALUE)
    public TodayOutfitResponse today(@RequestParam(required = false) String regionName,
                                     @RequestParam(required = false) String gu,
                                     @RequestParam(required = false) Gender gender,
                                     @RequestParam(required = false) Integer count,
                                     @RequestParam(required = false) Long seed) {
        return todayOutfitService.recommendToday(resolve(regionName, gu), gender, count, seed);
    }

    @GetMapping(value = "/by-hour", produces = MediaType.APPLICATION_JSON_VALUE)
    public OutfitResponse byHour(@RequestParam(required = false) String regionName,
                                 @RequestParam(required = false) String gu,
                                 @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE_TIME) LocalDateTime at,
                                 @RequestParam(required = false) Gender gender,
                                 @RequestParam(required = false) Integer count,
                                 @RequestParam(required = false) Long seed) {
        return todayOutfitService.recommendForHour(resolve(regionName, gu), at, gender, count, seed);
    }

    private static String resolve(String regionName, String gu) {
        String selected = gu != null && !gu.isBlank() ? gu : regionName;
        if (selected == null || selected.isBlank())
            throw new IllegalArgumentException("regionName 또는 gu 파라미터를 지정해 주세요.");
        return selected;
    }
}
