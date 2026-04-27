package com.aimodel.javademo.api.dto.vector;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

/**
 * 与 Python <code>POST /search</code> 中 results 单条对齐。
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public class VectorChunkItem {

    private String id;
    private String text;
    private double score;

    public String getId() {
        return id;
    }

    public void setId(String id) {
        this.id = id;
    }

    public String getText() {
        return text;
    }

    public void setText(String text) {
        this.text = text;
    }

    public double getScore() {
        return score;
    }

    public void setScore(double score) {
        this.score = score;
    }
}
