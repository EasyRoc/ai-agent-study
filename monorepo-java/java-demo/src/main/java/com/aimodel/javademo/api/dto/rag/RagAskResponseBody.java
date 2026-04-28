package com.aimodel.javademo.api.dto.rag;

import java.util.ArrayList;
import java.util.List;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * 与 Python <code>/rag/ask</code> 响应一致。
 */
public class RagAskResponseBody {

    private String answer;

    private List<RagCitationItem> citations = new ArrayList<>();

    /** 与 Python <code>cited_ids</code> 一致：模型在 citation_ids 里声明的 id，条数可少于 <code>citations</code> */
    @JsonProperty("cited_ids")
    private List<String> citedIds = new ArrayList<>();

    @JsonProperty("memory_layer")
    /** L2 企业知识（非 L0 会话） */
    private String memoryLayer = "L2_rag";

    public String getAnswer() {
        return answer;
    }

    public void setAnswer(String answer) {
        this.answer = answer;
    }

    public List<RagCitationItem> getCitations() {
        return citations;
    }

    public void setCitations(List<RagCitationItem> citations) {
        this.citations = citations;
    }

    public List<String> getCitedIds() {
        return citedIds;
    }

    public void setCitedIds(List<String> citedIds) {
        this.citedIds = citedIds;
    }

    public String getMemoryLayer() {
        return memoryLayer;
    }

    public void setMemoryLayer(String memoryLayer) {
        this.memoryLayer = memoryLayer;
    }
}
