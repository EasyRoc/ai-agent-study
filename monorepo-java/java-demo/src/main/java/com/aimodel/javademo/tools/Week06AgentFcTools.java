package com.aimodel.javademo.tools;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.aimodel.javademo.api.dto.vector.VectorChunkItem;
import com.aimodel.javademo.api.dto.vector.VectorSearchResponseBody;
import com.aimodel.javademo.service.VectorServiceClient;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ResponseStatusException;

/**
 * 第 6 周：<code>/api/v1/agent/fc</code> 专用工具集。
 */

@Component
public class Week06AgentFcTools {

    private static final Logger log = LoggerFactory.getLogger(Week06AgentFcTools.class);

    private final VectorServiceClient vectorServiceClient;
    private final ObjectMapper objectMapper;

    private final ConcurrentHashMap<String, String> preferenceByUserKey = new ConcurrentHashMap<>();

    public Week06AgentFcTools(VectorServiceClient vectorServiceClient, ObjectMapper objectMapper) {
        this.vectorServiceClient = vectorServiceClient;
        this.objectMapper = objectMapper;
    }

    @Tool(
            name = "knowledge_search",
            description = "在企业 HR/制度向量库检索相关片段（内部调 Python POST /search）；参数 query 中文短句。"
    )
    public String knowledgeSearch(
            @ToolParam(description = "检索查询语句") String query
    ) {
        try {
            String q = query == null ? "" : query.trim();
            log.info("Week06AgentFcTools.knowledge_search start queryPreview={}",
                    preview(q, 160));
            ObjectNode root = this.objectMapper.createObjectNode();
            ArrayNode hits = root.putArray("hits");
            if (q.isEmpty()) {
                log.info("Week06AgentFcTools.knowledge_search skip empty_query");
                root.put("note", "empty query");
                return this.objectMapper.writeValueAsString(root);
            }
            VectorSearchResponseBody resp = this.vectorServiceClient.search(q, 5);
            if (resp.getResults() != null) {
                for (VectorChunkItem hit : resp.getResults()) {
                    ObjectNode row = hits.addObject();
                    row.put("id", hit.getId() == null ? "" : hit.getId());
                    String t = hit.getText() == null ? "" : hit.getText();
                    row.put("text", t.length() > 500 ? t.substring(0, 500) + "…" : t);
                }
            }
            log.info("Week06AgentFcTools.knowledge_search done hits={}", hits.size());
            return this.objectMapper.writeValueAsString(root);
        } catch (ResponseStatusException e) {
            log.warn("Week06AgentFcTools.knowledge_search vector_http status={} reason={}",
                    e.getStatusCode(), e.getReason());
            return errorJson(String.valueOf(e.getReason()));
        } catch (Exception e) {
            log.error("Week06AgentFcTools.knowledge_search failed", e);
            return errorJson(e.getMessage());
        }
    }

    @org.springframework.ai.tool.annotation.Tool(
            name = "get_weather_mock",
            description = "查询城市天气（演示 Mock）；参数 city。"
    )
    public String getWeatherMock(
            @org.springframework.ai.tool.annotation.ToolParam(description = "城市名") String city
    ) {
        String c = city == null || city.isBlank() ? "未知" : city.trim();
        log.info("Week06AgentFcTools.get_weather_mock city={}", preview(c, 80));
        try {
            ObjectNode root = this.objectMapper.createObjectNode();
            root.put("city", c);
            root.put("condition", "晴");
            root.put("temp_c", 26);
            root.put("mock", true);
            log.debug("Week06AgentFcTools.get_weather_mock done city={}", c);
            return this.objectMapper.writeValueAsString(root);
        } catch (Exception e) {
            log.error("Week06AgentFcTools.get_weather_mock failed", e);
            return errorJson(e.getMessage());
        }
    }

    @org.springframework.ai.tool.annotation.Tool(
            name = "save_user_preference",
            description = "写入用户偏好（L3 mock，进程内存）；参数 userKey 与偏好 JSON 片段 jsonValue。"
    )
    public String saveUserPreference(
            @org.springframework.ai.tool.annotation.ToolParam(description = "用户键") String userKey,
            @org.springframework.ai.tool.annotation.ToolParam(description = "JSON 偏好") String jsonValue
    ) {
        if (userKey == null || userKey.isBlank()) {
            log.warn("Week06AgentFcTools.save_user_preference rejected empty_userKey");
            return "{\"error\":\"empty userKey\"}";
        }
        String v = jsonValue == null ? "" : jsonValue;
        String key = userKey.trim();
        this.preferenceByUserKey.put(key, v);
        log.info("Week06AgentFcTools.save_user_preference userKey={} storedChars={}", preview(key, 128), v.length());
        try {
            Map<String, Object> m = new HashMap<>();
            m.put("ok", true);
            m.put("stored_chars", v.length());
            return this.objectMapper.writeValueAsString(m);
        } catch (Exception e) {
            log.error("Week06AgentFcTools.save_user_preference serialize failed", e);
            return "{\"ok\":false}";
        }
    }

    public Map<String, String> snapshotPreferencesForDemo() {
        return Map.copyOf(this.preferenceByUserKey);
    }

    private static String preview(String s, int max) {
        if (s == null) {
            return "";
        }
        if (s.length() <= max) {
            return s;
        }
        return s.substring(0, max) + "…";
    }

    private String errorJson(String msg) {
        try {
            ObjectNode n = this.objectMapper.createObjectNode();
            n.put("error", msg == null ? "" : msg);
            return this.objectMapper.writeValueAsString(n);
        } catch (Exception ignored) {
            return "{\"error\":\"serialization\"}";
        }
    }
}
