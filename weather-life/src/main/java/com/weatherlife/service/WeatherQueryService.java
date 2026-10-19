package com.weatherlife.service;

import com.weatherlife.dto.ForecastDayResponse;
import com.weatherlife.dto.RegionShort;
import com.weatherlife.entity.HourlyForecast;
import com.weatherlife.repository.HourlyForecastRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;

/** Only reads the database. Neither this service nor the frontend calls KMA. */
@Service
public class WeatherQueryService {
    private final OfficialRegionService regionService;
    private final SeoulDistrictService districts;
    private final HourlyForecastRepository repository;
    public WeatherQueryService(OfficialRegionService regionService, SeoulDistrictService districts, HourlyForecastRepository repository) {
        this.regionService = regionService;
        this.districts = districts;
        this.repository = repository;
    }
    @Transactional(readOnly = true)
    public List<HourlyForecast> loadDay(String regionName, LocalDate date) {
        if (date == null) throw new IllegalArgumentException("date(YYYY-MM-DD)가 필요합니다.");
        RegionShort region = regionService.getShortRegion(districts.normalizeRegionName(regionName));
        if (region == null) throw new IllegalArgumentException("존재하지 않는 지역: " + regionName);
        var rows = repository.findByGridXAndGridYAndForecastAtGreaterThanEqualAndForecastAtLessThanOrderByForecastAtAsc(
                region.nx(), region.ny(), date.atStartOfDay(), date.plusDays(1).atStartOfDay());
        if (rows.isEmpty()) throw new ForecastNotFoundException(
                date + " / " + regionName + " 예보가 DB에 없습니다. 수집 지역과 마지막 수집 시각을 확인하세요.");
        return rows;
    }
    @Transactional(readOnly = true)
    public ForecastDayResponse.Hour getHour(String regionName, LocalDateTime forecastAt) {
        RegionShort region = regionService.getShortRegion(districts.normalizeRegionName(regionName));
        if (region == null) throw new IllegalArgumentException("존재하지 않는 지역: " + regionName);
        HourlyForecast row = repository.findByGridXAndGridYAndForecastAt(
                region.nx(), region.ny(), forecastAt).orElseThrow(() ->
                new ForecastNotFoundException(forecastAt + " / " + regionName + " 예보가 DB에 없습니다."));
        return ForecastDayResponse.Hour.from(row);
    }

    @Transactional(readOnly = true)
    public ForecastDayResponse getDay(String regionName, LocalDate date) {
        return ForecastDayResponse.from(date, regionName, loadDay(regionName, date));
    }
}
