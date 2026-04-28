package com.aimodel.javademo.api.dto.rag;

import com.fasterxml.jackson.annotation.JsonProperty;

import jakarta.validation.constraints.NotBlank;

/**
 * 第 4 周 <code>POST /api/v1/ask</code> 请求体，转发 Python <code>POST /rag/ask</code>。
 */
public class RagAskRequestBody {

    @NotBlank
    private String question;

    @JsonProperty("topK")
    /** 检索 top-K，默认 4 */
    private Integer topK = 4;

    @JsonProperty("sessionId")
    /** 可选；多轮/审计；L0 短期记忆在 Python 侧，不入向量库 */
    private String sessionId;

    /**
     * 可选；第 5 周幂等：同一值重复提交时直接返回**同一份**已缓存的聚合结果（与 question 解耦的演示型实现）。
     */
    @JsonProperty("clientRequestId")
    private String clientRequestId;

    public String getQuestion() {
        return question;
    }

    public void setQuestion(String question) {
        this.question = question;
    }

    public Integer getTopK() {
        return topK;
    }

    public void setTopK(Integer topK) {
        this.topK = topK;
    }

    public String getSessionId() {
        return sessionId;
    }

    public void setSessionId(String sessionId) {
        this.sessionId = sessionId;
    }

    public String getClientRequestId() {
        return clientRequestId;
    }

    public void setClientRequestId(String clientRequestId) {
        this.clientRequestId = clientRequestId;
    }
}
