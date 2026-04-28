package com.aimodel.javademo.web;

import com.aimodel.javademo.api.dto.FcChatRequest;
import com.aimodel.javademo.api.dto.FcChatResponse;
import com.aimodel.javademo.service.AgentFcService;

import jakarta.validation.Valid;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 第 6 周：聚合「请假相关政策检索 + mock 天气」等多意图；由模型选择 {@link com.aimodel.javademo.tools.Week06AgentFcTools}。
 */
@RestController
@RequestMapping(AgentFcV1Controller.BASE)
public class AgentFcV1Controller {

    public static final String BASE = "/api/v1/agent/fc";

    private final AgentFcService agentFcService;

    public AgentFcV1Controller(AgentFcService agentFcService) {
        this.agentFcService = agentFcService;
    }

    /**
     * 与 FC 语义一致：<code>persist</code> 由 Spring AI 在多轮工具内自动完成直至终答。
     */
    @PostMapping(consumes = MediaType.APPLICATION_JSON_VALUE, produces = MediaType.APPLICATION_JSON_VALUE)
    public FcChatResponse agentFc(@RequestBody @Valid FcChatRequest request) {
        return this.agentFcService.invoke(request.getPrompt().trim());
    }
}
