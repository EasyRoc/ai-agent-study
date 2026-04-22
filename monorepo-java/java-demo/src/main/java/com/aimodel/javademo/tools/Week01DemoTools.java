package com.aimodel.javademo.tools;

import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;

import org.springframework.ai.tool.annotation.Tool;
import org.springframework.ai.tool.annotation.ToolParam;
import org.springframework.stereotype.Component;

/**
 * 第 1 周 Function Calling 演示工具：与 Python {@code fc_min.py} 中两枚函数语义对齐，便于双端对比。
 */
@Component
public class Week01DemoTools {

    @Tool(name = "add_numbers", description = "计算两个实数之和")
    public double addNumbers(
            @ToolParam(description = "第一个加数") double a,
            @ToolParam(description = "第二个加数") double b
    ) {
        return a + b;
    }

    @Tool(name = "server_time_iso", description = "当前时间的 ISO-8601 字符串；时区为 IANA 名如 Asia/Shanghai，缺省为系统默认")
    public String serverTimeIso(
            @ToolParam(description = "IANA 时区，可空", required = false) String timezone
    ) {
        ZoneId z = (timezone == null || timezone.isBlank())
                ? ZoneId.systemDefault()
                : ZoneId.of(timezone.trim());
        return ZonedDateTime.now(z).format(DateTimeFormatter.ISO_OFFSET_DATE_TIME);
    }
}
