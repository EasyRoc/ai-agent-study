package com.aimodel.javademo.config;

import java.time.Duration;

import io.netty.channel.ChannelOption;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.reactive.ReactorClientHttpConnector;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.netty.http.client.HttpClient;

/**
 * 调 Python 向量 HTTP 的 {@link WebClient}：连接/读超时与课表「约 5s」一致。
 */
@Configuration
public class VectorWebClientConfiguration {

    @Bean
    @Qualifier("vectorServiceWebClient")
    public WebClient vectorServiceWebClient(AppVectorProperties props) {
        HttpClient httpClient = HttpClient.create()
                .option(ChannelOption.CONNECT_TIMEOUT_MILLIS, props.getConnectTimeoutMs())
                .responseTimeout(Duration.ofMillis(props.getReadTimeoutMs()));
        return WebClient.builder()
                .baseUrl(props.getBaseUrl().replaceAll("/$", ""))
                .clientConnector(new ReactorClientHttpConnector(httpClient))
                .build();
    }

    /**
     * 第 4 周 RAG：同基址、更长读超时，调 <code>POST /rag/ask</code>。
     */
    @Bean
    @Qualifier("ragServiceWebClient")
    public WebClient ragServiceWebClient(AppVectorProperties props) {
        HttpClient httpClient = HttpClient.create()
                .option(ChannelOption.CONNECT_TIMEOUT_MILLIS, props.getConnectTimeoutMs())
                .responseTimeout(Duration.ofMillis(props.getRagReadTimeoutMs()));
        return WebClient.builder()
                .baseUrl(props.getBaseUrl().replaceAll("/$", ""))
                .clientConnector(new ReactorClientHttpConnector(httpClient))
                .build();
    }
}
