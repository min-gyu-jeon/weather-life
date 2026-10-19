package com.weatherlife.service;

import org.springframework.http.HttpStatus;

/** 외부 AI 예측 서버 호출 실패를 프론트에 안전한 형태로 전달합니다. */
public class AiForecastException extends RuntimeException {
    private final HttpStatus status;

    public AiForecastException(HttpStatus status, String message) {
        super(message);
        this.status = status;
    }

    public HttpStatus status() {
        return status;
    }
}
