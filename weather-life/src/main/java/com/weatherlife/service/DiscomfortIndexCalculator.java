package com.weatherlife.service;

/**
 * Temperature/humidity discomfort index (DI), calculated on demand from KMA TMP and REH.
 * DI = 0.81*T + 0.01*RH*(0.99*T - 14.3) + 46.3
 * T is degrees Celsius and RH is percent (0-100).
 *
 * This is not the official perceived temperature or heat index.
 * Invalid/missing input returns null so the API doesn't fabricate a weather value.
 */
public final class DiscomfortIndexCalculator {
    private DiscomfortIndexCalculator() { }

    public static Double calculate(String temperature, String humidity) {
        try {
            if (temperature == null || humidity == null) return null;
            double t = Double.parseDouble(temperature.trim());
            double rh = Double.parseDouble(humidity.trim());
            if (!Double.isFinite(t) || !Double.isFinite(rh) || rh < 0 || rh > 100) return null;
            double di = 0.81 * t + 0.01 * rh * (0.99 * t - 14.3) + 46.3;
            return Math.round(di * 10.0) / 10.0;
        } catch (NumberFormatException ex) {
            return null;
        }
    }
}
