package com.aimodel.javademo.api.dto;

/**
 * {@code POST /api/v1/structure} 响应：强类型解析结果 + Prompt 版本 + 生效的 sessionId。
 */
public class StructureResponse {

    private IntentSlotsResult parsed;
    /**
     * 与 Profile / 配置一致，如 {@code v1}、{@code v2}。
     */
    private String promptVersion;
    /**
     * L0 会话 id（若请求未带则为本端新生成）。
     */
    private String sessionId;
    /**
     * 当前会话在滑窗内保留的消息条数（user+assistant 合计，便于验收 L0）。
     */
    private int historyMessageCount;

    public IntentSlotsResult getParsed() {
        return parsed;
    }

    public void setParsed(IntentSlotsResult parsed) {
        this.parsed = parsed;
    }

    public String getPromptVersion() {
        return promptVersion;
    }

    public void setPromptVersion(String promptVersion) {
        this.promptVersion = promptVersion;
    }

    public String getSessionId() {
        return sessionId;
    }

    public void setSessionId(String sessionId) {
        this.sessionId = sessionId;
    }

    public int getHistoryMessageCount() {
        return historyMessageCount;
    }

    public void setHistoryMessageCount(int historyMessageCount) {
        this.historyMessageCount = historyMessageCount;
    }
}
