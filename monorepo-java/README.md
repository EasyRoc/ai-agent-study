# monorepo-java

本目录为 **Java** 子工程：Spring Boot 3 + **Spring AI Alibaba** 对外网关、鉴权、SSE 等，与 `../monorepo-py` **代码分离**。

## 子工程

| 目录 | 说明 |
|------|------|
| [`java-demo/`](./java-demo/) | 第 0 周起：DashScope + 探活；第 1 周对话接口需 **`X-API-Key: demo`**、内存按 IP 限流；**`POST /api/v1/fc/chat`**（Function Calling）；第 6 天联调见 [根 `README` 第1周`#week1-acceptance`](../README.md#week1-acceptance)（详见 [`java-demo/README`](./java-demo/README.md)） |

## 第 0 周：建工程

- 依赖与 **BOM** 以 [Spring AI Alibaba 官方仓库](https://github.com/alibaba/spring-ai-alibaba) 当前文档为准。  
- 第 0 周第 2 天目标：**已落在 `java-demo`**，本地 `cd java-demo && mvn spring-boot:run` 可验证。  

## 与 Python 的协作

- 后续若 Python 提供向量/RAG 的 HTTP 服务，Java 用 `WebClient` / `RestTemplate` 调用其 **URL** 即可，**本仓库** 仅约定**兄弟目录** 分工，不强制 monolithic 合仓编译。
