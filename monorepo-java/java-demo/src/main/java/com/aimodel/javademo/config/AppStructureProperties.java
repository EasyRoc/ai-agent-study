package com.aimodel.javademo.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

/**
 * 第 2 周：外置 Prompt 版本、L0 滑窗、兜底重试与日志脱敏。
 */
@ConfigurationProperties(prefix = "app.structure")
public class AppStructureProperties {

    /**
     * 与 <code>application-v1.yml</code> / <code>application-v2.yml</code> 或 <code>app.structure.prompt-version</code> 对齐；决定加载哪个 <code>prompts/structure-v*.txt</code>。
     */
    private String promptVersion = "v1";

    private L0 l0 = new L0();

    private Log log = new Log();

    public String getPromptVersion() {
        return promptVersion;
    }

    public void setPromptVersion(String promptVersion) {
        this.promptVersion = promptVersion;
    }

    public L0 getL0() {
        return l0;
    }

    public void setL0(L0 l0) {
        this.l0 = l0;
    }

    public Log getLog() {
        return log;
    }

    public void setLog(Log log) {
        this.log = log;
    }

    public static class L0 {
        /**
         * 滑窗内最多保留的「消息条数」（含 user 与 assistant），超过则丢弃最早成对或单条。
         */
        private int maxMessages = 12;

        public int getMaxMessages() {
            return maxMessages;
        }

        public void setMaxMessages(int maxMessages) {
            this.maxMessages = maxMessages;
        }
    }

    public static class Log {
        /**
         * 选做：日志中 user 原文最大长度，防完整 PII 落日志（第 8 周可深化）。
         */
        private int maxUserCharsInLog = 100;

        public int getMaxUserCharsInLog() {
            return maxUserCharsInLog;
        }

        public void setMaxUserCharsInLog(int maxUserCharsInLog) {
            this.maxUserCharsInLog = maxUserCharsInLog;
        }
    }
}
