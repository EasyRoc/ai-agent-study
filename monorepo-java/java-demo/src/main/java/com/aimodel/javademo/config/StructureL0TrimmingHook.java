package com.aimodel.javademo.config;

import java.util.ArrayList;
import java.util.List;

import com.alibaba.cloud.ai.graph.RunnableConfig;
import com.alibaba.cloud.ai.graph.agent.hook.HookPosition;
import com.alibaba.cloud.ai.graph.agent.hook.HookPositions;
import com.alibaba.cloud.ai.graph.agent.hook.messages.AgentCommand;
import com.alibaba.cloud.ai.graph.agent.hook.messages.MessagesModelHook;
import com.alibaba.cloud.ai.graph.agent.hook.messages.UpdatePolicy;

import org.springframework.ai.chat.messages.Message;
import org.springframework.stereotype.Component;

/**
 * L0 滑窗：在进模型前裁剪 <code>messages</code>，与 <code>app.structure.l0.max-messages</code> 一致；配合 {@link com.alibaba.cloud.ai.graph.checkpoint.savers.MemorySaver} 的 thread 状态使用。
 * 与官方 <a href="https://java2ai.com/docs/frameworks/agent-framework/tutorials/memory">MessagesModelHook</a> 文档同一套路。
 */
@Component
@HookPositions({HookPosition.BEFORE_MODEL})
public class StructureL0TrimmingHook extends MessagesModelHook {

    private final AppStructureProperties structureProperties;

    public StructureL0TrimmingHook(AppStructureProperties structureProperties) {
        this.structureProperties = structureProperties;
    }

    @Override
    public String getName() {
        return "structure_l0_trim";
    }

    @Override
    public AgentCommand beforeModel(List<Message> previousMessages, RunnableConfig config) {
        if (previousMessages == null) {
            return new AgentCommand(List.of());
        }
        int max = this.structureProperties.getL0().getMaxMessages();
        List<Message> next = L0MessageWindow.keepLastN(previousMessages, max);
        if (next.size() == previousMessages.size()) {
            return new AgentCommand(previousMessages);
        }
        return new AgentCommand(new ArrayList<>(next), UpdatePolicy.REPLACE);
    }
}
