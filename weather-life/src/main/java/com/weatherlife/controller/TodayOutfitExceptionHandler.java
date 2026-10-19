package com.weatherlife.controller;

import com.weatherlife.service.NoOutfitException;
import com.weatherlife.service.ForecastNotFoundException;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.List;
import jakarta.validation.ConstraintViolationException;

/** DB 예보 기반 시간별 의상 추천 API의 오류를 처리합니다. */
@RestControllerAdvice(assignableTypes = TodayOutfitController.class)
public class TodayOutfitExceptionHandler {
    public record ApiError(String code, String message, List<String> details) { }

    @ExceptionHandler(ConstraintViolationException.class)
    ResponseEntity<ApiError> invalidSelection(ConstraintViolationException ex) {
        return ResponseEntity.badRequest().body(new ApiError("INVALID_REQUEST", "추천 입력값을 확인하세요.",
                ex.getConstraintViolations().stream().map(v -> v.getPropertyPath() + ": " + v.getMessage()).sorted().toList()));
    }

    @ExceptionHandler(ForecastNotFoundException.class)
    ResponseEntity<ApiError> notFound(ForecastNotFoundException ex) {
        return ResponseEntity.status(404).body(new ApiError("FORECAST_NOT_FOUND", ex.getMessage(), List.of()));
    }

    @ExceptionHandler(NoOutfitException.class)
    ResponseEntity<ApiError> noOutfit(NoOutfitException ex) {
        return ResponseEntity.status(422).body(
                new ApiError("NO_MATCHING_OUTFIT", ex.getMessage(), List.of()));
    }

    @ExceptionHandler(IllegalArgumentException.class)
    ResponseEntity<ApiError> unknownRegion(IllegalArgumentException ex) {
        return ResponseEntity.badRequest().body(
                new ApiError("INVALID_REGION", ex.getMessage(), List.of()));
    }
}
