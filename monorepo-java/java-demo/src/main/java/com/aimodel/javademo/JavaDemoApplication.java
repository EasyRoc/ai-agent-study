package com.aimodel.javademo;

import com.aimodel.javademo.config.AppRateLimitProperties;
import com.aimodel.javademo.config.AppSecurityProperties;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.context.properties.EnableConfigurationProperties;

/**
 * Spring Boot 入口：@SpringBootApplication = @Configuration + @EnableAutoConfiguration + @ComponentScan。
 * Spring AI Alibaba 的 DashScope 自动配置会随类路径中的 starter 生效（见 application.yml）。
 */
@SpringBootApplication
@EnableConfigurationProperties({AppSecurityProperties.class, AppRateLimitProperties.class})
public class JavaDemoApplication {

    public static void main(String[] args) {
        SpringApplication.run(JavaDemoApplication.class, args);
    }
}
