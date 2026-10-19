package com.weatherlife.service;

import com.weatherlife.dto.RegionShort;
import jakarta.annotation.PostConstruct;
import lombok.extern.slf4j.Slf4j;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;

@Slf4j
@Service
public class OfficialRegionService {

    // 단기예보 지역정보
    private Map<String, RegionShort> shortRegions = Map.of();
    // AI 예측 서버에는 기상청 격자(nx, ny)가 아닌 실제 위도/경도를 전달합니다.
    private Map<String, GeoCoordinates> geoCoordinates = Map.of();

    public record GeoCoordinates(double latitude, double longitude) { }

    // 서버 실행 시 자동 호출
    @PostConstruct
    public void init() {
        try {
            loadShortRegions();
        } catch (Exception e) {
            log.error("CSV 초기화 실패! 원인: {}", e.getMessage(), e);
            throw new IllegalStateException("지역정보 CSV 로딩 실패", e);
        }
        log.info("단기예보 지역정보 {}건 로딩 완료", shortRegions.size());
    }

    // CSV 파일 읽기
    private CSVParser openCsv(String fileName) throws IOException {

        ClassPathResource resource =
                new ClassPathResource("data/" + fileName);

        BufferedReader reader = new BufferedReader(
                new InputStreamReader(
                        resource.getInputStream(),
                        StandardCharsets.UTF_8
                )
        );

        // UTF-8 BOM이 있어도 읽을 수 있도록 처리
        reader.mark(1);

        if (reader.read() != '\uFEFF') {
            reader.reset();
        }

        CSVFormat format = CSVFormat.DEFAULT.builder()
                .setHeader()
                .setSkipHeaderRecord(true)
                .setIgnoreSurroundingSpaces(true)
                .build();

        try {
            return format.parse(reader);
        } catch (IOException | RuntimeException e) {
            reader.close();
            throw e;
        }
    }

    // 단기예보 CSV 로딩
    private void loadShortRegions() throws IOException {

        Map<String, RegionShort> data = new HashMap<>();
        Map<String, GeoCoordinates> locations = new HashMap<>();

        try (CSVParser parser =
                     openCsv("short_range_region.csv")) {

            for (CSVRecord row : parser) {

                String step1 = row.get("1단계").trim();
                String step2 = row.get("2단계").trim();
                String step3 = row.get("3단계").trim();

                // 지역명 합치기
                String regionName = String.join(" ", step1, step2, step3)
                        .replaceAll("\\s+", " ")
                        .trim();

                // 좌표 가져오기

                int nx = Integer.parseInt(row.get("격자 X").trim());
                int ny = Integer.parseInt(row.get("격자 Y").trim());

                RegionShort region = new RegionShort(nx, ny);
                // 원본 CSV: 위도(초/100), 경도(초/100) 열에 십진수 좌표가 저장되어 있습니다.
                double latitude = Double.parseDouble(row.get("위도(초/100)").trim());
                double longitude = Double.parseDouble(row.get("경도(초/100)").trim());

                if (data.putIfAbsent(regionName, region) != null) {
                    log.warn("중복된 지역명 스킵: {}", regionName);
                } else {
                    locations.put(regionName, new GeoCoordinates(latitude, longitude));
                }
            }
        }

        shortRegions = Map.copyOf(data);
        geoCoordinates = Map.copyOf(locations);
    }

    // 단기예보 지역정보 조회
    public RegionShort getShortRegion(String regionName) {
        return shortRegions.get(regionName);
    }

    public GeoCoordinates getGeoCoordinates(String regionName) {
        return geoCoordinates.get(regionName);
    }
}
