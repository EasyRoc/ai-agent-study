package com.aimodel.javademo.service;

import java.util.List;
import java.util.Map;
import java.util.UUID;

import com.aimodel.javademo.api.dto.IntentSlotsResult;
import com.aimodel.javademo.api.dto.StructureResponse;
import com.aimodel.javademo.config.AppStructureProperties;

import com.alibaba.cloud.ai.graph.RunnableConfig;
import com.alibaba.cloud.ai.graph.agent.ReactAgent;
import com.alibaba.cloud.ai.graph.exception.GraphRunnerException;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.chat.messages.AssistantMessage;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

/**
 * 第 2 周：<strong>短期记忆（L0）</strong> 使用 <strong>checkpointer</strong> ——
 * {@link com.alibaba.cloud.ai.graph.checkpoint.savers.MemorySaver} 挂到
 * {@link com.alibaba.cloud.ai.graph.agent.ReactAgent#builder() ReactAgent}，通过
 * {@link RunnableConfig#threadId()} 隔离会话，与
 * <a href="https://java2ai.com/docs/frameworks/agent-framework/tutorials/memory">官方短期记忆</a> 说明一致。
 * <p>
 * <strong>Structured Output</strong>：由 {@code outputType(IntentSlotsResult.class)} 在图内产生 JSON，再将
 * {@link AssistantMessage#getText()} 反序列化为强类型；非手写 <code>json.loads</code> 主路径。
 * </p>
 * <p>
 * 多轮进模型前由 {@link com.aimodel.javademo.config.StructureL0TrimmingHook} 做滑窗，对应原 {@code app.structure.l0.max-messages}。
 * </p>
 * <p>
 * 与手写 {@code ConcurrentHashMap} 相比：会话状态由 <strong>Graph checkpoint</strong> 管理，可替换为
 * <code>RedisSaver</code> 等而<strong>不</strong>改业务代码形态。
 * </p>
 */
@Service
public class StructureExtractionService {

    private static final Logger log = LoggerFactory.getLogger(StructureExtractionService.class);

    private final ReactAgent structureAgent;
    private final AppStructureProperties structureProperties;
    private final StructurePromptLoader promptLoader;
    private final ObjectMapper objectMapper;
    private final Object agentLock = new Object();

    public StructureExtractionService(
            ReactAgent structureIntentReactAgent,
            AppStructureProperties structureProperties,
            StructurePromptLoader promptLoader,
            ObjectMapper objectMapper
    ) {
        this.structureAgent = structureIntentReactAgent;
        this.structureProperties = structureProperties;
        this.promptLoader = promptLoader;
        this.objectMapper = objectMapper;
    }

    public StructureResponse extract(String raw, String sessionIdIn) {
        if (raw == null || raw.isBlank()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "raw 不能为空");
        }
        String sid = (sessionIdIn == null || sessionIdIn.isBlank())
                ? UUID.randomUUID().toString()
                : sessionIdIn.trim();
        String pv = this.structureProperties.getPromptVersion();
        String system = this.promptLoader.loadSystemPrompt();

        if (log.isInfoEnabled()) {
            String preview = truncateForLog(raw, this.structureProperties.getLog().getMaxUserCharsInLog());
            log.info("structure(checkpointer): sessionId={} promptVersion={} userPreview=\"{}\"", sid, pv, preview);
        }

        RunnableConfig config = RunnableConfig.builder()
                .threadId(sid)
                .build();

        AssistantMessage assistant;
        try {
            synchronized (this.agentLock) {
                this.structureAgent.setSystemPrompt(system);
                assistant = this.structureAgent.call(raw.trim(), config);
            }
        } catch (GraphRunnerException e) {
            log.warn("ReactAgent 调用失败: {}", e.toString());
            throw new ResponseStatusException(HttpStatus.BAD_GATEWAY, "结构抽取或图执行失败: " + e.getMessage());
        }

        IntentSlotsResult result = parseAssistantToIntent(assistant);
        if (result == null) {
            throw new ResponseStatusException(HttpStatus.BAD_GATEWAY, "无法将模型输出反序列化为 IntentSlots");
        }

        var res = new StructureResponse();
        res.setParsed(result);
        res.setPromptVersion(pv);
        res.setSessionId(sid);
        res.setHistoryMessageCount(countThreadMessages(sid));
        return res;
    }

    @SuppressWarnings("unchecked")
    private int countThreadMessages(String threadId) {
        try {
            Map<String, Object> st = this.structureAgent.getThreadState(threadId);
            if (st == null) {
                return 0;
            }
            Object msg = st.get("messages");
            if (msg instanceof List) {
                return ((List<?>) msg).size();
            }
        } catch (Exception e) {
            log.debug("getThreadState 读取失败: {}", e.toString());
        }
        return 0;
    }

    private IntentSlotsResult parseAssistantToIntent(AssistantMessage assistant) {
        if (assistant == null) {
            return null;
        }
        String text = assistant.getText();
        if (text == null || text.isBlank()) {
            return null;
        }
        String cleaned = text.trim();
        if (cleaned.startsWith("```")) {
            cleaned = stripMarkdownFence(cleaned);
        }
        try {
            return this.objectMapper.readValue(cleaned, IntentSlotsResult.class);
        } catch (JsonProcessingException e) {
            log.debug("强类型反序列化失败: {}", e.getMessage());
            return null;
        }
    }

    private static String stripMarkdownFence(String s) {
        String t = s;
        if (t.startsWith("```json")) {
            t = t.substring("```json".length()).trim();
        } else if (t.startsWith("```")) {
            t = t.substring(3).trim();
        }
        if (t.endsWith("```")) {
            t = t.substring(0, t.length() - 3).trim();
        }
        return t;
    }

    private static String truncateForLog(String raw, int max) {
        if (raw == null) {
            return "";
        }
        if (raw.length() <= max) {
            return raw;
        }
        return raw.substring(0, max) + "…(截断)";
    }
}
