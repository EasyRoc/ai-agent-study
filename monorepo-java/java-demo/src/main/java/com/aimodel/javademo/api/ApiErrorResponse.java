package com.aimodel.javademo.api;

import com.fasterxml.jackson.annotation.JsonInclude;

/**
 * 统一错误体：与课表第 1 周第 3 天要求一致，含 <code>code</code>、<code>message</code>，不直接暴露密钥或长堆栈给客户端。
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
public class ApiErrorResponse {

    private String code;
    private String message;

    public ApiErrorResponse() {
    }

    public ApiErrorResponse(String code, String message) {
        this.code = code;
        this.message = message;
    }

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }
}
