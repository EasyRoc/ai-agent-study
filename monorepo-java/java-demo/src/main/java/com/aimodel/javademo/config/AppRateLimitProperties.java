package com.aimodel.javademo.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

/**
 * 第 1 周第 5 天（可选）：按客户端 IP 的「滑动窗口内每分钟请求数」上限，内存实现，多实例<strong>不</strong>共享。
 */
@ConfigurationProperties(prefix = "app.rate-limit")
public class AppRateLimitProperties {

    private boolean enabled = true;

    /**
     * 每 IP、每 60s 内最多通过次数；超过则 HTTP 429。
     */
    private int perMinute = 30;

    public boolean isEnabled() {
        return enabled;
    }

    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
    }

    public int getPerMinute() {
        return perMinute;
    }

    public void setPerMinute(int perMinute) {
        this.perMinute = perMinute;
    }
}
