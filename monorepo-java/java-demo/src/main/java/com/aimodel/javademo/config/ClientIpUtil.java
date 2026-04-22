package com.aimodel.javademo.config;

import jakarta.servlet.http.HttpServletRequest;

/**
 * 取「逻辑客户端」IP：优先 <code>X-Forwarded-For</code> 第一个 hop（经网关/反代时），否则 <code>remoteAddr</code>。
 */
public final class ClientIpUtil {

    private ClientIpUtil() {
    }

    public static String resolve(HttpServletRequest request) {
        String xff = request.getHeader("X-Forwarded-For");
        if (xff != null) {
            String trimmed = xff.trim();
            if (!trimmed.isEmpty()) {
                int pos = trimmed.indexOf(',');
                if (pos > 0) {
                    return trimmed.substring(0, pos).trim();
                }
                return trimmed;
            }
        }
        return request.getRemoteAddr();
    }
}
