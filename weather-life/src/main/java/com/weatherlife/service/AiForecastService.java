package com.weatherlife.service;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.weatherlife.dto.AiForecastResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Service;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestClientResponseException;

import java.time.LocalDate;
import java.time.OffsetDateTime;
import java.util.List;

/** 서울 지역의 위도/경도로 별도 AI 서버를 호출하고 필요한 결과만 프론트에 반환합니다. */
@Service
public class AiForecastService {
    private final OfficialRegionService regions;
    private final SeoulDistrictService districts;
    private final RestClient client;
    private final String apiKey;

    public AiForecastService(OfficialRegionService regions,
                             SeoulDistrictService districts,
                             RestClient.Builder builder,
                             @Value("${ai.forecast.base-url:http://localhost:8000}") String baseUrl,
                             @Value("${ai.forecast.api-key:}") String apiKey) {
        this.regions = regions;
        this.districts = districts;
        this.apiKey = apiKey;

        // AI 서버가 실행 중이지 않거나 응답이 느릴 때 웹 요청이 무한 대기하지 않도록 합니다.
        var requestFactory = new SimpleClientHttpRequestFactory();
        requestFactory.setConnectTimeout(3_000);
        requestFactory.setReadTimeout(15_000);
        this.client = builder.clone().baseUrl(baseUrl).requestFactory(requestFactory).build();
    }

    public AiForecastResponse getForecast(String regionName) {
        String normalized = districts.normalizeRegionName(regionName);
        var coordinates = regions.getGeoCoordinates(normalized);
        if (coordinates == null) {
            throw new IllegalArgumentException("존재하지 않는 지역: " + regionName);
        }
        if (apiKey == null || apiKey.isBlank()) {
            throw new AiForecastException(HttpStatus.SERVICE_UNAVAILABLE,
                    "AI 예측 서버 API 키가 설정되어 있지 않습니다. AI_FORECAST_API_KEY 환경 변수를 확인하세요.");
        }

        UpstreamResponse result;
        try {
            result = client.get()
                    .uri(uri -> uri.path("/v1/forecasts")
                            .queryParam("latitude", coordinates.latitude())
                            .queryParam("longitude", coordinates.longitude())
                            .build())
                    .accept(MediaType.APPLICATION_JSON)
                    .header("X-API-Key", apiKey)
                    .retrieve()
                    .body(UpstreamResponse.class);
        } catch (ResourceAccessException e) {
            throw new AiForecastException(HttpStatus.SERVICE_UNAVAILABLE,
                    "AI 예측 서버에 연결할 수 없거나 응답이 지연되고 있습니다. 서버 실행 상태를 확인하세요.");
        } catch (RestClientResponseException e) {
            // 외부 응답 본문이나 인증키는 오류 메시지에 노출하지 않습니다.
            throw new AiForecastException(HttpStatus.BAD_GATEWAY,
                    "AI 예측 서버 호출에 실패했습니다. (HTTP " + e.getStatusCode().value() + ")");
        } catch (RestClientException e) {
            throw new AiForecastException(HttpStatus.BAD_GATEWAY,
                    "AI 예측 서버 응답을 처리할 수 없습니다.");
        }

        if (result == null || result.forecasts() == null || result.forecasts().isEmpty()) {
            throw new AiForecastException(HttpStatus.BAD_GATEWAY,
                    "AI 예측 서버 응답에 forecasts 데이터가 없습니다.");
        }
        List<AiForecastResponse.Forecast> forecasts = result.forecasts().stream().map(item -> {
            if (item == null || item.date() == null || item.validTimeKst() == null
                    || item.temperatureC() == null || !Double.isFinite(item.temperatureC())) {
                throw new AiForecastException(HttpStatus.BAD_GATEWAY,
                        "AI 예측 서버 응답의 날짜 또는 기온 데이터가 올바르지 않습니다.");
            }
            return new AiForecastResponse.Forecast(item.date(), item.validTimeKst(), item.temperatureC());
        }).toList();
        return new AiForecastResponse(regionName.strip(), result.model(), forecasts);
    }

    // AI 원본 응답의 다른 항목(run_id, pressure 등)은 무시합니다.
    @JsonIgnoreProperties(ignoreUnknown = true)
    public record UpstreamResponse(String model, List<UpstreamForecast> forecasts) { }

    @JsonIgnoreProperties(ignoreUnknown = true)
    public record UpstreamForecast(LocalDate date,
                                    @JsonProperty("valid_time_kst") OffsetDateTime validTimeKst,
                                    @JsonProperty("temperature_c") Double temperatureC) { }
}
