package com.aimodel.javademo.config;

import java.util.ArrayList;
import java.util.List;

import org.springframework.ai.chat.messages.Message;

/**
 * L0 滑窗：只保留最后 <code>max</code> 条消息（与 checkpointer 里累积的 full history 在进模型前对齐）。
 */
public final class L0MessageWindow {

    private L0MessageWindow() {
    }

    public static List<Message> keepLastN(List<Message> full, int max) {
        if (full == null || full.isEmpty()) {
            return List.of();
        }
        if (max <= 0) {
            return List.of();
        }
        if (full.size() <= max) {
            return new ArrayList<>(full);
        }
        return new ArrayList<>(full.subList(full.size() - max, full.size()));
    }
}
