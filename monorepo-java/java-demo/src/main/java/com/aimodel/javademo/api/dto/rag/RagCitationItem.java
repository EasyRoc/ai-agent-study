package com.aimodel.javademo.api.dto.rag;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * 第 4 周 RAG 引用项，与 Python <code>POST /rag/ask</code> 的 <code>citations[]</code> 对齐。
 */
public class RagCitationItem {

    private String id;
    private String excerpt;

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getExcerpt() {
        return excerpt;
    }

    public void setExcerpt(String excerpt) {
        this.excerpt = excerpt;
    }
}
