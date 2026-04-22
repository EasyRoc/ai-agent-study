package com.aimodel.javademo.config;

import java.util.ArrayList;
import java.util.List;

import org.springframework.boot.context.properties.ConfigurationProperties;

/**
 * 第 1 周第 5 天：业务 API 的密钥头、期望值与<strong>不鉴权</strong>白名单（探活、Spring <code>/error</code> 等）。
 */
@ConfigurationProperties(prefix = "app.security")
public class AppSecurityProperties {

    /**
     * 请求头名，与课表 <code>X-API-Key</code> 一致。
     */
    private String apiKeyHeader = "X-API-Key";

    /**
     * 占位期允许的值，默认 <code>demo</code>；生产应改为从密钥管理拉取，可用环境变量覆盖（见 <code>application.yml</code>）。
     */
    private String expectedApiKey = "demo";

    private List<String> publicPaths = new ArrayList<>(List.of(
            "/api/v1/health/**",
            "/error"
    ));

    public String getApiKeyHeader() {
        return apiKeyHeader;
    }

    public void setApiKeyHeader(String apiKeyHeader) {
        this.apiKeyHeader = apiKeyHeader;
    }

    public String getExpectedApiKey() {
        return expectedApiKey;
    }

    public void setExpectedApiKey(String expectedApiKey) {
        this.expectedApiKey = expectedApiKey;
    }

    public List<String> getPublicPaths() {
        return publicPaths;
    }

    public void setPublicPaths(List<String> publicPaths) {
        this.publicPaths = publicPaths;
    }
}
