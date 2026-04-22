package com.aimodel.javademo.config;

import java.io.IOException;

import com.aimodel.javademo.api.ApiErrorResponse;

import com.fasterxml.jackson.databind.ObjectMapper;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.util.AntPathMatcher;
import org.springframework.web.filter.OncePerRequestFilter;

/**
 * 第 1 周第 5 天：对非白名单路径校验 <code>X-API-Key: demo</code>（可配置），缺/错时 401；可选按 IP 的每分钟限流，超额 429。  
 * 与课表第 3 天错误体风格一致，直接写出 JSON，不经 {@code GlobalExceptionHandler}（过滤器阶段）。
 */
@Component
@Order(Ordered.HIGHEST_PRECEDENCE + 20)
public class ApiKeyAndRateLimitFilter extends OncePerRequestFilter {

    private final AppSecurityProperties securityProperties;
    private final AppRateLimitProperties rateLimitProperties;
    private final SlidingWindowRateLimiter rateLimiter;
    private final ObjectMapper objectMapper;
    private final AntPathMatcher pathMatcher = new AntPathMatcher();

    public ApiKeyAndRateLimitFilter(
            AppSecurityProperties securityProperties,
            AppRateLimitProperties rateLimitProperties,
            SlidingWindowRateLimiter rateLimiter,
            ObjectMapper objectMapper
    ) {
        this.securityProperties = securityProperties;
        this.rateLimitProperties = rateLimitProperties;
        this.rateLimiter = rateLimiter;
        this.objectMapper = objectMapper;
    }

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        if (request.getDispatcherType() == jakarta.servlet.DispatcherType.ASYNC) {
            // SSE 子请求不再重复做鉴权/限流（主请求已做过一次）
            return true;
        }
        return false;
    }

    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain
    ) throws ServletException, IOException {
        if (HttpMethod.OPTIONS.matches(request.getMethod())) {
            filterChain.doFilter(request, response);
            return;
        }
        String uri = request.getRequestURI();
        if (isPublicPath(uri)) {
            filterChain.doFilter(request, response);
            return;
        }
        if (!isApiKeyValid(request)) {
            writeJson(
                    response,
                    HttpServletResponse.SC_UNAUTHORIZED,
                    new ApiErrorResponse("UNAUTHORIZED", "缺少或无效的 " + this.securityProperties.getApiKeyHeader())
            );
            return;
        }
        if (this.rateLimitProperties.isEnabled()) {
            String clientIp = ClientIpUtil.resolve(request);
            if (!this.rateLimiter.tryAcquire(clientIp, this.rateLimitProperties.getPerMinute())) {
                writeJson(
                        response,
                        429,
                        new ApiErrorResponse("RATE_LIMITED", "请求过于频繁，请稍后再试")
                );
                return;
            }
        }
        filterChain.doFilter(request, response);
    }

    private boolean isPublicPath(String uri) {
        for (String pattern : this.securityProperties.getPublicPaths()) {
            if (this.pathMatcher.match(pattern, uri)) {
                return true;
            }
        }
        return false;
    }

    private boolean isApiKeyValid(HttpServletRequest request) {
        String expected = this.securityProperties.getExpectedApiKey();
        if (expected == null || expected.isEmpty()) {
            // 未配置则不做密钥校验（仅白名单 + 限流若开启）
            return true;
        }
        String header = request.getHeader(this.securityProperties.getApiKeyHeader());
        return expected.equals(header);
    }

    private void writeJson(HttpServletResponse response, int status, ApiErrorResponse body) throws IOException {
        if (response.isCommitted()) {
            return;
        }
        response.setStatus(status);
        response.setContentType(MediaType.APPLICATION_JSON_VALUE);
        response.setCharacterEncoding("utf-8");
        this.objectMapper.writeValue(response.getWriter(), body);
    }
}
