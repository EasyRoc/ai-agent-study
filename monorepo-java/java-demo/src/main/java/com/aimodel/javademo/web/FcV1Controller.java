package com.aimodel.javademo.web;

import com.aimodel.javademo.api.dto.FcChatRequest;
import com.aimodel.javademo.api.dto.FcChatResponse;
import com.aimodel.javademo.service.FunctionCallingChatService;

import jakarta.validation.Valid;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 第 1 周第 7 天（扩展）：Function Calling 最小入口，经网关、需 {@code X-API-Key}（与 /chat 一致）。
 */
@RestController
@RequestMapping(FcV1Controller.BASE)
public class FcV1Controller {

    public static final String BASE = "/api/v1/fc";

    private final FunctionCallingChatService functionCallingChatService;

    public FcV1Controller(FunctionCallingChatService functionCallingChatService) {
        this.functionCallingChatService = functionCallingChatService;
    }

    @PostMapping(
            value = "/chat",
            consumes = MediaType.APPLICATION_JSON_VALUE,
            produces = MediaType.APPLICATION_JSON_VALUE
    )
    public FcChatResponse chat(@RequestBody @Valid FcChatRequest request) {
        return this.functionCallingChatService.invoke(request.getPrompt().trim());
    }
}
