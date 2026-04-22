package com.aimodel.javademo.config;

import java.util.ArrayDeque;
import java.util.Deque;
import java.util.concurrent.ConcurrentHashMap;

import org.springframework.stereotype.Component;

/**
 * 内存滑动窗口限流：按 key（此处为 IP 字符串）独立计数。窗口长度 60s，超过 <code>maxPerWindow</code> 返回 <code>false</code>。
 */
@Component
public class SlidingWindowRateLimiter {

    private static final long WINDOW_MILLIS = 60_000L;

    private final ConcurrentHashMap<String, Deque<Long>> buckets = new ConcurrentHashMap<>();

    /**
     * @return <code>true</code> 表示放行并记入一次；<code>false</code> 表示本窗口内已超过配额。
     */
    public boolean tryAcquire(String key, int maxPerWindow) {
        if (maxPerWindow <= 0) {
            return true;
        }
        long now = System.currentTimeMillis();
        long windowStart = now - WINDOW_MILLIS;
        Deque<Long> q = this.buckets.computeIfAbsent(key, k -> new ArrayDeque<>());
        synchronized (q) {
            while (!q.isEmpty() && q.peekFirst() < windowStart) {
                q.pollFirst();
            }
            if (q.size() >= maxPerWindow) {
                return false;
            }
            q.addLast(now);
        }
        return true;
    }
}
