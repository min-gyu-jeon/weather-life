package com.weatherlife.service;

/** 기상청 원본 응답이 오류이거나 기대한 JSON 구조와 맞지 않을 때 발생합니다. */
public class WeatherForecastMappingException extends RuntimeException {
    public WeatherForecastMappingException(String message) {
        super(message);
    }
    public WeatherForecastMappingException(String message, Throwable cause) {
        super(message, cause);
    }
}
