package com.weatherlife.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

/** One weather-grid/time row. Timestamps are Korea local (KST), no timezone conversion. */
@Entity
@Table(name = "weather_hourly_forecast", uniqueConstraints = @UniqueConstraint(
        name = "uk_weather_grid_forecast_at", columnNames = {"grid_x", "grid_y", "forecast_at"}),
        indexes = @Index(name = "idx_weather_forecast_at", columnList = "forecast_at"))
public class HourlyForecast {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @Column(name = "grid_x", nullable = false) private int gridX;
    @Column(name = "grid_y", nullable = false) private int gridY;
    @Column(name = "forecast_at", nullable = false) private LocalDateTime forecastAt;
    @Column(name = "issued_at", nullable = false) private LocalDateTime issuedAt;
    @Column(name = "collected_at", nullable = false) private LocalDateTime collectedAt;

    // Preserve KMA's original values. Some future forecasts use qualitative values rather than numerics.
    @Column(length = 30) private String tmp;
    @Column(length = 30) private String reh;
    @Column(length = 30) private String wsd;
    @Column(length = 30) private String sky;
    @Column(length = 30) private String pty;
    @Column(length = 30) private String pop;
    @Column(length = 40) private String pcp;
    @Column(length = 40) private String sno;
    @Column(length = 30) private String uuu;
    @Column(length = 30) private String vvv;
    @Column(length = 30) private String vec;
    @Column(length = 30) private String wav;
    @Column(length = 30) private String tmn;
    @Column(length = 30) private String tmx;

    protected HourlyForecast() { }
    public HourlyForecast(int gridX, int gridY, LocalDateTime forecastAt) {
        this.gridX = gridX;
        this.gridY = gridY;
        this.forecastAt = forecastAt;
    }
    public void replaceWith(LocalDateTime issue, LocalDateTime collection, java.util.Map<String, String> values) {
        this.issuedAt = issue;
        this.collectedAt = collection;
        this.tmp = values.get("TMP"); this.reh = values.get("REH"); this.wsd = values.get("WSD");
        this.sky = values.get("SKY"); this.pty = values.get("PTY"); this.pop = values.get("POP");
        this.pcp = values.get("PCP"); this.sno = values.get("SNO"); this.uuu = values.get("UUU");
        this.vvv = values.get("VVV"); this.vec = values.get("VEC"); this.wav = values.get("WAV");
        this.tmn = values.get("TMN"); this.tmx = values.get("TMX");
    }
    public Long getId() { return id; }
    public int getGridX() { return gridX; }
    public int getGridY() { return gridY; }
    public LocalDateTime getForecastAt() { return forecastAt; }
    public LocalDateTime getIssuedAt() { return issuedAt; }
    public LocalDateTime getCollectedAt() { return collectedAt; }
    public String getTmp() { return tmp; } public String getReh() { return reh; }
    public String getWsd() { return wsd; } public String getSky() { return sky; }
    public String getPty() { return pty; } public String getPop() { return pop; }
    public String getPcp() { return pcp; } public String getSno() { return sno; }
    public String getUuu() { return uuu; } public String getVvv() { return vvv; }
    public String getVec() { return vec; } public String getWav() { return wav; }
    public String getTmn() { return tmn; } public String getTmx() { return tmx; }
    public java.util.Map<String, String> categories() {
        var result = new java.util.LinkedHashMap<String, String>();
        add(result,"TMP",tmp); add(result,"REH",reh); add(result,"WSD",wsd);
        add(result,"SKY",sky); add(result,"PTY",pty); add(result,"POP",pop);
        add(result,"PCP",pcp); add(result,"SNO",sno); add(result,"UUU",uuu);
        add(result,"VVV",vvv); add(result,"VEC",vec); add(result,"WAV",wav);
        add(result,"TMN",tmn); add(result,"TMX",tmx);
        return result;
    }
    private static void add(java.util.Map<String,String> result, String key, String value) {
        if (value != null) result.put(key, value);
    }
}
