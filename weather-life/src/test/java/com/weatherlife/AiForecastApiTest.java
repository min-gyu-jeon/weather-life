package com.weatherlife;

import com.sun.net.httpserver.HttpServer;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.web.servlet.MockMvc;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

/** 실제 AI 서버 없이 로컬 HTTP 테스트 서버로 좌표·인증·JSON 변환을 검증합니다. */
@SpringBootTest
@AutoConfigureMockMvc
class AiForecastApiTest {
    private static final AtomicReference<String> LAST_QUERY = new AtomicReference<>();
    private static final AtomicReference<String> LAST_KEY = new AtomicReference<>();
    private static final AtomicInteger RETURN_STATUS = new AtomicInteger(200);
    private static final HttpServer AI_SERVER = startFakeAiServer();

    @Autowired MockMvc mvc;

    @DynamicPropertySource
    static void aiEndpoint(DynamicPropertyRegistry properties) {
        properties.add("ai.forecast.base-url", () -> "http://127.0.0.1:" + AI_SERVER.getAddress().getPort());
        properties.add("ai.forecast.api-key", () -> "TEST_API_KEY");
    }

    private static HttpServer startFakeAiServer() {
        try {
            HttpServer server = HttpServer.create(new InetSocketAddress("127.0.0.1", 0), 0);
            server.createContext("/v1/forecasts", exchange -> {
                LAST_QUERY.set(exchange.getRequestURI().getRawQuery());
                LAST_KEY.set(exchange.getRequestHeaders().getFirst("X-API-Key"));
                int status = RETURN_STATUS.get();
                String json = """
                        {
                          "model":"Pangu-Weather", "ignored":"extra",
                          "forecasts":[
                            {"date":"2026-10-16", "valid_time_kst":"2026-10-16T09:00:00+09:00", "temperature_c":16.617, "wind_speed_ms":1.23},
                            {"date":"2026-10-17", "valid_time_kst":"2026-10-17T09:00:00+09:00", "temperature_c":16.664},
                            {"date":"2026-10-18", "valid_time_kst":"2026-10-18T09:00:00+09:00", "temperature_c":18.588}
                          ]
                        }
                        """;
                byte[] response = json.getBytes(StandardCharsets.UTF_8);
                exchange.getResponseHeaders().set("Content-Type", "application/json; charset=UTF-8");
                exchange.sendResponseHeaders(status, response.length);
                try (var body = exchange.getResponseBody()) { body.write(response); }
            });
            server.start();
            return server;
        } catch (IOException e) {
            throw new IllegalStateException("로컬 AI 테스트 서버 시작 실패", e);
        }
    }

    @BeforeEach void resetStatus() { RETURN_STATUS.set(200); }

    @AfterAll static void stop() { AI_SERVER.stop(0); }

    @Test void translatesDistrictCoordinatesAndTemperatureForecasts() throws Exception {
        mvc.perform(get("/api/weather/ai").param("gu", "영등포구"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.regionName").value("영등포구"))
                .andExpect(jsonPath("$.model").value("Pangu-Weather"))
                .andExpect(jsonPath("$.forecasts.length()").value(3))
                .andExpect(jsonPath("$.forecasts[0].validTimeKst").value("2026-10-16T09:00:00+09:00"))
                .andExpect(jsonPath("$.forecasts[0].date").value("2026-10-16"))
                .andExpect(jsonPath("$.forecasts[0].temperatureC").value(16.617))
                .andExpect(jsonPath("$.forecasts[2].temperatureC").value(18.588));
        assertThat(LAST_KEY.get()).isEqualTo("TEST_API_KEY");
        assertThat(LAST_QUERY.get()).contains("latitude=37.5236111111111", "longitude=126.898341666666");
    }

    @Test void invalidDistrictIsRejectedBeforeAiCall() throws Exception {
        mvc.perform(get("/api/weather/ai").param("gu", "없는구"))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.code").value("INVALID_REQUEST"));
    }

    @Test void aiServerErrorIsReturnedAsBadGateway() throws Exception {
        RETURN_STATUS.set(500);
        mvc.perform(get("/api/weather/ai").param("regionName", "서울특별시 영등포구"))
                .andExpect(status().isBadGateway())
                .andExpect(jsonPath("$.code").value("AI_FORECAST_ERROR"));
    }
}
