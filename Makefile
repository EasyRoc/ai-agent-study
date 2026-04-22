# 第 0 周第 3 天可选：双端健康检查（需已配置密钥，见根 README「第 3 天」）
.PHONY: health-py health-java health

# Python：不需要单独起服务，直接跑脚本
health-py:
	cd monorepo-py && python scripts/health_chat.py

# Java：需本机已启动 java-demo（另开终端: cd monorepo-java/java-demo && mvn spring-boot:run）
health-java:
	curl -sS http://localhost:8080/api/v1/health/llm || echo "(失败：请先启动 java-demo 且端口 8080 未被占用)"

# 顺序执行：先 Python 探针，再 Java HTTP（若未起 Java 会失败，属预期）
health: health-py
	@echo "---"
	@$(MAKE) health-java
