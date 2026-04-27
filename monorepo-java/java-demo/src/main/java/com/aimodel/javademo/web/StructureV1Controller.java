package com.aimodel.javademo.web;

import com.aimodel.javademo.api.dto.StructureRequest;
import com.aimodel.javademo.api.dto.StructureResponse;
import com.aimodel.javademo.service.StructureExtractionService;

import jakarta.validation.Valid;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 第 2 周：<code>POST /api/v1/structure</code> —— Structured Output + L0 <code>sessionId</code>。
 */
@RestController
@RequestMapping(ChatV1Controller.BASE)
public class StructureV1Controller {

    private final StructureExtractionService extractionService;

    public StructureV1Controller(StructureExtractionService extractionService) {
        this.extractionService = extractionService;
    }

    @PostMapping(
            value = "/structure",
            consumes = MediaType.APPLICATION_JSON_VALUE,
            produces = MediaType.APPLICATION_JSON_VALUE
    )
    public StructureResponse structure(@RequestBody @Valid StructureRequest request) {
        return this.extractionService.extract(request.getRaw(), request.getSessionId());
    }
}
