package com.weatherlife.service;

import com.weatherlife.dto.RegionShort;

import lombok.extern.slf4j.Slf4j;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;

@Slf4j
@Service
public class OfficialWeatherService {

    private final OfficialRegionService regionService;

    // 단기예보: 기상청 API허브
    private final RestClient shortClient;

    // 중기예보: 공공데이터포털
    private final RestClient mediumClient;

    // 인증키
    private final String shortApiKey;
    private final String mediumApiKey;


    private static final ZoneId KST =
            ZoneId.of("Asia/Seoul");


    // =====================================
    // 생성자
    // =====================================

    public OfficialWeatherService(
            OfficialRegionService regionService,
            RestClient.Builder builder,
            @Value("${kma.short.auth-key}") String shortApiKey,
            @Value("${kma.medium.service-key}") String mediumApiKey
    ) {
        this.regionService = regionService;

        // 단기예보 API
        this.shortClient = builder.clone()
                .baseUrl("https://apihub.kma.go.kr")
                .build();

        // 중기예보 API
        this.mediumClient = builder.clone()
                .baseUrl("https://apis.data.go.kr")
                .build();

        this.shortApiKey = shortApiKey;
        this.mediumApiKey = mediumApiKey;
    }


    // =====================================
    // 단기예보 조회
    // =====================================

    public String getShortRangeForecast(String regionName) {

        // 1. 지역명으로 좌표 조회
        RegionShort region =
                regionService.getShortRegion(regionName);

        if (region == null) {
            throw new IllegalArgumentException(
                    "존재하지 않는 지역: " + regionName
            );
        }

        int nx = region.nx();
        int ny = region.ny();

        // 2. 최신 발표시간 계산
        LocalDateTime baseTime = getLatestShortBaseTime();

        String baseDate = baseTime.format(
                DateTimeFormatter.ofPattern("yyyyMMdd")
        );

        String baseHour = baseTime.format(
                DateTimeFormatter.ofPattern("HHmm")
        );

        log.info(
                "단기예보 요청 - 지역: {}, nx: {}, ny: {}, 발표: {} {}",
                regionName, nx, ny, baseDate, baseHour
        );

        // 3. 공공데이터포털 API 호출
        String response = shortClient.get()
                .uri(uriBuilder -> uriBuilder
                        .path("/api/typ02/openApi/VilageFcstInfoService_2.0/getVilageFcst")
                        .queryParam("authKey", shortApiKey)
                        .queryParam("pageNo", 1)
                        .queryParam("numOfRows", 3000)
                        .queryParam("dataType", "JSON")
                        .queryParam("base_date", baseDate)
                        .queryParam("base_time", baseHour)
                        .queryParam("nx", nx)
                        .queryParam("ny", ny)
                        .build())
                .retrieve()
                .body(String.class);

        log.info("단기예보 API 응답 수신 완료");

        return response;
    }


    // =====================================
    // 중기육상예보 조회
    // =====================================

    public String getMediumLandForecast(String regId) {

        return callMediumForecast(
                "/1360000/MidFcstInfoService/getMidLandFcst",
                regId
        );
    }


    // =====================================
    // 중기기온예보 조회
    // =====================================

    public String getMediumTemperatureForecast(String regId) {

        return callMediumForecast(
                "/1360000/MidFcstInfoService/getMidTa",
                regId
        );
    }


    // =====================================
    // 중기예보 공통 API 호출
    // =====================================

    private String callMediumForecast(
            String path,
            String regId
    ) {

        if (regId == null || regId.isBlank()) {
            throw new IllegalArgumentException(
                    "중기예보 지역코드가 필요합니다."
            );
        }

        String tmFc = getLatestMediumBaseTime();

        log.info(
                "중기예보 요청 - API: {}, regId: {}, tmFc: {}",
                path, regId, tmFc
        );

        String response = mediumClient.get()
                .uri(uriBuilder -> uriBuilder
                        .path(path)
                        .queryParam("serviceKey", "{serviceKey}")
                        .queryParam("pageNo", 1)
                        .queryParam("numOfRows", 10)
                        .queryParam("dataType", "JSON")
                        .queryParam("regId", regId)
                        .queryParam("tmFc", tmFc)
                        .build(mediumApiKey))
                .retrieve()
                .body(String.class);

        log.info("중기예보 API 응답 수신 완료");

        return response;
    }


    // =====================================
    // 단기예보 최신 발표시간 계산
    // =====================================

    private LocalDateTime getLatestShortBaseTime() {

        // 발표 직후 데이터 제공 지연 고려
        LocalDateTime now =
                LocalDateTime.now(KST).minusMinutes(20);

        int[] hours = {2, 5, 8, 11, 14, 17, 20, 23};

        for (int i = hours.length - 1; i >= 0; i--) {

            if (now.getHour() >= hours[i]) {

                return now.toLocalDate()
                        .atTime(hours[i], 0);
            }
        }

        // 02시 이전이면 전날 23시 발표
        return now.toLocalDate()
                .minusDays(1)
                .atTime(23, 0);
    }


    // =====================================
    // 중기예보 최신 발표시간 계산
    // =====================================

    private String getLatestMediumBaseTime() {

        LocalDateTime now =
                LocalDateTime.now(KST).minusMinutes(30);

        LocalDateTime baseTime;

        if (now.getHour() >= 18) {

            baseTime = now.toLocalDate().atTime(18, 0);

        } else if (now.getHour() >= 6) {

            baseTime = now.toLocalDate().atTime(6, 0);

        } else {

            baseTime = now.toLocalDate()
                    .minusDays(1)
                    .atTime(18, 0);
        }

        return baseTime.format(
                DateTimeFormatter.ofPattern("yyyyMMddHHmm")
        );
    }
}