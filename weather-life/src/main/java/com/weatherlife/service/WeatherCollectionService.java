package com.weatherlife.service;

import com.weatherlife.dto.RegionShort;
import com.weatherlife.entity.HourlyForecast;
import com.weatherlife.repository.HourlyForecastRepository;
import org.springframework.boot.json.JsonParserFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.support.TransactionTemplate;
import org.springframework.transaction.PlatformTransactionManager;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.TreeMap;

/** Fetch once, validate, and upsert each grid/forecast-hour with the newest issuance. */
@Service
public class WeatherCollectionService {
    private static final ZoneId KST = ZoneId.of("Asia/Seoul");
    private final OfficialRegionService regionService;
    private final SeoulDistrictService districts;
    private final OfficialWeatherService weatherService;
    private final HourlyForecastRepository repository;
    private final TransactionTemplate transactionTemplate;

    public record CollectionResult(String regionName, int gridX, int gridY,
                                   LocalDateTime issuedAt, int inserted, int updated, int unchanged, int skipped) {}
    public WeatherCollectionService(OfficialRegionService regionService,
                                    SeoulDistrictService districts,
                                    OfficialWeatherService weatherService,
                                    HourlyForecastRepository repository,
                                    PlatformTransactionManager transactionManager) {
        this.regionService = regionService;
        this.districts = districts;
        this.weatherService = weatherService;
        this.repository = repository;
        this.transactionTemplate = new TransactionTemplate(transactionManager);
    }

    // Do not hold a DB transaction while waiting for KMA's network response.
    public CollectionResult collect(String regionName) {
        String normalized = districts.normalizeRegionName(regionName);
        RegionShort region = regionService.getShortRegion(normalized);
        if (region == null) throw new IllegalArgumentException("존재하지 않는 지역: " + regionName);
        String raw = weatherService.getShortRangeForecast(normalized);
        return upsertParsed(regionName, region, parse(raw));
    }

    /** Network-free entry point, also useful for integration tests. */
    public CollectionResult upsertParsed(String regionName, RegionShort region, ParsedForecast parsed) {
        return transactionTemplate.execute(status -> doUpsert(regionName, region, parsed));
    }

    private CollectionResult doUpsert(String regionName, RegionShort region, ParsedForecast parsed) {
        if (parsed.hours().isEmpty()) throw new WeatherForecastMappingException("저장할 예보가 없습니다.");
        LocalDateTime start = parsed.hours().firstKey();
        LocalDateTime end = parsed.hours().lastKey().plusMinutes(1);
        var existing = repository.findByGridXAndGridYAndForecastAtGreaterThanEqualAndForecastAtLessThanOrderByForecastAtAsc(
                region.nx(), region.ny(), start, end);
        Map<LocalDateTime, HourlyForecast> byHour = new HashMap<>();
        for (var row : existing) byHour.put(row.getForecastAt(), row);
        LocalDateTime fetchedAt = LocalDateTime.now(KST);
        int inserted = 0, updated = 0, unchanged = 0, skipped = 0;
        for (var entry : parsed.hours().entrySet()) {
            var values = entry.getValue();
            // Reject incomplete core conditions to avoid destroying a usable older forecast.
            boolean complete = validCore(values);
            boolean extremeOnly = hasDailyExtreme(values);
            if (!complete && !extremeOnly) { skipped++; continue; }
            HourlyForecast row = byHour.get(entry.getKey());
            if (row != null && !parsed.issuedAt().isAfter(row.getIssuedAt())) { unchanged++; continue; }
            // New partial data must not erase an old complete forecast for this hour.
            if (row != null && !complete && validCore(row.categories())) { skipped++; continue; }
            if (row == null) { row = new HourlyForecast(region.nx(), region.ny(), entry.getKey()); inserted++; }
            else updated++;
            row.replaceWith(parsed.issuedAt(), fetchedAt, values);
            repository.save(row);
        }
        if (inserted + updated == 0 && existing.isEmpty()) {
            throw new WeatherForecastMappingException("유효한 기온/습도/풍속/하늘/강수 데이터가 없습니다.");
        }
        return new CollectionResult(regionName, region.nx(), region.ny(), parsed.issuedAt(),
                inserted, updated, unchanged, skipped);
    }
    private static boolean hasDailyExtreme(Map<String, String> v) {
        // KMA TMN/TMX may be published at hours lacking other hourly categories.
        return range(v.get("TMN"), -50, 50) || range(v.get("TMX"), -50, 50);
    }
    private static boolean validCore(Map<String, String> v) {
        return range(v.get("TMP"), -50,50) && range(v.get("REH"), 0,100) && range(v.get("WSD"),0,60)
                && ("1".equals(v.get("SKY")) || "3".equals(v.get("SKY")) || "4".equals(v.get("SKY")))
                && v.containsKey("PTY");
    }
    private static boolean range(String value, double min, double max) {
        try { double n = Double.parseDouble(value); return Double.isFinite(n) && n >= min && n <= max; }
        catch (RuntimeException ex) { return false; }
    }
    public record ParsedForecast(LocalDateTime issuedAt, TreeMap<LocalDateTime, Map<String,String>> hours) { }

    @SuppressWarnings("unchecked")
    public ParsedForecast parse(String raw) {
        try {
            Map<String, Object> root = JsonParserFactory.getJsonParser().parseMap(raw);
            Map<String, Object> response = map(root.get("response"));
            Map<String, Object> header = map(response.get("header"));
            if (!"00".equals(String.valueOf(header.get("resultCode")))) {
                throw new WeatherForecastMappingException("기상청 API 오류: " + header.get("resultMsg"));
            }
            Map<String, Object> body = map(response.get("body"));
            Map<String, Object> items = map(body.get("items"));
            if (!(items.get("item") instanceof java.util.List<?> rows) || rows.isEmpty()) {
                throw new WeatherForecastMappingException("기상청 단기예보 항목이 비어 있습니다.");
            }
            // An incomplete page must never silently replace DB data.
            int totalCount = Integer.parseInt(String.valueOf(body.get("totalCount")));
            if (totalCount > rows.size()) {
                throw new WeatherForecastMappingException("기상청 응답 일부만 수신: " + rows.size() + "/" + totalCount
                        + ". numOfRows/페이지네이션을 확인하세요.");
            }
            TreeMap<LocalDateTime, Map<String,String>> hourly = new TreeMap<>();
            LocalDateTime issuance = null;
            for (Object item : rows) {
                Map<String, Object> row = map(item);
                LocalDateTime issue = LocalDate.parse(str(row.get("baseDate")), DateTimeFormatter.BASIC_ISO_DATE)
                        .atTime(LocalTime.parse(str(row.get("baseTime")), DateTimeFormatter.ofPattern("HHmm")));
                LocalDateTime at = LocalDate.parse(str(row.get("fcstDate")), DateTimeFormatter.BASIC_ISO_DATE)
                        .atTime(LocalTime.parse(str(row.get("fcstTime")), DateTimeFormatter.ofPattern("HHmm")));
                if (issuance == null) issuance = issue;
                if (!issue.equals(issuance)) throw new WeatherForecastMappingException("발표시각이 섞인 응답입니다.");
                hourly.computeIfAbsent(at, ignored -> new LinkedHashMap<>())
                        .put(str(row.get("category")), str(row.get("fcstValue")));
            }
            return new ParsedForecast(issuance, hourly);
        } catch (WeatherForecastMappingException ex) {
            throw ex;
        } catch (Exception ex) {
            throw new WeatherForecastMappingException("기상청 응답 파싱/검증 오류", ex);
        }
    }
    private static String str(Object value) { return value == null ? "" : value.toString(); }
    @SuppressWarnings("unchecked")
    private static Map<String,Object> map(Object v) {
        if (!(v instanceof Map<?,?> m)) throw new WeatherForecastMappingException("기상청 응답 구조가 다릅니다.");
        return (Map<String,Object>)m;
    }
}
