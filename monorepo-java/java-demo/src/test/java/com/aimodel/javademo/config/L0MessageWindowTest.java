package com.aimodel.javademo.config;

import java.util.ArrayList;
import java.util.List;

import org.junit.jupiter.api.Test;
import org.springframework.ai.chat.messages.UserMessage;

import static org.junit.jupiter.api.Assertions.assertEquals;

class L0MessageWindowTest {

    @Test
    void keepLastNTrimsFromFront() {
        List<org.springframework.ai.chat.messages.Message> in = new ArrayList<>();
        for (int i = 0; i < 8; i++) {
            in.add(new UserMessage("m" + i));
        }
        var out = L0MessageWindow.keepLastN(in, 4);
        assertEquals(4, out.size());
        assertEquals("m4", ((UserMessage) out.get(0)).getText());
    }
}
