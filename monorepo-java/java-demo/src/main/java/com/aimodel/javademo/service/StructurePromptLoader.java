package com.aimodel.javademo.service;

import java.io.IOException;
import java.nio.charset.StandardCharsets;

import com.aimodel.javademo.config.AppStructureProperties;

import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Component;
import org.springframework.util.StreamUtils;

/**
 * 从 <code>classpath:prompts/structure-v1.txt</code> / <code>structure-v2.txt</code> 加载外置 system 提示词。
 */
@Component
public class StructurePromptLoader {

    private final AppStructureProperties properties;

    public StructurePromptLoader(AppStructureProperties properties) {
        this.properties = properties;
    }

    public String loadSystemPrompt() {
        String v = this.properties.getPromptVersion().trim().toLowerCase();
        if (!v.startsWith("v")) {
            v = "v" + v;
        }
        String path = "prompts/structure-" + v + ".txt";
        var resource = new ClassPathResource(path);
        if (!resource.exists()) {
            throw new IllegalStateException("未找到外置提示词: " + path + "，请检查 app.structure.prompt-version 与资源文件。");
        }
        try {
            return StreamUtils.copyToString(resource.getInputStream(), StandardCharsets.UTF_8).trim();
        } catch (IOException e) {
            throw new IllegalStateException("无法读取: " + path, e);
        }
    }
}
