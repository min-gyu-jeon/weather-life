package com.weatherlife.repository;

import com.weatherlife.entity.HourlyForecast;
import org.springframework.data.jpa.repository.JpaRepository;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface HourlyForecastRepository extends JpaRepository<HourlyForecast, Long> {
    Optional<HourlyForecast> findByGridXAndGridYAndForecastAt(int gridX, int gridY, LocalDateTime forecastAt);

    @Modifying
    @Query("delete from HourlyForecast f where f.forecastAt < :cutoff")
    int deleteForecastsBefore(@Param("cutoff") LocalDateTime cutoff);

    List<HourlyForecast> findByGridXAndGridYAndForecastAtGreaterThanEqualAndForecastAtLessThanOrderByForecastAtAsc(
            int gridX, int gridY, LocalDateTime start, LocalDateTime end);
}
