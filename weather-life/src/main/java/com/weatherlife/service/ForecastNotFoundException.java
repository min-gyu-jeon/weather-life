package com.weatherlife.service;

public class ForecastNotFoundException extends RuntimeException {
    public ForecastNotFoundException(String message) { super(message); }
}
