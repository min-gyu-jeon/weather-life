package com.weatherlife.dto;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;

/** 서울 시간 기준 '오늘'에 대한 시간별 코디 추천 결과입니다. */
public record TodayOutfitResponse(
        LocalDate date,
        String regionName,
        // "09:00" -> 이 시간의 날씨 및 추천 코디. 시간순으로 유지합니다.
        Map<String, OutfitResponse> hourlyRecommendations,
        // 기상청의 필수 데이터 누락/알 수 없는 코드로 추천하지 못한 시간
        List<String> skippedHours
) { }
