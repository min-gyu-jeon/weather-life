package com.weatherlife.controller;

import com.weatherlife.service.OfficialWeatherService;
import com.weatherlife.service.ClothingCatalog;
import com.weatherlife.service.OutfitService;
import com.weatherlife.dto.OutfitRequest;
import com.weatherlife.dto.OutfitResponse;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class APIController {

    private final OfficialWeatherService weatherService;
    private final OutfitService outfitService;
    private final ClothingCatalog clothingCatalog;

    // 날씨와 선호 조건을 받아 한 벌 단위의 옷차림을 추천합니다.
    @PostMapping(
            value = "/outfits/recommend",
            consumes = MediaType.APPLICATION_JSON_VALUE,
            produces = MediaType.APPLICATION_JSON_VALUE
    )
    public OutfitResponse recommendOutfit(@Valid @RequestBody OutfitRequest request) {
        return outfitService.recommend(request);
    }

    // 추천에 사용하는 의류 목록입니다. data/clothing-catalog.json에서 수정합니다.
    @GetMapping(value = "/outfits/catalog", produces = MediaType.APPLICATION_JSON_VALUE)
    public ClothingCatalog.Data getClothingCatalog() {
        return clothingCatalog.data();
    }

    // 기상청 원본 단기예보 조회. DB 기반 /api/weather/short와 별개입니다.
    @GetMapping(value = "/short", produces = MediaType.APPLICATION_JSON_VALUE)
    public String getShortForecast(@RequestParam String regionName) {
        return weatherService.getShortRangeForecast(regionName);
    }

    // 중기 육상예보
    @GetMapping(value = "/medium/land", produces = MediaType.APPLICATION_JSON_VALUE)
    public String getMediumLandForecast(@RequestParam String regId) {
        return weatherService.getMediumLandForecast(regId);
    }

    // 중기 기온예보
    @GetMapping(value = "/medium/temperature", produces = MediaType.APPLICATION_JSON_VALUE)
    public String getMediumTemperatureForecast(@RequestParam String regId) {
        return weatherService.getMediumTemperatureForecast(regId);
    }
}
