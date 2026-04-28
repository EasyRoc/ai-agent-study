package com.aimodel.javademo.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

/**
 * 第 3 周：Python 向量服务基址与超时，对应课表 <code>vector.baseUrl</code>。
 */
@ConfigurationProperties(prefix = "app.vector")
public class AppVectorProperties {

    private String baseUrl = "http://127.0.0.1:8010";
    private int connectTimeoutMs = 5000;
    private int readTimeoutMs = 5000;
    /** 第 4 周：<code>POST /rag/ask</code> 聚合链略长，默认 60s */
    private int ragReadTimeoutMs = 60000;

    public String getBaseUrl() {
        return baseUrl;
    }

    public void setBaseUrl(String baseUrl) {
        this.baseUrl = baseUrl;
    }

    public int getConnectTimeoutMs() {
        return connectTimeoutMs;
    }

    public void setConnectTimeoutMs(int connectTimeoutMs) {
        this.connectTimeoutMs = connectTimeoutMs;
    }

    public int getReadTimeoutMs() {
        return readTimeoutMs;
    }

    public void setReadTimeoutMs(int readTimeoutMs) {
        this.readTimeoutMs = readTimeoutMs;
    }

    public int getRagReadTimeoutMs() {
        return ragReadTimeoutMs;
    }

    public void setRagReadTimeoutMs(int ragReadTimeoutMs) {
        this.ragReadTimeoutMs = ragReadTimeoutMs;
    }
}
