# OpenManus 禁止事项

- 不要硬编码 API Key
- 不要提交 `config/config.toml`（包含敏感信息）
- 不要将 `workspace/` 和 `logs/` 目录提交到版本控制
- 不要在同步函数中调用异步函数（除非使用 `asyncio.run()`）
