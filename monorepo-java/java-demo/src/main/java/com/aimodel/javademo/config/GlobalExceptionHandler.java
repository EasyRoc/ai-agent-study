package com.aimodel.javademo.config;

import com.aimodel.javademo.api.ApiErrorResponse;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.lang.Nullable;
import org.springframework.validation.FieldError;
import org.springframework.validation.ObjectError;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.server.ResponseStatusException;

/**
 * 将可预期异常与校验失败映射为统一 JSON 体 {@link ApiErrorResponse}，避免把密钥、内部细节直接返回给客户端。
 */
@RestControllerAdvice
public class GlobalExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(GlobalExceptionHandler.class);

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ApiErrorResponse> handleValid(MethodArgumentNotValidException e) {
        String message = e.getAllErrors().stream()
                .map(GlobalExceptionHandler::formatError)
                .reduce((a, b) -> a + "；" + b)
                .orElse("参数不合法");
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                .body(new ApiErrorResponse("VALIDATION_ERROR", message));
    }

    private static String formatError(ObjectError err) {
        if (err instanceof FieldError fe) {
            return fe.getField() + ": " + fe.getDefaultMessage();
        }
        return err.getDefaultMessage() != null ? err.getDefaultMessage() : err.getCode();
    }

    @ExceptionHandler(HttpMessageNotReadableException.class)
    public ResponseEntity<ApiErrorResponse> handleBadJson(HttpMessageNotReadableException e) {
        return ResponseEntity.status(HttpStatus.BAD_REQUEST)
                .body(new ApiErrorResponse("BAD_REQUEST", "JSON 体无法解析或结构不正确"));
    }

    @ExceptionHandler(ResponseStatusException.class)
    public ResponseEntity<ApiErrorResponse> handleRse(ResponseStatusException e) {
        int status = e.getStatusCode().value();
        String reason = e.getReason() != null ? e.getReason() : "请求处理失败";
        String code = mapStatusToCode(status);
        if (status == 502 && reason.startsWith("VECTOR_TIMEOUT")) {
            code = "VECTOR_TIMEOUT";
        }
        if (status == 502 && reason.startsWith("RAG_TIMEOUT")) {
            code = "RAG_TIMEOUT";
        }
        return ResponseEntity.status(status).body(new ApiErrorResponse(code, reason));
    }

    private static String mapStatusToCode(int status) {
        return switch (status) {
            case 400 -> "BAD_REQUEST";
            case 404 -> "NOT_FOUND";
            case 401 -> "UNAUTHORIZED";
            case 403 -> "FORBIDDEN";
            case 429 -> "RATE_LIMITED";
            case 502 -> "LLM_UPSTREAM";
            case 503 -> "SERVICE_UNAVAILABLE";
            default -> "HTTP_" + status;
        };
    }

    @ExceptionHandler(Exception.class)
    public ResponseEntity<ApiErrorResponse> handleAny(Exception e, @Nullable org.springframework.web.context.request.WebRequest w) {
        log.error("未处理异常: {}", w != null ? w.getDescription(false) : "", e);
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(new ApiErrorResponse("INTERNAL_ERROR", "服务内部错误"));
    }
}
