package com.weatherlife.controller;

import com.weatherlife.service.NoOutfitException;
import jakarta.validation.ConstraintViolationException;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import java.util.List;

/** 기존 프로젝트에 복사해도 다른 컨트롤러의 예외 처리에 영향을 주지 않게 범위를 한정합니다. */
@RestControllerAdvice(assignableTypes = APIController.class)
public class OutfitExceptionHandler {
    public record ApiError(String code, String message, List<String> details) { }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    ResponseEntity<ApiError> invalid(MethodArgumentNotValidException ex) {
        var details = ex.getBindingResult().getFieldErrors().stream()
                .map(e -> e.getField() + ": " + e.getDefaultMessage()).distinct().sorted().toList();
        return ResponseEntity.badRequest().body(new ApiError("INVALID_REQUEST", "입력값을 확인하세요.", details));
    }
    @ExceptionHandler(ConstraintViolationException.class)
    ResponseEntity<ApiError> invalidService(ConstraintViolationException ex) {
        var details = ex.getConstraintViolations().stream()
                .map(e -> e.getPropertyPath() + ": " + e.getMessage()).sorted().toList();
        return ResponseEntity.badRequest().body(new ApiError("INVALID_REQUEST", "입력값을 확인하세요.", details));
    }
    @ExceptionHandler(HttpMessageNotReadableException.class)
    ResponseEntity<ApiError> malformed(HttpMessageNotReadableException ex) {
        return ResponseEntity.badRequest().body(new ApiError("INVALID_JSON",
                "JSON 형식·숫자 타입·필드명·enum 값을 확인하세요. enum은 대문자입니다.", List.of()));
    }
    @ExceptionHandler(NoOutfitException.class)
    ResponseEntity<ApiError> noOutfit(NoOutfitException ex) {
        return ResponseEntity.status(422).body(new ApiError("NO_MATCHING_OUTFIT", ex.getMessage(), List.of()));
    }
}
