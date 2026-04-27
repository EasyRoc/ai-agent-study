package com.aimodel.javademo.web;

import com.aimodel.javademo.api.dto.vector.VectorSearchResponseBody;
import com.aimodel.javademo.service.VectorServiceClient;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

/**
 * 第 3 周：经网关转调 Python <code>POST /search</code>，与课表 <code>GET /api/v1/vector-demo?q=</code> 对齐。
 */
@RestController
@RequestMapping(ChatV1Controller.BASE)
public class VectorV1Controller {

    private final VectorServiceClient vectorServiceClient;

    public VectorV1Controller(VectorServiceClient vectorServiceClient) {
        this.vectorServiceClient = vectorServiceClient;
    }

    @GetMapping("/vector-demo")
    public VectorSearchResponseBody vectorDemo(
            @RequestParam("q") String q,
            @RequestParam(value = "k", defaultValue = "3") int k
    ) {
        if (q == null || q.isBlank()) {
            throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "q 不能为空");
        }
        return this.vectorServiceClient.search(q.trim(), k);
    }
}
