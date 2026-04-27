package com.aimodel.javademo.api.dto.vector;

import java.util.ArrayList;
import java.util.List;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * Python FastAPI 返回体；字段名与第 3 周课表 <code>results</code> 一致，便于第 4 周 RAG 衔接。
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public class VectorSearchResponseBody {

    private List<VectorChunkItem> results = new ArrayList<>();
    private String model;
    @JsonProperty("memory_layer")
    private String memoryLayer;

    public List<VectorChunkItem> getResults() {
        return results;
    }

    public void setResults(List<VectorChunkItem> results) {
        this.results = results;
    }

    public String getModel() {
        return model;
    }

    public void setModel(String model) {
        this.model = model;
    }

    public String getMemoryLayer() {
        return memoryLayer;
    }

    public void setMemoryLayer(String memoryLayer) {
        this.memoryLayer = memoryLayer;
    }
}
